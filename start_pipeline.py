#!/usr/bin/env python3
"""
TikTok Pipeline Starter - Maximum Velocity Mode
Initializes complete video processing pipeline
"""

import subprocess
import time
import requests
import os
import sys

def start_pipeline():
    """Maximum Velocity Pipeline Starter"""
    print("🚀 STARTING TIKTOK PIPELINE - MAXIMUM VELOCITY MODE")
    print("=" * 60)
    
    # Configuration
    DO_URL = "https://tiktok-automation-xqbnb.ondigitalocean.app"
    COOKIE_FILE = "config/youtube_cookies.txt"
    
    print(f"📍 Target: {DO_URL}")
    print(f"🍪 Cookies: {COOKIE_FILE}")
    
    # Tier 1: Check DO health
    print("\n📡 Checking DigitalOcean app health...")
    try:
        r = requests.get(f"{DO_URL}/health", timeout=10)
        if r.status_code == 200:
            print("✅ DigitalOcean app is healthy")
        else:
            print(f"⚠️ DO returned {r.status_code}, continuing anyway")
    except Exception as e:
        print(f"⚠️ Health check failed: {e}, continuing (Tier 2)")
    
    # Check for transit script
    transit_script = None
    for script in ["scripts/mac_transit.py", "scripts/zero_storage_transit.py", "scripts/simple_transit.py"]:
        if os.path.exists(script):
            transit_script = script
            print(f"\n✅ Found transit script: {script}")
            break
    
    if not transit_script:
        print("❌ No transit script found - creating minimal version")
        create_minimal_transit()
        transit_script = "minimal_transit.py"
    
    # Update the DO URL in the transit script
    print(f"\n🔧 Updating DO URL in transit script...")
    try:
        with open(transit_script, 'r') as f:
            content = f.read()
        
        # Replace any old DO URLs
        content = content.replace('https://[YOUR-APP-NAME].ondigitalocean.app', DO_URL)
        content = content.replace('https://powerpro-automation-f2k4p.ondigitalocean.app', DO_URL)
        
        # Also update cookie path if needed
        if 'cookies.txt' in content and not '~/cookies.txt' in content:
            content = content.replace('cookies.txt', COOKIE_FILE)
        
        with open(transit_script, 'w') as f:
            f.write(content)
        print("✅ Updated script with current DO URL")
    except Exception as e:
        print(f"⚠️ Could not update script: {e}")
    
    # Start transit
    print("\n🎬 Starting video transit (processing 3 videos)...")
    try:
        # Set environment variable for DO URL
        env = os.environ.copy()
        env['DO_URL'] = DO_URL
        
        result = subprocess.run([
            sys.executable,  # Use current Python
            transit_script
        ], capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print("✅ Transit completed successfully")
            if result.stdout:
                print("\nOutput (last 500 chars):")
                print(result.stdout[-500:])
        else:
            print(f"⚠️ Transit had issues (code {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[-500:]}")
            # Tier 3: Continue anyway, some videos may have worked
            
    except Exception as e:
        print(f"❌ Transit failed: {e}")
        print("Attempting direct upload with test video...")
        direct_upload_test()
    
    # Wait for processing
    print("\n⏳ Waiting 2 minutes for initial video processing...")
    for i in range(4):
        time.sleep(30)
        print(f"   {30 * (i + 1)}s elapsed...")
    
    # Check results
    print("\n📊 Checking processing results...")
    try:
        # Check queue status
        r = requests.get(f"{DO_URL}/api/queue/status")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Videos in queue: {data.get('downloaded_count', 'Unknown')}")
        
        # Check clips
        r = requests.get(f"{DO_URL}/api/clips")
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Clips generated: {data.get('total_clips', 0)}")
    except Exception as e:
        print(f"⚠️ Could not get status: {e}")
        print("Check dashboard manually")
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE INITIALIZATION COMPLETE")
    print(f"🌐 Dashboard: {DO_URL}/dashboard")
    print(f"📱 Clips will continue processing...")
    print("💡 Run this script again to process more videos")
    print("=" * 60)

def create_minimal_transit():
    """Create minimal transit script if none exists"""
    minimal_script = '''#!/usr/bin/env python3
import os
import subprocess
import requests
from pathlib import Path

DO_URL = os.getenv('DO_URL', 'https://tiktok-automation-xqbnb.ondigitalocean.app')
COOKIE_FILE = 'config/youtube_cookies.txt'

# Test videos from fitness creators
test_videos = [
    'https://www.youtube.com/watch?v=0AeghlYBfPc',  # Example fitness video
]

for video_url in test_videos[:1]:  # Just one for testing
    try:
        print(f"Downloading {video_url}...")
        output = f"/tmp/test_video.mp4"
        
        # Download with yt-dlp
        subprocess.run([
            "yt-dlp", 
            "--cookies", COOKIE_FILE,
            "-f", "best[height<=720]/best",
            "--max-filesize", "200M",
            "-o", output,
            video_url
        ], check=True)
        
        # Upload to DO
        if os.path.exists(output):
            print(f"Uploading to {DO_URL}...")
            with open(output, 'rb') as f:
                files = {'video': ('video.mp4', f, 'video/mp4')}
                data = {'video_id': 'test_1'}
                r = requests.post(f"{DO_URL}/api/upload", files=files, data=data)
                print(f"Upload result: {r.status_code}")
            
            # Delete
            os.remove(output)
            print("✅ Cleaned up temp file")
    except Exception as e:
        print(f"Failed: {e}")
'''
    
    with open("minimal_transit.py", "w") as f:
        f.write(minimal_script)
    os.chmod("minimal_transit.py", 0o755)
    print("✅ Created minimal_transit.py")

def direct_upload_test():
    """Direct test upload as last resort"""
    try:
        # Create a test video info file
        test_data = {
            "video_id": "direct_test_1",
            "title": "Direct Upload Test"
        }
        
        DO_URL = "https://tiktok-automation-xqbnb.ondigitalocean.app"
        r = requests.post(f"{DO_URL}/api/queue/seed")
        print(f"Seeded queue: {r.status_code}")
    except Exception as e:
        print(f"Direct upload failed: {e}")

if __name__ == "__main__":
    start_pipeline()