"""
Clip Selector Agent - Selects best clips based on viral potential
Uses ML to rank and select optimal clips
"""

import asyncio
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ClipSelectorAgent:
    """AI agent that selects the best clips from analyzed videos"""
    
    def __init__(self):
        self.selection_criteria = {
            "hook_strength": 0.3,
            "viral_potential": 0.25,
            "energy_level": 0.2,
            "visual_quality": 0.15,
            "trend_alignment": 0.1
        }
        
    async def initialize(self):
        """Initialize the clip selector agent"""
        logger.info("Initializing Clip Selector Agent")
        return True
        
    async def rank_clips(self, clips: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank clips and return top K selections"""
        # Score each clip
        scored_clips = []
        
        for clip in clips:
            score = await self._score_clip(clip)
            clip["selection_score"] = score
            clip["selection_reasons"] = self._get_selection_reasons(clip)
            scored_clips.append(clip)
            
        # Sort by score and return top K
        scored_clips.sort(key=lambda x: x["selection_score"], reverse=True)
        
        selected = scored_clips[:top_k]
        logger.info(f"Selected {len(selected)} clips from {len(clips)} candidates")
        
        return selected
        
    async def _score_clip(self, clip: Dict[str, Any]) -> float:
        """Score a single clip based on multiple criteria"""
        score = 0.0
        
        # Base score from clip analysis
        base_score = clip.get("score", 0.5)
        score += base_score * 0.3
        
        # Clip type scoring
        if clip.get("type") == "energy_peak":
            score += 0.2
        elif clip.get("type") == "scene_based":
            score += 0.1
            
        # Duration scoring (optimal: 15-30 seconds)
        duration = clip.get("end_time", 0) - clip.get("start_time", 0)
        if 15 <= duration <= 30:
            score += 0.25
        elif 30 < duration <= 45:
            score += 0.15
        elif 45 < duration <= 60:
            score += 0.1
            
        # Hook timing (clips starting within first 10 seconds get bonus)
        if clip.get("start_time", 0) < 10:
            score += 0.15
            
        # Ensure score is between 0 and 1
        return min(max(score, 0.0), 1.0)
        
    def _get_selection_reasons(self, clip: Dict[str, Any]) -> List[str]:
        """Generate human-readable selection reasons"""
        reasons = []
        
        if clip.get("type") == "energy_peak":
            reasons.append("High energy moment detected")
            
        duration = clip.get("end_time", 0) - clip.get("start_time", 0)
        if 15 <= duration <= 30:
            reasons.append("Optimal duration for engagement")
            
        if clip.get("start_time", 0) < 10:
            reasons.append("Strong hook potential")
            
        if clip.get("score", 0) > 0.8:
            reasons.append("Exceptional viral indicators")
            
        return reasons
        
    async def update_patterns(self, new_patterns: List[Dict[str, Any]]):
        """Update selection patterns based on performance data"""
        logger.info(f"Updating selection patterns with {len(new_patterns)} new patterns")
        
        # Adjust criteria weights based on successful patterns
        for pattern in new_patterns:
            if pattern.get("type") == "content" and pattern.get("confidence", 0) > 0.8:
                features = pattern.get("features", {})
                # Update selection criteria based on successful features
                if "hook_strength" in features:
                    self.selection_criteria["hook_strength"] = min(
                        self.selection_criteria["hook_strength"] * 1.1, 0.4
                    )