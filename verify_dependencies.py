#!/usr/bin/env python3
"""Verify all required dependencies are installed."""

import sys

def check_import(module_name, package_name=None):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - FAILED: {e}")
        return False

print("=== Dependency Verification ===")
print()

# Critical dependencies
critical = [
    ("googleapiclient.discovery", "google-api-python-client"),
    ("googleapiclient.errors", "google-api-python-client"),
    ("google.auth", "google-auth"),
    ("yt_dlp", "yt-dlp"),
    ("openai", "openai"),
    ("TikTokApi", "TikTokApi"),
    ("sqlalchemy", "sqlalchemy"),
    ("dotenv", "python-dotenv"),
]

# Check critical dependencies
print("Critical Dependencies:")
critical_ok = True
for module, package in critical:
    if not check_import(module, package):
        critical_ok = False

print()

# Optional dependencies
optional = [
    ("moviepy.editor", "moviepy"),
    ("PIL", "Pillow"),
    ("cv2", "opencv-python-headless"),
    ("playwright", "playwright"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
]

print("Optional Dependencies:")
for module, package in optional:
    check_import(module, package)

print()
if critical_ok:
    print("✅ All critical dependencies are installed!")
    sys.exit(0)
else:
    print("❌ Some critical dependencies are missing!")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)