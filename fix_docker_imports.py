#!/usr/bin/env python3
"""
Fix import issues in Docker environment
This script ensures all modules can be imported correctly
"""

import os
import sys
import shutil

def ensure_init_files():
    """Ensure all __init__.py files exist"""
    print("🔧 Ensuring all __init__.py files exist...")
    
    dirs_needing_init = [
        'src',
        'src/database',
        'src/core',
        'src/agents',
        'src/agents/content_agents',
        'src/utils',
        'src/api',
        'src/mcp'
    ]
    
    for dir_path in dirs_needing_init:
        init_file = os.path.join(dir_path, '__init__.py')
        if not os.path.exists(init_file):
            print(f"   Creating {init_file}")
            os.makedirs(dir_path, exist_ok=True)
            with open(init_file, 'w') as f:
                f.write('# Auto-generated __init__.py\n')
        else:
            # Ensure file is not empty (can cause import issues)
            if os.path.getsize(init_file) == 0:
                print(f"   Fixing empty {init_file}")
                with open(init_file, 'w') as f:
                    f.write('# Auto-generated __init__.py\n')

def fix_imports_in_files():
    """Fix common import issues in Python files"""
    print("\n🔧 Fixing imports in Python files...")
    
    # Files that might have import issues
    files_to_check = [
        'src/core/main_controller.py',
        'src/core/main_wrapper.py',
        'src/database/migrations.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   Checking {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix common import patterns
            original_content = content
            
            # Ensure absolute imports
            if 'from database.queries import' in content:
                content = content.replace('from database.queries import', 'from src.database.queries import')
            
            if 'from database.models import' in content:
                content = content.replace('from database.models import', 'from src.database.models import')
            
            if content != original_content:
                print(f"     Fixed imports in {file_path}")
                with open(file_path, 'w') as f:
                    f.write(content)

def create_import_wrapper():
    """Create a wrapper that handles import issues gracefully"""
    print("\n🔧 Creating import wrapper...")
    
    wrapper_content = '''#!/usr/bin/env python3
"""
Import wrapper for Docker environment
Handles different import scenarios gracefully
"""

import sys
import os

# Add both /app and /app/src to Python path
app_path = '/app' if os.path.exists('/app') else os.getcwd()
src_path = os.path.join(app_path, 'src')

for path in [app_path, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Set database path
os.environ['DATABASE_PATH'] = os.path.join(app_path, 'database', 'tiktok.db')
os.environ['DATABASE_URL'] = f"sqlite:///{os.environ['DATABASE_PATH']}"

# Import helper function
def safe_import(module_name, class_name=None):
    """Safely import a module or class"""
    try:
        if class_name:
            module = __import__(module_name, fromlist=[class_name])
            return getattr(module, class_name)
        else:
            return __import__(module_name)
    except ImportError as e:
        print(f"Import error for {module_name}: {e}")
        # Try alternative import paths
        if module_name.startswith('src.'):
            alt_name = module_name[4:]  # Remove 'src.' prefix
            try:
                if class_name:
                    module = __import__(alt_name, fromlist=[class_name])
                    return getattr(module, class_name)
                else:
                    return __import__(alt_name)
            except ImportError:
                pass
        raise

# Pre-import critical modules
try:
    DatabaseQueries = safe_import('src.database.queries', 'DatabaseQueries')
    print("✓ DatabaseQueries imported successfully")
except Exception as e:
    print(f"✗ Failed to import DatabaseQueries: {e}")
'''
    
    with open('src/import_helper.py', 'w') as f:
        f.write(wrapper_content)
    print("   Created src/import_helper.py")

def verify_docker_setup():
    """Verify the Docker setup will work"""
    print("\n🔍 Verifying setup...")
    
    issues = []
    
    # Check critical files
    critical_files = [
        'src/__init__.py',
        'src/database/__init__.py',
        'src/database/queries.py',
        'src/database/models.py',
        'src/core/main_controller.py',
        'start.py'
    ]
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing file: {file_path}")
        elif os.path.getsize(file_path) == 0:
            issues.append(f"Empty file: {file_path}")
    
    # Check if queries.py has DatabaseQueries class
    if os.path.exists('src/database/queries.py'):
        with open('src/database/queries.py', 'r') as f:
            content = f.read()
            if 'class DatabaseQueries' not in content:
                issues.append("DatabaseQueries class not found in queries.py")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ All checks passed!")

def main():
    print("="*60)
    print("DOCKER IMPORT FIX SCRIPT")
    print("="*60)
    
    # Run fixes
    ensure_init_files()
    fix_imports_in_files()
    create_import_wrapper()
    verify_docker_setup()
    
    print("\n" + "="*60)
    print("✅ Fix script completed!")
    print("\nNext steps:")
    print("1. Build Docker image: docker build -f Dockerfile.fixed -t powerpro-fixed .")
    print("2. Run with debug: docker run -it powerpro-fixed python docker_debug_imports.py")
    print("3. Run normally: docker run -it powerpro-fixed")
    print("="*60)

if __name__ == "__main__":
    main()