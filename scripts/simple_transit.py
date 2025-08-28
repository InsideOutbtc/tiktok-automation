#!/usr/bin/env python3
"""
simple_transit.py - Downloads videos and uploads to DO
Run this once per day on your Mac
"""

import os
import requests
import yt_dlp
from pathlib import Path

# Configuration - CHANGE THIS TO YOUR DO URL
DO_URL = 'https://powerpro-automation-f2k4p.ondigitalocean.app'

def download_and_upload(video_url, video_id):
    """Download one video and upload it"""
    
    # Download to temp file
    temp_file = f'/tmp/video_{video_id}.mp4'
    
    print(f"Downloading {video_url}...")
    
    ydl_opts = {
        'outtmpl': temp_file,
        'format': 'best[height<=720]',
        'quiet': True,
        'cookiefile': 'cookies.txt'  # Use cookies for authentication
    }
    
    try:
        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        if not os.path.exists(temp_file):
            print("Download failed")
            return False
            
        print(f"Downloaded! Size: {os.path.getsize(temp_file) / 1024 / 1024:.1f}MB")
        
        # Upload
        print("Uploading to DO...")
        with open(temp_file, 'rb') as f:
            response = requests.post(
                f'{DO_URL}/api/upload',
                files={'video': f}
            )
        
        if response.status_code == 200:
            print("Upload successful!")
        else:
            print(f"Upload failed: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Always delete
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print("Deleted local file")
    
    return True

def main():
    """Main process"""
    print("=" * 50)
    print("SIMPLE VIDEO TRANSIT")
    print("=" * 50)
    
    # Get queue from DO
    try:
        response = requests.get(f'{DO_URL}/api/queue')
        videos = response.json()
    except:
        print("Couldn't get queue from DO. Using local list.")
        # Fallback list
        videos = [
            {'id': 1, 'url': 'https://www.youtube.com/@sam_sulek/videos'},
            {'id': 2, 'url': 'https://www.youtube.com/@thetrentwins/videos'},
        ]
    
    # Process each video
    for video in videos[:5]:  # Limit to 5 for testing
        print(f"\nProcessing video {video['id']}...")
        download_and_upload(video['url'], video['id'])
    
    print("\n✅ Done!")

if __name__ == '__main__':
    main()