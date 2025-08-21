#!/usr/bin/env python3
# Run system in test mode (no actual posting)
# Safe testing with real video processing

import asyncio
import os
import sys
from pathlib import Path
import signal
import json
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from src.core.main_controller import MainController


class TestModeController:
    """Run system in test mode with safety checks"""
    
    def __init__(self):
        # Override environment for safety
        os.environ["AUTO_PUBLISH"] = "false"
        os.environ["TEST_MODE"] = "true"
        os.environ["MAX_VIDEOS_PER_RUN"] = "3"
        
        self.controller = MainController()
        self.start_time = datetime.now()
        self.test_duration = 300  # 5 minutes
        self.stats = {
            "videos_discovered": 0,
            "videos_downloaded": 0,
            "clips_generated": 0,
            "ai_analyses": 0,
            "would_have_posted": 0,
            "errors": 0
        }
        
    async def initialize(self):
        """Initialize system in test mode"""
        print("🧪 INITIALIZING TEST MODE")
        print("=" * 50)
        print("⚠️  SAFETY CHECKS:")
        print("  ✅ Auto Publishing: DISABLED")
        print("  ✅ Test Mode: ENABLED")
        print("  ✅ Max Videos: 3")
        print("  ✅ Duration: 5 minutes")
        print("=" * 50)
        
        # Initialize controller
        await self.controller.initialize()
        
        # Override publishing method to track instead of post
        self.controller._publish_clip = self._mock_publish_clip
        
        print("\n✅ System initialized in TEST MODE")
        
    async def _mock_publish_clip(self, clip):
        """Mock publishing - just track what would be posted"""
        self.stats["would_have_posted"] += 1
        print(f"\n📤 MOCK POST: {clip.get('title', 'Untitled')[:50]}...")
        print(f"   Platform: {clip.get('platform', 'unknown')}")
        print(f"   Score: {clip.get('viral_score', 0):.2f}")
        
        # Save to test log
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": clip.get("title"),
            "platform": clip.get("platform"),
            "score": clip.get("viral_score"),
            "hashtags": clip.get("hashtags", [])
        }
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/test_posts.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    async def run_test(self):
        """Run the test with time limit"""
        print(f"\n🚀 Starting {self.test_duration}s test run...")
        print("Press Ctrl+C to stop early\n")
        
        # Set up graceful shutdown
        def signal_handler(sig, frame):
            print("\n\n⏹️ Stopping test...")
            self.controller.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Create test timer
        async def test_timer():
            await asyncio.sleep(self.test_duration)
            print(f"\n\n⏰ Test duration ({self.test_duration}s) reached")
            self.controller.running = False
            
        # Track stats during run
        original_discover = self.controller._content_discovery_loop
        original_process = self.controller._video_processing_loop
        
        async def tracked_discovery():
            """Track discovery stats"""
            async def count_discoveries():
                while self.controller.running:
                    current = self.controller.metrics.get("api_calls", 0)
                    if current > self.stats["videos_discovered"]:
                        self.stats["videos_discovered"] = current
                    await asyncio.sleep(1)
            
            await asyncio.gather(
                original_discover(),
                count_discoveries()
            )
            
        async def tracked_processing():
            """Track processing stats"""
            async def count_processing():
                while self.controller.running:
                    self.stats["videos_downloaded"] = self.controller.metrics.get("videos_processed", 0)
                    self.stats["clips_generated"] = self.controller.metrics.get("clips_generated", 0)
                    await asyncio.sleep(1)
            
            await asyncio.gather(
                original_process(),
                count_processing()
            )
        
        # Replace methods
        self.controller._content_discovery_loop = tracked_discovery
        self.controller._video_processing_loop = tracked_processing
        
        # Run system with timer
        try:
            await asyncio.gather(
                self.controller.start("full"),
                test_timer(),
                return_exceptions=True
            )
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            self.stats["errors"] += 1
            
    def generate_report(self):
        """Generate test report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 50)
        print("📊 TEST MODE REPORT")
        print("=" * 50)
        print(f"\n⏱️ Test Duration: {duration:.1f} seconds")
        print("\n📈 Processing Stats:")
        print(f"  Videos Discovered: {self.stats['videos_discovered']}")
        print(f"  Videos Downloaded: {self.stats['videos_downloaded']}")
        print(f"  Clips Generated: {self.stats['clips_generated']}")
        print(f"  Would Have Posted: {self.stats['would_have_posted']}")
        print(f"  Errors: {self.stats['errors']}")
        
        # Check for downloaded files
        download_dir = "input/downloads"
        if os.path.exists(download_dir):
            downloads = [f for f in os.listdir(download_dir) if f.endswith('.mp4')]
            print(f"\n📁 Downloaded Files: {len(downloads)}")
            for f in downloads[:5]:
                size = os.path.getsize(os.path.join(download_dir, f)) / (1024 * 1024)
                print(f"    - {f} ({size:.2f} MB)")
                
        # Check for clips
        clips_dir = "processing/clips"
        if os.path.exists(clips_dir):
            clips = [f for f in os.listdir(clips_dir) if f.endswith('.mp4')]
            print(f"\n✂️ Generated Clips: {len(clips)}")
            for f in clips[:5]:
                print(f"    - {f}")
                
        # Performance
        if self.stats['videos_downloaded'] > 0:
            avg_time = duration / self.stats['videos_downloaded']
            print(f"\n⚡ Performance:")
            print(f"  Avg time per video: {avg_time:.1f}s")
            
        # Save full report
        report = {
            "test_date": self.start_time.isoformat(),
            "duration_seconds": duration,
            "stats": self.stats,
            "controller_metrics": self.controller.metrics
        }
        
        report_path = f"logs/test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("logs", exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Full report saved to: {report_path}")
        
        # Verdict
        if self.stats['errors'] == 0 and self.stats['clips_generated'] > 0:
            print("\n✅ TEST PASSED - System working correctly!")
        elif self.stats['errors'] > 0:
            print("\n⚠️ TEST COMPLETED WITH ERRORS - Check logs")
        else:
            print("\n❌ TEST FAILED - No clips generated")
            
    async def cleanup(self):
        """Optional cleanup after test"""
        print("\n🧹 Test cleanup...")
        
        # Ask user if they want to clean up test files
        response = input("Delete test downloads and clips? (y/N): ").lower()
        
        if response == 'y':
            import shutil
            
            # Clean downloads
            if os.path.exists("input/downloads"):
                shutil.rmtree("input/downloads")
                os.makedirs("input/downloads")
                print("  ✅ Cleaned downloads")
                
            # Clean clips
            if os.path.exists("processing/clips"):
                shutil.rmtree("processing/clips")
                os.makedirs("processing/clips")
                print("  ✅ Cleaned clips")
                
            print("\n✅ Cleanup complete")
        else:
            print("\n⏭️ Skipping cleanup - files preserved")


async def main():
    """Run test mode"""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/test_mode.log"),
            logging.StreamHandler()
        ]
    )
    
    print("🧪 TIKTOK AI AUTOMATION - TEST MODE")
    print("=" * 50)
    
    controller = TestModeController()
    
    try:
        # Initialize
        await controller.initialize()
        
        # Run test
        await controller.run_test()
        
        # Generate report
        controller.generate_report()
        
        # Optional cleanup
        await controller.cleanup()
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n👋 Test mode complete!")


if __name__ == "__main__":
    asyncio.run(main())