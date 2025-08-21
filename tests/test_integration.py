"""
Integration Tests
Test full system integration and workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.core.main_controller import MainController
from src.database.models import Video, Clip, get_db
from src.database.queries import OptimizedQueries


class TestSystemIntegration:
    """Test full system integration"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete content pipeline"""
        controller = MainController()
        
        # Mock external dependencies
        controller.content_sourcer.discover_content = AsyncMock(return_value=[
            {
                "platform": "tiktok",
                "source_url": "https://example.com/video1",
                "viral_score": 0.85,
                "metadata": {"views": 1000000}
            }
        ])
        
        controller.content_sourcer.download_video = AsyncMock(return_value="/tmp/video1.mp4")
        
        controller.smart_clipper.analyze_video = AsyncMock(return_value={
            "duration": 120,
            "fps": 30,
            "viral_score": 0.85
        })
        
        controller.smart_clipper.create_clips = AsyncMock(return_value=[
            {"path": "/tmp/clip1.mp4", "score": 0.9, "start_time": 0, "end_time": 30}
        ])
        
        controller.video_editor.apply_effects = AsyncMock(return_value={
            "path": "/tmp/clip1_edited.mp4",
            "effects_applied": ["auto_caption", "hook_enhance"]
        })
        
        # Initialize controller
        await controller.initialize()
        
        # Run one discovery cycle
        controller.running = True
        discovery_task = asyncio.create_task(controller._content_discovery_loop())
        await asyncio.sleep(0.1)  # Let it run briefly
        controller.running = False
        
        # Verify pipeline execution
        assert controller.content_sourcer.discover_content.called
        assert controller.metrics["discovery_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self):
        """Test error recovery across components"""
        controller = MainController()
        
        # Simulate various errors
        errors_to_test = [
            (Exception("Connection timeout"), ErrorTier.TIER1),
            (Exception("Invalid video format"), ErrorTier.TIER2),
            (Exception("Database connection lost"), ErrorTier.TIER3)
        ]
        
        for error, expected_tier in errors_to_test:
            result = await controller.error_handler.handle(
                error,
                {"default_value": "recovered"},
                tier=None  # Let it auto-classify
            )
            
            # Verify recovery
            assert controller.error_handler.error_stats[expected_tier.value] > 0
    
    def test_database_integration(self):
        """Test database operations"""
        db = next(get_db())
        
        try:
            # Test video insertion
            video = Video(
                platform="tiktok",
                platform_id="test123",
                url="https://example.com/video",
                title="Test Video",
                engagement_score=0.85,
                viral_score=0.9
            )
            db.add(video)
            db.commit()
            
            # Test query optimization
            unprocessed = OptimizedQueries.get_unprocessed_videos(db, limit=5)
            assert isinstance(unprocessed, list)
            
            # Test clip insertion
            clips = [
                {"video_id": video.id, "path": "/tmp/clip1.mp4", "score": 0.8, "start_time": 0, "end_time": 30}
            ]
            OptimizedQueries.bulk_insert_clips(db, clips)
            
            # Verify insertion
            publishable = OptimizedQueries.get_publishable_clips(db)
            assert len(publishable) > 0
            
        finally:
            db.rollback()
            db.close()
    
    @pytest.mark.asyncio
    async def test_mcp_integration_flow(self):
        """Test MCP server integration in workflow"""
        controller = MainController()
        
        # Test pattern storage during processing
        pattern_data = {
            "type": "viral_hook",
            "success_rate": 0.92,
            "features": {"duration": 25, "hook_type": "transformation"}
        }
        
        pattern_id = await controller.mcp_client.pieces(
            "store",
            category="test_patterns",
            data=pattern_data
        )
        
        assert pattern_id is not None
        
        # Test pattern recall
        patterns = await controller.mcp_client.pieces(
            "recall",
            category="test_patterns",
            limit=5
        )
        
        assert len(patterns) > 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self):
        """Test performance monitoring across system"""
        from src.utils.monitoring import MetricsCollector
        
        metrics = MetricsCollector()
        
        # Simulate various operations
        metrics.record_api_response("discovery", 18.5)
        metrics.record_db_query("get_videos", 3.2)
        metrics.record_video_processing(25.5, 5)
        metrics.record_error("timeout", 1, True)
        
        # Check compliance
        compliance = metrics.get_constitutional_compliance()
        assert compliance["overall_compliant"] is True
        
        # Check system stats
        stats = metrics.get_system_stats()
        assert stats["total_api_requests"] > 0
        assert stats["videos_processed"] > 0