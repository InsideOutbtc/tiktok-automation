#!/usr/bin/env python3
"""Safe startup wrapper with fallback to dashboard"""
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, '/app')
os.environ['PYTHONPATH'] = '/app'

def run_dashboard_fallback():
    """Fallback to just run the dashboard"""
    logger.info("Running dashboard in fallback mode...")
    os.system("python /app/src/api/simple_dashboard.py")

def main():
    """Main entry with error handling"""
    try:
        logger.info("Starting TikTok Automation System...")
        from src.core.main_controller import main as controller_main
        import asyncio
        
        # Get command from args or default to 'start'
        command = sys.argv[1] if len(sys.argv) > 1 else 'start'
        
        # Run the main controller
        asyncio.run(controller_main())
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("Falling back to dashboard only mode...")
        run_dashboard_fallback()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        logger.info("Falling back to dashboard only mode...")
        run_dashboard_fallback()

if __name__ == '__main__':
    main()