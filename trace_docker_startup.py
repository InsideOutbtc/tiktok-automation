#!/usr/bin/env python3
"""
Trace the exact startup sequence to identify where imports fail
"""
import os
import sys
import traceback

def log(msg):
    """Simple logging function"""
    print(f"[TRACE] {msg}", flush=True)

def main():
    log("="*60)
    log("Docker Startup Trace")
    log("="*60)
    
    # Environment info
    log(f"Python: {sys.version}")
    log(f"CWD: {os.getcwd()}")
    log(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    log(f"AUTO_PUBLISH: {os.getenv('AUTO_PUBLISH', 'Not set')}")
    log(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    
    # Check if we're in Docker
    is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER', False)
    log(f"Running in Docker: {is_docker}")
    
    # Step 1: Basic imports
    log("\n--- Step 1: Basic imports ---")
    try:
        import sqlite3
        log("✅ sqlite3")
    except Exception as e:
        log(f"❌ sqlite3: {e}")
    
    try:
        import logging
        log("✅ logging")
    except Exception as e:
        log(f"❌ logging: {e}")
    
    # Step 2: Third-party dependencies
    log("\n--- Step 2: Third-party dependencies ---")
    deps = [
        'sqlalchemy',
        'tenacity', 
        'openai',
        'yt_dlp',
        'moviepy',
        'PIL',
        'requests',
        'beautifulsoup4',
        'aiohttp',
        'fastapi',
        'prometheus_client'
    ]
    
    missing_deps = []
    for dep in deps:
        try:
            __import__(dep)
            log(f"✅ {dep}")
        except ImportError:
            log(f"❌ {dep} - NOT INSTALLED")
            missing_deps.append(dep)
        except Exception as e:
            log(f"⚠️  {dep}: {type(e).__name__}: {e}")
    
    if missing_deps:
        log(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        log("These need to be installed for the app to work!")
    
    # Step 3: App structure
    log("\n--- Step 3: App structure ---")
    
    # Add app to path
    if os.getcwd() not in sys.path:
        sys.path.insert(0, os.getcwd())
        log("Added current directory to Python path")
    
    # Check src directory
    if not os.path.exists('src'):
        log("❌ 'src' directory not found!")
        log(f"Directory contents: {os.listdir('.')}")
        return
    
    # Step 4: Import chain
    log("\n--- Step 4: Import chain ---")
    
    import_chain = [
        ('src', 'Package root'),
        ('src.database', 'Database package'),
        ('src.database.models', 'Database models (needs sqlalchemy)'),
        ('src.database.migrations', 'Migrations'),
        ('src.database.queries', 'Database queries'),
        ('src.utils', 'Utils package'),
        ('src.utils.constitutional_monitor', 'Constitutional monitor'),
        ('src.core', 'Core package'),
        ('src.core.error_handler', 'Error handler'),
        ('src.core.main_wrapper', 'Main wrapper'),
        ('src.core.main_controller', 'Main controller')
    ]
    
    for module_name, desc in import_chain:
        try:
            module = __import__(module_name, fromlist=[''])
            log(f"✅ {module_name} - {desc}")
        except ImportError as e:
            log(f"❌ {module_name} - {desc}")
            log(f"   ImportError: {e}")
            # Show which specific import failed
            if "No module named" in str(e):
                missing = str(e).split("'")[1]
                log(f"   → Missing: {missing}")
            break
        except Exception as e:
            log(f"❌ {module_name} - {desc}")
            log(f"   {type(e).__name__}: {e}")
            break
    
    # Step 5: Try the actual startup sequence
    log("\n--- Step 5: Startup sequence ---")
    
    try:
        log("Setting up directories...")
        dirs = ['input', 'output', 'processing', 'posted', 'logs', 'database']
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        log("✅ Directories created")
    except Exception as e:
        log(f"❌ Directory setup failed: {e}")
    
    try:
        log("Testing database access...")
        db_path = os.getenv('DATABASE_PATH', 'database/tiktok.db')
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute('SELECT 1')
        conn.close()
        log(f"✅ Database accessible at {db_path}")
    except Exception as e:
        log(f"❌ Database test failed: {e}")
    
    # Final attempt to run main
    log("\n--- Step 6: Main execution ---")
    
    try:
        from src.core.main_wrapper import main
        log("✅ Successfully imported main function")
        log("🚀 Would start automation here...")
        
        # Check if we should actually start
        if os.getenv('AUTO_PUBLISH', 'false').lower() == 'true':
            log("AUTO_PUBLISH=true - automation would start")
        else:
            log("AUTO_PUBLISH=false - would enter health check mode")
            
    except ImportError as e:
        log(f"❌ Cannot import main: {e}")
        log("\nFull traceback:")
        traceback.print_exc()
        log("\n💡 This is why the app falls back to health check mode!")
    except Exception as e:
        log(f"❌ Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()