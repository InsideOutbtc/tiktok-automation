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

def ensure_database():
    """Ensure database directory and file exist"""
    import os
    from pathlib import Path
    
    # Create database directory if it doesn't exist
    db_dir = '/app/database'
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    # Create database file if it doesn't exist
    db_file = os.path.join(db_dir, 'tiktok.db')
    if not os.path.exists(db_file):
        Path(db_file).touch()
        logger.info(f"Created database file at {db_file}")
    
    # Set environment variable
    os.environ['DATABASE_URL'] = f'sqlite:///{db_file}'
    return db_file

def run_dashboard_fallback():
    """Fallback to just run the dashboard"""
    logger.info("Running dashboard in fallback mode...")
    # Ensure output directory exists
    os.makedirs('/app/output', exist_ok=True)
    # Import and run Flask directly to ensure proper binding
    sys.path.insert(0, '/app/src/api')
    from simple_dashboard import app
    app.run(host='0.0.0.0', port=8000, debug=False)

def main():
    """Main entry with error handling"""
    try:
        # Ensure database exists
        ensure_database()
        
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