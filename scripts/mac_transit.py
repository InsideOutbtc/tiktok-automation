#!/usr/bin/env python3
"""
mac_transit.py - Downloads discovered videos and uploads to DO
"""

import os
import sys
import json
import time
import requests
import yt_dlp
from pathlib import Path
from datetime import datetime

# CHANGE THIS TO YOUR ACTUAL DO URL
DO_URL = os.getenv('DO_URL', 'https://[YOUR-APP-NAME].ondigitalocean.app')
MAX_VIDEOS_PER_RUN = 10
LOG_FILE = Path.home() / '.video_transit.log'

# Cookie file path (if you have YouTube cookies)
COOKIE_FILE = Path.home() / 'cookies.txt'

class VideoTransit:
    def __init__(self):
        self.do_url = DO_URL
        self.session = requests.Session()
        self.results = {'success': [], 'failed': []}
        
    def log(self, message):
        """Simple logging"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        with open(LOG_FILE, 'a') as f:
            f.write(log_line + '\n')
    
    def download_and_upload(self, video):
        """Download video and immediately upload"""
        video_id = video['id']
        video_url = video['url']
        creator = video.get('creator', 'unknown')
        
        # Use /tmp for automatic cleanup
        temp_file = Path(f'/tmp/transit_{video_id}.mp4')
        
        try:
            self.log(f"Downloading: {creator} - {video.get('title', 'Unknown')}")
            
            # yt-dlp options
            ydl_opts = {
                'outtmpl': str(temp_file),
                'format': 'best[height<=720]/best',
                'quiet': True,
                'no_warnings': True,
                'max_filesize': 200 * 1024 * 1024  # 200MB max
            }
            
            # Add cookies if available
            if COOKIE_FILE.exists():
                ydl_opts['cookiefile'] = str(COOKIE_FILE)
                self.log("Using cookies for authentication")
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            if not temp_file.exists():
                raise Exception("Download failed - file not created")
            
            file_size_mb = temp_file.stat().st_size / (1024 * 1024)
            self.log(f"Downloaded {file_size_mb:.1f}MB")
            
            # Upload to DO
            self.log("Uploading to DO...")
            with open(temp_file, 'rb') as f:
                response = self.session.post(
                    f'{self.do_url}/api/upload',
                    files={'video': (f'{video_id}.mp4', f, 'video/mp4')},
                    data={'video_id': video_id},
                    timeout=120
                )
            
            if response.status_code == 200:
                self.log("Upload successful!")
                self.results['success'].append(video_id)
                return True
            else:
                raise Exception(f"Upload failed: {response.status_code}")
                
        except Exception as e:
            self.log(f"Error: {str(e)[:200]}")
            self.results['failed'].append(video_id)
            return False
            
        finally:
            # ALWAYS delete temp file
            if temp_file.exists():
                temp_file.unlink()
                self.log("Deleted temp file")
    
    def run(self):
        """Main process"""
        self.log("=" * 50)
        self.log("VIDEO TRANSIT STARTING")
        self.log(f"DO URL: {self.do_url}")
        self.log("=" * 50)
        
        # Get queue from DO
        try:
            response = self.session.get(f'{self.do_url}/api/queue', timeout=30)
            if response.status_code != 200:
                self.log(f"Failed to get queue: {response.status_code}")
                return
            videos = response.json()
        except Exception as e:
            self.log(f"Cannot reach DO server: {e}")
            self.log("Check your DO_URL environment variable")
            return
        
        if not videos:
            self.log("Queue empty - no new videos from creators")
            return
        
        self.log(f"Found {len(videos)} new videos")
        
        # Process videos
        for i, video in enumerate(videos[:MAX_VIDEOS_PER_RUN], 1):
            self.log(f"\n[{i}/{min(len(videos), MAX_VIDEOS_PER_RUN)}] {video['creator']}")
            self.download_and_upload(video)
            
            # Brief pause
            if i < len(videos):
                time.sleep(3)
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log(f"COMPLETE: {len(self.results['success'])} success, {len(self.results['failed'])} failed")

if __name__ == '__main__':
    if DO_URL.startswith('https://[YOUR-APP-NAME]'):
        print("ERROR: You need to set your actual DO URL!")
        print("Edit this script or set DO_URL environment variable")
        sys.exit(1)
    
    transit = VideoTransit()
    transit.run()