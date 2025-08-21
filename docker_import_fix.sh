#!/bin/bash
# Script to diagnose and fix DatabaseQueries import issues in Docker

echo "=== Docker Import Fix Script ==="
echo "Run this script inside your Docker container"
echo ""

# 1. Show environment
echo "1. Environment Check:"
echo "   Python version: $(python --version 2>&1)"
echo "   Working directory: $(pwd)"
echo "   PYTHONPATH: $PYTHONPATH"
echo ""

# 2. Check file existence
echo "2. File System Check:"
echo "   src directory exists: $(test -d src && echo 'YES' || echo 'NO')"
echo "   src/database exists: $(test -d src/database && echo 'YES' || echo 'NO')"
echo "   queries.py exists: $(test -f src/database/queries.py && echo 'YES' || echo 'NO')"

# 3. Case sensitivity test
echo ""
echo "3. Case Sensitivity Test:"
if [ -d "src" ] && [ ! -d "SRC" ]; then
    echo "   File system is case-sensitive (Linux-like) ✓"
else
    echo "   File system might be case-insensitive"
fi

# 4. List actual files
echo ""
echo "4. Actual files in src/database:"
ls -la src/database/ 2>/dev/null | grep -E "\.py$" | head -5

# 5. Test imports
echo ""
echo "5. Testing imports..."

# Create test script
cat > /tmp/test_import.py << 'EOF'
import sys
import os

print("\nTest 1: Standard import")
try:
    from src.database.queries import DatabaseQueries
    print("✓ SUCCESS: Standard import works")
except Exception as e:
    print("✗ FAILED:", str(e))
    
    print("\nTest 2: Adding /app to path")
    if '/app' not in sys.path:
        sys.path.insert(0, '/app')
    try:
        from src.database.queries import DatabaseQueries
        print("✓ SUCCESS: Import works with /app in path")
    except Exception as e2:
        print("✗ FAILED:", str(e2))
        
        print("\nTest 3: Module import")
        try:
            import src.database.queries as queries_module
            if hasattr(queries_module, 'DatabaseQueries'):
                print("✓ SUCCESS: Module has DatabaseQueries")
            else:
                attrs = [x for x in dir(queries_module) if 'Database' in x or 'Query' in x]
                print("✗ DatabaseQueries not found. Similar attrs:", attrs)
        except Exception as e3:
            print("✗ Module import failed:", str(e3))

print("\nDiagnostic info:")
print("sys.path:", sys.path[:3])
print("Current dir:", os.getcwd())
EOF

python /tmp/test_import.py

# 6. Suggested fixes
echo ""
echo "=== SUGGESTED FIXES ==="
echo ""
echo "If imports are failing, try these solutions:"
echo ""
echo "1. In your Dockerfile, ensure:"
echo "   ENV PYTHONPATH=/app:\$PYTHONPATH"
echo "   WORKDIR /app"
echo ""
echo "2. In your Python code, add at the top:"
echo "   import sys"
echo "   import os"
echo "   sys.path.insert(0, '/app')"
echo ""
echo "3. Alternative import methods:"
echo "   # Method A - Via __init__.py"
echo "   from src.database import DatabaseQueries"
echo ""
echo "   # Method B - Direct with path fix"
echo "   import sys"
echo "   sys.path.append('/app')"
echo "   from src.database.queries import DatabaseQueries"
echo ""
echo "4. Check for typos in case-sensitive Linux:"
echo "   - 'DatabaseQueries' not 'databasequeries'"
echo "   - 'queries.py' not 'Queries.py'"
echo ""

# Clean up
rm -f /tmp/test_import.py