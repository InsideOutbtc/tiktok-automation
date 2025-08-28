# src/api/video_processor.py - NEW FILE
import os
import json
import time
import traceback
import logging
from pathlib import Path
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing components (with fallback)
try:
    from src.core.smart_clipper import SmartClipper
    from src.core.video_editor import VideoEditor
    logger.info("Successfully imported video processing modules")
except ImportError as e:
    logger.warning(f"Could not import video modules: {e}. Using fallback processing.")
    SmartClipper = None
    VideoEditor = None

video_processor = Blueprint('video_processor', __name__)

# Check multiple possible upload locations
POSSIBLE_UPLOAD_PATHS = [
    Path('/app/uploads'),         # Docker volume mount
    Path('/app/input'),          # Mac transit might use this
    Path('/tmp/uploads'),         # Alternative location
    Path('./uploads'),           # Local testing
    Path('./input')              # Local testing alternative
]

# Find the actual upload folder
UPLOAD_FOLDER = None
for path in POSSIBLE_UPLOAD_PATHS:
    if path.exists():
        UPLOAD_FOLDER = path
        logger.info(f"Using upload folder: {UPLOAD_FOLDER}")
        break

if not UPLOAD_FOLDER:
    UPLOAD_FOLDER = Path('/tmp/uploads')
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    logger.warning(f"No existing upload folder found, created: {UPLOAD_FOLDER}")

CLIPS_FOLDER = Path('/tmp/clips')
OUTPUT_FOLDER = Path('/app/output')
PROCESSING_STATUS_FILE = Path('/tmp/processing_status.json')

