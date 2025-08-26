"""
Resilient YouTube Downloader with Multi-Strategy Fallbacks
Implements Constitutional AI Tier 1-4 error handling with automatic recovery
"""
import os
import json
import time
import random
from typing import Optional, Dict, Any, List
import yt_dlp
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ResilientYouTubeDownloader:
    """Multi-strategy YouTube downloader with automatic fallbacks"""
    
    def __init__(self):
        self.cookie_file = os.environ.get('YOUTUBE_COOKIE_FILE', '/app/config/youtube_cookies.txt')
        self.strategies_tried = []
        self.success_count = 0
        self.failure_count = 0
        self.output_dir = '/app/input'
        
    def download_video(self, url: str, video_id: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Download video using cascading fallback strategies
        Following Constitutional AI Tier 2 error handling - 3 retries with backoff
        """
        if output_dir:
            self.output_dir = output_dir
            
        # Reset strategies for this download
        self.strategies_tried = []
        
        strategies = [
            ('cookies', self._download_with_cookies),
            ('user_agent', self._download_with_user_agent),
            ('invidious', self._download_with_invidious),
            ('cobalt', self._download_with_cobalt),
            ('proxy', self._download_with_proxy),
        ]
        
        for strategy_name, strategy_func in strategies:
            self.strategies_tried.append(strategy_name)
            logger.info(f"Attempting download with strategy: {strategy_name}")
            
            # Tier 2 error handling - 3 retries with exponential backoff
            for attempt in range(3):
                try:
                    result = strategy_func(url, video_id)
                    if result and os.path.exists(result):
                        self.success_count += 1
                        logger.info(f"SUCCESS: Downloaded via {strategy_name}")
                        self._store_successful_pattern(strategy_name, url)
                        return result
                except Exception as e:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"{strategy_name} attempt {attempt+1} failed: {e}")
                    if attempt < 2:  # Don't sleep on last attempt
                        time.sleep(wait_time)
            
            # Add small delay between strategies to avoid rate limiting
            time.sleep(random.uniform(2, 4))
        
        # Tier 3 - Implement workaround
        self.failure_count += 1
        return self._queue_for_manual_download(url, video_id)
    
    def _download_with_cookies(self, url: str, video_id: str) -> Optional[str]:
        """Strategy 1: Use authenticated cookies"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        ydl_opts = {
            'format': 'best[height<=1080]/bestvideo[height<=1080]+bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'ignoreerrors': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }
        
        # Add cookies if available
        if os.path.exists(self.cookie_file):
            ydl_opts['cookiefile'] = self.cookie_file
            logger.info(f"Using cookies from {self.cookie_file}")
        
        # Rate limiting to appear human
        ydl_opts['sleep_interval'] = random.uniform(3, 6)
        ydl_opts['max_sleep_interval'] = 10
        ydl_opts['ratelimit'] = 150000  # 150KB/s
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        # Check if file was created
        if os.path.exists(output_path):
            return output_path
        return None
    
    def _download_with_user_agent(self, url: str, video_id: str) -> Optional[str]:
        """Strategy 2: Rotate user agents and headers"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        ydl_opts = {
            'format': 'best[height<=1080]/bestvideo[height<=1080]+bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'http_headers': {
                'User-Agent': random.choice(user_agents),
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'DNT': '1',
                'Referer': 'https://www.youtube.com/',
                'Origin': 'https://www.youtube.com'
            },
            'sleep_interval': 5,
            'max_sleep_interval': 15,
            'ratelimit': 100000  # 100KB/s - slower to avoid detection
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        if os.path.exists(output_path):
            return output_path
        return None
    
    def _download_with_invidious(self, url: str, video_id: str) -> Optional[str]:
        """Strategy 3: Use Invidious proxy instances"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        # Active Invidious instances (as of 2024)
        instances = [
            'https://inv.tux.pizza',
            'https://invidious.fdn.fr',
            'https://yewtu.be',
            'https://invidious.namazso.eu',
            'https://inv.riverside.rocks',
            'https://invidious.snopyta.org',
            'https://inv.privacy.com.de'
        ]
        
        random.shuffle(instances)  # Randomize order
        
        for instance in instances[:3]:  # Try top 3 instances
            try:
                logger.info(f"Trying Invidious instance: {instance}")
                
                # Use yt-dlp with Invidious
                ydl_opts = {
                    'format': 'best[height<=1080]/best',
                    'outtmpl': output_path,
                    'quiet': True,
                    'geo_bypass': True,
                    'socket_timeout': 20,
                    'retries': 2
                }
                
                # Convert YouTube URL to Invidious URL
                invidious_url = url.replace('youtube.com', instance.replace('https://', ''))
                invidious_url = invidious_url.replace('youtu.be', instance.replace('https://', ''))
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(invidious_url, download=True)
                    
                if os.path.exists(output_path):
                    return output_path
                    
            except Exception as e:
                logger.warning(f"Invidious instance {instance} failed: {e}")
                continue
        
        return None
    
    def _download_with_cobalt(self, url: str, video_id: str) -> Optional[str]:
        """Strategy 4: Use Cobalt.tools API"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        try:
            # Cobalt API endpoints
            api_urls = [
                "https://api.cobalt.tools/api/json",
                "https://cobalt.tools/api/json",
                "https://co.wuk.sh/api/json"
            ]
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            payload = {
                "url": url,
                "vQuality": "1080",
                "filenamePattern": "basic",
                "isAudioOnly": False,
                "disableMetadata": False,
                "dubLang": False,
                "vimeoDash": False
            }
            
            for api_url in api_urls:
                try:
                    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('status') == 'stream':
                            download_url = data.get('url')
                            
                            if download_url:
                                logger.info("Downloading from Cobalt stream URL")
                                
                                # Download with streaming
                                video_response = requests.get(download_url, stream=True, timeout=60, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                                })
                                
                                # Save video
                                with open(output_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)
                                
                                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                                    return output_path
                                    
                except Exception as e:
                    logger.warning(f"Cobalt API {api_url} failed: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Cobalt strategy failed completely: {e}")
        
        return None
    
    def _download_with_proxy(self, url: str, video_id: str) -> Optional[str]:
        """Strategy 5: Use proxy service (requires configuration)"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        proxy = os.environ.get('YOUTUBE_PROXY', None)
        
        if not proxy:
            logger.warning("No proxy configured, skipping proxy strategy")
            return None
        
        logger.info(f"Attempting download with proxy: {proxy}")
        
        ydl_opts = {
            'format': 'best[height<=1080]/best',
            'outtmpl': output_path,
            'proxy': proxy,
            'quiet': True,
            'geo_bypass': True,
            'socket_timeout': 30,
            'retries': 2
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        if os.path.exists(output_path):
            return output_path
        return None
    
    def _queue_for_manual_download(self, url: str, video_id: str) -> Optional[str]:
        """Tier 3 Workaround: Queue for manual download"""
        queue_file = '/app/output/manual_download_queue.json'
        
        os.makedirs(os.path.dirname(queue_file), exist_ok=True)
        
        try:
            with open(queue_file, 'r') as f:
                queue = json.load(f)
        except:
            queue = []
        
        # Add to queue if not already present
        if not any(item['video_id'] == video_id for item in queue):
            queue.append({
                'video_id': video_id,
                'url': url,
                'timestamp': time.time(),
                'strategies_tried': self.strategies_tried,
                'retry_count': 0
            })
            
            with open(queue_file, 'w') as f:
                json.dump(queue, f, indent=2)
            
            logger.warning(f"WORKAROUND: Video {video_id} queued for manual download")
        
        return None
    
    def _store_successful_pattern(self, strategy_name: str, url: str):
        """Store successful download pattern for future optimization"""
        pattern = {
            'type': 'youtube_download_success',
            'strategy': strategy_name,
            'timestamp': time.time(),
            'url_pattern': 'youtube.com' if 'youtube.com' in url else 'youtu.be',
            'success_rate': self.success_count / max(1, self.success_count + self.failure_count)
        }
        
        # Store in local pattern file
        pattern_file = '/app/context/patterns/download_patterns.json'
        os.makedirs(os.path.dirname(pattern_file), exist_ok=True)
        
        try:
            with open(pattern_file, 'r') as f:
                patterns = json.load(f)
        except:
            patterns = []
        
        # Keep last 100 patterns
        patterns.append(pattern)
        patterns = patterns[-100:]
        
        try:
            with open(pattern_file, 'w') as f:
                json.dump(patterns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to store pattern: {e}")
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get download statistics"""
        total = self.success_count + self.failure_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        return {
            'total_attempts': total,
            'successful': self.success_count,
            'failed': self.failure_count,
            'success_rate': f"{success_rate:.1f}%",
            'strategies_used': list(set(self.strategies_tried))
        }