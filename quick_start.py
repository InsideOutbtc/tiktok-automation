#!/usr/bin/env python3
"""
Quick Pipeline Start - Uses built-in modules only
"""

import subprocess
import os
import sys
import time
import urllib.request
import json

def quick_start():
    print("🚀 QUICK START - TIKTOK PIPELINE")
    print("=" * 60)
    
    DO_URL = "https://tiktok-automation-xqbnb.ondigitalocean.app"
    
    # Check health with urllib
    print(f"📡 Checking {DO_URL}...")
    try:
        with urllib.request.urlopen(f"{DO_URL}/health", timeout=10) as response:
            if response.status == 200:
                print("✅ DigitalOcean app is healthy")
    except Exception as e:
        print(f"⚠️ Health check failed: {e}")
    
    # Try to run existing transit script
    print("\n🔍 Looking for transit scripts...")
    
    transit_scripts = [
        "scripts/mac_transit.py",
        "scripts/simple_transit.py",
        "scripts/zero_storage_transit.py"
    ]
    
    script_run = False
    for script in transit_scripts:
        if os.path.exists(script):
            print(f"\n✅ Found: {script}")
            print("📝 Updating DO URL...")
            
            # Read and update the script
            try:
                with open(script, 'r') as f:
                    content = f.read()
                
                # Update URL
                if 'DO_URL' in content:
                    # Save backup
                    with open(f"{script}.backup", 'w') as f:
                        f.write(content)
                    
                    # Update URL
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'DO_URL' in line and 'ondigitalocean.app' in line:
                            lines[i] = f'DO_URL = "{DO_URL}"'
                            print(f"✅ Updated DO_URL in line {i+1}")
                            break
                    
                    # Write back
                    with open(script, 'w') as f:
                        f.write('\n'.join(lines))
                
                # Try to run it
                print(f"\n🎬 Running {script}...")
                env = os.environ.copy()
                env['DO_URL'] = DO_URL
                
                result = subprocess.run([sys.executable, script], 
                                      capture_output=True, text=True, env=env)
                
                if result.returncode == 0:
                    print("✅ Script completed successfully!")
                    script_run = True
                else:
                    print(f"⚠️ Script exited with code {result.returncode}")
                    if result.stderr:
                        print(f"Error: {result.stderr[:200]}")
                
                break
                
            except Exception as e:
                print(f"❌ Error running {script}: {e}")
    
    if not script_run:
        print("\n⚠️ No transit script could be run successfully")
        print("📝 Creating manual instructions...")
        create_manual_instructions()
    
    print("\n⏳ Waiting 2 minutes for processing...")
    time.sleep(120)
    
    # Check results
    print("\n📊 Checking results...")
    try:
        with urllib.request.urlopen(f"{DO_URL}/dashboard") as response:
            if response.status == 200:
                print("✅ Dashboard is accessible")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ PIPELINE INITIALIZATION ATTEMPT COMPLETE")
    print(f"🌐 Check dashboard: {DO_URL}/dashboard")
    print(f"📝 If no videos uploaded, see manual_instructions.txt")
    print("=" * 60)

def create_manual_instructions():
    """Create manual instructions file"""
    instructions = f"""
MANUAL VIDEO UPLOAD INSTRUCTIONS
================================

Since automated transit couldn't run, follow these steps:

1. Install yt-dlp (if not installed):
   brew install yt-dlp
   OR
   pip3 install yt-dlp

2. Download a test video:
   yt-dlp --cookies config/youtube_cookies.txt -o test.mp4 "https://www.youtube.com/watch?v=ScMzIvxBSi4"

3. Check the file:
   ls -la test.mp4

4. Visit the dashboard and use the web interface:
   https://tiktok-automation-xqbnb.ondigitalocean.app/dashboard

5. Or use curl to upload directly:
   curl -X POST https://tiktok-automation-xqbnb.ondigitalocean.app/api/upload \\
        -F "video=@test.mp4" \\
        -F "video_id=test_1"

6. Delete the test file:
   rm test.mp4

The dashboard will show processing progress and generated clips.
"""
    
    with open("manual_instructions.txt", "w") as f:
        f.write(instructions)
    print("✅ Created manual_instructions.txt")

if __name__ == "__main__":
    quick_start()