"""
Video Utilities - Helper functions for video processing
Optimized for performance and reliability
"""

import os
import subprocess
import asyncio
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VideoUtils:
    """Video processing utilities"""
    
    @staticmethod
    async def get_video_info(video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"ffprobe error: {stderr.decode()}")
                return {}
            
            import json
            data = json.loads(stdout.decode())
            
            # Extract relevant info
            video_stream = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), {})
            
            return {
                'duration': float(data.get('format', {}).get('duration', 0)),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate': int(data.get('format', {}).get('bit_rate', 0))
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    @staticmethod
    async def extract_clip(video_path: str, start: float, end: float, output_path: str) -> bool:
        """Extract clip from video"""
        try:
            duration = end - start
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', str(start),
                '-t', str(duration),
                '-c', 'copy',  # Fast copy without re-encoding
                '-y',  # Overwrite output
                output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            _, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"ffmpeg error: {stderr.decode()}")
                return False
                
            return os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Error extracting clip: {e}")
            return False
    
    @staticmethod
    async def add_text_overlay(video_path: str, text: str, output_path: str) -> bool:
        """Add text overlay to video"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f"drawtext=text='{text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=h-100",
                '-codec:a', 'copy',
                '-y', output_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {e}")
            return False
    
    @staticmethod
    def validate_video_path(path: str) -> bool:
        """Validate video file path"""
        if not os.path.exists(path):
            return False
            
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        return any(path.lower().endswith(ext) for ext in valid_extensions)