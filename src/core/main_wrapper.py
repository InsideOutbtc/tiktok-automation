"""
Simple wrapper to run the async main controller
"""
import asyncio
import os
import sys

# Ensure database path is set
if not os.getenv('DATABASE_PATH'):
    os.environ['DATABASE_PATH'] = os.path.abspath('database/tiktok.db')

from src.core.main_controller import main as async_main

def main():
    """Synchronous wrapper for async main"""
    # Log database path
    print(f"Main: Using database at {os.getenv('DATABASE_PATH')}")
    asyncio.run(async_main())

if __name__ == "__main__":
    main()