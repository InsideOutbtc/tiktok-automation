"""
Simple wrapper to run the async main controller
"""
import asyncio
from src.core.main_controller import main as async_main

def main():
    """Synchronous wrapper for async main"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()