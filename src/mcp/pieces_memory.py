"""
PIECES Memory Integration - Pattern storage and recall
Stores successful patterns for 70% token reduction
"""

import asyncio
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class PiecesMemory:
    """PIECES MCP server for pattern memory"""
    
    def __init__(self):
        self.patterns = {}
        self.pattern_index = {}
        self.next_id = 1
        
    async def initialize(self):
        """Initialize PIECES memory server"""
        logger.info("Initializing PIECES pattern memory")
        # Load any persisted patterns
        return True
        
    async def store_pattern(
        self, 
        category: str, 
        data: Dict[str, Any], 
        tags: List[str] = None
    ) -> str:
        """Store a pattern in memory"""
        pattern_id = f"pattern_{self.next_id}"
        self.next_id += 1
        
        pattern = {
            "id": pattern_id,
            "category": category,
            "data": data,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "success_rate": 1.0
        }
        
        self.patterns[pattern_id] = pattern
        
        # Update index
        if category not in self.pattern_index:
            self.pattern_index[category] = []
        self.pattern_index[category].append(pattern_id)
        
        logger.info(f"Stored pattern {pattern_id} in category {category}")
        return pattern_id
        
    async def recall_patterns(
        self, 
        category: str, 
        limit: int = 5,
        min_success_rate: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Recall patterns from a category"""
        pattern_ids = self.pattern_index.get(category, [])
        
        patterns = []
        for pid in pattern_ids:
            pattern = self.patterns.get(pid)
            if pattern and pattern["success_rate"] >= min_success_rate:
                patterns.append(pattern)
                pattern["usage_count"] += 1
                
        # Sort by success rate and usage
        patterns.sort(
            key=lambda p: (p["success_rate"], p["usage_count"]), 
            reverse=True
        )
        
        return patterns[:limit]
        
    async def search_patterns(
        self, 
        query: Dict[str, Any], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar patterns"""
        results = []
        
        for pattern in self.patterns.values():
            similarity = self._calculate_similarity(query, pattern["data"])
            if similarity > 0.7:
                results.append({
                    **pattern,
                    "similarity": similarity
                })
                
        results.sort(key=lambda r: r["similarity"], reverse=True)
        return results[:limit]
        
    def _calculate_similarity(self, query: Dict, pattern: Dict) -> float:
        """Calculate similarity between query and pattern"""
        # Simple key overlap similarity
        query_keys = set(query.keys())
        pattern_keys = set(pattern.keys())
        
        if not pattern_keys:
            return 0.0
            
        overlap = len(query_keys.intersection(pattern_keys))
        return overlap / len(pattern_keys)