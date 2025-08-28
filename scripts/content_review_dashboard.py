#!/usr/bin/env python3
"""
Power Pro Review Dashboard - Manual quality control before posting
Aligns with content strategy and maintains standards
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, send_file

app = Flask(__name__)
BASE_DIR = Path("/Users/Patrick/Fitness TikTok")

class ContentReviewDashboard:
    """Dashboard for reviewing and editing clips before posting"""
    
    def __init__(self):
        self.clips_dir = BASE_DIR / "clips" / datetime.now().strftime("%Y-%m-%d")
        self.approved_dir = BASE_DIR / "approved"
        self.approved_dir.mkdir(exist_ok=True)
        
        # Power Pro content categories
        self.content_categories = {
            'influencer': '30% - Viral influencer clips',
            'motivation': '25% - Motivation edits',
            'bodybuilding': '15% - Modern pros',
            'training': '15% - Form/technique',
            'funny': '10% - Funny moments',
            'educational': '5% - Tips/nutrition'
        }
    
    def get_pending_clips(self):
        """Get all clips awaiting review"""
        if not self.clips_dir.exists():
            return []
        
        clips = []
        for clip in self.clips_dir.glob("*.mp4"):
            clips.append({
                'filename': clip.name,
                'path': str(clip),
                'size_mb': clip.stat().st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(clip.stat().st_mtime).isoformat()
            })
        
        return clips
    
    def categorize_clip(self, clip_path, category):
        """Assign content category to clip"""
        metadata_file = Path(clip_path).with_suffix('.json')
        metadata = {
            'category': category,
            'reviewed_at': datetime.now().isoformat(),
            'content_mix_percentage': self.content_categories.get(category, 'Unknown')
        }
        metadata_file.write_text(json.dumps(metadata))
    
    def approve_clip(self, clip_name, category, edits=None):
        """Approve clip for posting"""
        source = self.clips_dir / clip_name
        
        if edits:
            # If edits needed, mark for editing
            edit_marker = source.with_suffix('.edit')
            edit_marker.write_text(json.dumps(edits))
            return {'status': 'needs_editing', 'edits': edits}
        
        # Move to approved folder with category
        dest = self.approved_dir / f"{category}_{clip_name}"
        shutil.move(str(source), str(dest))
        
        # Categorize for tracking
        self.categorize_clip(dest, category)
        
        return {'status': 'approved', 'path': str(dest)}
    
    def reject_clip(self, clip_name, reason):
        """Reject and delete clip"""
        clip_path = self.clips_dir / clip_name
        
        # Log rejection
        log_entry = {
            'clip': clip_name,
            'rejected_at': datetime.now().isoformat(),
            'reason': reason
        }
        
        log_file = BASE_DIR / "logs" / "rejections.jsonl"
        log_file.parent.mkdir(exist_ok=True)
        with log_file.open('a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Delete the clip
        clip_path.unlink()
        
        return {'status': 'rejected', 'reason': reason}

# Flask routes for dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Power Pro Review Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            font-family: -apple-system, system-ui; 
            padding: 20px;
            background: #1a1a1a;
            color: #fff;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .clip-card {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #333;
        }
        .clip-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .clip-info {
            color: #888;
            margin-bottom: 15px;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .approve { background: #4caf50; color: white; }
        .edit { background: #ff9800; color: white; }
        .reject { background: #f44336; color: white; }
        select {
            padding: 10px;
            border-radius: 5px;
            background: #333;
            color: white;
            border: 1px solid #555;
        }
        .content-mix {
            background: #333;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .mix-item {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
        }
        .percentage {
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ Power Pro Review Dashboard</h1>
        <p>Review and categorize clips before posting</p>
    </div>
    
    <div class="content-mix">
        <h3>Content Mix Strategy</h3>
        <div class="mix-item">
            <span>Viral Influencer Clips</span>
            <span class="percentage">30%</span>
        </div>
        <div class="mix-item">
            <span>Motivation Edits</span>
            <span class="percentage">25%</span>
        </div>
        <div class="mix-item">
            <span>Modern Bodybuilding Pros</span>
            <span class="percentage">15%</span>
        </div>
        <div class="mix-item">
            <span>Training/Form Content</span>
            <span class="percentage">15%</span>
        </div>
        <div class="mix-item">
            <span>Funny Gym Moments</span>
            <span class="percentage">10%</span>
        </div>
        <div class="mix-item">
            <span>Educational</span>
            <span class="percentage">5%</span>
        </div>
    </div>
    
    <div id="clips-container">
        <!-- Clips will be loaded here -->
    </div>
    
    <script>
        async function loadClips() {
            const response = await fetch('/api/pending_clips');
            const clips = await response.json();
            
            const container = document.getElementById('clips-container');
            container.innerHTML = '';
            
            if (clips.length === 0) {
                container.innerHTML = '<p>No clips to review. Run the daily batch processor first.</p>';
                return;
            }
            
            clips.forEach(clip => {
                const card = document.createElement('div');
                card.className = 'clip-card';
                card.innerHTML = `
                    <div class="clip-title">${clip.filename}</div>
                    <div class="clip-info">
                        Size: ${clip.size_mb.toFixed(1)}MB | 
                        Created: ${new Date(clip.created).toLocaleString()}
                    </div>
                    <select id="category-${clip.filename}">
                        <option value="">Select Category...</option>
                        <option value="influencer">Influencer Clip (30%)</option>
                        <option value="motivation">Motivation Edit (25%)</option>
                        <option value="bodybuilding">Bodybuilding Pro (15%)</option>
                        <option value="training">Training/Form (15%)</option>
                        <option value="funny">Funny Moment (10%)</option>
                        <option value="educational">Educational (5%)</option>
                    </select>
                    <div class="action-buttons">
                        <button class="approve" onclick="approveClip('${clip.filename}')">✅ Approve</button>
                        <button class="edit" onclick="markForEdit('${clip.filename}')">✏️ Needs Edit</button>
                        <button class="reject" onclick="rejectClip('${clip.filename}')">❌ Reject</button>
                    </div>
                `;
                container.appendChild(card);
            });
        }
        
        async function approveClip(filename) {
            const category = document.getElementById(`category-${filename}`).value;
            if (!category) {
                alert('Please select a category first');
                return;
            }
            
            const response = await fetch('/api/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename, category})
            });
            
            const result = await response.json();
            alert(`Approved: ${filename} as ${category}`);
            loadClips();
        }
        
        async function rejectClip(filename) {
            const reason = prompt('Rejection reason:');
            if (!reason) return;
            
            const response = await fetch('/api/reject', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename, reason})
            });
            
            alert(`Rejected: ${filename}`);
            loadClips();
        }
        
        async function markForEdit(filename) {
            const edits = prompt('What edits are needed?');
            if (!edits) return;
            
            alert(`Marked for editing: ${filename}\\nEdits: ${edits}`);
        }
        
        // Load clips on page load
        loadClips();
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/pending_clips')
def pending_clips():
    reviewer = ContentReviewDashboard()
    return jsonify(reviewer.get_pending_clips())

@app.route('/api/approve', methods=['POST'])
def approve():
    data = request.json
    reviewer = ContentReviewDashboard()
    result = reviewer.approve_clip(data['filename'], data['category'])
    return jsonify(result)

@app.route('/api/reject', methods=['POST'])
def reject():
    data = request.json
    reviewer = ContentReviewDashboard()
    result = reviewer.reject_clip(data['filename'], data['reason'])
    return jsonify(result)

if __name__ == '__main__':
    # Run on local network so you can access from phone too
    app.run(host='0.0.0.0', port=5000, debug=True)