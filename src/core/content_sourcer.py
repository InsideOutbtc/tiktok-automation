# src/core/content_sourcer.py - Real API Integration
# Constitutional AI compliant content discovery

import os
import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

# YouTube API
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# TikTok Free API - Disabled temporarily
# from TikTokApi import TikTokApi

# Video Downloader
import yt_dlp

# OpenAI for content analysis
from openai import OpenAI

# Core imports
from src.core.error_handler import ErrorHandler, ErrorTier

load_dotenv()
logger = logging.getLogger(__name__)


class ContentSourcer:
    """Real content discovery from actual platforms"""
    
    def __init__(self):
        # Load API keys from environment
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate keys exist
        if not self.youtube_api_key:
            logger.warning("YouTube API key not found - YouTube discovery disabled")
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found - AI analysis limited")
            
        # Initialize APIs
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key) if self.youtube_api_key else None
        # self.tiktok_api = TikTokApi()  # Disabled temporarily
        
        # Configure OpenAI v1.0+
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI v1.0+ initialized")
            except:
                self.openai_client = None
                logger.warning("OpenAI init failed")
        else:
            self.openai_client = None
        
        # Video download configuration
        self.download_dir = "input/downloads"
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Error handler
        self.error_handler = ErrorHandler()
        
    async def discover_viral_content(
        self,
        platforms: List[str] = None,
        keywords: List[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Discover real viral content from actual platforms"""
        logger.info("🔍 Discovering REAL viral content")
        
        if platforms is None:
            platforms = ["youtube", "tiktok"]
        if keywords is None:
            keywords = ["fitness", "workout", "gym", "transformation", "motivation"]
            
        all_content = []
        
        # Discover from each platform
        if "youtube" in platforms and self.youtube:
            youtube_content = await self._discover_youtube_real(keywords)
            all_content.extend(youtube_content)
            
        if "tiktok" in platforms:
            tiktok_content = await self._discover_tiktok_free(keywords)
            all_content.extend(tiktok_content)
            
        # Analyze with AI if available
        if self.openai_api_key and all_content:
            all_content = await self._analyze_with_ai(all_content)
            
        # Sort by combined score (engagement + AI)
        all_content.sort(
            key=lambda x: (
                x.get("engagement_score", 0) * 0.6 +
                x.get("ai_score", 0) * 0.4
            ),
            reverse=True
        )
        
        logger.info(f"✅ Found {len(all_content)} real videos")
        return all_content[:limit]
    
    async def _discover_youtube_real(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Discover real YouTube videos using actual API"""
        content = []
        
        try:
            for keyword in keywords:
                # Search for videos
                request = self.youtube.search().list(
                    q=f"{keyword} viral challenge transformation",
                    part="snippet",
                    type="video",
                    order="viewCount",
                    maxResults=10,
                    videoDuration="short",  # Prefer short videos
                    publishedAfter=(datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_id = item['id']['videoId']
                    
                    # Get video statistics
                    stats_request = self.youtube.videos().list(
                        part="statistics,contentDetails",
                        id=video_id
                    )
                    stats_response = stats_request.execute()
                    
                    if stats_response['items']:
                        stats = stats_response['items'][0]['statistics']
                        details = stats_response['items'][0]['contentDetails']
                        
                        # Parse duration
                        duration = self._parse_youtube_duration(details['duration'])
                        
                        # Skip videos longer than 3 minutes
                        if duration > 180:
                            continue
                        
                        video_data = {
                            "platform": "youtube",
                            "id": video_id,
                            "title": item['snippet']['title'],
                            "description": item['snippet']['description'][:500],
                            "channel": item['snippet']['channelTitle'],
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "thumbnail": item['snippet']['thumbnails']['high']['url'],
                            "published_at": item['snippet']['publishedAt'],
                            "duration": duration,
                            "views": int(stats.get('viewCount', 0)),
                            "likes": int(stats.get('likeCount', 0)),
                            "comments": int(stats.get('commentCount', 0)),
                            "engagement_score": self._calculate_youtube_engagement(stats),
                            "download_status": "pending",
                            "keywords": [keyword],
                            "discovered_at": datetime.utcnow().isoformat()
                        }
                        content.append(video_data)
                        
        except HttpError as e:
            await self.error_handler.handle(e, {"platform": "youtube"}, ErrorTier.TIER2)
        except Exception as e:
            await self.error_handler.handle(e, {"platform": "youtube"}, ErrorTier.TIER3)
            
        return content
    
    async def _discover_tiktok_free(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Discover TikTok - temporarily disabled, using mock data"""
        content = []
        
        # TikTokApi temporarily disabled - return empty list
        logger.info("TikTok discovery temporarily disabled - using YouTube only")
        return content
        
        # Original code commented out:
        # try:
        #     # Try new API syntax
        #     async with TikTokApi() as api:
        #         await api.create_sessions(num_sessions=1, sleep_after=3)
        #         
        #         for keyword in keywords:
        #             try:
        #                 # Search by hashtag
        #                 tag = api.hashtag(name=keyword)
        #                 
        #                 async for video in tag.videos(count=10):
        #                     video_data = {
        #                         "platform": "tiktok",
        #                         "id": video.id,
        #                         "title": video.desc,
        #                         "author": video.author.username,
        #                         "author_id": video.author.id,
        #                         "url": f"https://www.tiktok.com/@{video.author.username}/video/{video.id}",
        #                         "music": video.sound.title if video.sound else "Unknown",
        #                         "duration": video.video.duration,
        #                         "views": video.stats.play_count,
        #                         "likes": video.stats.digg_count,
        #                         "shares": video.stats.share_count,
        #                         "comments": video.stats.comment_count,
        #                         "engagement_score": self._calculate_tiktok_engagement({
        #                             'playCount': video.stats.play_count,
        #                             'diggCount': video.stats.digg_count,
        #                             'shareCount': video.stats.share_count,
        #                             'commentCount': video.stats.comment_count
        #                         }),
        #                         "download_status": "pending",
        #                         "keywords": [keyword],
        #                         "discovered_at": datetime.utcnow().isoformat()
        #                     }
        #                     content.append(video_data)
        #             except Exception as e:
        #                 logger.warning(f"Error processing keyword {keyword}: {e}")
        #                 continue
                        
        # except AttributeError as e:
        #     # Tier 3: Use mock data for attribute errors
        #     logger.warning(f"TikTok API attribute issue: {e}, using mock data")
        #     return self._get_mock_tiktok_data(keywords)
        # except Exception as e:
        #     logger.error(f"TikTok API error: {e}")
        #     # Try trending as fallback
        #     try:
        #         async with TikTokApi() as api:
        #             await api.create_sessions(num_sessions=1, sleep_after=3)
        #             async for video in api.trending.videos(count=20):
        #                 # Check if fitness related
        #                 if any(kw in video.desc.lower() for kw in ["fitness", "workout", "gym"]):
        #                     video_data = {
        #                         "platform": "tiktok",
        #                         "id": video.id,
        #                         "title": video.desc,
        #                         "author": video.author.username,
        #                         "url": f"https://www.tiktok.com/@{video.author.username}/video/{video.id}",
        #                         "duration": video.video.duration,
        #                         "views": video.stats.play_count,
        #                         "likes": video.stats.digg_count,
        #                         "engagement_score": self._calculate_tiktok_engagement({
        #                             'playCount': video.stats.play_count,
        #                             'diggCount': video.stats.digg_count,
        #                             'shareCount': video.stats.share_count,
        #                             'commentCount': video.stats.comment_count
        #                         }),
        #                         "download_status": "pending",
        #                         "discovered_at": datetime.utcnow().isoformat()
        #                     }
        #                     content.append(video_data)
        #     except:
        #         logger.error("TikTok API failed completely, using mock data")
        #         return self._get_mock_tiktok_data(keywords)
        #         
        # return content
    
    def _get_mock_tiktok_data(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """Tier 3 workaround - mock TikTok data"""
        mock_data = []
        base_videos = [
            {"title": "Amazing fitness transformation", "views": 1500000, "likes": 250000},
            {"title": "30 day abs challenge results", "views": 2000000, "likes": 350000},
            {"title": "Gym motivation - never give up", "views": 800000, "likes": 120000},
            {"title": "Home workout no equipment", "views": 3000000, "likes": 450000},
            {"title": "Before and after 90 days", "views": 5000000, "likes": 800000},
        ]
        
        for i, video in enumerate(base_videos * 4):  # Generate 20 videos
            mock_data.append({
                'platform': 'tiktok',
                'id': f'mock_{i}_{int(datetime.now().timestamp())}',
                'title': f"{video['title']} #{keywords[0] if keywords else 'fitness'}",
                'author': f'fitness_user_{i % 5}',
                'url': f'https://www.tiktok.com/@mock_user/video/mock_{i}',
                'duration': 30 + (i % 30),
                'views': video['views'] + (i * 10000),
                'likes': video['likes'] + (i * 1000),
                'shares': video['likes'] // 10,
                'comments': video['likes'] // 20,
                'engagement_score': min(0.15 + (i * 0.02), 0.9),
                'download_status': 'mock',
                'keywords': keywords or ['fitness'],
                'discovered_at': datetime.utcnow().isoformat()
            })
        
        logger.info(f"Generated {len(mock_data)} mock TikTok videos")
        return mock_data[:20]  # Return max 20
    
    async def download_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Download video with Tier 2 multi-strategy retry"""
        output_path = os.path.join(
            self.download_dir,
            f"{video_data['platform']}_{video_data['id']}.mp4"
        )
        
        # Skip if already downloaded
        if os.path.exists(output_path):
            logger.info(f"Video already downloaded: {output_path}")
            video_data['download_status'] = 'completed'
            video_data['local_path'] = output_path
            return output_path
        
        # Tier 2: Multiple retry strategies
        strategies = [
            {  # Strategy 1: User agent spoofing
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'format': 'best[height<=1080]/best',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'referer': 'https://www.youtube.com/' if video_data['platform'] == 'youtube' else 'https://www.tiktok.com/',
                'headers': {
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                },
                'extract_flat': False,
                'socket_timeout': 30,
            },
            {  # Strategy 2: Alternative format
                'outtmpl': output_path,
                'quiet': True,
                'format': 'worst',  # Try lowest quality if high quality blocked
            },
            {  # Strategy 3: Extract info only
                'quiet': True,
                'extract_flat': True,
                'dump_single_json': True,
            }
        ]
        
        # Add cookies for TikTok if available
        if video_data['platform'] == 'tiktok' and os.getenv('TIKTOK_COOKIES_FILE'):
            for strategy in strategies:
                strategy['cookiefile'] = os.getenv('TIKTOK_COOKIES_FILE')
        
        for i, opts in enumerate(strategies):
            try:
                logger.info(f"Download attempt {i+1} for {video_data['id']}")
                with yt_dlp.YoutubeDL(opts) as ydl:
                    if i == 2:  # Info only
                        info = ydl.extract_info(video_data['url'], download=False)
                        logger.info(f"Video info extracted, manual download needed: {info.get('title')}")
                        video_data['download_status'] = 'info_only'
                        return None
                    else:
                        ydl.download([video_data['url']])
                        if os.path.exists(output_path):
                            logger.info(f"✅ Downloaded: {output_path}")
                            video_data['download_status'] = 'completed'
                            video_data['local_path'] = output_path
                            return output_path
            except Exception as e:
                logger.warning(f"Strategy {i+1} failed: {str(e)[:100]}")
                if i < len(strategies) - 1:
                    await asyncio.sleep(2 ** i)  # Exponential backoff
        
        # Tier 3: Return None, system continues with other videos
        logger.error(f"All download strategies failed for {video_data['id']}")
        video_data['download_status'] = 'failed'
        return None
    
    async def _analyze_with_ai(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use OpenAI to analyze content for viral potential"""
        if not self.openai_api_key:
            return content
            
        try:
            # Batch analyze to save tokens
            batch_size = 5
            for i in range(0, min(len(content), 20), batch_size):
                batch = content[i:i+batch_size]
                
                # Create batch prompt
                videos_desc = "\n\n".join([
                    f"Video {j+1}:\n"
                    f"Platform: {v['platform']}\n"
                    f"Title: {v.get('title', '')[:100]}\n"
                    f"Views: {v.get('views', 0):,}\n"
                    f"Likes: {v.get('likes', 0):,}\n"
                    f"Engagement: {v.get('engagement_score', 0):.2%}"
                    for j, v in enumerate(batch)
                ])
                
                prompt = f"""Analyze these videos for viral potential in the fitness niche.
Rate each from 0-1 and explain why in one sentence.

{videos_desc}

Format each as: Video X: SCORE: 0.XX | REASON: explanation"""

                # OpenAI v1.0+ API call
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a viral fitness content expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.3
                )
                
                # Parse responses
                analysis = response.choices[0].message.content
                lines = analysis.split('\n')
                
                for j, line in enumerate(lines):
                    if f"Video {j+1}:" in line and "SCORE:" in line:
                        try:
                            score = float(line.split("SCORE:")[1].split("|")[0].strip())
                            reason = line.split("REASON:")[1].strip() if "REASON:" in line else ""
                            
                            if i+j < len(content):
                                content[i+j]['ai_score'] = score
                                content[i+j]['ai_analysis'] = reason
                        except:
                            pass
                            
        except Exception as e:
            await self.error_handler.handle(e, {"service": "openai"}, ErrorTier.TIER2)
            
        return content
    
    def _calculate_youtube_engagement(self, stats: Dict) -> float:
        """Calculate engagement score for YouTube video"""
        views = int(stats.get('viewCount', 1))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        if views > 0:
            engagement_rate = (likes + comments * 2) / views
            # Normalize to 0-1 scale with curve
            return min(engagement_rate * 50, 1.0)
        return 0.0
    
    def _calculate_tiktok_engagement(self, stats: Dict) -> float:
        """Calculate engagement score for TikTok video"""
        views = stats.get('playCount', 1)
        likes = stats.get('diggCount', 0)
        shares = stats.get('shareCount', 0)
        comments = stats.get('commentCount', 0)
        
        if views > 0:
            # TikTok weights shares heavily
            engagement_rate = (likes + shares * 3 + comments * 2) / views
            return min(engagement_rate * 25, 1.0)
        return 0.0
    
    def _parse_youtube_duration(self, duration: str) -> int:
        """Parse YouTube duration format (PT1M30S) to seconds"""
        import re
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
            
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    async def batch_download(self, videos: List[Dict[str, Any]], max_concurrent: int = 3) -> List[str]:
        """Download multiple videos concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(video):
            async with semaphore:
                return await self.download_video(video)
        
        tasks = [download_with_semaphore(video) for video in videos]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        downloaded = []
        for i, result in enumerate(results):
            if isinstance(result, str) and result:
                downloaded.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Download failed for {videos[i]['url']}: {result}")
                
        return downloaded