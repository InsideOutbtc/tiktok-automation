#!/usr/bin/env python3
"""
Diagnose import failures in production environment
"""
import os
import sys
import traceback
import importlib.util

def check_module_exists(module_name):
    """Check if a module can be found"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def test_import(module_path, description):
    """Test importing a specific module"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Module: {module_path}")
    
    try:
        # Check if module exists first
        if '.' in module_path:
            parts = module_path.split('.')
            parent = '.'.join(parts[:-1])
            if parent and not check_module_exists(parent):
                print(f"❌ Parent module '{parent}' not found")
                return False
        
        # Try to import
        module = __import__(module_path, fromlist=[''])
        print(f"✅ Import successful")
        
        # Check module file location
        if hasattr(module, '__file__'):
            print(f"📁 Located at: {module.__file__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        # Get more details about the import error
        tb = traceback.format_exc()
        if "No module named" in str(e):
            missing = str(e).split("'")[1]
            print(f"   Missing module: {missing}")
        print("\nTraceback:")
        print(tb)
        return False
        
    except Exception as e:
        print(f"❌ {type(e).__name__}: {e}")
        print("\nTraceback:")
        print(traceback.format_exc())
        return False

def check_path_setup():
    """Check Python path configuration"""
    print("\n" + "="*60)
    print("Python Path Configuration")
    print("="*60)
    
    print(f"Current directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    print("\nPYTHONPATH:")
    for i, path in enumerate(sys.path):
        print(f"  [{i}] {path}")
    
    print("\nEnvironment variables:")
    print(f"  PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print(f"  DATABASE_PATH: {os.getenv('DATABASE_PATH', 'Not set')}")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")

def check_file_structure():
    """Check if all expected files exist"""
    print("\n" + "="*60)
    print("File Structure Check")
    print("="*60)
    
    critical_files = [
        'src/__init__.py',
        'src/core/__init__.py',
        'src/core/main_controller.py',
        'src/core/main_wrapper.py',
        'src/database/__init__.py',
        'src/database/migrations.py',
        'src/database/queries.py',
        'src/utils/__init__.py',
        'src/utils/constitutional_monitor.py',
        'src/core/error_handler.py',
        'src/core/content_sourcer.py',
        'src/core/smart_clipper.py',
        'src/core/video_editor.py',
        'src/agents/__init__.py',
        'src/agents/ai_agent_system.py',
        'src/mcp/__init__.py',
        'src/mcp/mcp_client.py',
        'src/utils/monitoring.py'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def main():
    """Run complete diagnostic"""
    print("🔍 Docker Import Diagnostic Tool")
    print("================================\n")
    
    # Add current directory to Python path if not present
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
    
    # Check path setup
    check_path_setup()
    
    # Check file structure
    files_ok = check_file_structure()
    if not files_ok:
        print("\n⚠️  Some files are missing! This will cause import failures.")
    
    # Test imports in order of dependency
    test_imports = [
        ('src', 'Source package root'),
        ('src.database', 'Database package'),
        ('src.database.migrations', 'Database migrations'),
        ('src.database.queries', 'Database queries'),
        ('src.utils', 'Utils package'),
        ('src.utils.constitutional_monitor', 'Constitutional Monitor'),
        ('src.core', 'Core package'),
        ('src.core.error_handler', 'Error Handler'),
        ('src.core.content_sourcer', 'Content Sourcer'),
        ('src.core.smart_clipper', 'Smart Clipper'),
        ('src.core.video_editor', 'Video Editor'),
        ('src.agents', 'Agents package'),
        ('src.agents.ai_agent_system', 'AI Agent System'),
        ('src.mcp', 'MCP package'),
        ('src.mcp.mcp_client', 'MCP Client'),
        ('src.utils.monitoring', 'Monitoring'),
        ('src.core.main_controller', 'Main Controller'),
        ('src.core.main_wrapper', 'Main Wrapper'),
    ]
    
    success_count = 0
    failed_imports = []
    
    for module_path, description in test_imports:
        if test_import(module_path, description):
            success_count += 1
        else:
            failed_imports.append((module_path, description))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tests: {len(test_imports)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(failed_imports)}")
    
    if failed_imports:
        print("\n❌ Failed imports:")
        for module_path, description in failed_imports:
            print(f"   - {module_path} ({description})")
        
        # Suggest fixes
        print("\n💡 Suggested fixes:")
        print("1. Ensure PYTHONPATH includes the app directory:")
        print("   export PYTHONPATH=/app:$PYTHONPATH")
        print("2. Check if all __init__.py files exist")
        print("3. Verify all dependencies are installed")
        print("4. Check for circular imports")
    else:
        print("\n✅ All imports successful!")

if __name__ == "__main__":
    main()