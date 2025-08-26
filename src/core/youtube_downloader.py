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
        self._check_cookie_validity()
        
    def download_video(self, url: str, video_id: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Download video using cascading fallback strategies
        Following Constitutional AI Tier 2 error handling - 3 retries with backoff
        """
        if output_dir:
            self.output_dir = output_dir
            
        # Reset strategies for this download
        self.strategies_tried = []
        
        # CRITICAL: Cookies are the ONLY proven method for cloud servers
        # Other strategies are mostly for fallback/redundancy
        strategies = [
            ('cookies', self._download_with_cookies),  # PRIMARY METHOD
            ('cookies_retry', self._download_with_cookies),  # Try again with cookies
            ('user_agent', self._download_with_user_agent),  # Fallback 1
            ('invidious', self._download_with_invidious),  # Fallback 2
            ('cobalt', self._download_with_cobalt),  # Fallback 3
            ('proxy', self._download_with_proxy),  # Last resort
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
        """Strategy 1: Use authenticated cookies - PROVEN METHOD FOR CLOUD SERVERS"""
        output_path = f'{self.output_dir}/{video_id}.mp4'
        
        # Check if cookies exist, if not, log critical warning
        if not os.path.exists(self.cookie_file):
            logger.critical(f"COOKIES FILE NOT FOUND at {self.cookie_file}")
            logger.critical("Cookies are REQUIRED for cloud server downloads!")
            logger.critical("Run: python scripts/extract_cookies.py")
            return None
        
        ydl_opts = {
            'format': 'best[height<=1080]/bestvideo[height<=1080]+bestaudio/best',
            'outtmpl': output_path,
            'quiet': False,  # Show output for debugging
            'no_warnings': False,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 5,  # More retries
            'fragment_retries': 5,
            'ignoreerrors': False,  # Don't ignore errors
            'cookiefile': self.cookie_file,  # Always use cookies
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            },
            # Additional options for better cookie handling
            'cookiesfrombrowser': None,  # Don't try browser extraction
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            # Slow down to appear more human
            'sleep_interval': random.uniform(5, 10),
            'max_sleep_interval': 15,
            'sleep_interval_requests': 1,
            'sleep_interval_subtitles': 1,
            'ratelimit': 100000,  # 100KB/s - slower for safety
            # Additional safety options
            'age_limit': None,
            'download_archive': None,
            'break_on_existing': False,
            'break_on_reject': False,
            'skip_playlist_after_errors': 3,
            'concurrent_fragment_downloads': 1,
            # Progress hooks for monitoring
            'progress_hooks': [self._download_progress_hook],
        }
        
        logger.info(f"Using authenticated cookies from {self.cookie_file}")
        logger.info("This is the ONLY proven method for cloud server downloads")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
            # Verify file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"SUCCESS: Downloaded {os.path.getsize(output_path)/1024/1024:.1f}MB")
                return output_path
            else:
                logger.error("Download failed or file too small")
                return None
                
        except yt_dlp.utils.DownloadError as e:
            if "Sign in to confirm you're not a bot" in str(e):
                logger.error("BOT DETECTION: Cookies may be expired or invalid!")
                logger.error("Solution: Run python scripts/extract_cookies.py")
            raise
    
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
    
    def _download_progress_hook(self, d):
        """Progress hook to monitor download status"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            logger.info(f"Downloading: {percent} at {speed} ETA: {eta}")
        elif d['status'] == 'finished':
            logger.info("Download completed, processing...")
    
    def _check_cookie_validity(self):
        """Check if cookies exist and are valid"""
        if not os.path.exists(self.cookie_file):
            logger.critical("="*60)
            logger.critical("CRITICAL: NO YOUTUBE COOKIES FOUND!")
            logger.critical("="*60)
            logger.critical("")
            logger.critical("Cookies are REQUIRED for cloud server downloads!")
            logger.critical("All other methods WILL FAIL from datacenter IPs!")
            logger.critical("")
            logger.critical("To fix this:")
            logger.critical("1. Run: python scripts/extract_cookies.py")
            logger.critical("2. Or manually export cookies from browser")
            logger.critical("3. Save to: /app/config/youtube_cookies.txt")
            logger.critical("")
            logger.critical("="*60)
            return False
        
        # Check if cookies are recent (less than 30 days old)
        cookie_age = time.time() - os.path.getmtime(self.cookie_file)
        days_old = cookie_age / (24 * 3600)
        
        if days_old > 25:
            logger.warning(f"COOKIES ARE {days_old:.0f} DAYS OLD - May expire soon!")
            logger.warning("Consider refreshing: python scripts/extract_cookies.py")
        
        logger.info(f"✓ Cookies found: {self.cookie_file} ({days_old:.1f} days old)")
        return True
    
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