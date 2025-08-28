from flask import Flask, send_file, jsonify, request
import os
import glob
import json
import yt_dlp
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Increase upload limit to 500MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Use absolute paths
APP_DIR = os.environ.get('APP_DIR', '/app')
OUTPUT_DIR = os.path.join(APP_DIR, 'output')
UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
QUEUE_FILE = os.path.join(APP_DIR, 'queue_status.json')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_queue_status():
    """Load queue status from file"""
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_queue_status(status):
    """Save queue status to file"""
    with open(QUEUE_FILE, 'w') as f:
        json.dump(status, f)

@app.route('/')
def home():
    """Show list of videos ready to download"""
    # Use absolute path
    videos = glob.glob(os.path.join(OUTPUT_DIR, '*.mp4'))
    
    if not videos:
        return "<h1>No videos ready yet. Check back later!</h1>"
    
    html = "<h1>TikTok Videos Ready</h1><ul>"
    for video in videos:
        filename = os.path.basename(video)
        html += f'<li>{filename} - <a href="/download/{filename}">Download</a></li>'
    html += "</ul>"
    
    return html

@app.route('/download/<filename>')
def download(filename):
    """Download a video"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

@app.route('/health')
def health():
    """Health check for DigitalOcean"""
    return jsonify({"status": "healthy"})

@app.route('/api/upload', methods=['POST'])
def receive_video():
    """Receive video from Mac"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video'}), 400
    
    video_id = request.form.get('video_id', 'unknown')
    file = request.files['video']
    filename = f"{video_id}_{secure_filename(file.filename)}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
        
        # Mark as downloaded in queue
        queue_status = load_queue_status()
        queue_status[video_id] = {
            'status': 'downloaded',
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'size_mb': os.path.getsize(filepath) / (1024 * 1024)
        }
        save_queue_status(queue_status)
        
        # Here you'd trigger clip processing with smart_clipper.py
        # For now, just store it
        
        return jsonify({
            'success': True, 
            'filename': filename,
            'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/queue', methods=['GET'])
def get_queue():
    """Dynamically discover latest videos from target creators"""
    
    target_channels = [
        'https://www.youtube.com/@sam_sulek/videos',
        'https://www.youtube.com/@thetrentwins/videos',
        'https://www.youtube.com/@ChrisBumstead/videos',
        'https://www.youtube.com/@BradleyMartyn/videos',
        'https://www.youtube.com/@JeffNippard/videos',
        'https://www.youtube.com/@GregDoucette/videos',
    ]
    
    all_videos = []
    ydl_opts = {
        'extract_flat': True,
        'playlist_items': '1-3',  # Get 3 latest videos per channel
        'quiet': True,
        'no_warnings': True
    }
    
    for channel_url in target_channels:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                channel_name = info.get('channel', 'Unknown')
                
                for entry in info.get('entries', []):
                    if entry and entry.get('id'):
                        all_videos.append({
                            'id': entry['id'],
                            'url': f"https://www.youtube.com/watch?v={entry['id']}",
                            'title': entry.get('title', 'Unknown'),
                            'creator': channel_name,
                            'duration': entry.get('duration', 0)
                        })
        except Exception as e:
            print(f"Error getting videos from {channel_url}: {e}")
            continue
    
    # Filter out already downloaded
    queue_status = load_queue_status()
    pending = [
        v for v in all_videos 
        if v['id'] not in queue_status
    ]
    
    return jsonify(pending)

@app.route('/api/queue/status', methods=['GET'])
def queue_status():
    """Check download history"""
    status = load_queue_status()
    return jsonify({
        'downloaded_count': len(status),
        'videos': status
    })

@app.route('/api/queue/reset', methods=['POST'])
def reset_queue():
    """Reset queue to re-download everything"""
    save_queue_status({})
    return jsonify({'status': 'reset'})

@app.route('/dashboard')
def clip_dashboard():
    """Enhanced dashboard showing processed clips"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>TikTok Clips Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                background: #f0f2f5;
            }
            h1 { 
                color: #333; 
                border-bottom: 3px solid #00f2ea;
                padding-bottom: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #00f2ea;
            }
            .clips-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .clip-card {
                background: white;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .clip-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
            }
            .clip-info {
                margin: 10px 0;
            }
            .download-btn {
                background: #00f2ea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
                transition: background 0.2s;
            }
            .download-btn:hover {
                background: #00d4ce;
            }
            .process-btn {
                background: #ff0050;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 20px 0;
            }
            .queue-section {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <h1>🎥 TikTok Clips Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-videos">0</div>
                <div>Videos Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="total-clips">0</div>
                <div>Clips Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="ready-clips">0</div>
                <div>Ready to Post</div>
            </div>
        </div>
        
        <div class="queue-section">
            <h2>📥 Pending Videos</h2>
            <div id="pending-videos"></div>
            <button class="process-btn" onclick="processNext()">Process Next Video</button>
        </div>
        
        <h2>🎬 Available Clips</h2>
        <div class="clips-grid" id="clips-grid">
            Loading clips...
        </div>
        
        <script>
            async function loadClips() {
                try {
                    const response = await fetch('/api/clips');
                    const data = await response.json();
                    
                    document.getElementById('total-clips').textContent = data.total_clips;
                    document.getElementById('ready-clips').textContent = 
                        data.clips.filter(c => c.ready).length;
                    
                    const grid = document.getElementById('clips-grid');
                    
                    if (data.clips.length === 0) {
                        grid.innerHTML = '<p>No clips available. Process some videos first!</p>';
                        return;
                    }
                    
                    grid.innerHTML = data.clips.map(clip => `
                        <div class="clip-card">
                            <h3>Clip: ${clip.id}</h3>
                            <div class="clip-info">
                                <p>📏 Duration: ${clip.duration}s</p>
                                <p>⭐ Score: ${(clip.score * 100).toFixed(0)}%</p>
                                <p>🪝 Hook: "${clip.hook || 'No hook'}"</p>
                                <p>📁 Video: ${clip.video_id}</p>
                            </div>
                            <button class="download-btn" 
                                    onclick="downloadClip('${clip.id}')">
                                📥 Download for TikTok
                            </button>
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Error loading clips:', error);
                }
            }
            
            async function loadQueue() {
                try {
                    const response = await fetch('/api/queue/status');
                    const data = await response.json();
                    
                    document.getElementById('total-videos').textContent = 
                        data.downloaded_count || 0;
                    
                    // Show pending videos
                    const pending = document.getElementById('pending-videos');
                    const videos = Object.entries(data.videos || {}).slice(0, 5);
                    
                    if (videos.length === 0) {
                        pending.innerHTML = '<p>No pending videos</p>';
                    } else {
                        pending.innerHTML = videos.map(([id, info]) => 
                            `<div>📹 ${id}: ${info.status || 'pending'}</div>`
                        ).join('');
                    }
                } catch (error) {
                    console.error('Error loading queue:', error);
                }
            }
            
            async function processNext() {
                // Get first unprocessed video
                const response = await fetch('/api/queue/status');
                const data = await response.json();
                const videos = Object.keys(data.videos || {});
                
                if (videos.length > 0) {
                    const videoId = videos[0];
                    
                    // Show processing status
                    document.getElementById('pending-videos').innerHTML = 
                        `<div style="color: #00f2ea;">⏳ Processing ${videoId}...</div>`;
                    
                    // Trigger processing
                    await fetch(`/api/process/${videoId}`, { method: 'POST' });
                    
                    // Start polling for status
                    checkProcessingStatus(videoId);
                }
            }
            
            async function checkProcessingStatus(videoId) {
                const statusInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`/api/process/status/${videoId}`);
                        const status = await response.json();
                        
                        // Update UI with status
                        document.getElementById('pending-videos').innerHTML = 
                            `<div style="color: #00f2ea;">
                                ⏳ ${status.message || 'Processing...'} 
                                (${status.progress || 0}%)
                            </div>`;
                        
                        if (status.status === 'completed' || status.status === 'failed') {
                            clearInterval(statusInterval);
                            loadClips();
                            loadQueue();
                            
                            if (status.status === 'failed') {
                                alert(`Processing failed: ${status.message}`);
                            }
                        }
                    } catch (error) {
                        console.error('Error checking status:', error);
                    }
                }, 2000); // Check every 2 seconds
            }
            
            function downloadClip(clipId) {
                window.location.href = `/api/download_clip/${clipId}`;
            }
            
            // Load data on page load
            loadClips();
            loadQueue();
            
            // Refresh every 30 seconds
            setInterval(() => {
                loadClips();
                loadQueue();
            }, 30000);
        </script>
    </body>
    </html>
    '''

# Register the video processor blueprint - CRITICAL COMPONENT
try:
    from src.api.video_processor import video_processor
    app.register_blueprint(video_processor)
    print("✅ Video processor registered successfully")
except ImportError as e:
    import sys
    print("="*60)
    print("❌ CRITICAL ERROR: Video processor failed to load!")
    print(f"❌ Error details: {e}")
    print("❌ The system CANNOT function without video processing")
    print("❌ Please check:")
    print("   1. video_processor.py exists in src/api/")
    print("   2. All imports in video_processor.py are valid")
    print("   3. FFmpeg is installed")
    print("="*60)
    sys.exit(1)  # Exit with error code - prevents broken deployment

if __name__ == '__main__':
    # CRITICAL FIX: Must bind to 0.0.0.0 for Docker/DigitalOcean
    # NOT 127.0.0.1 or localhost!
    app.run(host='0.0.0.0', port=8000, debug=False)