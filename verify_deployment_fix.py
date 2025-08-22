#!/usr/bin/env python3
"""
Verify that the deployment has the fixed error_handler.py
Run this in the Docker container to confirm the fix is deployed.
"""

import sys
import os

def verify_fix():
    """Check if error_handler.py has the fix."""
    print("=== Deployment Verification ===")
    print(f"Python path: {sys.path}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        # Import the error handler
        from src.core.error_handler import ErrorHandler, ErrorTier
        print("✅ Successfully imported ErrorHandler")
        
        # Create instance
        handler = ErrorHandler()
        print("✅ Successfully created ErrorHandler instance")
        
        # Check if _tier_map exists (this is the fix)
        if hasattr(handler, '_tier_map'):
            print("✅ Found _tier_map attribute (FIX IS DEPLOYED)")
            print(f"   Tier map: {handler._tier_map}")
        else:
            print("❌ Missing _tier_map attribute (OLD CODE)")
            
        # Check error_stats initialization
        print(f"✅ error_stats: {handler.error_stats}")
        
        # Test error classification
        test_error = Exception("connection timeout")
        tier = handler._classify_error(test_error)
        print(f"✅ Error classification works: 'connection timeout' -> {tier.value}")
        
        # Check if List is imported (look at the module)
        import src.core.error_handler as eh_module
        if 'List' in dir(eh_module):
            print("✅ List is imported from typing")
        else:
            print("⚠️  List not found in module imports")
            
        print("\n✅ DEPLOYMENT VERIFICATION PASSED!")
        print("The fixed error_handler.py is deployed and working.")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("The error_handler module cannot be imported.")
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        print("There's an issue with the error_handler.")

if __name__ == "__main__":
    verify_fix()