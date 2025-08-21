"""
MCP Integration Tests
Test MCP server functionality and token optimization
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.mcp.mcp_client import MCPClientManager
from src.mcp.ref_integration import RefServer
from src.mcp.pieces_memory import PiecesMemory
from src.mcp.semgrep_scanner import SemgrepScanner


class TestMCPIntegration:
    """Test MCP server integration"""
    
    @pytest.mark.asyncio
    async def test_mcp_manager_initialization(self):
        """Test MCP manager initialization"""
        manager = MCPClientManager()
        
        with patch.object(RefServer, 'initialize', return_value=True):
            with patch.object(PiecesMemory, 'initialize', return_value=True):
                with patch.object(SemgrepScanner, 'initialize', return_value=True):
                    result = await manager.initialize()
                    
        assert result is True
        assert "ref" in manager.servers
        assert "pieces" in manager.servers
        assert "semgrep" in manager.servers
    
    @pytest.mark.asyncio
    async def test_ref_documentation_access(self):
        """Test REF documentation retrieval"""
        ref_server = RefServer()
        await ref_server.initialize()
        
        result = await ref_server.get_documentation("ffmpeg", "video_filters")
        
        assert "documentation" in result
        assert "token_reduction" in result
        assert result["token_reduction"] == 0.85
    
    @pytest.mark.asyncio
    async def test_pieces_pattern_storage(self):
        """Test PIECES pattern storage and recall"""
        pieces = PiecesMemory()
        await pieces.initialize()
        
        # Store pattern
        pattern_id = await pieces.store_pattern(
            category="viral_hooks",
            data={"hook_type": "transformation", "success_rate": 0.9},
            tags=["fitness", "viral"]
        )
        
        assert pattern_id.startswith("pattern_")
        
        # Recall patterns
        patterns = await pieces.recall_patterns("viral_hooks", limit=5)
        
        assert len(patterns) > 0
        assert patterns[0]["category"] == "viral_hooks"
    
    @pytest.mark.asyncio
    async def test_semgrep_security_scanning(self):
        """Test SEMGREP security scanning"""
        scanner = SemgrepScanner()
        await scanner.initialize()
        
        result = await scanner.scan("src/test.py", auto_fix=True)
        
        assert "findings" in result
        assert "scan_time" in result
        assert "fixed" in result
    
    @pytest.mark.asyncio
    async def test_token_reduction_tracking(self):
        """Test token reduction tracking"""
        manager = MCPClientManager()
        
        # Simulate token usage
        manager._update_token_stats(1000, 150)
        manager._update_token_stats(2000, 300)
        
        reduction = await manager.get_token_reduction()
        
        assert reduction == 0.85  # (1000+2000)-(150+300) / (1000+2000)
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test MCP response caching"""
        manager = MCPClientManager()
        
        # Test cache miss
        cached = manager._get_cached("test_key")
        assert cached is None
        
        # Cache result
        manager._cache_result("test_key", {"data": "test"})
        
        # Test cache hit
        cached = manager._get_cached("test_key")
        assert cached == {"data": "test"}
        
        # Test cache expiration
        manager.cache["test_key"]["timestamp"] = datetime.now() - timedelta(hours=2)
        cached = manager._get_cached("test_key")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_pattern_search(self):
        """Test pattern search functionality"""
        pieces = PiecesMemory()
        
        # Store multiple patterns
        await pieces.store_pattern("hooks", {"type": "shock", "score": 0.9}, ["viral"])
        await pieces.store_pattern("hooks", {"type": "reveal", "score": 0.8}, ["viral"])
        await pieces.store_pattern("clips", {"duration": 30, "score": 0.7}, ["optimal"])
        
        # Search patterns
        results = await pieces.search_patterns({"type": "shock"}, limit=2)
        
        assert len(results) > 0
        assert all("similarity" in r for r in results)