#!/usr/bin/env python3
"""
Check YouTube Cookie Validity
Tests if cookies are working for YouTube downloads
"""
import os
import sys
import json
import time
import yt_dlp
from pathlib import Path
from datetime import datetime

def check_cookie_file(cookie_path: str):
    """Check if cookie file exists and parse it"""
    if not os.path.exists(cookie_path):
        print(f"❌ Cookie file not found: {cookie_path}")
        return False
    
    # Check file age
    file_age = time.time() - os.path.getmtime(cookie_path)
    days_old = file_age / (24 * 3600)
    
    print(f"✅ Cookie file found: {cookie_path}")
    print(f"📅 File age: {days_old:.1f} days")
    
    if days_old > 30:
        print("⚠️  WARNING: Cookies are over 30 days old and may be expired!")
    elif days_old > 25:
        print("⚠️  WARNING: Cookies will expire soon (>25 days old)")
    
    # Check file size
    file_size = os.path.getsize(cookie_path)
    print(f"📏 File size: {file_size} bytes")
    
    if file_size < 100:
        print("❌ Cookie file seems too small!")
        return False
    
    # Count cookies
    cookie_count = 0
    important_cookies = []
    
    try:
        with open(cookie_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    cookie_count += 1
                    parts = line.strip().split('\t')
                    if len(parts) >= 7:
                        cookie_name = parts[5]
                        if cookie_name in ['SID', 'HSID', 'SSID', 'SAPISID', 'APISID', 
                                         'LOGIN_INFO', 'VISITOR_INFO1_LIVE', 'YSC', 'PREF']:
                            important_cookies.append(cookie_name)
    
        print(f"🍪 Total cookies: {cookie_count}")
        print(f"🔑 Important cookies found: {', '.join(important_cookies)}")
        
        if len(important_cookies) < 3:
            print("⚠️  WARNING: Missing some important authentication cookies!")
            
    except Exception as e:
        print(f"❌ Error reading cookie file: {e}")
        return False
    
    return True

def test_youtube_download(cookie_path: str):
    """Test downloading with cookies"""
    print("\n" + "="*50)
    print("Testing YouTube Download with Cookies")
    print("="*50 + "\n")
    
    # Test URL (short public domain video)
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"  # Big Buck Bunny trailer
    
    print(f"🎬 Test video: {test_url}")
    print("⏳ Attempting to extract video info...\n")
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'cookiefile': cookie_path,
        'socket_timeout': 30,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
            print("\n✅ SUCCESS: Video info extracted!")
            print(f"📹 Title: {info.get('title', 'N/A')}")
            print(f"👤 Uploader: {info.get('uploader', 'N/A')}")
            print(f"⏱️  Duration: {info.get('duration', 0)} seconds")
            print(f"👁️  Views: {info.get('view_count', 0):,}")
            
            # Check if we got a valid format
            formats = info.get('formats', [])
            print(f"📊 Available formats: {len(formats)}")
            
            if formats:
                print("\n✅ COOKIES ARE WORKING!")
                print("You should be able to download videos from cloud servers.")
                return True
            else:
                print("\n⚠️  WARNING: No formats found - cookies might not be working properly")
                return False
                
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print(f"\n❌ DOWNLOAD ERROR: {error_msg}")
        
        if "Sign in to confirm you're not a bot" in error_msg:
            print("\n🤖 BOT DETECTION: YouTube is blocking access!")
            print("Your cookies are either:")
            print("1. Expired (need to re-login and extract new cookies)")
            print("2. Invalid (extraction failed)")
            print("3. From a different IP region than the server")
            print("\nSolution: Run python scripts/extract_cookies.py again")
        elif "Video unavailable" in error_msg:
            print("\n📹 Video is unavailable (might be region locked)")
            print("But this doesn't mean cookies are invalid - try another video")
        else:
            print("\n❓ Unknown error - cookies might be invalid")
            
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Main function"""
    print("🍪 YouTube Cookie Validity Checker")
    print("==================================\n")
    
    # Check for cookie file
    cookie_path = os.environ.get('YOUTUBE_COOKIE_FILE', '/app/config/youtube_cookies.txt')
    
    # Also check local path
    if not os.path.exists(cookie_path):
        local_path = 'config/youtube_cookies.txt'
        if os.path.exists(local_path):
            cookie_path = local_path
    
    print(f"📁 Checking cookie file: {cookie_path}\n")
    
    # Check cookie file
    if not check_cookie_file(cookie_path):
        print("\n❌ Cookie file check failed!")
        print("\nTo fix this:")
        print("1. Run: python scripts/extract_cookies.py")
        print("2. Make sure you're logged into YouTube in your browser")
        print("3. Try the browser extension method if automatic extraction fails")
        sys.exit(1)
    
    # Test download
    if test_youtube_download(cookie_path):
        print("\n✅ All checks passed! Cookies are valid and working.")
        print("You can download videos from cloud servers!")
    else:
        print("\n❌ Cookie validation failed!")
        print("Please refresh your cookies by running:")
        print("python scripts/extract_cookies.py")
        sys.exit(1)

if __name__ == "__main__":
    main()