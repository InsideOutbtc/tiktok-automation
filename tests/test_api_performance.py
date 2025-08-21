"""
API Performance Tests
Benchmark API endpoints for <22ms response time
"""

import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
import statistics

from src.api.rest_api import app


class TestAPIPerformance:
    """Test API performance standards"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.mark.benchmark
    def test_health_endpoint_performance(self, client, benchmark):
        """Benchmark health endpoint <22ms"""
        def make_request():
            return client.get("/api/v1/health")
        
        result = benchmark(make_request)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.022  # 22ms
    
    @pytest.mark.benchmark
    def test_discovery_endpoint_performance(self, client, benchmark):
        """Benchmark discovery endpoint <22ms"""
        def make_request():
            return client.post("/api/v1/discover", json={
                "platforms": ["tiktok"],
                "keywords": ["fitness"],
                "limit": 10
            })
        
        result = benchmark(make_request)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.022
    
    @pytest.mark.benchmark
    def test_prediction_endpoint_performance(self, client, benchmark):
        """Benchmark prediction endpoint <22ms (cached)"""
        # Warm up cache
        client.post("/api/v1/agent/predict", json={
            "clip_metadata": {"score": 0.8, "duration": 30}
        })
        
        def make_request():
            return client.post("/api/v1/agent/predict", json={
                "clip_metadata": {"score": 0.8, "duration": 30}
            })
        
        result = benchmark(make_request)
        assert result.status_code == 200
        assert benchmark.stats["mean"] < 0.022
    
    def test_concurrent_requests(self, client):
        """Test API under concurrent load"""
        def make_request():
            start = time.time()
            response = client.get("/api/v1/health")
            duration = (time.time() - start) * 1000
            return duration, response.status_code
        
        # Make 100 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [f.result() for f in futures]
        
        durations = [r[0] for r in results]
        status_codes = [r[1] for r in results]
        
        # All requests should succeed
        assert all(code == 200 for code in status_codes)
        
        # 95th percentile should be under 50ms even under load
        p95 = statistics.quantiles(durations, n=20)[18]  # 95th percentile
        assert p95 < 50
    
    def test_response_headers(self, client):
        """Test response time headers"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/metrics",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "X-Response-Time" in response.headers
            
            # Parse response time from header
            response_time = float(response.headers["X-Response-Time"].replace("ms", ""))
            assert response_time < 22
    
    @pytest.mark.asyncio
    async def test_background_task_performance(self, client):
        """Test background task queuing performance"""
        start = time.time()
        
        response = client.post("/api/v1/process/clip", json={
            "video_url": "https://example.com/video.mp4",
            "extract_clips": True,
            "apply_effects": True
        })
        
        duration = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert "task_id" in response.json()
        assert duration < 22  # Should return immediately
    
    def test_cache_effectiveness(self, client):
        """Test cache hit rate for repeated requests"""
        # First request - cache miss
        response1 = client.post("/api/v1/agent/predict", json={
            "clip_metadata": {"test": "data"}
        })
        assert response1.headers.get("X-Cache") == "MISS"
        
        # Second request - cache hit
        response2 = client.post("/api/v1/agent/predict", json={
            "clip_metadata": {"test": "data"}
        })
        assert response2.headers.get("X-Cache") == "HIT"
        
        # Response time should be faster for cached request
        time1 = float(response1.headers["X-Response-Time"].replace("ms", ""))
        time2 = float(response2.headers["X-Response-Time"].replace("ms", ""))
        assert time2 < time1