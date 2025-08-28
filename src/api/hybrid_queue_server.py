# src/api/hybrid_queue_server.py on DigitalOcean
from flask import Flask, request, jsonify
from pathlib import Path
import subprocess
import json
from datetime import datetime
from sqlalchemy import create_engine
import logging

app = Flask(__name__)
BASE_DIR = Path('/app')
UPLOAD_DIR = BASE_DIR / 'uploads'
CLIPS_DIR = BASE_DIR / 'clips'
UPLOAD_DIR.mkdir(exist_ok=True)
CLIPS_DIR.mkdir(exist_ok=True)

class QueueProcessor:
    """Manages queue and processes uploaded videos"""
    
    def __init__(self):
        self.db = create_engine('sqlite:///queue.db')
        self.setup_database()
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Create queue table - Maximum Velocity, no confirmations"""
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS video_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                platform TEXT DEFAULT 'youtube',
                status TEXT DEFAULT 'pending',
                title TEXT,
                creator TEXT,
                downloaded_at TIMESTAMP,
                processed_at TIMESTAMP,
                clips_generated INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                error_tier INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    def add_to_queue(self, urls):
        """Add videos to download queue"""
        for url_data in urls:
            # Tier 1 error handling - continue on duplicate
            try:
                self.db.execute(
                    "INSERT INTO video_queue (url, platform, creator) VALUES (?, ?, ?)",
                    [url_data['url'], url_data.get('platform', 'youtube'), url_data.get('creator', 'unknown')]
                )
            except:
                pass  # Skip duplicates
                
    def get_pending_batch(self, limit=20):
        """Get next batch for Mac to download"""
        results = self.db.execute("""
            SELECT id, url, platform, creator 
            FROM video_queue 
            WHERE status = 'pending' 
            AND error_tier < 4
            ORDER BY created_at ASC 
            LIMIT ?
        """, [limit]).fetchall()
        
        return [dict(row) for row in results]
    
    def process_uploaded_video(self, video_id, file_path):
        """Process video into clips using existing smart_clipper"""
        try:
            # Update status
            self.db.execute(
                "UPDATE video_queue SET status = 'processing', downloaded_at = ? WHERE id = ?",
                [datetime.now(), video_id]
            )
            
            # Use existing video processing pipeline
            clips = self.extract_clips(file_path, video_id)
            
            # Update with results
            self.db.execute(
                "UPDATE video_queue SET status = 'completed', clips_generated = ?, processed_at = ? WHERE id = ?",
                [len(clips), datetime.now(), video_id]
            )
            
            # Delete original to save space (Tier 3 disk management)
            Path(file_path).unlink()
            
            return {'success': True, 'clips': len(clips)}
            
        except Exception as e:
            # Tier 2-3 error handling
            self.handle_processing_error(video_id, str(e))
            return {'success': False, 'error': str(e)}
    
    def extract_clips(self, video_path, video_id):
        """Extract 2-3 clips per video"""
        clips = []
        video_file = Path(video_path)
        
        # Simple clip extraction (replace with smart_clipper.py logic)
        # For now, split into 30-second segments
        output_pattern = str(CLIPS_DIR / f"{video_id}_clip_%03d.mp4")
        
        cmd = [
            'ffmpeg', '-i', str(video_file),
            '-c', 'copy', '-map', '0',
            '-segment_time', '30',
            '-f', 'segment',
            '-reset_timestamps', '1',
            output_pattern
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            clips = list(CLIPS_DIR.glob(f"{video_id}_clip_*.mp4"))
            
        return clips
    
    def handle_processing_error(self, video_id, error):
        """Implement Tier 1-4 error handling"""
        self.db.execute("""
            UPDATE video_queue 
            SET error_count = error_count + 1,
                error_tier = CASE 
                    WHEN error_count < 2 THEN 1
                    WHEN error_count < 4 THEN 2  
                    WHEN error_count < 6 THEN 3
                    ELSE 4
                END,
                status = CASE
                    WHEN error_count < 6 THEN 'pending'
                    ELSE 'failed'
                END
            WHERE id = ?
        """, [video_id])

# Initialize processor
processor = QueueProcessor()

@app.route('/api/queue/pending', methods=['GET'])
def get_pending():
    """Mac polls this to get videos to download"""
    batch = processor.get_pending_batch()
    return jsonify({'videos': batch, 'count': len(batch)})

@app.route('/api/video/upload', methods=['POST'])
def upload_video():
    """Mac uploads video here, then deletes locally"""
    video_id = request.form.get('video_id')
    video_file = request.files.get('video')
    
    if not video_file or not video_id:
        return jsonify({'error': 'Missing video or ID'}), 400
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{video_id}.mp4"
    video_file.save(str(file_path))
    
    # Mark as downloaded
    processor.db.execute(
        "UPDATE video_queue SET status = 'downloaded' WHERE id = ?",
        [video_id]
    )
    
    # Trigger processing (async in production)
    result = processor.process_uploaded_video(video_id, file_path)
    
    return jsonify(result)

@app.route('/api/clips/ready', methods=['GET'])
def get_ready_clips():
    """Get processed clips ready for review"""
    clips = []
    for clip_file in CLIPS_DIR.glob('*.mp4'):
        clips.append({
            'filename': clip_file.name,
            'size_mb': clip_file.stat().st_size / (1024*1024),
            'created': datetime.fromtimestamp(clip_file.stat().st_mtime).isoformat()
        })
    return jsonify({'clips': clips[:20]})  # Limit to 20 most recent

@app.route('/api/queue/seed', methods=['POST'])
def seed_queue():
    """Seed queue with target creators"""
    targets = [
        {'url': 'https://youtube.com/@sam_sulek', 'creator': 'sam_sulek'},
        {'url': 'https://youtube.com/@thetrentwins', 'creator': 'trentwins'},
        {'url': 'https://youtube.com/@ChrisBumstead', 'creator': 'cbum'},
    ]
    processor.add_to_queue(targets)
    return jsonify({'added': len(targets)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)