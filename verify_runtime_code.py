#!/usr/bin/env python3
"""
Verify which version of error_handler.py is running in production
"""

import subprocess
import sys

def check_error_handler():
    """Check the actual error_handler.py content at runtime"""
    
    print("=== Runtime Code Verification ===")
    print("This script will check which version of error_handler.py is actually running")
    print()
    
    # Check 1: File location
    print("1. Checking file location:")
    try:
        import src.core.error_handler as eh
        print(f"   Module loaded from: {eh.__file__}")
    except ImportError as e:
        print(f"   ERROR: Could not import error_handler: {e}")
        return
    
    # Check 2: Check for the problematic line
    print("\n2. Checking for old code pattern:")
    with open(eh.__file__, 'r') as f:
        content = f.read()
        line_41 = content.split('\n')[40] if len(content.split('\n')) > 40 else "N/A"
        print(f"   Line 41: {line_41.strip()}")
        
        if "self.error_stats[tier.value] += 1" in content:
            print("   ❌ OLD CODE DETECTED! Found 'self.error_stats[tier.value] += 1'")
            print("   This is the old version that causes errors.")
        else:
            print("   ✅ New code detected (no direct tier.value usage)")
    
    # Check 3: Check error_stats initialization
    print("\n3. Checking error_stats initialization:")
    init_line = next((line for line in content.split('\n') if 'self.error_stats = {' in line), None)
    if init_line:
        print(f"   Found: {init_line.strip()}")
    
    # Check 4: Check for .pyc files
    print("\n4. Checking for compiled bytecode:")
    result = subprocess.run(['find', '/app', '-name', '*.pyc', '-path', '*/error_handler*'], 
                          capture_output=True, text=True)
    if result.stdout:
        print("   ⚠️  Found .pyc files:")
        for line in result.stdout.strip().split('\n'):
            print(f"      {line}")
    else:
        print("   ✅ No error_handler .pyc files found")
    
    # Check 5: Python path
    print("\n5. Python path:")
    print(f"   {sys.path}")
    
    # Check 6: File modification time
    print("\n6. File timestamps:")
    import os
    import datetime
    
    stat = os.stat(eh.__file__)
    mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
    print(f"   Modified: {mod_time}")
    print(f"   Size: {stat.st_size} bytes")

if __name__ == "__main__":
    check_error_handler()