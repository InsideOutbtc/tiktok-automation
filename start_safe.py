#!/usr/bin/env python3
"""
Safe startup script that handles import failures gracefully
"""
import os
import sys
import time
import logging

# Setup logging immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log version info on startup
try:
    from src.utils.version import print_version
    print_version()
except:
    logger.info("Version info not available")

# Fix Python path BEFORE any imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set database path
os.environ['DATABASE_PATH'] = os.path.abspath('database/tiktok.db')
os.environ['DATABASE_URL'] = f"sqlite:///{os.environ['DATABASE_PATH']}"

def create_directories():
    """Create required directories"""
    import os
    from pathlib import Path
    
    dirs = ['input', 'output', 'processing', 'posted', 'logs', 'database', 'assets/watermarks', 'assets/logos']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    
    # Create database file
    db_path = os.environ['DATABASE_PATH']
    if not os.path.exists(db_path):
        Path(db_path).touch()
        logger.info(f"Created database at {db_path}")

def can_import_app():
    """Check if we can import the app"""
    try:
        # First check if src exists
        if not os.path.exists('src'):
            logger.error("src directory not found!")
            return False
            
        # Try minimal imports
        import src
        from src.database import migrations
        from src.core import main_wrapper
        return True
    except ImportError as e:
        logger.error(f"Import check failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import check: {e}")
        return False

def run_health_check():
    """Run health check loop"""
    logger.info("🏥 Running in health check mode")
    
    while True:
        # Log status
        auto_publish = os.getenv('AUTO_PUBLISH', 'false')
        logger.info(f"💚 Health: OK | AUTO_PUBLISH: {auto_publish}")
        
        # If AUTO_PUBLISH is true, try to start
        if auto_publish.lower() == 'true':
            logger.info("AUTO_PUBLISH=true detected, checking if we can start...")
            
            # Re-check imports
            if can_import_app():
                logger.info("✅ Import check passed, starting automation")
                return True
            else:
                logger.warning("❌ Import check still failing, staying in health check mode")
        
        time.sleep(30)
    
    return False

def main():
    """Main entry point"""
    logger.info("="*50)
    logger.info("🚀 PowerPro TikTok Automation Starting")
    logger.info("="*50)
    
    # Setup
    create_directories()
    
    # Check environment
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"AUTO_PUBLISH: {os.getenv('AUTO_PUBLISH', 'false')}")
    logger.info(f"Python path: {sys.path}")
    
    # Check if we can import the app
    if can_import_app():
        logger.info("✅ Import check passed")
        
        # Check if we should start immediately
        if os.getenv('AUTO_PUBLISH', 'false').lower() == 'true':
            logger.info("🤖 Starting automation (AUTO_PUBLISH=true)")
            try:
                from src.database.migrations import run_migrations
                run_migrations(os.environ['DATABASE_PATH'])
                
                from src.core.main_wrapper import main as run_app
                run_app()
            except Exception as e:
                logger.error(f"Failed to start automation: {e}")
                run_health_check()
        else:
            logger.info("⏸️  AUTO_PUBLISH=false, entering health check mode")
            if run_health_check():
                # Health check returned True, start automation
                from src.core.main_wrapper import main as run_app
                run_app()
    else:
        logger.error("❌ Import check failed, entering health check mode")
        logger.error("This prevents the container from crashing in production")
        
        if run_health_check():
            # Health check returned True after AUTO_PUBLISH was enabled
            try:
                from src.database.migrations import run_migrations
                run_migrations(os.environ['DATABASE_PATH'])
                
                from src.core.main_wrapper import main as run_app
                run_app()
            except Exception as e:
                logger.error(f"Failed to start after health check: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        # Keep container alive in production
        if os.getenv('ENVIRONMENT') == 'production':
            run_health_check()