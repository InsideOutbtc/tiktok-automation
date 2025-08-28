#!/usr/bin/env python3
"""
Mac Transit Downloader - Zero Storage Implementation
Constitutional AI Maximum Velocity Mode with Tier 1-4 Error Handling
Downloads one video at a time, uploads immediately, deletes instantly
"""

import yt_dlp
import requests
import time
import os
import tempfile
from pathlib import Path
from datetime import datetime
import logging
import json
import sys

# Configuration - follows QUALITY_METRICS.md standards
DO_URL = os.environ.get('DO_URL', "https://tiktok-automation-xqbnb.ondigitalocean.app")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB max per video
TEMP_DIR = Path(tempfile.gettempdir()) / "tiktok_transit"
TEMP_DIR.mkdir(exist_ok=True)

class ZeroStorageTransit:
    """Downloads and uploads one video at a time with immediate deletion"""
    
    def __init__(self):
        self.do_url = DO_URL
        self.temp_dir = TEMP_DIR
        self.session = requests.Session()
        
        # Performance metrics per QUALITY_METRICS.md
        self.metrics = {
            'downloads_success': 0,
            'downloads_failed': 0,
            'uploads_success': 0,
            'uploads_failed': 0,
            'total_transit_mb': 0,
            'avg_transit_time': 0,
            'error_tiers': {1: 0, 2: 0, 3: 0, 4: 0}
        }
        
        # Configure logging per constitutional-ai standards
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def download_single_video(self, video_data):
        """Download one video with immediate upload intent"""
        video_id = video_data['id']
        url = video_data['url']
        
        # Use system temp to ensure we don't fill user directory
        temp_path = self.temp_dir / f"{video_id}_temp.mp4"
        
        ydl_opts = {
            'outtmpl': str(temp_path),
            'format': 'best[filesize<100M]/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            # No cookies needed on residential IP
        }
        
        start_time = time.time()
        
        try:
            # Tier 1: Single retry on download failure
            for attempt in range(2):
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        
                        if temp_path.exists():
                            file_size_mb = temp_path.stat().st_size / (1024*1024)
                            self.logger.info(f"✅ Downloaded {video_id} ({file_size_mb:.1f}MB)")
                            self.metrics['downloads_success'] += 1
                            self.metrics['total_transit_mb'] += file_size_mb
                            
                            # IMMEDIATE UPLOAD - no storage
                            upload_success = self.upload_and_delete(temp_path, video_id)
                            
                            elapsed = time.time() - start_time
                            self.update_avg_time(elapsed)
                            
                            return upload_success
                            
                except Exception as e:
                    if attempt == 0:
                        self.logger.warning(f"Tier 1 retry for {video_id}")
                        self.metrics['error_tiers'][1] += 1
                        time.sleep(2)
                    else:
                        raise
                        
        except Exception as e:
            self.metrics['downloads_failed'] += 1
            self.logger.error(f"Download failed for {video_id}: {str(e)[:100]}")
            
            # Ensure cleanup even on failure
            if temp_path.exists():
                temp_path.unlink()
                
            return False
    
    def upload_and_delete(self, file_path, video_id):
        """Upload to DO and DELETE IMMEDIATELY - zero storage"""
        try:
            file_size = file_path.stat().st_size
            
            # Tier 2: Multiple upload attempts with exponential backoff
            for attempt in range(3):
                try:
                    with open(file_path, 'rb') as f:
                        response = self.session.post(
                            f"{self.do_url}/api/video/upload",
                            files={'video': f},
                            data={'video_id': video_id},
                            timeout=120  # 2 min timeout
                        )
                    
                    if response.status_code == 200:
                        self.metrics['uploads_success'] += 1
                        self.logger.info(f"☁️ Uploaded {video_id} to DigitalOcean")
                        
                        # DELETE IMMEDIATELY - Constitutional AI Maximum Velocity
                        file_path.unlink()
                        self.logger.info(f"🗑️ Deleted local file (saved {file_size/(1024*1024):.1f}MB)")
                        
                        return True
                    else:
                        raise Exception(f"Upload failed: {response.status_code}")
                        
                except Exception as e:
                    if attempt < 2:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Tier 2: Upload retry {attempt+1}, waiting {wait_time}s")
                        self.metrics['error_tiers'][2] += 1
                        time.sleep(wait_time)
                    else:
                        raise
                        
        except Exception as e:
            self.metrics['uploads_failed'] += 1
            self.logger.error(f"Upload failed after retries: {str(e)[:100]}")
            
        finally:
            # Tier 3: ALWAYS delete local file, even on upload failure
            if file_path.exists():
                file_path.unlink()
                self.logger.info("🗑️ Cleaned up local file (upload failed)")
                self.metrics['error_tiers'][3] += 1
                
        return False
    
    def update_avg_time(self, elapsed):
        """Update average transit time metric"""
        current_total = self.metrics['downloads_success'] + self.metrics['uploads_success']
        if current_total > 0:
            self.metrics['avg_transit_time'] = (
                (self.metrics['avg_transit_time'] * (current_total - 1) + elapsed) / current_total
            )
    
    def cleanup_temp_dir(self):
        """Tier 3: Emergency cleanup if any files somehow remain"""
        for file in self.temp_dir.glob("*.mp4"):
            try:
                age_minutes = (time.time() - file.stat().st_mtime) / 60
                if age_minutes > 10:  # Older than 10 minutes = stuck
                    file.unlink()
                    self.logger.warning(f"Tier 3: Cleaned up stuck file {file.name}")
                    self.metrics['error_tiers'][3] += 1
            except:
                pass
    
    def process_batch(self):
        """Process daily batch with zero storage accumulation"""
        self.logger.info("🚀 Starting Zero-Storage Transit Processor")
        self.logger.info(f"Target: 20 videos → DigitalOcean → 5-10 TikTok posts\n")
        
        # Clean any stuck files from previous runs
        self.cleanup_temp_dir()
        
        try:
            # Get pending videos from DigitalOcean
            response = self.session.get(f"{self.do_url}/api/queue/pending")
            
            if response.status_code != 200:
                self.logger.error(f"Failed to get queue: {response.status_code}")
                return
                
            queue_data = response.json()
            videos = queue_data.get('videos', [])
            
            if not videos:
                self.logger.info("📭 Queue empty. Run seed endpoint on DigitalOcean first.")
                return
                
            self.logger.info(f"📥 Processing {len(videos)} videos through transit pipeline\n")
            
            # Process ONE AT A TIME - never accumulate
            for video in videos:
                self.logger.info(f"Processing {video['creator']}: {video['url']}")
                
                # Download, upload, delete - atomic operation
                success = self.download_single_video(video)
                
                if success:
                    self.logger.info(f"✅ Complete transit for video {video['id']}\n")
                else:
                    self.logger.warning(f"⚠️ Failed transit for video {video['id']}\n")
                
                # Brief pause between videos (rate limiting)
                time.sleep(2)
                
                # Show stats every 5 videos
                if (self.metrics['downloads_success'] % 5) == 0:
                    self.show_statistics()
                    
        except Exception as e:
            # Tier 4: Complete failure
            self.logger.error(f"Tier 4 error: {e}")
            self.metrics['error_tiers'][4] += 1
            self.generate_recovery_plan()
            
        finally:
            # Final cleanup check
            self.cleanup_temp_dir()
            self.show_statistics()
            self.save_metrics()
    
    def show_statistics(self):
        """Display performance metrics per QUALITY_METRICS.md"""
        total_processed = self.metrics['downloads_success']
        success_rate = (self.metrics['uploads_success'] / max(total_processed, 1)) * 100
        
        self.logger.info(f"""
        📊 TRANSIT STATISTICS:
        ========================
        Downloads: {self.metrics['downloads_success']} ✅ / {self.metrics['downloads_failed']} ❌
        Uploads: {self.metrics['uploads_success']} ✅ / {self.metrics['uploads_failed']} ❌
        Success Rate: {success_rate:.1f}%
        Total Transit: {self.metrics['total_transit_mb']:.1f}MB
        Avg Transit Time: {self.metrics['avg_transit_time']:.1f}s
        Error Distribution: T1={self.metrics['error_tiers'][1]}, T2={self.metrics['error_tiers'][2]}, T3={self.metrics['error_tiers'][3]}, T4={self.metrics['error_tiers'][4]}
        Current Disk Usage: {self.check_disk_usage():.1f}MB (should be ~0)
        """)
    
    def check_disk_usage(self):
        """Verify zero storage is maintained"""
        total = sum(f.stat().st_size for f in self.temp_dir.glob("*.mp4"))
        return total / (1024*1024)
    
    def save_metrics(self):
        """Save metrics for monitoring per Constitutional AI standards"""
        metrics_file = Path.home() / '.tiktok_transit_metrics.json'
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def generate_recovery_plan(self):
        """Tier 4 recovery plan per ERROR_HANDLING_TIERS.md"""
        plan = {
            'timestamp': datetime.now().isoformat(),
            'failures': {
                'downloads': self.metrics['downloads_failed'],
                'uploads': self.metrics['uploads_failed']
            },
            'recovery_steps': [
                "1. Check internet connection",
                "2. Verify DigitalOcean is running",
                "3. Check yt-dlp is updated",
                "4. Restart the script",
                "5. If persists, check DO logs"
            ]
        }
        
        recovery_file = Path.home() / '.tiktok_recovery_plan.json'
        with open(recovery_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        self.logger.error(f"Recovery plan saved to {recovery_file}")

# Maximum Velocity Execution
def main():
    """Execute with no confirmations per Constitutional AI"""
    processor = ZeroStorageTransit()
    
    # Check if already ran today (prevent duplicate runs)
    marker = Path.home() / '.tiktok_last_run'
    today = datetime.now().strftime('%Y-%m-%d')
    
    if marker.exists():
        last_run = marker.read_text().strip()
        if last_run == today and '--force' not in sys.argv:
            print("Already ran today. Use --force to override")
            return
    
    # Run the batch
    processor.process_batch()
    
    # Mark as complete
    marker.write_text(today)
    
    print("\n✅ Transit processing complete!")
    print("Check DigitalOcean for processed clips")

if __name__ == "__main__":
    main()