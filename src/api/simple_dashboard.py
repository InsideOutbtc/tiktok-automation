from flask import Flask, send_file, jsonify
import os
import glob
from pathlib import Path

app = Flask(__name__)

# Use absolute paths
APP_DIR = os.environ.get('APP_DIR', '/app')
OUTPUT_DIR = os.path.join(APP_DIR, 'output')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)