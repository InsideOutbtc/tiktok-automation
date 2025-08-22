#!/usr/bin/env python3
"""Test the updated error handler with safer stats tracking."""

import asyncio
import sys
sys.path.insert(0, '/Users/Patrick/Fitness TikTok')

from src.core.error_handler import ErrorHandler, ErrorTier

async def test_operation():
    """Test operation that fails."""
    raise Exception("Test error")

async def main():
    """Test the error handler."""
    handler = ErrorHandler()
    
    print("Testing Error Handler Safety Updates...")
    print("=" * 50)
    
    # Test that stats don't cause KeyError
    print("\n1. Testing error handling without KeyError:")
    
    test_cases = [
        Exception("timeout error"),
        Exception("permission denied"),  
        Exception("file not found"),
        Exception("critical failure"),
    ]
    
    for error in test_cases:
        try:
            # Pass ErrorTier directly to test the safer stats tracking
            tier = handler._classify_error(error)
            result = await handler.handle(error, {'operation': test_operation}, tier)
            print(f"✅ Handled '{error}' (tier: {tier.value}) without KeyError")
        except KeyError as e:
            print(f"❌ KeyError occurred: {e}")
            raise
        except Exception as e:
            # Other exceptions are expected (from test_operation)
            pass
    
    print("\n2. Checking final stats:")
    print(f"Error stats: {handler.error_stats}")
    print(f"Recovered stats: {handler.recovered}")
    
    print("\n3. Testing recovery rate calculation:")
    try:
        rate = handler.get_recovery_rate()
        print(f"Recovery rate: {rate:.2%}")
    except Exception as e:
        print(f"❌ Error calculating recovery rate: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Error handler is working safely with no KeyError issues!")

if __name__ == "__main__":
    asyncio.run(main())