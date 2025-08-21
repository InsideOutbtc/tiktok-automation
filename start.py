#!/usr/bin/env python3
"""
PowerPro Safe Startup - Prevents container crash
"""
import os
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set consistent database path
DB_PATH = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
os.environ['DATABASE_PATH'] = DB_PATH

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
        os.chmod(str(dir_path), 0o755)
        logger.info(f"✅ Created/verified directory: {dir_name}")
    
    # Create database file with absolute path
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    if not os.path.exists(DB_PATH):
        Path(DB_PATH).touch()
        os.chmod(DB_PATH, 0o666)
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
        
        # Use the global DB_PATH
        conn = sqlite3.connect(DB_PATH)
        conn.execute('SELECT 1')
        conn.close()
        
        logger.info(f"✅ Database accessible at: {DB_PATH}")
        
        # Set both environment variables
        os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'
        os.environ['DATABASE_PATH'] = DB_PATH
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cannot access database at {DB_PATH}: {e}")
        return False

def health_check_loop():
    """Keep container alive for DigitalOcean health checks"""
    logger.info("🏥 Running in health check mode (container staying alive)")
    logger.info("📝 To start processing: Create /tmp/start_processing file")
    
    while True:
        logger.info(f"💚 Health: OK | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if os.path.exists('/tmp/start_processing'):
            logger.info("🚀 Manual start triggered!")
            return True
            
        if os.getenv('AUTO_PUBLISH', 'false').lower() == 'true':
            logger.info("🚀 AUTO_PUBLISH enabled - starting automation")
            return True
            
        time.sleep(30)

def main():
    """Main entry point with error handling"""
    try:
        logger.info("="*50)
        logger.info("🎬 PowerPro TikTok Automation Starting")
        logger.info("="*50)
        
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
        logger.info("🤖 Starting main automation system...")
        logger.info(f"📁 Using database at: {DB_PATH}")
        logger.info(f"📁 DATABASE_URL: {os.getenv('DATABASE_URL')}")
        
        try:
            # Pass database path explicitly
            from src.database.migrations import run_migrations
            run_migrations(DB_PATH)
            
            from src.core.main_wrapper import main as run_automation
            run_automation()
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            logger.info("🔧 Falling back to health check mode")
            health_check_loop()
            
    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.info("🔧 Entering health check mode to prevent crash")
        health_check_loop()

if __name__ == "__main__":
    main()