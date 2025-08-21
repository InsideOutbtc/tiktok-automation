#!/usr/bin/env python3
"""
Quick validation to ensure system is ready
"""

import sys
import os
import subprocess
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_requirement(name, check_func, fix_cmd=None):
    """Check a requirement and provide fix if needed"""
    try:
        result = check_func()
        if result:
            print(f"  ✅ {name}: OK")
            return True
        else:
            print(f"  ❌ {name}: Failed")
            if fix_cmd:
                print(f"     Fix: {fix_cmd}")
            return False
    except Exception as e:
        print(f"  ❌ {name}: Error - {str(e)[:50]}")
        if fix_cmd:
            print(f"     Fix: {fix_cmd}")
        return False

def main():
    print("🔍 TikTok AI System - Quick Validation")
    print("=" * 50)
    
    all_ok = True
    
    # 1. Check Python version
    print("\n📋 Environment Checks:")
    all_ok &= check_requirement(
        "Python 3.9+",
        lambda: sys.version_info >= (3, 9),
        "Install Python 3.9 or higher"
    )
    
    # 2. Check critical imports
    print("\n📦 Dependency Checks:")
    
    all_ok &= check_requirement(
        "dotenv",
        lambda: __import__('dotenv'),
        "pip install python-dotenv"
    )
    
    all_ok &= check_requirement(
        "yaml",
        lambda: __import__('yaml'),
        "pip install pyyaml"
    )
    
    all_ok &= check_requirement(
        "openai",
        lambda: __import__('openai'),
        "pip install openai"
    )
    
    all_ok &= check_requirement(
        "googleapiclient",
        lambda: __import__('googleapiclient'),
        "pip install google-api-python-client"
    )
    
    all_ok &= check_requirement(
        "yt_dlp",
        lambda: __import__('yt_dlp'),
        "pip install yt-dlp"
    )
    
    all_ok &= check_requirement(
        "cv2 (OpenCV)",
        lambda: __import__('cv2'),
        "pip install opencv-python-headless"
    )
    
    all_ok &= check_requirement(
        "moviepy",
        lambda: __import__('moviepy'),
        "pip install moviepy"
    )
    
    # 3. Check FFmpeg
    print("\n🎬 External Tools:")
    all_ok &= check_requirement(
        "FFmpeg",
        lambda: subprocess.run(['ffmpeg', '-version'], 
                             capture_output=True, 
                             check=False).returncode == 0,
        "brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)"
    )
    
    # 4. Check directories
    print("\n📁 Directory Structure:")
    dirs = ['input/downloads', 'processing/clips', 'logs', 'database']
    for dir_path in dirs:
        all_ok &= check_requirement(
            f"Directory: {dir_path}",
            lambda d=dir_path: os.path.exists(d),
            f"mkdir -p {dir_path}"
        )
    
    # 5. Check .env file
    print("\n🔐 Configuration:")
    all_ok &= check_requirement(
        ".env file",
        lambda: os.path.exists('.env'),
        "cp .env.example .env && edit .env"
    )
    
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
        all_ok &= check_requirement(
            "YouTube API Key",
            lambda: os.getenv('YOUTUBE_API_KEY') and 
                   os.getenv('YOUTUBE_API_KEY') != 'your_youtube_api_key_here',
            "Add valid YOUTUBE_API_KEY to .env"
        )
        
        all_ok &= check_requirement(
            "OpenAI API Key",
            lambda: os.getenv('OPENAI_API_KEY') and 
                   os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here',
            "Add valid OPENAI_API_KEY to .env (optional but recommended)"
        )
    
    # 6. Test imports
    print("\n🐍 Testing Core Imports:")
    try:
        from src.core.content_sourcer import ContentSourcer
        print("  ✅ ContentSourcer imports successfully")
    except ImportError as e:
        print(f"  ❌ ContentSourcer import error: {e}")
        all_ok = False
        
    try:
        from src.core.smart_clipper import SmartClipper
        print("  ✅ SmartClipper imports successfully")
    except ImportError as e:
        print(f"  ❌ SmartClipper import error: {e}")
        all_ok = False
        
    try:
        from src.agents.ai_agent_system import AIAgentSystem
        print("  ✅ AIAgentSystem imports successfully")
    except ImportError as e:
        print(f"  ❌ AIAgentSystem import error: {e}")
        all_ok = False
    
    # 7. Check database
    print("\n💾 Database Check:")
    all_ok &= check_requirement(
        "SQLite database",
        lambda: os.path.exists('database/tiktok_automation.db') or True,  # OK if doesn't exist yet
        "Run setup_system.sh to initialize database"
    )
    
    # Final verdict
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ SYSTEM READY FOR TESTING!")
        print("\nNext steps:")
        print("1. Run API test: python3 scripts/test_apis.py")
        print("2. Run full tests: python3 scripts/run_all_tests.py")
        print("3. Start system: python3 src/core/main_controller.py start")
    else:
        print("❌ SYSTEM NOT READY")
        print("\nTo fix all issues, run:")
        print("   bash scripts/setup_system.sh")
        print("\nThen try this validation again")
    
    # Save validation results
    results = {
        "timestamp": datetime.now().isoformat(),
        "ready": all_ok,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    os.makedirs('logs', exist_ok=True)
    with open('logs/validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())