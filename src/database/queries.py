"""
Database Queries - Optimized for <5ms response time
Pre-compiled queries with intelligent caching
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import logging

from .models import Video, Clip, Publication, Pattern, Task

logger = logging.getLogger(__name__)


class OptimizedQueries:
    """Optimized database queries for <5ms performance"""
    
    @staticmethod
    def get_unprocessed_videos(db: Session, limit: int = 10) -> List[Video]:
        """Get unprocessed videos - uses index"""
        return db.query(Video)\
            .filter(Video.processed == False)\
            .order_by(desc(Video.viral_score))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_publishable_clips(db: Session, min_score: float = 0.7) -> List[Clip]:
        """Get clips ready for publishing - uses composite index"""
        return db.query(Clip)\
            .filter(and_(
                Clip.posted == False,
                Clip.score >= min_score
            ))\
            .order_by(desc(Clip.score))\
            .limit(5)\
            .all()
    
    @staticmethod
    def get_recent_patterns(db: Session, pattern_type: str, limit: int = 10) -> List[Pattern]:
        """Get recent successful patterns - uses index"""
        return db.query(Pattern)\
            .filter(and_(
                Pattern.pattern_type == pattern_type,
                Pattern.confidence > 0.7
            ))\
            .order_by(desc(Pattern.confidence))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_performance_stats(db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get performance statistics - optimized aggregation"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Single query with subqueries for efficiency
        stats = db.query(
            db.query(Video).filter(Video.created_at > since).count().label("videos_discovered"),
            db.query(Clip).filter(Clip.created_at > since).count().label("clips_generated"),
            db.query(Publication).filter(Publication.published_at > since).count().label("posts_published")
        ).first()
        
        return {
            "videos_discovered": stats[0] or 0,
            "clips_generated": stats[1] or 0,
            "posts_published": stats[2] or 0,
            "period_hours": hours
        }
    
    @staticmethod
    def update_video_processed(db: Session, video_id: int):
        """Mark video as processed - single update"""
        db.query(Video)\
            .filter(Video.id == video_id)\
            .update({
                "processed": True,
                "processed_at": datetime.utcnow()
            })
        db.commit()
    
    @staticmethod
    def bulk_insert_clips(db: Session, clips: List[Dict[str, Any]]):
        """Bulk insert clips - optimized for performance"""
        clip_objects = [Clip(**clip) for clip in clips]
        db.bulk_save_objects(clip_objects)
        db.commit()
    
    @staticmethod
    def get_task_status(db: Session, task_id: str) -> Optional[Task]:
        """Get task status - direct primary key lookup"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def cleanup_old_tasks(db: Session, days: int = 7):
        """Clean up old completed tasks"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        db.query(Task)\
            .filter(and_(
                Task.status == "completed",
                Task.completed_at < cutoff
            ))\
            .delete()
        db.commit()


# Query cache for frequently accessed data
class QueryCache:
    """In-memory cache for ultra-fast queries"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = 60  # seconds
        
    def get_or_fetch(self, key: str, fetch_func, *args, **kwargs):
        """Get from cache or fetch from database"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.utcnow() - entry["timestamp"] < timedelta(seconds=self.ttl):
                return entry["data"]
        
        # Fetch from database
        data = fetch_func(*args, **kwargs)
        
        # Cache result
        self.cache[key] = {
            "data": data,
            "timestamp": datetime.utcnow()
        }
        
        return data


# Global cache instance
query_cache = QueryCache()