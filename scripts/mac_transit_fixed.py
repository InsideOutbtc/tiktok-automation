#!/usr/bin/env python3
"""
mac_transit_fixed.py - Reliable video transit with error handling
"""

import os
import sys
import json
import time
import requests
import yt_dlp
from pathlib import Path
from datetime import datetime

# Configuration
DO_URL = 'https://tiktok-automation-xqbnb.ondigitalocean.app'
MAX_VIDEOS_PER_RUN = 10
LOG_FILE = Path.home() / '.video_transit.log'

class VideoTransit:
    def __init__(self):
        self.do_url = DO_URL
        self.session = requests.Session()
        self.results = {
            'success': [],
            'failed': [],
            'start_time': datetime.now().isoformat()
        }
    
    def log(self, message):
        """Log to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + '\n')
    
    def download_and_upload(self, video):
        """Download one video and upload it"""
        video_id = video['id']
        video_url = video['url']
        creator = video.get('creator', 'unknown')
        
        # Use /tmp for automatic cleanup
        temp_file = Path(f'/tmp/transit_{video_id}.mp4')
        
        try:
            self.log(f"Downloading {creator} video {video_id}...")
            
            ydl_opts = {
                'outtmpl': str(temp_file),
                'format': 'best[height<=720]/best',
                'quiet': True,
                'no_warnings': True,
                # Don't download if over 200MB
                'max_filesize': 200 * 1024 * 1024,
                'cookiefile': 'cookies.txt'  # Use cookies if available
            }
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                actual_title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
            
            if not temp_file.exists():
                raise Exception("Download completed but file not found")
            
            file_size_mb = temp_file.stat().st_size / (1024 * 1024)
            self.log(f"Downloaded '{actual_title}' ({file_size_mb:.1f}MB, {duration}s)")
            
            # Upload
            self.log("Uploading to DO...")
            with open(temp_file, 'rb') as f:
                response = self.session.post(
                    f'{self.do_url}/api/upload',
                    files={'video': (f'{video_id}.mp4', f, 'video/mp4')},
                    data={'video_id': video_id},
                    timeout=120  # 2 minute timeout
                )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"Upload successful! Stored as {result.get('filename')}")
                self.results['success'].append(video_id)
                return True
            else:
                raise Exception(f"Upload failed with status {response.status_code}")
                
        except yt_dlp.utils.DownloadError as e:
            if 'File is larger than max' in str(e):
                self.log(f"Video too large, skipping")
            else:
                self.log(f"Download failed: {str(e)[:100]}")
            self.results['failed'].append(video_id)
            return False
            
        except Exception as e:
            self.log(f"Error: {str(e)[:200]}")
            self.results['failed'].append(video_id)
            return False
            
        finally:
            # ALWAYS delete the temp file
            if temp_file.exists():
                temp_file.unlink()
                self.log("Deleted temp file")
    
    def run(self):
        """Main process"""
        self.log("=" * 50)
        self.log("VIDEO TRANSIT STARTING")
        self.log("=" * 50)
        
        # Check DO is accessible
        try:
            response = self.session.get(f'{self.do_url}/api/queue', timeout=5)
            if response.status_code != 200:
                self.log(f"DO server returned {response.status_code}")
                return
            videos = response.json()
        except Exception as e:
            self.log(f"Cannot reach DO server: {e}")
            return
        
        if not videos:
            self.log("Queue is empty - all videos already downloaded!")
            return
        
        self.log(f"Found {len(videos)} videos in queue")
        
        # Process videos (limit to prevent long runs)
        for i, video in enumerate(videos[:MAX_VIDEOS_PER_RUN], 1):
            self.log(f"\n[{i}/{min(len(videos), MAX_VIDEOS_PER_RUN)}] Processing {video.get('title', video['id'])}")
            self.download_and_upload(video)
            
            # Brief pause between downloads
            if i < len(videos):
                time.sleep(3)
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log(f"COMPLETE: {len(self.results['success'])} success, {len(self.results['failed'])} failed")
        
        # Save results
        results_file = Path.home() / '.video_transit_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

if __name__ == '__main__':
    # Check if already running (prevent multiple instances)
    pid_file = Path.home() / '.video_transit.pid'
    
    if pid_file.exists():
        old_pid = pid_file.read_text().strip()
        # Check if process is actually running
        try:
            os.kill(int(old_pid), 0)
            print("Transit already running")
            sys.exit(0)
        except OSError:
            # Process not running, remove stale PID file
            pid_file.unlink()
    
    # Write PID
    pid_file.write_text(str(os.getpid()))
    
    try:
        transit = VideoTransit()
        transit.run()
    finally:
        # Clean up PID file
        pid_file.unlink()