# Ensure folders exist
for folder in [CLIPS_FOLDER, OUTPUT_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# Supported video formats
SUPPORTED_FORMATS = ['.mp4', '.webm', '.mkv', '.mov', '.avi', '.m4v']

# Processing status tracking
processing_status = {}

def cleanup_old_files():
    """Remove clips and temp files older than 7 days"""
    try:
        current_time = time.time()
        seven_days_ago = current_time - (7 * 24 * 60 * 60)
        
        # Clean clips folder
        for clip in CLIPS_FOLDER.glob("*"):
            if clip.stat().st_mtime < seven_days_ago:
                clip.unlink()
                logger.info(f"Deleted old clip: {clip.name}")
        
        # Clean upload folder (keep only last 48 hours)
        two_days_ago = current_time - (2 * 24 * 60 * 60)
        for upload in UPLOAD_FOLDER.glob("*"):
            if upload.stat().st_mtime < two_days_ago:
                upload.unlink()
                logger.info(f"Deleted old upload: {upload.name}")
                
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

def update_processing_status(video_id, status, message="", progress=0):
    """Update and persist processing status"""
    processing_status[video_id] = {
        'status': status,  # pending, processing, completed, failed
        'message': message,
        'progress': progress,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save to file for persistence
    try:
        with open(PROCESSING_STATUS_FILE, 'w') as f:
            json.dump(processing_status, f)
    except:
        pass

def find_video_file(video_id):
    """Find video file with any supported extension"""
    # First check if video_id already has extension
    for ext in SUPPORTED_FORMATS:
        if video_id.endswith(ext):
            video_path = UPLOAD_FOLDER / video_id
            if video_path.exists():
                return video_path
            # Try without double extension
            base_id = video_id.replace(ext, '')
            video_path = UPLOAD_FOLDER / f"{base_id}{ext}"
            if video_path.exists():
                return video_path
    
    # Try each supported format
    for ext in SUPPORTED_FORMATS:
        video_path = UPLOAD_FOLDER / f"{video_id}{ext}"
        if video_path.exists():
            return video_path
    
    return None

@video_processor.route('/api/process/<video_id>', methods=['POST'])
def process_video(video_id):
    """Process uploaded video into TikTok clips"""
    
    # Run cleanup first (non-blocking)
    cleanup_old_files()
    
    # Update status to processing
    update_processing_status(video_id, 'processing', 'Starting video processing...', 10)
    
    # Tier 1 Error Handling - Retry once on failure
    def attempt_processing():
        try:
            # Find uploaded video with any format
            video_path = find_video_file(video_id)
            if not video_path:
                logger.error(f"Video not found: {video_id}")
                update_processing_status(video_id, 'failed', 'Video file not found')
                return {'error': 'Video not found'}, 404
            
            logger.info(f"Processing video: {video_path}")
            update_processing_status(video_id, 'processing', 'Analyzing video...', 20)
            
            # Check file size (limit to 500MB to prevent memory issues)
            file_size = video_path.stat().st_size / (1024 * 1024)  # MB
            if file_size > 500:
                logger.warning(f"Video too large: {file_size}MB")
                update_processing_status(video_id, 'failed', f'Video too large: {file_size:.1f}MB')
                return {'error': f'Video too large: {file_size:.1f}MB (max 500MB)'}, 413
            
            # Initialize processors (with fallback)
            if SmartClipper is None:
                logger.info("Using fallback clip extraction")
                update_processing_status(video_id, 'processing', 'Using basic extraction...', 30)
                # Fallback: Basic clip extraction
                return basic_clip_extraction(video_path, video_id)
            
            # Smart clip extraction
            update_processing_status(video_id, 'processing', 'Extracting interesting moments...', 40)
            clipper = SmartClipper(config={
                'min_duration': 15,
                'max_duration': 30,  # Cap at 30 for TikTok sweet spot
                'target_clips': 6,  # More clips for variety
                'quality_threshold': 0.7,
                'preferred_durations': [15, 20, 25, 30],  # Target these specific durations
                'variety_mode': True  # Try to vary clip lengths
            })
            
            # Extract interesting segments
            clips = clipper.extract_clips(str(video_path))
            
            if not clips:
                logger.warning("Smart extraction failed, using time-based splitting")
                update_processing_status(video_id, 'processing', 'Using time-based splitting...', 50)
                # Tier 2: Fallback to time-based splitting
                clips = fallback_time_split(video_path)
            
            # Process each clip
            processed_clips = []
            editor = VideoEditor() if VideoEditor else None
            
            total_clips = len(clips)
            for idx, clip in enumerate(clips):
                progress = 50 + (40 * (idx / total_clips))
                update_processing_status(video_id, 'processing', 
                                       f'Processing clip {idx+1}/{total_clips}...', progress)
                
                clip_path = CLIPS_FOLDER / f"{video_id}_clip_{idx}.mp4"
                
                if editor:
                    # Professional editing
                    edited = editor.process_clip(
                        clip,
                        output_path=str(clip_path),
                        options={
                            'aspect_ratio': '9:16',  # TikTok vertical
                            'resolution': (1080, 1920),
                            'add_captions': True,
                            'add_hook': True,
                            'optimize_for_tiktok': True
                        }
                    )
                else:
                    # Basic processing
                    edited = basic_process_clip(clip, clip_path)
                
                processed_clips.append({
                    'id': f"{video_id}_clip_{idx}",
                    'path': str(clip_path),
                    'duration': clip.get('duration', 30),
                    'score': clip.get('score', 0.5),
                    'hook': clip.get('hook', 'Check this out!')
                })
            
            # Save processing results
            save_processing_results(video_id, processed_clips)
            update_processing_status(video_id, 'completed', 
                                   f'Successfully generated {len(processed_clips)} clips', 100)
            
            return {
                'video_id': video_id,
                'clips_generated': len(processed_clips),
                'clips': processed_clips,
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            traceback.print_exc()
            update_processing_status(video_id, 'failed', str(e))
            return None
    
    # Tier 1: Try once, retry on failure
    result = attempt_processing()
    if result:
        return jsonify(result)
    
    # Retry once
    result = attempt_processing()
    if result:
        return jsonify(result)
    
    # Tier 3: Fallback to basic splitting
    return jsonify(emergency_basic_split(video_id))

def basic_clip_extraction(video_path, video_id):
    """Fallback: Extract clips with varied durations for TikTok variety"""
    import subprocess
    import random
    
    clips = []
    duration = get_video_duration(video_path)
    
    # Update status
    update_processing_status(video_id, 'processing', 'Using varied clip extraction...', 60)
    
    # TikTok optimal durations - mix of lengths for variety
    clip_durations = [15, 20, 25, 30, 15, 20]  # 6 clips with varied lengths
    random.shuffle(clip_durations)  # Randomize order for variety
    
    # Calculate distribution across video
    total_clips = min(len(clip_durations), 6)
    if duration < 60:  # Very short video
        total_clips = 2
        clip_durations = [15, 15]
    
    # Space clips evenly across the video
    segment_length = duration / (total_clips + 1)  # +1 for padding
    
    clips_created = 0
    for i, clip_duration in enumerate(clip_durations[:total_clips]):
        # Calculate start time - distributed across video
        if i == 0:
            # First clip from beginning
            start_time = random.uniform(0, min(10, duration * 0.1))
        elif i == total_clips - 1:
            # Last clip from near end
            start_time = max(0, duration - clip_duration - random.uniform(5, 15))
        else:
            # Middle clips distributed
            base_position = segment_length * i
            variation = segment_length * 0.3  # 30% variation
            start_time = base_position + random.uniform(-variation, variation)
        
        # Ensure we don't exceed video duration
        start_time = max(0, min(start_time, duration - clip_duration))
        
        if start_time + clip_duration > duration:
            continue
        
        progress = 60 + (30 * (clips_created / total_clips))
        update_processing_status(video_id, 'processing', 
                               f'Extracting {clip_duration}s clip {clips_created+1}/{total_clips}...', progress)
        
        clip_path = CLIPS_FOLDER / f"{video_id}_clip_{clips_created}_{clip_duration}s.mp4"
        
        # Use FFmpeg with TikTok optimization
        cmd = [
            'ffmpeg', '-i', str(video_path),
            '-ss', str(start_time),
            '-t', str(clip_duration),
            '-c:v', 'libx264',
            '-preset', 'fast',  # Faster processing
            '-crf', '23',  # Good quality
            '-c:a', 'aac',
            '-b:a', '128k',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
            '-y', str(clip_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error for clip {clips_created}: {result.stderr[:200]}")
        
        if clip_path.exists():
            # Calculate basic quality score based on position and duration
            position_score = 0.5
            if i == 0:  # Beginning clips often have intros
                position_score = 0.7
            elif i == total_clips - 1:  # End clips might have calls-to-action
                position_score = 0.6
            else:  # Middle clips tend to have best content
                position_score = 0.8 + (random.random() * 0.2)
            
            # Shorter clips get slight score boost (more likely to be watched fully)
            duration_score = 1.0 - (clip_duration - 15) / 30  # 15s = 1.0, 30s = 0.5
            
            final_score = (position_score * 0.7 + duration_score * 0.3)
            
            clips.append({
                'id': f"{video_id}_clip_{clips_created}",
                'path': str(clip_path),
                'duration': clip_duration,
                'start_time': round(start_time, 1),
                'score': round(final_score, 2),
                'hook': f"{clip_duration}s clip from {format_time(start_time)}"
            })
            clips_created += 1
    
    # Sort clips by score (best first)
    clips.sort(key=lambda x: x['score'], reverse=True)
    
    update_processing_status(video_id, 'completed', 
                           f'Generated {len(clips)} varied clips', 100)
    
    # Save results
    save_processing_results(video_id, clips)
    
    return {
        'video_id': video_id,
        'clips_generated': len(clips),
        'clips': clips,
        'status': 'basic_processing',
        'message': f'Created {len(clips)} clips with durations: {[c["duration"] for c in clips]}'
    }

def format_time(seconds):
    """Format seconds to MM:SS"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def fallback_time_split(video_path):
    """Fallback method to split video into time-based segments"""
    # Simple implementation - returns empty list for now
    # Would implement actual time-based splitting
    return []

def basic_process_clip(clip, clip_path):
    """Basic clip processing without advanced editing"""
    # Simple implementation - just copy the clip
    # Would implement actual basic processing
    return clip

def emergency_basic_split(video_id):
    """Emergency fallback when everything else fails"""
    update_processing_status(video_id, 'failed', 'All processing methods failed')
    return {
        'video_id': video_id,
        'clips_generated': 0,
        'clips': [],
        'status': 'failed',
        'error': 'Unable to process video'
    }

def get_video_duration(video_path):
    """Get video duration using FFprobe"""
    import subprocess
    
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(video_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 600  # Default 10 minutes

def save_processing_results(video_id, clips):
    """Save processing results for dashboard"""
    results_file = OUTPUT_FOLDER / 'processing_results.json'
    
    # Load existing results
    if results_file.exists():
        with open(results_file, 'r') as f:
            results = json.load(f)
    else:
        results = {}
    
    # Add new results
    results[video_id] = {
        'timestamp': datetime.now().isoformat(),
        'clips': clips,
        'status': 'ready_for_download'
    }
    
    # Save
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

@video_processor.route('/api/process/status/<video_id>', methods=['GET'])
def get_process_status(video_id):
    """Check processing status for a video"""
    # Load status from file if not in memory
    if video_id not in processing_status and PROCESSING_STATUS_FILE.exists():
        try:
            with open(PROCESSING_STATUS_FILE, 'r') as f:
                saved_status = json.load(f)
                processing_status.update(saved_status)
        except:
            pass
    
    if video_id in processing_status:
        return jsonify(processing_status[video_id])
    
    return jsonify({
        'status': 'unknown',
        'message': 'No processing information available'
    })

@video_processor.route('/api/clips', methods=['GET'])
def get_clips():
    """Get all processed clips for dashboard display"""
    results_file = OUTPUT_FOLDER / 'processing_results.json'
    
    if not results_file.exists():
        return jsonify({'clips': []})
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    # Flatten clips for display
    all_clips = []
    for video_id, data in results.items():
        for clip in data.get('clips', []):
            clip['video_id'] = video_id
            clip['ready'] = Path(clip['path']).exists()
            all_clips.append(clip)
    
    return jsonify({
        'total_clips': len(all_clips),
        'clips': all_clips
    })

@video_processor.route('/api/download_clip/<clip_id>')
def download_clip(clip_id):
    """Download specific clip for manual TikTok upload"""
    # Find clip path
    results_file = OUTPUT_FOLDER / 'processing_results.json'
    if not results_file.exists():
        return jsonify({'error': 'No clips found'}), 404
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    for video_id, data in results.items():
        for clip in data.get('clips', []):
            if clip['id'] == clip_id:
                clip_path = Path(clip['path'])
                if clip_path.exists():
                    return send_file(
                        str(clip_path),
                        as_attachment=True,
                        download_name=f"{clip_id}.mp4"
                    )
    
    return jsonify({'error': 'Clip not found'}), 404