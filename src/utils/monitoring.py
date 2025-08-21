"""
Monitoring - System metrics collection
Tracks Constitutional AI compliance
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import time
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and tracks system metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.response_times = deque(maxlen=1000)  # Last 1000 requests
        self.start_time = datetime.utcnow()
        
    def record_api_response(self, endpoint: str, response_time_ms: float):
        """Record API response time"""
        self.response_times.append(response_time_ms)
        self.metrics[f"api_{endpoint}"].append({
            "time": response_time_ms,
            "timestamp": datetime.utcnow()
        })
        
        # Log if exceeds Constitutional AI standard
        if response_time_ms > 22:
            logger.warning(f"API response exceeded 22ms: {endpoint} took {response_time_ms}ms")
    
    def record_db_query(self, query_type: str, query_time_ms: float):
        """Record database query time"""
        self.metrics[f"db_{query_type}"].append({
            "time": query_time_ms,
            "timestamp": datetime.utcnow()
        })
        
        # Log if exceeds standard
        if query_time_ms > 5:
            logger.warning(f"DB query exceeded 5ms: {query_type} took {query_time_ms}ms")
    
    def record_video_processing(self, duration_seconds: float, clips_generated: int):
        """Record video processing metrics"""
        self.metrics["video_processing"].append({
            "duration": duration_seconds,
            "clips": clips_generated,
            "timestamp": datetime.utcnow()
        })
    
    def record_error(self, error_type: str, tier: int, recovered: bool):
        """Record error and recovery"""
        self.metrics["errors"].append({
            "type": error_type,
            "tier": tier,
            "recovered": recovered,
            "timestamp": datetime.utcnow()
        })
    
    def get_average_response_time(self) -> float:
        """Get average API response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_constitutional_compliance(self) -> Dict[str, Any]:
        """Check Constitutional AI compliance"""
        avg_api = self.get_average_response_time()
        
        # Get recent DB query times
        recent_db_times = []
        for key, values in self.metrics.items():
            if key.startswith("db_"):
                recent = [v["time"] for v in values[-100:]]
                recent_db_times.extend(recent)
        
        avg_db = sum(recent_db_times) / len(recent_db_times) if recent_db_times else 0
        
        # Calculate error recovery rate
        errors = self.metrics.get("errors", [])
        if errors:
            recovered = sum(1 for e in errors if e["recovered"])
            recovery_rate = recovered / len(errors)
        else:
            recovery_rate = 1.0
        
        return {
            "api_response_avg": avg_api,
            "api_compliant": avg_api <= 22,
            "db_query_avg": avg_db,
            "db_compliant": avg_db <= 5,
            "error_recovery_rate": recovery_rate,
            "error_compliant": recovery_rate >= 0.95,
            "overall_compliant": avg_api <= 22 and avg_db <= 5 and recovery_rate >= 0.95
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        uptime = datetime.utcnow() - self.start_time
        
        return {
            "uptime_hours": uptime.total_seconds() / 3600,
            "total_api_requests": len(self.response_times),
            "videos_processed": len(self.metrics.get("video_processing", [])),
            "total_errors": len(self.metrics.get("errors", [])),
            "constitutional_compliance": self.get_constitutional_compliance()
        }
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # API metrics
        lines.append(f"# HELP api_response_time_ms API response time in milliseconds")
        lines.append(f"# TYPE api_response_time_ms gauge")
        lines.append(f"api_response_time_ms {self.get_average_response_time():.2f}")
        
        # Compliance metrics
        compliance = self.get_constitutional_compliance()
        lines.append(f"# HELP constitutional_compliance Constitutional AI compliance status")
        lines.append(f"# TYPE constitutional_compliance gauge")
        lines.append(f"constitutional_compliance {1 if compliance['overall_compliant'] else 0}")
        
        return "\n".join(lines)


# Performance decorator
def track_performance(metric_type: str):
    """Decorator to track function performance"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # Convert to ms
            
            # Record metric
            if hasattr(args[0], 'metrics'):
                if metric_type == "api":
                    args[0].metrics.record_api_response(func.__name__, duration)
                elif metric_type == "db":
                    args[0].metrics.record_db_query(func.__name__, duration)
                    
            return result
        return wrapper
    return decorator