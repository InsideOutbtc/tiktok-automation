#!/usr/bin/env python3
"""
Quick test video uploader - downloads and uploads a test video
"""

import os
import subprocess
import sys
import time
from pathlib import Path

DO_URL = "https://powerpro-automation-f2k4p.ondigitalocean.app"
TEST_VIDEO = "https://www.youtube.com/watch?v=ScMzIvxBSi4"
OUTPUT = "/tmp/test_fitness.mp4"

print("🚀 TEST VIDEO UPLOAD")
print("===================")

# Check DO health
print("📡 Checking DO app...")
result = subprocess.run(
    ["curl", "-s", "-f", f"{DO_URL}/health"],
    capture_output=True
)
if result.returncode == 0:
    print("✅ DO app is healthy")
else:
    print("⚠️ DO app may be down, continuing anyway...")

print("\n🎬 Attempting download with youtube-dl fallback...")

# Try different download methods
methods = [
    # Method 1: yt-dlp
    ["yt-dlp", "--no-check-certificates", "-f", "best[height<=720]", "--max-filesize", "100M", "-o", OUTPUT, TEST_VIDEO],
    # Method 2: youtube-dl  
    ["youtube-dl", "--no-check-certificates", "-f", "best[height<=720]", "-o", OUTPUT, TEST_VIDEO],
]

download_success = False
for method in methods:
    try:
        print(f"Trying: {method[0]}...")
        result = subprocess.run(method, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(OUTPUT):
            download_success = True
            print(f"✅ Downloaded with {method[0]}")
            break
    except FileNotFoundError:
        continue

if not download_success:
    print("\n❌ Automated download failed")
    print("\n📝 MANUAL DOWNLOAD INSTRUCTIONS:")
    print("1. Go to: https://www.youtube.com/watch?v=ScMzIvxBSi4")
    print("2. Use any online downloader (search 'youtube downloader')")
    print("3. Download as MP4 to your Downloads folder")
    print("4. Run this command:")
    print(f"\n   python3 upload_test_video.py ~/Downloads/yourfile.mp4\n")
    
    # Check if user provided a file
    if len(sys.argv) > 1:
        manual_file = sys.argv[1]
        if os.path.exists(manual_file):
            print(f"\n✅ Using provided file: {manual_file}")
            OUTPUT = manual_file
            download_success = True

if download_success and os.path.exists(OUTPUT):
    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"\n📦 File size: {size_mb:.1f}MB")
    
    print("\n⬆️ Uploading to DigitalOcean...")
    
    # Upload with curl
    cmd = [
        "curl", "-X", "POST", f"{DO_URL}/api/upload",
        "-F", f"video=@{OUTPUT}",
        "-F", f"video_id=test_{int(time.time())}",
        "-w", "\nHTTP_CODE:%{http_code}",
        "-s"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout
    
    if "HTTP_CODE:200" in output:
        print("✅ Upload successful!")
        print("\n🎉 SUCCESS! Your video is being processed")
        print(f"\n🌐 Dashboard: {DO_URL}/dashboard")
        print("⏰ Clips will be ready in 5-10 minutes")
    else:
        print("❌ Upload failed")
        print(f"Response: {output[:200]}")
    
    # Cleanup if it was downloaded
    if OUTPUT == "/tmp/test_fitness.mp4":
        os.remove(OUTPUT)
        print("🗑️ Cleaned up temp file")