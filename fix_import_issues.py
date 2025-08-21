#!/usr/bin/env python3
"""
Fix common import issues for DatabaseQueries in Docker container
"""

import os
import sys

def fix_init_files():
    """Ensure all __init__.py files exist and are properly formatted"""
    init_files = [
        'src/__init__.py',
        'src/database/__init__.py',
        'src/core/__init__.py',
        'src/agents/__init__.py',
        'src/utils/__init__.py',
        'src/mcp/__init__.py'
    ]
    
    for init_file in init_files:
        dir_path = os.path.dirname(init_file)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print("Created directory:", dir_path)
        
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Auto-generated __init__.py\n')
            print("Created:", init_file)
        else:
            # Ensure file is not empty and has proper encoding
            with open(init_file, 'r+') as f:
                content = f.read()
                if not content or content.isspace():
                    f.seek(0)
                    f.write('# Auto-generated __init__.py\n')
                    f.truncate()
                    print("Fixed empty:", init_file)

def fix_database_init():
    """Add proper exports to database __init__.py"""
    db_init = 'src/database/__init__.py'
    
    init_content = '''# Database module initialization
from .models import Base, Video, Clip, Publication, Pattern, Task, get_session
from .queries import DatabaseQueries, OptimizedQueries, QueryCache

__all__ = [
    'Base', 'Video', 'Clip', 'Publication', 'Pattern', 'Task',
    'get_session', 'DatabaseQueries', 'OptimizedQueries', 'QueryCache'
]
'''
    
    with open(db_init, 'w') as f:
        f.write(init_content)
    print("Updated database __init__.py with proper exports")

def check_file_permissions():
    """Ensure all Python files are readable"""
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    # Make sure file is readable
                    os.chmod(filepath, 0o644)
                except Exception as e:
                    print("Could not fix permissions for {}: {}".format(filepath, e))

def create_import_wrapper():
    """Create a wrapper that handles import issues gracefully"""
    wrapper_content = '''#!/usr/bin/env python3
"""
Import wrapper for DatabaseQueries to handle Docker environment issues
"""

import sys
import os

# Ensure src is in path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    # Try standard import
    from src.database.queries import DatabaseQueries
except ImportError:
    try:
        # Try without src prefix
        sys.path.insert(0, os.path.join(src_path, 'src'))
        from database.queries import DatabaseQueries
    except ImportError:
        # Last resort - import directly
        import importlib.util
        queries_path = os.path.join(src_path, 'src', 'database', 'queries.py')
        spec = importlib.util.spec_from_file_location("queries", queries_path)
        queries = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(queries)
        DatabaseQueries = queries.DatabaseQueries

# Export
__all__ = ['DatabaseQueries']
'''
    
    wrapper_path = 'src/database/database_queries_wrapper.py'
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    print("Created import wrapper at:", wrapper_path)

def main():
    print("=== Fixing Import Issues ===")
    
    print("\n1. Fixing __init__.py files...")
    fix_init_files()
    
    print("\n2. Updating database __init__.py...")
    fix_database_init()
    
    print("\n3. Checking file permissions...")
    check_file_permissions()
    
    print("\n4. Creating import wrapper...")
    create_import_wrapper()
    
    print("\n=== Fixes Applied ===")
    print("\nTo use in your code, you can now import in multiple ways:")
    print("1. Standard: from src.database.queries import DatabaseQueries")
    print("2. Via init: from src.database import DatabaseQueries")
    print("3. Via wrapper: from src.database.database_queries_wrapper import DatabaseQueries")
    
    print("\nFor Docker, make sure your Dockerfile includes:")
    print("ENV PYTHONPATH=/app:$PYTHONPATH")
    print("WORKDIR /app")

if __name__ == "__main__":
    main()