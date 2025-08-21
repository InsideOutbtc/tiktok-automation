"""
Video Processing Tests
Test core video processing functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import numpy as np

from src.core.smart_clipper import SmartClipper
from src.core.video_editor import VideoEditor
from src.core.content_sourcer import ContentSourcer


class TestVideoProcessing:
    """Test video processing pipeline"""
    
    @pytest.mark.asyncio
    async def test_smart_clipper_analysis(self):
        """Test video analysis for clips"""
        clipper = SmartClipper()
        
        # Mock video capture
        with patch('cv2.VideoCapture') as mock_cap:
            mock_instance = Mock()
            mock_instance.get.side_effect = lambda x: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 3600
            }.get(x, 0)
            mock_instance.read.return_value = (True, np.zeros((1080, 1920, 3)))
            mock_cap.return_value = mock_instance
            
            analysis = await clipper.analyze_video("test_video.mp4")
            
            assert "duration" in analysis
            assert "viral_score" in analysis
            assert analysis["fps"] == 30.0
            assert analysis["duration"] == 120.0  # 3600 frames / 30 fps
    
    @pytest.mark.asyncio
    async def test_clip_creation(self):
        """Test clip extraction"""
        clipper = SmartClipper()
        
        analysis = {
            "duration": 120,
            "fps": 30,
            "scene_changes": [0, 30, 60, 90],
            "energy_peaks": [15, 45, 75]
        }
        
        clips = await clipper.create_clips("test_video.mp4", analysis)
        
        assert len(clips) > 0
        assert all("start_time" in clip for clip in clips)
        assert all("end_time" in clip for clip in clips)
        assert all("score" in clip for clip in clips)
    
    @pytest.mark.asyncio
    async def test_video_editor_effects(self):
        """Test video effect application"""
        editor = VideoEditor()
        
        # Mock ffmpeg operations
        with patch('ffmpeg.input') as mock_input:
            mock_stream = Mock()
            mock_input.return_value = mock_stream
            mock_stream.filter.return_value = mock_stream
            mock_stream.output.return_value = mock_stream
            
            clip = {
                "path": "test_clip.mp4",
                "score": 0.85
            }
            
            result = await editor.apply_effects(clip["path"], ["auto_caption", "energy_boost"])
            
            assert "path" in result
            assert "effects_applied" in result
            assert len(result["effects_applied"]) >= 2
    
    @pytest.mark.asyncio
    async def test_content_discovery(self):
        """Test content discovery from platforms"""
        sourcer = ContentSourcer()
        
        # Mock API calls
        with patch('aiohttp.ClientSession') as mock_session:
            content = await sourcer.discover_content(
                platforms=["tiktok", "youtube"],
                categories=["fitness"],
                limit=10
            )
            
            assert len(content) <= 10
            assert all("platform" in item for item in content)
            assert all("viral_score" in item for item in content)
            assert all(item["viral_score"] >= 0.7 for item in content)
    
    def test_clip_duration_validation(self):
        """Test clip duration constraints"""
        clipper = SmartClipper()
        
        # Test minimum duration
        clip = clipper._create_clip_around_point(10.0, 120.0)
        if clip:
            assert clip.end_time - clip.start_time >= clipper.min_clip_duration
            assert clip.end_time - clip.start_time <= clipper.max_clip_duration
    
    @pytest.mark.asyncio
    async def test_video_download(self):
        """Test video download functionality"""
        sourcer = ContentSourcer()
        
        with patch('asyncio.sleep'):
            path = await sourcer.download_video("https://example.com/video")
            
            assert path.endswith(".mp4")
            assert "/tmp/videos/" in path