"""
Version tracking for deployment verification.
This file is updated on each deployment to track which version is running.
"""

import os
from datetime import datetime

# Deployment version info
VERSION = "1.0.3"
BUILD_DATE = "2025-08-22T14:15:00Z"
FIXES_INCLUDED = [
    "error_handler.py: Added _tier_map for safe tier value mapping",
    "error_handler.py: Added List import from typing",
    "error_handler.py: Safe error stats tracking without KeyError",
    "Dockerfile: Added .pyc cleanup to prevent stale bytecode",
    ".dockerignore: Added to exclude cache files from Docker build"
]

def get_version_info():
    """Get current version information."""
    return {
        "version": VERSION,
        "build_date": BUILD_DATE,
        "fixes": FIXES_INCLUDED,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "container_id": os.getenv("HOSTNAME", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }

def print_version():
    """Print version information."""
    info = get_version_info()
    print(f"=== TikTok Automation v{info['version']} ===")
    print(f"Build Date: {info['build_date']}")
    print(f"Environment: {info['environment']}")
    print(f"Container: {info['container_id']}")
    print(f"Current Time: {info['timestamp']}")
    print("\nFixes in this version:")
    for fix in info['fixes']:
        print(f"  - {fix}")

if __name__ == "__main__":
    print_version()