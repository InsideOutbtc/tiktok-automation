#!/usr/bin/env python3
"""Simple diagnosis of DatabaseQueries import issue"""

import sys
import os

print("=== Simple Import Diagnosis ===")
print("Python:", sys.version)
print("CWD:", os.getcwd())
print()

# Check file exists
queries_file = 'src/database/queries.py'
print("1. File check:")
print("   Path:", queries_file)
print("   Exists:", os.path.exists(queries_file))

# Try import
print("\n2. Import test:")
try:
    from src.database.queries import DatabaseQueries
    print("   SUCCESS: DatabaseQueries imported")
except ImportError as e:
    print("   FAILED:", str(e))
    print("\n3. Trying module import:")
    try:
        import src.database.queries as q
        print("   Module imported OK")
        print("   Has DatabaseQueries:", hasattr(q, 'DatabaseQueries'))
        if hasattr(q, 'DatabaseQueries'):
            print("   DatabaseQueries class found!")
        else:
            print("   Available classes:", [x for x in dir(q) if not x.startswith('_')])
    except Exception as e2:
        print("   Module import also failed:", str(e2))

# Check case sensitivity
print("\n4. Case sensitivity check:")
for root, dirs, files in os.walk('src'):
    if 'database' in root.lower():
        print("   Found:", root)
        for f in files:
            if 'queries' in f.lower():
                print("     File:", f)