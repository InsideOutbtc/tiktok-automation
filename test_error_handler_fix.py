#!/usr/bin/env python3
"""Test the error handler fix for KeyError issue"""

import sys
import asyncio
sys.path.insert(0, '/Users/Patrick/Fitness TikTok')

from src.core.error_handler import ErrorHandler, ErrorTier


async def test_error_handler():
    """Test error handler with all tier types"""
    handler = ErrorHandler()
    
    # Test each tier type
    errors = [
        (ErrorTier.TIER1, "Connection timeout error"),
        (ErrorTier.TIER2, "Invalid format error"), 
        (ErrorTier.TIER3, "System resource error"),
        (ErrorTier.TIER4, "Critical security error")
    ]
    
    print("Testing error handler fix...")
    print(f"Initial error_stats: {handler.error_stats}")
    print(f"Tier mapping: {handler._tier_map}")
    
    for tier, error_msg in errors:
        print(f"\nTesting {tier.name} (value: {tier.value})...")
        try:
            result = await handler.handle(
                Exception(error_msg),
                {"operation": lambda: "test"},
                tier=tier
            )
            print(f"✓ Success - Stats: {handler.error_stats}")
        except KeyError as e:
            print(f"✗ KeyError: {e}")
        except Exception as e:
            print(f"✗ Other error: {type(e).__name__}: {e}")
    
    print(f"\nFinal error_stats: {handler.error_stats}")
    print(f"Final recovered: {handler.recovered}")
    print(f"Recovery rate: {handler.get_recovery_rate():.2%}")


if __name__ == "__main__":
    asyncio.run(test_error_handler())