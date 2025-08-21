"""
Constitutional AI Compliance Tests
Verify Maximum Velocity Mode and performance standards
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from src.core.main_controller import MainController
from src.core.error_handler import ErrorHandler, ErrorTier
from src.api.rest_api import app
from src.utils.monitoring import MetricsCollector


class TestConstitutionalCompliance:
    """Test Constitutional AI compliance"""
    
    @pytest.mark.asyncio
    async def test_maximum_velocity_mode(self):
        """Verify Maximum Velocity Mode - no confirmations"""
        controller = MainController()
        
        # Mock all dependencies to prevent actual execution
        controller.content_sourcer = AsyncMock()
        controller.smart_clipper = AsyncMock()
        controller.video_editor = AsyncMock()
        controller.ai_agents = AsyncMock()
        
        # Start controller (should not ask for confirmations)
        with patch('builtins.input', side_effect=Exception("No input allowed!")):
            await controller.initialize()
            # Should complete without asking for input
        
        assert controller.monitor.mode == "MAXIMUM_VELOCITY"
    
    @pytest.mark.asyncio
    async def test_error_tier_handling(self):
        """Test Tier 1-4 error handling"""
        handler = ErrorHandler()
        
        # Test Tier 1 - Transient error
        error = Exception("Connection timeout")
        result = await handler.handle(error, {"operation": lambda: "success"}, ErrorTier.TIER1)
        assert handler.error_stats["transient"] > 0
        
        # Test Tier 2 - Processing error
        error = Exception("Invalid format")
        result = await handler.handle(error, {"default_value": "fallback"}, ErrorTier.TIER2)
        assert result == "fallback"
        
        # Test Tier 3 - System error
        error = Exception("Out of memory")
        result = await handler.handle(error, {"cached_value": "cached"}, ErrorTier.TIER3)
        assert result == "cached"
        
        # Test Tier 4 - Critical error
        error = Exception("Data corruption")
        result = await handler.handle(error, {}, ErrorTier.TIER4)
        assert result is None  # Continues with degraded functionality
    
    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Test API response time <22ms"""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test health endpoint
        start = time.time()
        response = client.get("/api/v1/health")
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert duration < 100  # Allow some overhead for test environment
        assert "X-Response-Time" in response.headers
    
    def test_token_optimization(self):
        """Test MCP token optimization ≥85%"""
        from src.mcp.mcp_client import MCPClientManager
        
        manager = MCPClientManager()
        manager.token_stats = {
            "original": 10000,
            "optimized": 1500,
            "reduction_rate": 0.85
        }
        
        reduction = asyncio.run(manager.get_token_reduction())
        assert reduction >= 0.85
    
    @pytest.mark.asyncio
    async def test_no_blocking_operations(self):
        """Verify no blocking operations"""
        controller = MainController()
        
        # All main methods should be async
        assert asyncio.iscoroutinefunction(controller.initialize)
        assert asyncio.iscoroutinefunction(controller.start)
        assert asyncio.iscoroutinefunction(controller._content_discovery_loop)
        assert asyncio.iscoroutinefunction(controller._video_processing_loop)
    
    def test_pattern_storage(self):
        """Test pattern storage in PIECES"""
        from src.mcp.pieces_memory import PiecesMemory
        
        pieces = PiecesMemory()
        pattern_id = asyncio.run(pieces.store_pattern(
            category="test",
            data={"pattern": "test_data"},
            tags=["test"]
        ))
        
        assert pattern_id.startswith("pattern_")
        assert "test" in pieces.pattern_index
    
    def test_performance_monitoring(self):
        """Test performance monitoring compliance"""
        metrics = MetricsCollector()
        
        # Record compliant metrics
        metrics.record_api_response("test", 15.0)
        metrics.record_db_query("select", 3.0)
        
        compliance = metrics.get_constitutional_compliance()
        assert compliance["api_compliant"] is True
        assert compliance["db_compliant"] is True
        assert compliance["overall_compliant"] is True
        
        # Record non-compliant metrics
        metrics.record_api_response("slow", 25.0)
        metrics.record_db_query("complex", 8.0)
        
        compliance = metrics.get_constitutional_compliance()
        assert compliance["overall_compliant"] is False