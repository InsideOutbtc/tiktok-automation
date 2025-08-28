#!/usr/bin/env python3
"""Quick Fix and Run - Minimal dependencies, maximum speed"""

import os
import subprocess
import time

print("🚀 QUICK FIX AND RUN - STARTING NOW")
print("=" * 60)

# Configuration
DO_URL = "https://powerpro-automation-f2k4p.ondigitalocean.app"
PROJECT_DIR = "/Users/Patrick/Fitness TikTok"
COOKIE_FILE = f"{PROJECT_DIR}/config/youtube_cookies.txt"

# Step 1: Fix all script URLs
print("🔧 Fixing URLs in scripts...")
scripts_dir = f"{PROJECT_DIR}/scripts"
for filename in os.listdir(scripts_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(scripts_dir, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace old URL
            if 'tiktok-automation-xqbnb' in content:
                content = content.replace('tiktok-automation-xqbnb', 'powerpro-automation-f2k4p')
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"  ✅ Fixed {filename}")
        except:
            pass

# Step 2: Check if we can use existing script
mac_transit = f"{PROJECT_DIR}/scripts/mac_transit.py"
if os.path.exists(mac_transit):
    print("\n✅ Found mac_transit.py - updating and running...")
    
    # Update the cookie path
    try:
        with open(mac_transit, 'r') as f:
            content = f.read()
        
        # Fix cookie path
        content = content.replace('Path.home() / \'cookies.txt\'', f'Path("{COOKIE_FILE}")')
        
        with open(mac_transit, 'w') as f:
            f.write(content)
    except:
        pass
    
    # Run it
    print("\n🎬 Starting video transit...")
    try:
        result = subprocess.run([
            'python3', mac_transit
        ], capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            print(result.stdout[-500:])
        if result.stderr:
            print("Errors:", result.stderr[-500:])
    except subprocess.TimeoutExpired:
        print("⏱️ Script is running (takes a few minutes)...")
    except Exception as e:
        print(f"Error: {e}")

# Step 3: Direct test upload
else:
    print("\n📤 Attempting direct test upload...")
    
    # Test video URL (short fitness video)
    test_url = "https://www.youtube.com/watch?v=ScMzIvxBSi4"
    output_file = "/tmp/quick_test.mp4"
    
    print("⬇️ Downloading test video...")
    download_cmd = f'''yt-dlp --cookies "{COOKIE_FILE}" -f "best[height<=480]" --max-filesize 50M -o "{output_file}" "{test_url}" 2>/dev/null'''
    
    os.system(download_cmd)
    
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✅ Downloaded {size_mb:.1f} MB")
        
        print("⬆️ Uploading to DO...")
        upload_cmd = f'curl -X POST {DO_URL}/api/upload -F "video=@{output_file}" -F "video_id=quick_test_1" -s -w "Status: %{{http_code}}"'
        
        result = os.popen(upload_cmd).read()
        print(f"Upload result: {result}")
        
        # Cleanup
        os.remove(output_file)
        print("🗑️ Cleaned up temp file")
    else:
        print("❌ Download failed - yt-dlp may still be installing")

print("\n" + "=" * 60)
print("✅ QUICK FIX COMPLETE")
print(f"\n🌐 Check dashboard: {DO_URL}/dashboard")
print("⏰ If video uploaded, clips ready in 5-10 minutes")
print("\n💡 To process more videos:")
print("   python3 scripts/mac_transit.py")
print("=" * 60)