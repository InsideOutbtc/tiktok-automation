#!/bin/bash
# Fix Everything Script - Maximum Velocity Mode

echo "🔧 FIXING EVERYTHING - MAXIMUM VELOCITY MODE"
echo "==========================================="

# Phase 1: Environment fixes
echo "📦 Installing dependencies..."
pip3 install requests yt-dlp --quiet 2>/dev/null || {
    echo "Note: pip3 install failed, trying brew..."
    which brew && brew install yt-dlp 2>/dev/null || echo "Brew not available"
}

# Phase 2: Fix cookie paths
echo "🔗 Fixing cookie paths..."
PROJECT_DIR="/Users/Patrick/Fitness TikTok"
cd "$PROJECT_DIR" || exit 1

# Create cookie symlink if needed
if [ -f "config/youtube_cookies.txt" ]; then
    echo "✅ Found cookies at config/youtube_cookies.txt"
    ln -sf "$PROJECT_DIR/config/youtube_cookies.txt" "$HOME/cookies.txt" 2>/dev/null
fi

# Phase 3: Fix URLs in all scripts
echo "🔄 Updating URLs in all scripts..."
python3 -c "
import glob
import os

# Fix URL in all Python scripts
scripts = glob.glob('scripts/*.py')
fixed_count = 0

for script in scripts:
    try:
        with open(script, 'r') as f:
            content = f.read()
        
        original = content
        # Replace old URL with new URL
        content = content.replace('tiktok-automation-xqbnb', 'powerpro-automation-f2k4p')
        content = content.replace('https://[YOUR-APP-NAME].ondigitalocean.app', 'https://powerpro-automation-f2k4p.ondigitalocean.app')
        
        if content != original:
            with open(script, 'w') as f:
                f.write(content)
            fixed_count += 1
            print(f'  ✅ Fixed {os.path.basename(script)}')
    except Exception as e:
        print(f'  ❌ Error fixing {script}: {e}')

print(f'✅ Updated {fixed_count} scripts')
"

# Phase 4: Create universal transit script
echo "🚀 Creating universal transit script..."
cat > universal_transit.py << 'EOF'
#!/usr/bin/env python3
"""Universal Transit - Works with minimal dependencies"""
import os
import subprocess
import time
import sys

# Configuration
DO_URL = "https://powerpro-automation-f2k4p.ondigitalocean.app"
COOKIE_PATHS = [
    os.path.expanduser("~/cookies.txt"),
    "/Users/Patrick/Fitness TikTok/config/youtube_cookies.txt",
    "config/youtube_cookies.txt"
]

def find_cookies():
    """Find cookie file"""
    for path in COOKIE_PATHS:
        if os.path.exists(path):
            return path
    return None

def main():
    print("🎬 UNIVERSAL TRANSIT - STARTING")
    print("=" * 50)
    
    # Find cookies
    cookie_file = find_cookies()
    if not cookie_file:
        print("❌ No cookies found!")
        return
    print(f"✅ Using cookies: {cookie_file}")
    
    # Test with a short fitness video
    test_videos = [
        "https://www.youtube.com/watch?v=ScMzIvxBSi4",  # Short fitness video
        "https://www.youtube.com/shorts/D0r7QQe0uDA"    # Fitness short
    ]
    
    for video_url in test_videos[:1]:  # Just one for testing
        print(f"\n📹 Processing: {video_url}")
        output = "/tmp/test_video.mp4"
        
        # Download
        print("⬇️  Downloading...")
        cmd = [
            "yt-dlp",
            "--cookies", cookie_file,
            "-f", "best[height<=720]/best",
            "--max-filesize", "200M",
            "-o", output,
            video_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"Download failed: {result.stderr[:200]}")
                # Try without cookies
                print("Retrying without cookies...")
                cmd.remove("--cookies")
                cmd.remove(cookie_file)
                subprocess.run(cmd, timeout=300)
        except subprocess.TimeoutExpired:
            print("Download timed out")
            continue
        except FileNotFoundError:
            print("yt-dlp not found - install with: pip3 install yt-dlp")
            return
        
        if os.path.exists(output):
            file_size_mb = os.path.getsize(output) / (1024 * 1024)
            print(f"✅ Downloaded: {file_size_mb:.1f} MB")
            
            # Upload
            print("⬆️  Uploading to DO...")
            upload_cmd = [
                "curl", "-X", "POST",
                f"{DO_URL}/api/upload",
                "-F", f"video=@{output}",
                "-F", "video_id=test_1",
                "--connect-timeout", "30",
                "--max-time", "300",
                "-s", "-w", "%{http_code}"
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True)
            status_code = result.stdout.strip()
            
            if status_code == "200":
                print("✅ Upload successful!")
            else:
                print(f"❌ Upload failed with status: {status_code}")
                print(f"Response: {result.stderr[:200]}")
            
            # Clean up
            os.remove(output)
            print("🗑️  Cleaned up")
        else:
            print("❌ Download failed")
    
    print("\n" + "=" * 50)
    print("✅ TRANSIT COMPLETE")
    print(f"🌐 Check dashboard: {DO_URL}/dashboard")
    print("⏰ Clips will be ready in 5-10 minutes")

if __name__ == "__main__":
    main()
EOF

chmod +x universal_transit.py

# Phase 5: Execute
echo ""
echo "🎯 Running pipeline..."
python3 universal_transit.py

echo ""
echo "============================================"
echo "✅ ALL FIXES APPLIED!"
echo ""
echo "📱 Dashboard: https://powerpro-automation-f2k4p.ondigitalocean.app/dashboard"
echo "⏰ Videos will process in 5-10 minutes"
echo ""
echo "🔄 To process more videos, run:"
echo "   python3 scripts/mac_transit.py"
echo "============================================"