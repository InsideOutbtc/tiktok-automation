#!/usr/bin/env python3
"""
One-command cookie setup for YouTube downloads
Combines extraction and validation in a single script
"""
import os
import sys
import subprocess
import time

def print_banner():
    """Print setup banner"""
    print("\n" + "="*60)
    print("🍪 YouTube Cookie Setup - REQUIRED for Cloud Servers")
    print("="*60 + "\n")

def check_existing_cookies():
    """Check if cookies already exist"""
    cookie_paths = [
        'config/youtube_cookies.txt',
        '/app/config/youtube_cookies.txt',
        os.environ.get('YOUTUBE_COOKIE_FILE', '')
    ]
    
    for path in cookie_paths:
        if path and os.path.exists(path):
            print(f"✅ Found existing cookies at: {path}")
            
            # Check age
            age = time.time() - os.path.getmtime(path)
            days = age / (24 * 3600)
            
            if days > 25:
                print(f"⚠️  WARNING: Cookies are {days:.0f} days old and may expire soon!")
                return path, False
            else:
                print(f"📅 Cookies are {days:.1f} days old (still fresh)")
                return path, True
    
    print("❌ No existing cookies found")
    return None, False

def extract_cookies():
    """Run cookie extraction"""
    print("\n🔄 Extracting cookies from your browser...")
    print("Make sure you're logged into YouTube!\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/extract_cookies.py'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Extraction failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running extraction: {e}")
        return False

def validate_cookies():
    """Run cookie validation"""
    print("\n🔍 Validating cookies...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/check_youtube_cookies.py'],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error validating cookies: {e}")
        return False

def main():
    """Main setup flow"""
    print_banner()
    
    # Check existing cookies
    cookie_path, is_fresh = check_existing_cookies()
    
    if cookie_path and is_fresh:
        print("\n✅ Cookies are already set up and fresh!")
        
        # Validate them
        if validate_cookies():
            print("\n🎉 Cookie setup complete! You're ready to download from cloud servers.")
            return 0
        else:
            print("\n⚠️  Existing cookies failed validation. Re-extracting...")
    
    # Extract new cookies
    print("\n" + "-"*40)
    choice = input("\n🍪 Extract cookies now? [Y/n]: ").strip().lower()
    
    if choice == 'n':
        print("\n⚠️  Skipping extraction. You can run this script again later.")
        print("Without cookies, YouTube downloads WILL FAIL on cloud servers!")
        return 1
    
    # Extract
    if not extract_cookies():
        print("\n❌ Cookie extraction failed!")
        print("\nTry manual extraction:")
        print("1. Install browser extension: 'Get cookies.txt LOCALLY'")
        print("2. Click on YouTube while logged in")
        print("3. Save as config/youtube_cookies.txt")
        return 1
    
    # Validate
    if validate_cookies():
        print("\n🎉 Success! Cookies extracted and validated.")
        print("\nNext steps:")
        print("1. Deploy to server: scp config/youtube_cookies.txt server:/path/")
        print("2. Or use Docker: docker-compose up")
        return 0
    else:
        print("\n⚠️  Cookies extracted but validation failed.")
        print("Try logging into YouTube again and re-run this script.")
        return 1

if __name__ == "__main__":
    sys.exit(main())