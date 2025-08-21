#!/usr/bin/env python3
# Comprehensive test runner
# Executes all tests in proper sequence

import os
import sys
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Orchestrates all system tests"""
    
    def __init__(self):
        self.results = {
            "start_time": datetime.now(),
            "tests": {},
            "overall_status": "pending"
        }
        self.test_sequence = [
            ("Pre-test Setup", "scripts/pre_test_setup.py"),
            ("API Connectivity", "scripts/test_apis.py"),
            ("System Validation", "scripts/system_test.py"),
            ("Test Mode Run", "scripts/test_mode.py")
        ]
        
    def print_header(self):
        """Print test header"""
        print("🧪 TIKTOK AI AUTOMATION - COMPREHENSIVE TESTING")
        print("=" * 60)
        print(f"Start Time: {self.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print("\nThis will run all tests in sequence:")
        for i, (name, _) in enumerate(self.test_sequence, 1):
            print(f"  {i}. {name}")
        print("\n⚠️  IMPORTANT: No actual posts will be made to TikTok")
        print("=" * 60)
        
    def run_test(self, name, script_path):
        """Run a single test"""
        print(f"\n\n{'='*60}")
        print(f"🔄 Running: {name}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Check result
            if result.returncode == 0:
                status = "PASSED"
                print(f"\n✅ {name}: PASSED ({duration:.1f}s)")
            else:
                status = "FAILED"
                print(f"\n❌ {name}: FAILED ({duration:.1f}s)")
                print("\nError output:")
                print(result.stderr[-500:])  # Last 500 chars of error
                
            self.results["tests"][name] = {
                "status": status,
                "duration": duration,
                "returncode": result.returncode
            }
            
            # Show output
            if result.stdout:
                print("\nTest output:")
                print("-" * 60)
                print(result.stdout)
                
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"\n⏱️ {name}: TIMEOUT (exceeded 10 minutes)")
            self.results["tests"][name] = {
                "status": "TIMEOUT",
                "duration": 600
            }
            return False
            
        except Exception as e:
            print(f"\n❌ {name}: ERROR - {e}")
            self.results["tests"][name] = {
                "status": "ERROR",
                "error": str(e)
            }
            return False
            
    def check_critical_files(self):
        """Check if critical files were created"""
        print("\n📁 Checking Test Outputs...")
        
        checks = {
            "Test Report": "logs/test_report.json",
            "Downloaded Videos": "input/downloads",
            "Generated Clips": "processing/clips"
        }
        
        for name, path in checks.items():
            if os.path.exists(path):
                if os.path.isdir(path):
                    count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                    if count > 0:
                        print(f"  ✅ {name}: {count} files")
                    else:
                        print(f"  ⚠️ {name}: Empty directory")
                else:
                    print(f"  ✅ {name}: Created")
            else:
                print(f"  ❌ {name}: Not found")
                
    def generate_summary(self):
        """Generate test summary"""
        duration = (datetime.now() - self.results["start_time"]).total_seconds()
        
        print("\n\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"\nTotal Duration: {duration/60:.1f} minutes")
        
        # Count results
        passed = sum(1 for t in self.results["tests"].values() if t["status"] == "PASSED")
        failed = sum(1 for t in self.results["tests"].values() if t["status"] == "FAILED")
        total = len(self.results["tests"])
        
        print(f"\nTests Run: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        
        # Individual results
        print("\nDetailed Results:")
        for name, result in self.results["tests"].items():
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            duration_str = f"{result.get('duration', 0):.1f}s" if 'duration' in result else "N/A"
            print(f"  {status_icon} {name}: {result['status']} ({duration_str})")
            
        # Overall verdict
        if passed == total:
            self.results["overall_status"] = "SUCCESS"
            print("\n🎉 ALL TESTS PASSED!")
            print("\n✅ SYSTEM READY FOR PRODUCTION")
            print("\nNext Steps:")
            print("1. Review downloaded videos in input/downloads/")
            print("2. Check generated clips in processing/clips/")
            print("3. Review logs/test_report.json for details")
            print("4. When ready, set AUTO_PUBLISH=true in .env")
        elif passed > 0:
            self.results["overall_status"] = "PARTIAL"
            print("\n⚠️ SOME TESTS FAILED")
            print("\nRecommended Actions:")
            print("1. Check failed test outputs above")
            print("2. Review error logs")
            print("3. Fix issues and re-run failed tests")
        else:
            self.results["overall_status"] = "FAILED"
            print("\n❌ ALL TESTS FAILED")
            print("\nTroubleshooting:")
            print("1. Check .env file has valid API keys")
            print("2. Ensure all dependencies installed")
            print("3. Review error messages above")
            
        # Save summary
        import json
        summary_path = f"logs/test_summary_{self.results['start_time'].strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        with open(summary_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
            
        print(f"\n📄 Summary saved to: {summary_path}")
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header()
        
        # Ask for confirmation
        response = input("\nProceed with testing? (y/N): ").lower()
        if response != 'y':
            print("\n❌ Testing cancelled")
            return
            
        # Run each test
        for name, script in self.test_sequence:
            success = self.run_test(name, script)
            
            # Stop on critical failures
            if name == "Pre-test Setup" and not success:
                print("\n❌ Pre-test setup failed - cannot continue")
                break
                
            # Optional: pause between tests
            if success and name != self.test_sequence[-1][0]:
                print("\n⏸️ Pausing before next test...")
                import time
                time.sleep(3)
                
        # Check outputs
        self.check_critical_files()
        
        # Generate summary
        self.generate_summary()
        
        # Cleanup prompt
        print("\n" + "="*60)
        response = input("\nRun cleanup to remove test files? (y/N): ").lower()
        if response == 'y':
            self.cleanup_test_files()
            
    def cleanup_test_files(self):
        """Clean up test files"""
        print("\n🧹 Cleaning up test files...")
        
        import shutil
        
        cleanup_dirs = [
            "input/downloads",
            "processing/clips",
            "processing/temp",
            "processing/edited"
        ]
        
        for dir_path in cleanup_dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path)
                    print(f"  ✅ Cleaned: {dir_path}")
                except Exception as e:
                    print(f"  ❌ Failed to clean {dir_path}: {e}")
                    
        print("\n✅ Cleanup complete")


def main():
    """Run all tests"""
    runner = TestRunner()
    
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n👋 Testing complete!")


if __name__ == "__main__":
    # Make all scripts executable
    script_dir = Path(__file__).parent
    for script in script_dir.glob("*.py"):
        os.chmod(script, 0o755)
        
    main()