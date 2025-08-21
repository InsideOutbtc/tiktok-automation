"""
AI Utilities - Helper functions for AI operations
Pattern matching and optimization utilities
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AIUtils:
    """AI and ML utility functions"""
    
    @staticmethod
    def calculate_similarity(pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns"""
        # Extract common features
        common_keys = set(pattern1.keys()) & set(pattern2.keys())
        
        if not common_keys:
            return 0.0
        
        # Calculate feature similarity
        similarities = []
        for key in common_keys:
            val1 = pattern1[key]
            val2 = pattern2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric similarity
                max_val = max(abs(val1), abs(val2))
                if max_val == 0:
                    sim = 1.0
                else:
                    sim = 1 - abs(val1 - val2) / max_val
                similarities.append(sim)
            elif val1 == val2:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return sum(similarities) / len(similarities)
    
    @staticmethod
    def rank_by_score(items: List[Dict[str, Any]], score_key: str = "score") -> List[Dict[str, Any]]:
        """Rank items by score with tie-breaking"""
        # Sort by score, then by additional criteria
        return sorted(
            items,
            key=lambda x: (
                x.get(score_key, 0),
                x.get("confidence", 0),
                -len(str(x))  # Prefer simpler items as tie-breaker
            ),
            reverse=True
        )
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return list(set(keywords))[:10]  # Return top 10 unique keywords
    
    @staticmethod
    def calculate_engagement_score(metrics: Dict[str, int]) -> float:
        """Calculate engagement score from metrics"""
        views = metrics.get("views", 0)
        likes = metrics.get("likes", 0)
        comments = metrics.get("comments", 0)
        shares = metrics.get("shares", 0)
        
        if views == 0:
            return 0.0
        
        # Weighted engagement formula
        engagement = (
            (likes * 1.0) +
            (comments * 2.0) +
            (shares * 3.0)
        ) / views
        
        # Normalize to 0-1 range
        return min(engagement * 10, 1.0)
    
    @staticmethod
    def predict_best_time(historical_data: List[Dict[str, Any]]) -> str:
        """Predict best posting time based on historical data"""
        if not historical_data:
            return "18:00"  # Default to 6 PM
        
        # Analyze performance by hour
        hour_performance = {}
        
        for post in historical_data:
            hour = post.get("published_at", datetime.now()).hour
            score = post.get("engagement_score", 0)
            
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(score)
        
        # Calculate average performance by hour
        best_hour = 18  # Default
        best_score = 0
        
        for hour, scores in hour_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_hour = hour
        
        return f"{best_hour:02d}:00"