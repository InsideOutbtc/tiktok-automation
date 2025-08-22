#!/usr/bin/env python3
"""Test script for the fixed error handler."""

import asyncio
import sys
sys.path.insert(0, '/Users/Patrick/Fitness TikTok')

from src.core.error_handler_fixed import ErrorHandler, ErrorTier

async def test_operation():
    """Test operation that might fail."""
    raise Exception("Test error")

async def main():
    """Test the fixed error handler."""
    handler = ErrorHandler()
    
    print("Testing Error Handler Fixes...")
    print("=" * 50)
    
    # Test 1: Verify error_stats initialization
    print("\n1. Testing error_stats initialization:")
    print(f"Initial stats: {handler.get_stats()}")
    assert 'system' in handler.error_stats, "Missing 'system' key in error_stats!"
    print("✅ All required keys present in error_stats")
    
    # Test 2: Test different error types
    test_errors = [
        ("timeout error", ErrorTier.TIER_1),
        ("permission denied", ErrorTier.TIER_2),
        ("file not found", ErrorTier.TIER_3),
        ("critical failure", ErrorTier.TIER_4),
    ]
    
    print("\n2. Testing error classification:")
    for error_msg, expected_tier in test_errors:
        error = Exception(error_msg)
        tier = handler.classify_error(error)
        print(f"  '{error_msg}' -> {tier.name} (expected: {expected_tier.name})")
        assert tier == expected_tier, f"Misclassified: {error_msg}"
    print("✅ All errors classified correctly")
    
    # Test 3: Test error handling without KeyError
    print("\n3. Testing error handling (no KeyError):")
    for error_msg, _ in test_errors:
        try:
            error = Exception(error_msg)
            result = await handler.handle(error, {'operation': test_operation})
            print(f"  Handled '{error_msg}' successfully")
        except KeyError as e:
            print(f"❌ KeyError occurred: {e}")
            raise
    print("✅ No KeyError exceptions during handling")
    
    # Test 4: Verify stats are updated
    print("\n4. Testing stats updates:")
    final_stats = handler.get_stats()
    print(f"Final stats: {final_stats}")
    
    # Check that some stats were incremented
    total_errors = sum(v for k, v in final_stats.items() if isinstance(v, int))
    assert total_errors > 0, "No errors were counted!"
    print(f"✅ Total errors counted: {total_errors}")
    
    print("\n" + "=" * 50)
    print("All tests passed! The error handler is working correctly.")

if __name__ == "__main__":
    asyncio.run(main())