"""
AI Agent Tests
Test AI agent functionality and decision making
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.agents.ai_agent_system import AIAgentSystem
from src.agents.content_agents.viral_scout import ViralScoutAgent
from src.agents.content_agents.clip_selector import ClipSelectorAgent
from src.agents.content_agents.hook_writer import HookWriterAgent
from src.agents.content_agents.engagement_predictor import EngagementPredictorAgent


class TestAIAgents:
    """Test AI agent system"""
    
    @pytest.mark.asyncio
    async def test_viral_scout_analysis(self):
        """Test viral content analysis"""
        scout = ViralScoutAgent()
        await scout.initialize()
        
        content = {
            "platform": "tiktok",
            "source_id": "test123",
            "metadata": {
                "views": 1500000,
                "likes": 150000,
                "shares": 30000,
                "duration": 25,
                "hashtags": ["fitness", "transformation"]
            }
        }
        
        result = await scout.analyze_single(content)
        
        assert "viral_score" in result
        assert result["viral_score"] > 0.7
        assert "viral_features" in result
    
    @pytest.mark.asyncio
    async def test_clip_selector_ranking(self):
        """Test clip selection and ranking"""
        selector = ClipSelectorAgent()
        await selector.initialize()
        
        clips = [
            {"score": 0.9, "start_time": 0, "end_time": 30, "type": "energy_peak"},
            {"score": 0.6, "start_time": 30, "end_time": 60, "type": "scene_based"},
            {"score": 0.8, "start_time": 60, "end_time": 90, "type": "energy_peak"},
            {"score": 0.5, "start_time": 90, "end_time": 120, "type": "scene_based"}
        ]
        
        selected = await selector.rank_clips(clips, top_k=2)
        
        assert len(selected) == 2
        assert selected[0]["score"] >= selected[1]["score"]
        assert all("selection_score" in clip for clip in selected)
        assert all("selection_reasons" in clip for clip in selected)
    
    @pytest.mark.asyncio
    async def test_hook_writer_generation(self):
        """Test hook and metadata generation"""
        writer = HookWriterAgent()
        await writer.initialize()
        
        clip_data = {
            "clip": {"score": 0.85, "type": "transformation"},
            "metadata": {"title": "Amazing Workout Results"}
        }
        
        result = await writer.execute("generate", clip_data)
        
        assert "title" in result
        assert "description" in result
        assert "hashtags" in result
        assert len(result["hashtags"]) <= 10
        assert "hook_type" in result
    
    @pytest.mark.asyncio
    async def test_engagement_prediction(self):
        """Test engagement prediction"""
        predictor = EngagementPredictorAgent()
        await predictor.initialize()
        
        metadata = {
            "title": "30-Day Transformation",
            "hashtags": ["fitness", "transformation", "gym"],
            "hook_type": "shocking_reveal"
        }
        
        prediction = await predictor.execute("predict", {"metadata": metadata})
        
        assert "predicted_views" in prediction
        assert "predicted_likes" in prediction
        assert "engagement_rate" in prediction
        assert "best_time" in prediction
        assert prediction["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_agent_system_integration(self):
        """Test full agent system integration"""
        system = AIAgentSystem()
        await system.initialize()
        
        # Test viral analysis task
        viral_result = await system.execute_task("viral_analysis", {
            "content": {"platform": "tiktok", "metadata": {"views": 1000000}}
        })
        assert "score" in viral_result
        
        # Test clip selection task
        clip_result = await system.execute_task("clip_selection", {
            "clips": [{"score": 0.8}, {"score": 0.6}]
        })
        assert "selected" in clip_result
        
        # Test hook generation task
        hook_result = await system.execute_task("hook_generation", {
            "clip": {"score": 0.9},
            "metadata": {"title": "Test"}
        })
        assert "title" in hook_result
        
        # Test engagement prediction task
        prediction_result = await system.execute_task("engagement_prediction", {
            "metadata": {"title": "Test", "hashtags": ["fitness"]}
        })
        assert "predicted_views" in prediction_result
    
    @pytest.mark.asyncio
    async def test_pattern_learning(self):
        """Test pattern learning functionality"""
        system = AIAgentSystem()
        
        performance_data = {
            "views": {"first_hour_views": 15000, "growth_rate": 2.5},
            "engagement": {"rate": 0.18, "comment_ratio": 0.06},
            "content_features": {"hook_strength": 0.9, "duration": 25}
        }
        
        patterns = await system.identify_patterns(performance_data)
        
        assert len(patterns) > 0
        assert all("type" in p for p in patterns)
        assert all("confidence" in p for p in patterns)