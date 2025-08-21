#!/usr/bin/env python3
"""
PowerPro Safe Startup for Docker - Enhanced error handling
"""
import os
import sys
import time
import logging
import platform
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure Python path is set correctly for Docker
if platform.system() == 'Linux' and os.path.exists('/.dockerenv'):
    logger.info("🐳 Running in Docker container")
    # Add both /app and /app/src to path
    for path in ['/app', '/app/src']:
        if path not in sys.path:
            sys.path.insert(0, path)

# Set consistent database path
DB_PATH = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['DATABASE_PATH'] = DB_PATH

def diagnose_import_issues():
    """Diagnose import issues before attempting main import"""
    logger.info("🔍 Diagnosing import environment...")
    
    # Check Python path
    logger.info(f"   Python path: {sys.path[:3]}...")
    
    # Check if src directory exists
    if os.path.exists('src'):
        logger.info("   ✓ src/ directory found")
        
        # Check __init__.py files
        init_files = ['src/__init__.py', 'src/database/__init__.py']
        for init_file in init_files:
            if os.path.exists(init_file):
                size = os.path.getsize(init_file)
                logger.info(f"   ✓ {init_file} exists (size: {size})")
            else:
                logger.warning(f"   ✗ {init_file} missing!")
                # Create it
                Path(init_file).parent.mkdir(parents=True, exist_ok=True)
                with open(init_file, 'w') as f:
                    f.write('# Auto-generated\n')
                logger.info(f"   ✓ Created {init_file}")
    else:
        logger.error("   ✗ src/ directory not found!")
        return False
    
    # Test basic imports
    try:
        import src
        logger.info("   ✓ Can import src module")
    except ImportError as e:
        logger.error(f"   ✗ Cannot import src: {e}")
        return False
    
    try:
        import src.database
        logger.info("   ✓ Can import src.database module")
    except ImportError as e:
        logger.error(f"   ✗ Cannot import src.database: {e}")
        return False
    
    return True

def setup_directories():
    """Create all required directories with proper permissions"""
    dirs = [
        'input', 
        'output', 
        'processing', 
        'posted', 
        'logs', 
        'database',
        'assets/watermarks', 
        'assets/logos'
    ]
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(str(dir_path), 0o755)
        except Exception as e:
            logger.warning(f"Could not set permissions for {dir_name}: {e}")
        logger.info(f"✅ Created/verified directory: {dir_name}")
    
    # Create database file
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        Path(DB_PATH).touch()
        try:
            os.chmod(DB_PATH, 0o666)
        except Exception as e:
            logger.warning(f"Could not set database permissions: {e}")
        logger.info(f"✅ Created database file at: {DB_PATH}")
    
    logger.info("✅ All directories and files ready")

def check_environment():
    """Check if environment is properly configured"""
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not youtube_key:
        logger.warning("⚠️ YOUTUBE_API_KEY not set - will run in health check mode")
        return False
    if not openai_key:
        logger.warning("⚠️ OPENAI_API_KEY not set - will run in health check mode")
        return False
    
    logger.info("✅ All API keys configured")
    return True

def test_database_access():
    """Test if we can access the database"""
    try:
        import sqlite3
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute('SELECT 1')
        conn.close()
        
        logger.info(f"✅ Database accessible at: {DB_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cannot access database at {DB_PATH}: {e}")
        return False

def health_check_loop():
    """Keep container alive for DigitalOcean health checks"""
    logger.info("🏥 Running in health check mode (container staying alive)")
    logger.info("📝 System info:")
    logger.info(f"   Platform: {platform.system()} {platform.release()}")
    logger.info(f"   Python: {sys.version.split()[0]}")
    logger.info(f"   Working directory: {os.getcwd()}")
    
    while True:
        logger.info(f"💚 Health: OK | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if os.path.exists('/tmp/start_processing'):
            logger.info("🚀 Manual start triggered!")
            return True
            
        if os.getenv('AUTO_PUBLISH', 'false').lower() == 'true':
            logger.info("🚀 AUTO_PUBLISH enabled - starting automation")
            return True
            
        time.sleep(30)

def attempt_main_import():
    """Attempt to import main controller with detailed error handling"""
    logger.info("🤖 Attempting to import main automation system...")
    
    try:
        # First try migrations
        logger.info("   Loading database migrations...")
        from src.database.migrations import run_migrations
        run_migrations(DB_PATH)
        logger.info("   ✓ Migrations loaded")
        
        # Then try main wrapper
        logger.info("   Loading main controller...")
        from src.core.main_wrapper import main as run_automation
        logger.info("   ✓ Main controller loaded")
        
        return run_automation
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        
        # Try to diagnose specific import issue
        import traceback
        logger.error("Full traceback:")
        traceback.print_exc()
        
        # Check if it's the DatabaseQueries issue
        if 'DatabaseQueries' in str(e):
            logger.error("🔧 DatabaseQueries import issue detected")
            logger.info("   Attempting alternative import method...")
            
            try:
                # Try direct import
                import src.database.queries
                if hasattr(src.database.queries, 'DatabaseQueries'):
                    logger.info("   ✓ DatabaseQueries class found in module")
                else:
                    logger.error("   ✗ DatabaseQueries class not found in module")
                    logger.info(f"   Available: {[x for x in dir(src.database.queries) if not x.startswith('_')]}")
            except Exception as e2:
                logger.error(f"   Alternative import also failed: {e2}")
        
        return None

def main():
    """Main entry point with enhanced error handling"""
    try:
        logger.info("="*50)
        logger.info("🎬 PowerPro TikTok Automation Starting (Docker-Safe)")
        logger.info("="*50)
        
        # Diagnose import environment first
        if not diagnose_import_issues():
            logger.error("❌ Import diagnosis failed - entering health check mode")
            health_check_loop()
            return
        
        # Setup environment
        setup_directories()
        
        # Test database access
        if not test_database_access():
            logger.error("❌ Database access failed - entering health check mode")
            health_check_loop()
            return
        
        # Check configuration
        env_ready = check_environment()
        
        # In production, check if we should start
        if os.getenv('ENVIRONMENT') == 'production':
            if not env_ready:
                logger.info("⏸️ Missing configuration - staying in health check mode")
                health_check_loop()
            
            if os.getenv('AUTO_PUBLISH', 'false').lower() != 'true':
                logger.info("⏸️ AUTO_PUBLISH=false - staying in health check mode")
                if not health_check_loop():
                    return
        
        # Try to import and run main controller
        run_automation = attempt_main_import()
        
        if run_automation:
            logger.info("🚀 Starting automation...")
            run_automation()
        else:
            logger.error("❌ Failed to load main controller")
            logger.info("🔧 Falling back to health check mode")
            health_check_loop()
            
    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        logger.info("🔧 Entering health check mode to prevent crash")
        health_check_loop()

if __name__ == "__main__":
    main()