#!/usr/bin/env python3
"""
Comprehensive diagnosis for Docker import issues
Run this inside the Docker container to diagnose the DatabaseQueries import problem
"""

import sys
import os
import platform
import subprocess

print("=" * 60)
print("DOCKER IMPORT DIAGNOSIS FOR DATABASEQUERIES")
print("=" * 60)

# 1. Environment Information
print("\n1. ENVIRONMENT INFORMATION:")
print("   Python version:", sys.version)
print("   Platform:", platform.platform())
print("   Machine:", platform.machine())
print("   Working directory:", os.getcwd())
print("   PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))
print("   sys.path:", sys.path[:3], "...")  # Show first 3 entries

# 2. File System Check
print("\n2. FILE SYSTEM CHECK:")
print("   Case sensitive filesystem:", not os.path.exists('SRC') if os.path.exists('src') else 'Unknown')

# Check if directories exist with exact case
dirs_to_check = ['src', 'src/database', 'src/core']
for dir_path in dirs_to_check:
    exists = os.path.exists(dir_path)
    print("   {} exists: {}".format(dir_path, exists))
    if exists:
        # List contents
        contents = os.listdir(dir_path)[:5]  # Show first 5 items
        print("     Contents:", contents)

# 3. Check the specific file
print("\n3. QUERIES.PY FILE CHECK:")
queries_path = 'src/database/queries.py'
if os.path.exists(queries_path):
    print("   File exists:", queries_path)
    print("   File size:", os.path.getsize(queries_path), "bytes")
    print("   Readable:", os.access(queries_path, os.R_OK))
    
    # Check first few lines
    print("   First 3 lines:")
    with open(queries_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            print("     ", line.rstrip())
else:
    print("   FILE NOT FOUND:", queries_path)

# 4. Check __init__.py files
print("\n4. __INIT__.PY FILES:")
init_files = ['src/__init__.py', 'src/database/__init__.py']
for init_file in init_files:
    if os.path.exists(init_file):
        size = os.path.getsize(init_file)
        print("   {} exists (size: {} bytes)".format(init_file, size))
    else:
        print("   {} NOT FOUND".format(init_file))

# 5. Try different import methods
print("\n5. IMPORT TESTS:")

# Test 5.1: Direct import
print("\n   5.1 Direct import attempt:")
try:
    from src.database.queries import DatabaseQueries
    print("      ✓ SUCCESS: DatabaseQueries imported!")
    print("      Type:", type(DatabaseQueries))
except Exception as e:
    print("      ✗ FAILED:", type(e).__name__, "-", str(e))
    
    # If failed, try to import the module
    print("\n   5.2 Module import attempt:")
    try:
        import src.database.queries
        print("      ✓ Module imported")
        attrs = [x for x in dir(src.database.queries) if not x.startswith('_')]
        print("      Available attributes:", attrs[:10])  # Show first 10
        
        if 'DatabaseQueries' in attrs:
            print("      ✓ DatabaseQueries found in module")
        else:
            print("      ✗ DatabaseQueries NOT in module attributes")
            
            # Check for similar names
            similar = [x for x in attrs if 'query' in x.lower() or 'database' in x.lower()]
            if similar:
                print("      Similar attributes found:", similar)
                
    except Exception as e2:
        print("      ✗ Module import failed:", type(e2).__name__, "-", str(e2))

# 6. Check for import dependencies
print("\n6. DEPENDENCY CHECK:")
deps_to_check = ['sqlalchemy', 'sqlalchemy.orm', 'src.database.models']
for dep in deps_to_check:
    try:
        __import__(dep)
        print("   ✓", dep, "available")
    except ImportError as e:
        print("   ✗", dep, "NOT available:", str(e))

# 7. File encoding check
print("\n7. FILE ENCODING CHECK:")
if os.path.exists(queries_path):
    try:
        with open(queries_path, 'rb') as f:
            first_bytes = f.read(3)
            if first_bytes == b'\xef\xbb\xbf':
                print("   WARNING: File has UTF-8 BOM")
            else:
                print("   File encoding looks normal")
    except Exception as e:
        print("   Could not check encoding:", str(e))

# 8. Permission check
print("\n8. PERMISSION CHECK:")
print("   User ID:", os.getuid())
print("   Group ID:", os.getgid())
print("   queries.py permissions:", oct(os.stat(queries_path).st_mode)[-3:] if os.path.exists(queries_path) else "N/A")

# 9. Try importing with modified path
print("\n9. MODIFIED PATH IMPORT:")
src_path = os.path.abspath('src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
    print("   Added {} to sys.path".format(src_path))
    
try:
    from database.queries import DatabaseQueries as DQ
    print("   ✓ SUCCESS with modified path!")
except Exception as e:
    print("   ✗ Still failed:", str(e))

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)