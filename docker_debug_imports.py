#!/usr/bin/env python3
"""
Docker Import Debug Script
Tests imports in the same way Docker container would
"""

import sys
import os
import platform
import traceback

print("="*60)
print("DOCKER IMPORT DEBUG SCRIPT")
print("="*60)

# System info
print("\n1. SYSTEM INFO:")
print(f"   Platform: {platform.system()} {platform.release()}")
print(f"   Python: {sys.version}")
print(f"   Python executable: {sys.executable}")
print(f"   Current directory: {os.getcwd()}")
print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

# Check paths
print("\n2. PYTHON PATH:")
for i, p in enumerate(sys.path):
    print(f"   [{i}] {p}")

# Check directory structure
print("\n3. DIRECTORY STRUCTURE:")
for root_dir in ['src', '/app/src']:
    if os.path.exists(root_dir):
        print(f"   {root_dir}/ exists")
        db_dir = os.path.join(root_dir, 'database')
        if os.path.exists(db_dir):
            print(f"   {db_dir}/ exists")
            files = os.listdir(db_dir)
            for f in sorted(files):
                print(f"      - {f}")

# Check __init__.py files
print("\n4. CHECKING __init__.py FILES:")
init_files = [
    'src/__init__.py',
    'src/database/__init__.py',
    '/app/src/__init__.py',
    '/app/src/database/__init__.py'
]
for init_file in init_files:
    if os.path.exists(init_file):
        size = os.path.getsize(init_file)
        print(f"   ✓ {init_file} (size: {size} bytes)")
    else:
        print(f"   ✗ {init_file} NOT FOUND")

# Test imports step by step
print("\n5. TESTING IMPORTS STEP BY STEP:")

# Test 1: Import src
print("\n   Test 1: import src")
try:
    import src
    print("   ✓ SUCCESS: src imported")
    print(f"     src.__file__ = {getattr(src, '__file__', 'No __file__')}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()

# Test 2: Import src.database
print("\n   Test 2: import src.database")
try:
    import src.database
    print("   ✓ SUCCESS: src.database imported")
    print(f"     src.database.__file__ = {getattr(src.database, '__file__', 'No __file__')}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()

# Test 3: Import src.database.queries
print("\n   Test 3: import src.database.queries")
try:
    import src.database.queries
    print("   ✓ SUCCESS: src.database.queries imported")
    print(f"     Module attributes: {[x for x in dir(src.database.queries) if not x.startswith('_')]}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()

# Test 4: Import DatabaseQueries
print("\n   Test 4: from src.database.queries import DatabaseQueries")
try:
    from src.database.queries import DatabaseQueries
    print("   ✓ SUCCESS: DatabaseQueries imported")
    print(f"     Type: {type(DatabaseQueries)}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()

# Test models import (dependency)
print("\n   Test 5: from src.database.models import Video, Clip")
try:
    from src.database.models import Video, Clip
    print("   ✓ SUCCESS: Models imported")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()

# Check SQLAlchemy
print("\n6. CHECKING DEPENDENCIES:")
try:
    import sqlalchemy
    print(f"   ✓ SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError:
    print("   ✗ SQLAlchemy NOT INSTALLED")

# Check case sensitivity issue
print("\n7. CHECKING CASE SENSITIVITY:")
if platform.system() == "Linux":
    print("   Running on Linux - case sensitive filesystem")
    # Check if there are any case mismatches
    for root, dirs, files in os.walk('.'):
        if 'database' in root.lower():
            for f in files:
                if f.endswith('.py'):
                    print(f"   Found: {os.path.join(root, f)}")

# Docker-specific checks
print("\n8. DOCKER-SPECIFIC CHECKS:")
if os.path.exists('/.dockerenv'):
    print("   ✓ Running inside Docker container")
else:
    print("   ✗ NOT running in Docker container")

# Check if running as expected user
print(f"   User ID: {os.getuid() if hasattr(os, 'getuid') else 'N/A'}")
print(f"   User: {os.environ.get('USER', 'Unknown')}")

# File permissions
print("\n9. FILE PERMISSIONS:")
files_to_check = [
    'src/database/queries.py',
    'src/database/__init__.py',
    'src/__init__.py'
]
for file_path in files_to_check:
    if os.path.exists(file_path):
        stat = os.stat(file_path)
        print(f"   {file_path}: {oct(stat.st_mode)[-3:]}")

print("\n" + "="*60)
print("END OF DIAGNOSTICS")
print("="*60)