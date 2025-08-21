#!/usr/bin/env python3
"""
Production-ready startup script with proper error handling and diagnostics
"""
import os
import sys
import time
import logging
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/startup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Ensure Python can find our modules
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

# Set consistent database path
DB_PATH = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['DATABASE_PATH'] = DB_PATH

def setup_environment():
    """Setup the runtime environment"""
    logger.info("="*60)
    logger.info("🚀 PowerPro TikTok Automation - Production Startup")
    logger.info("="*60)
    
    # Log environment
    logger.info(f"Python: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    logger.info(f"AUTO_PUBLISH: {os.getenv('AUTO_PUBLISH', 'false')}")
    logger.info(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Create required directories
    dirs = [
        'input', 'output', 'processing', 'posted', 'logs', 'database',
        'assets/watermarks', 'assets/logos'
    ]
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    logger.info("✅ Directories created")
    
    # Initialize database file
    if not os.path.exists(DB_PATH):
        Path(DB_PATH).touch()
        logger.info(f"✅ Created database at {DB_PATH}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = [
        'sqlalchemy',
        'tenacity',
        'openai',
        'yt_dlp',
        'moviepy',
        'PIL',
        'aiohttp',
        'fastapi'
    ]
    
    missing = []
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"❌ Missing dependencies: {', '.join(missing)}")
        logger.error("Please ensure all requirements are installed")
        return False
    
    logger.info("✅ All dependencies available")
    return True

def validate_configuration():
    """Validate configuration"""
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not youtube_key:
        logger.warning("⚠️  YOUTUBE_API_KEY not set")
        return False
    if not openai_key:
        logger.warning("⚠️  OPENAI_API_KEY not set")
        return False
    
    logger.info("✅ API keys configured")
    return True

def test_imports():
    """Test critical imports before starting"""
    try:
        # Test database access first
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.execute('SELECT 1')
        conn.close()
        logger.info("✅ Database accessible")
        
        # Test core imports
        from src.database import migrations
        logger.info("✅ Database migrations importable")
        
        from src.core.main_wrapper import main
        logger.info("✅ Main controller importable")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.debug(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        return False

def health_check_server():
    """Run a simple health check server"""
    logger.info("🏥 Starting health check mode")
    logger.info("📝 Container is running but automation is paused")
    
    start_time = time.time()
    check_interval = 30
    
    while True:
        uptime = int(time.time() - start_time)
        logger.info(f"💚 Health: OK | Uptime: {uptime}s | AUTO_PUBLISH: {os.getenv('AUTO_PUBLISH', 'false')}")
        
        # Check if we should start processing
        if os.getenv('AUTO_PUBLISH', 'false').lower() == 'true':
            logger.info("🚀 AUTO_PUBLISH detected - attempting to start automation")
            
            # Re-check imports
            if test_imports():
                return True  # Exit health check mode
            else:
                logger.error("❌ Import check failed - staying in health check mode")
        
        # Check for manual trigger
        if os.path.exists('/tmp/start_processing'):
            logger.info("🚀 Manual trigger detected")
            os.remove('/tmp/start_processing')
            return True
        
        time.sleep(check_interval)

def run_automation():
    """Run the actual automation"""
    try:
        logger.info("🤖 Starting automation system...")
        
        # Run migrations
        from src.database.migrations import run_migrations
        run_migrations(DB_PATH)
        logger.info("✅ Database migrations complete")
        
        # Start main controller
        from src.core.main_wrapper import main
        main()
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        logger.error(traceback.format_exc())
        raise

def main():
    """Main entry point"""
    try:
        # Setup environment
        setup_environment()
        
        # Check dependencies
        if not check_dependencies():
            logger.error("❌ Dependency check failed")
            health_check_server()
            return
        
        # Validate configuration
        config_valid = validate_configuration()
        
        # Test imports
        imports_ok = test_imports()
        
        # Determine startup mode
        is_production = os.getenv('ENVIRONMENT') == 'production'
        auto_publish = os.getenv('AUTO_PUBLISH', 'false').lower() == 'true'
        
        if is_production and not (config_valid and imports_ok and auto_publish):
            logger.info("⏸️  Production mode: Entering health check")
            if health_check_server():
                # Health check returned True, try to start
                run_automation()
        else:
            # Development mode or everything ready
            if config_valid and imports_ok:
                run_automation()
            else:
                logger.error("❌ Cannot start automation - configuration or imports invalid")
                health_check_server()
                
    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
        
        # In production, keep container alive
        if os.getenv('ENVIRONMENT') == 'production':
            logger.info("🔧 Entering health check mode to prevent container restart")
            health_check_server()
        else:
            sys.exit(1)

if __name__ == "__main__":
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    main()