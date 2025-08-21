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

def setup_directories():
    """Create all required directories"""
    dirs = ['input', 'output', 'processing', 'posted', 'logs', 'database', 'assets/watermarks', 'assets/logos']
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    logger.info("✅ All directories created")

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

def health_check_loop():
    """Keep container alive for DigitalOcean health checks"""
    logger.info("🏥 Running in health check mode (container staying alive)")
    logger.info("📝 To start processing: Create /tmp/start_processing file")
    
    while True:
        # Log health status
        logger.info(f"💚 Health: OK | Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for manual start trigger
        if os.path.exists('/tmp/start_processing'):
            logger.info("🚀 Manual start triggered!")
            return True
            
        # Check if AUTO_PUBLISH is true (ready for production)
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
        
        # Check configuration
        env_ready = check_environment()
        
        # In production, always start with health check mode
        if os.getenv('ENVIRONMENT') == 'production':
            if not env_ready:
                logger.info("⏸️ Missing configuration - staying in health check mode")
                health_check_loop()
                # If we get here, manual start was triggered
            
            # Only proceed if AUTO_PUBLISH is true or manual trigger
            if os.getenv('AUTO_PUBLISH', 'false').lower() != 'true':
                logger.info("⏸️ AUTO_PUBLISH=false - staying in health check mode")
                if not health_check_loop():
                    return
        
        # Try to import and run main controller
        logger.info("🤖 Starting main automation system...")
        try:
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