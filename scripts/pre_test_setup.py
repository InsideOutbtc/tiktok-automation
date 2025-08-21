#!/usr/bin/env python3
# Pre-test setup and validation
# Ensures system is ready for testing

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def check_environment():
    """Check environment setup"""
    print("🔍 Checking Environment...")
    
    issues = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        issues.append(f"Python 3.9+ required (found {python_version.major}.{python_version.minor})")
    else:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required directories
    required_dirs = [
        "input/downloads",
        "processing/clips",
        "processing/temp",
        "processing/edited",
        "output",
        "logs",
        "data"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"  📁 Created directory: {dir_path}")
        else:
            print(f"  ✅ Directory exists: {dir_path}")
    
    # Check .env file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            issues.append("No .env file found - copy .env.example and add your API keys")
        else:
            issues.append("No .env file found")
    else:
        print("  ✅ .env file exists")
        
        # Check for API keys
        with open(".env", "r") as f:
            env_content = f.read()
            
        if "YOUTUBE_API_KEY=your_youtube_api_key_here" in env_content:
            issues.append("YouTube API key not configured in .env")
        elif "YOUTUBE_API_KEY=" in env_content:
            print("  ✅ YouTube API key configured")
            
        if "OPENAI_API_KEY=your_openai_api_key_here" in env_content:
            issues.append("OpenAI API key not configured in .env")
        elif "OPENAI_API_KEY=" in env_content:
            print("  ✅ OpenAI API key configured")
    
    # Check FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ FFmpeg installed")
        else:
            issues.append("FFmpeg not working properly")
    except FileNotFoundError:
        issues.append("FFmpeg not installed - required for video processing")
    
    # Check critical Python packages
    required_packages = [
        "googleapiclient",
        "TikTokApi",
        "yt_dlp",
        "openai",
        "fastapi",
        "sqlalchemy",
        "opencv-python",
        "moviepy"
    ]
    
    import importlib
    for package in required_packages:
        try:
            importlib.import_module(package.replace("-", "_"))
            print(f"  ✅ Package installed: {package}")
        except ImportError:
            issues.append(f"Missing package: {package}")
    
    return issues


def clean_test_data():
    """Clean up old test data"""
    print("\n🧹 Cleaning Old Test Data...")
    
    # Clean directories
    clean_dirs = [
        "input/downloads",
        "processing/clips",
        "processing/temp",
        "processing/edited"
    ]
    
    total_removed = 0
    for dir_path in clean_dirs:
        if os.path.exists(dir_path):
            files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
            for file in files:
                try:
                    os.remove(os.path.join(dir_path, file))
                    total_removed += 1
                except:
                    pass
                    
    print(f"  ✅ Removed {total_removed} old files")
    
    # Clean old logs
    if os.path.exists("logs"):
        old_logs = [
            "test_report.json",
            "test_posts.json",
            "test_mode.log"
        ]
        for log_file in old_logs:
            log_path = os.path.join("logs", log_file)
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    print(f"  ✅ Removed old log: {log_file}")
                except:
                    pass


def create_test_config():
    """Create test configuration"""
    print("\n⚙️ Creating Test Configuration...")
    
    test_config = {
        "test_mode": True,
        "auto_publish": False,
        "max_videos_per_run": 3,
        "max_clips_per_video": 3,
        "test_platforms": ["youtube"],
        "test_keywords": ["fitness", "workout", "gym"],
        "created_at": datetime.now().isoformat()
    }
    
    import json
    with open("config/test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
        
    print("  ✅ Created test configuration")


def display_test_plan():
    """Display the test plan"""
    print("\n📋 TEST PLAN")
    print("=" * 50)
    print("1. API Connectivity Test")
    print("   - YouTube API connection")
    print("   - OpenAI API connection")
    print("   - TikTok free API test")
    print("")
    print("2. Content Discovery Test")
    print("   - Find real fitness videos")
    print("   - Score viral potential")
    print("   - Download top videos")
    print("")
    print("3. Video Processing Test")
    print("   - Extract clips from videos")
    print("   - Apply AI selection")
    print("   - Generate metadata")
    print("")
    print("4. Full Pipeline Test")
    print("   - Complete end-to-end flow")
    print("   - No actual posting")
    print("   - Performance metrics")
    print("")
    print("5. Test Mode Run")
    print("   - 5-minute live test")
    print("   - Safe mode enabled")
    print("   - Comprehensive report")
    print("=" * 50)


def main():
    """Run pre-test setup"""
    print("🚀 TikTok AI Automation - Pre-Test Setup")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check environment
    issues = check_environment()
    
    if issues:
        print("\n❌ SETUP ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues before running tests.")
        sys.exit(1)
    
    # Clean old data
    clean_test_data()
    
    # Create test config
    os.makedirs("config", exist_ok=True)
    create_test_config()
    
    # Display test plan
    display_test_plan()
    
    print("\n✅ SYSTEM READY FOR TESTING!")
    print("\nNext steps:")
    print("1. Run API test: python scripts/test_apis.py")
    print("2. Run system test: python scripts/system_test.py")
    print("3. Run test mode: python scripts/test_mode.py")
    print("\n⚠️ Remember: No actual posts will be made during testing")


if __name__ == "__main__":
    main()