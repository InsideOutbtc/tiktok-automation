#!/usr/bin/env python3
"""
Diagnose import issues for DatabaseQueries class
Tests various import methods to identify the problem
"""

import sys
import os
import traceback

print("=== Import Diagnosis for DatabaseQueries ===")
print("Python version: " + str(sys.version))
print("Current working directory: " + str(os.getcwd()))
print("PYTHONPATH: " + str(sys.path))
print()

# Test 1: Check if the file exists
print("Test 1: Checking if queries.py exists...")
queries_path = os.path.join(os.getcwd(), 'src', 'database', 'queries.py')
if os.path.exists(queries_path):
    print(f"✅ File exists at: {queries_path}")
    print(f"   File size: {os.path.getsize(queries_path)} bytes")
else:
    print(f"❌ File NOT found at: {queries_path}")

# Test 2: Check case sensitivity
print("\nTest 2: Checking directory case sensitivity...")
for root, dirs, files in os.walk('src'):
    if 'database' in root:
        print(f"   Directory: {root}")
        print(f"   Files: {files}")

# Test 3: Try different import methods
print("\nTest 3: Testing different import methods...")

# Method 1: Direct import
print("\n3.1: Direct import from src.database.queries...")
try:
    from src.database.queries import DatabaseQueries
    print("✅ Success! DatabaseQueries imported")
    print(f"   Class type: {type(DatabaseQueries)}")
    print(f"   Module: {DatabaseQueries.__module__}")
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()

# Method 2: Import module first
print("\n3.2: Import module first...")
try:
    import src.database.queries
    print("✅ Module imported successfully")
    print(f"   Module path: {src.database.queries.__file__}")
    
    # Check what's in the module
    print("   Available attributes:")
    for attr in dir(src.database.queries):
        if not attr.startswith('_'):
            print(f"      - {attr}")
    
    # Try to get DatabaseQueries
    if hasattr(src.database.queries, 'DatabaseQueries'):
        print("✅ DatabaseQueries found in module")
        DatabaseQueries = src.database.queries.DatabaseQueries
        print(f"   Class: {DatabaseQueries}")
    else:
        print("❌ DatabaseQueries not found in module")
        
except Exception as e:
    print(f"❌ Failed: {e}")
    traceback.print_exc()

# Method 3: Add to path and import
print("\n3.3: Adding src to path explicitly...")
src_path = os.path.join(os.getcwd(), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print(f"   Added {src_path} to sys.path")

try:
    from database.queries import DatabaseQueries
    print("✅ Success with modified path!")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 4: Check for circular imports
print("\nTest 4: Checking for circular imports...")
try:
    # Import just the models to see if there's a circular dependency
    from src.database.models import Video, Clip
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Models import failed: {e}")

# Test 5: Check __init__.py files
print("\nTest 5: Checking __init__.py files...")
init_files = [
    'src/__init__.py',
    'src/database/__init__.py'
]
for init_file in init_files:
    if os.path.exists(init_file):
        size = os.path.getsize(init_file)
        print(f"✅ {init_file} exists (size: {size} bytes)")
        if size == 0:
            print("   ⚠️  File is empty")
    else:
        print(f"❌ {init_file} NOT found")

# Test 6: Environment differences
print("\nTest 6: Environment checks...")
print(f"Platform: {sys.platform}")
print(f"File system encoding: {sys.getfilesystemencoding()}")
print(f"Default encoding: {sys.getdefaultencoding()}")

# Test 7: Import with absolute path
print("\nTest 7: Import using importlib...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("queries", queries_path)
    queries_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(queries_module)
    print("✅ Module loaded with importlib")
    
    if hasattr(queries_module, 'DatabaseQueries'):
        print("✅ DatabaseQueries found via importlib")
    else:
        print("❌ DatabaseQueries not found in module loaded via importlib")
        print(f"   Available: {[attr for attr in dir(queries_module) if not attr.startswith('_')]}")
        
except Exception as e:
    print(f"❌ Importlib failed: {e}")
    traceback.print_exc()

print("\n=== Diagnosis Complete ===")