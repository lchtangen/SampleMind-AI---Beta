"""
Unit tests for Rate Limiting Middleware

Tests the rate limiting functionality including:
- Sliding window algorithm
- Per-IP and per-user tracking
- Tiered rate limits
- Redis operations
- Metrics collection
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
import redis

# Use try/except for flexible imports
try:
    from samplemind.middleware.rate_limiter import (
        RateLimitMiddleware,
        RateLimitTier,
        RateLimitConfig,
        RateLimitRules,
        SlidingWindowCounter,
        create_rate_limiter,
        rate_limit,
    )
except ImportError:
    import sys
    import os
    # Add src to path for direct execution
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    from samplemind.middleware.rate_limiter import (
        RateLimitMiddleware,
        RateLimitTier,
        RateLimitConfig,
        RateLimitRules,
        SlidingWindowCounter,
        create_rate_limiter,
        rate_limit,
    )


# ====================
# Fixtures
# ====================

@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    mock = MagicMock(spec=redis.Redis)
    mock.pipeline.return_value = mock
    mock.zremrangebyscore.return_value = None
    mock.zcard.return_value = 0
    mock.zadd.return_value = 1
    mock.expire.return_value = True
    mock.execute.return_value = [None, 0, 1, True]
    mock.zrange.return_value = []
    mock.delete.return_value = 1
    mock.ping.return_value = True
    return mock


@pytest.fixture
def sliding_window_counter(mock_redis):
    """Create SlidingWindowCounter instance"""
    return SlidingWindowCounter(mock_redis)


@pytest.fixture
def app_with_rate_limiter(mock_redis):
    """Create FastAPI app with rate limiter"""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    @app.get("/api/v1/analyze")
    async def analyze_endpoint():
        return {"message": "analysis complete"}
    
    # Add rate limit middleware
    app.add_middleware(
        RateLimitMiddleware,
        redis_client=mock_redis,
        enabled=True
    )
    
    return app


@pytest.fixture
def test_client(app_with_rate_limiter):
    """Create test client"""
    return TestClient(app_with_rate_limiter)


# ====================
# RateLimitConfig Tests
# ====================

class TestRateLimitConfig:
    """Test RateLimitConfig dataclass"""
    
    def test_config_creation(self):
        """Test creating rate limit configuration"""
        config = RateLimitConfig(requests=10, window=60)
        assert config.requests == 10
        assert config.window == 60
    
    def test_config_string_representation(self):
        """Test string representation"""
        config = RateLimitConfig(requests=100, window=3600)
        assert str(config) == "100 requests per 3600s"


# ====================
# RateLimitRules Tests
# ====================

class TestRateLimitRules:
    """Test rate limit rules"""
    
    def test_get_endpoint_limit(self):
        """Test getting limit for specific endpoint"""
        limit = RateLimitRules.get_limit("/api/v1/analyze", RateLimitTier.FREE)
        assert limit.requests == 10
        assert limit.window == 60
    
    def test_get_pro_tier_limit(self):
        """Test Pro tier has higher limits"""
        free_limit = RateLimitRules.get_limit("/api/v1/analyze", RateLimitTier.FREE)
        pro_limit = RateLimitRules.get_limit("/api/v1/analyze", RateLimitTier.PRO)
        assert pro_limit.requests > free_limit.requests
    
    def test_get_default_limit(self):
        """Test default limit for unknown endpoint"""
        limit = RateLimitRules.get_limit("/api/v1/unknown", RateLimitTier.FREE)
        assert limit == RateLimitRules.DEFAULT_LIMITS[RateLimitTier.FREE]
    
    def test_prefix_match(self):
        """Test endpoint prefix matching"""
        # Should match /api/v1/upload prefix
        limit = RateLimitRules.get_limit("/api/v1/upload/file", RateLimitTier.FREE)
        expected = RateLimitRules.ENDPOINT_LIMITS["/api/v1/upload"][RateLimitTier.FREE]
        assert limit.requests == expected.requests


# ====================
# SlidingWindowCounter Tests
# ====================

class TestSlidingWindowCounter:
    """Test sliding window counter implementation"""
    
    def test_check_rate_limit_allowed(self, sliding_window_counter, mock_redis):
        """Test request is allowed within limit"""
        # Mock Redis to return count less than limit
        mock_redis.execute.return_value = [None, 5, 1, True]
        
        allowed, count, retry_after = sliding_window_counter.check_rate_limit(
            identifier="user:123",
            endpoint="/api/v1/test",
            limit=10,
            window=60
        )
        
        assert allowed is True
        assert count == 6  # Current count + 1
        assert retry_after == 0
    
    def test_check_rate_limit_exceeded(self, sliding_window_counter, mock_redis):
        """Test request is blocked when limit exceeded"""
        # Mock Redis to return count at limit
        mock_redis.execute.return_value = [None, 10, 1, True]
        mock_redis.zrange.return_value = [(b"1234567890.123", 1234567890.123)]
        
        allowed, count, retry_after = sliding_window_counter.check_rate_limit(
            identifier="user:123",
            endpoint="/api/v1/test",
            limit=10,
            window=60
        )
        
        assert allowed is False
        assert count == 10
        assert retry_after > 0
    
    def test_redis_key_generation(self, sliding_window_counter):
        """Test Redis key generation"""
        key = sliding_window_counter._get_key("user:123", "/api/v1/test")
        assert key == "ratelimit:user:123:/api/v1/test"
    
    def test_get_current_usage(self, sliding_window_counter, mock_redis):
        """Test getting current usage count"""
        mock_redis.zcard.return_value = 5
        
        count = sliding_window_counter.get_current_usage(
            identifier="user:123",
            endpoint="/api/v1/test",
            window=60
        )
        
        assert count == 5
        mock_redis.zremrangebyscore.assert_called_once()
    
    def test_reset_limit(self, sliding_window_counter, mock_redis):
        """Test resetting rate limit"""
        result = sliding_window_counter.reset_limit("user:123", "/api/v1/test")
        
        assert result is True
        mock_redis.delete.assert_called_once()
    
    def test_redis_error_handling(self, sliding_window_counter, mock_redis):
        """Test graceful handling of Redis errors"""
        mock_redis.execute.side_effect = redis.RedisError("Connection failed")
        
        # Should fail open (allow request)
        allowed, count, retry_after = sliding_window_counter.check_rate_limit(
            identifier="user:123",
            endpoint="/api/v1/test",
            limit=10,
            window=60
        )
        
        assert allowed is True
        assert count == 0
        assert retry_after == 0


# ====================
# RateLimitMiddleware Tests
# ====================

class TestRateLimitMiddleware:
    """Test rate limit middleware"""
    
    def test_request_allowed(self, test_client, mock_redis):
        """Test request is allowed when under limit"""
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        response = test_client.get("/test")
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_request_blocked(self, test_client, mock_redis):
        """Test request is blocked when limit exceeded"""
        # Mock rate limit exceeded
        mock_redis.execute.return_value = [None, 100, 1, True]
        
        response = test_client.get("/test")
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        data = response.json()
        assert "error" in data
        assert "Rate limit exceeded" in data["error"]
    
    def test_skip_health_endpoints(self, test_client, mock_redis):
        """Test health endpoints skip rate limiting"""
        # Create app with health endpoint
        app = FastAPI()
        
        @app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=mock_redis,
            enabled=True
        )
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        # Redis should not be called for health check
        mock_redis.pipeline.assert_not_called()
    
    def test_disabled_rate_limiting(self, mock_redis):
        """Test middleware can be disabled"""
        app = FastAPI()
        
        @app.get("/test")
        async def test():
            return {"message": "success"}
        
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=mock_redis,
            enabled=False
        )
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        # Redis should not be called when disabled
        mock_redis.pipeline.assert_not_called()
    
    def test_identifier_from_user(self, mock_redis):
        """Test identifier extraction from authenticated user"""
        app = FastAPI()
        
        @app.get("/test")
        async def test(request: Request):
            # Simulate authenticated user
            request.state.user = Mock(id="user123", tier="pro")
            return {"message": "success"}
        
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=mock_redis,
            enabled=True
        )
        
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
    
    def test_identifier_from_api_key(self, test_client, mock_redis):
        """Test identifier extraction from API key"""
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        response = test_client.get(
            "/test",
            headers={"X-API-Key": "test_api_key_12345"}
        )
        
        assert response.status_code == 200
    
    def test_identifier_from_ip(self, test_client, mock_redis):
        """Test identifier extraction from IP address"""
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        response = test_client.get("/test")
        
        assert response.status_code == 200
        # Should fall back to IP-based identification
    
    def test_endpoint_normalization(self, mock_redis):
        """Test endpoint path normalization"""
        middleware = RateLimitMiddleware(
            app=Mock(),
            redis_client=mock_redis,
            enabled=True
        )
        
        # Test UUID replacement
        normalized = middleware._normalize_endpoint("/api/v1/users/123e4567-e89b-12d3-a456-426614174000")
        assert normalized == "/api/v1/users/{id}"
        
        # Test numeric ID replacement
        normalized = middleware._normalize_endpoint("/api/v1/files/12345")
        assert normalized == "/api/v1/files/{id}"


# ====================
# Helper Function Tests
# ====================

class TestHelperFunctions:
    """Test helper functions"""
    
    def test_create_rate_limiter_success(self):
        """Test creating rate limiter with valid Redis"""
        with patch('redis.from_url') as mock_redis_from_url:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis_from_url.return_value = mock_client
            
            factory = create_rate_limiter("redis://localhost:6379/0")
            
            assert callable(factory)
            mock_redis_from_url.assert_called_once()
    
    def test_create_rate_limiter_failure(self):
        """Test creating rate limiter with invalid Redis"""
        with patch('redis.from_url') as mock_redis_from_url:
            mock_redis_from_url.side_effect = Exception("Connection failed")
            
            factory = create_rate_limiter("redis://invalid:6379/0")
            
            assert callable(factory)
            # Should create disabled middleware on failure
    
    def test_rate_limit_decorator(self):
        """Test rate limit decorator"""
        @rate_limit(requests=5, window=300)
        async def test_function():
            return "success"
        
        assert hasattr(test_function, "_rate_limit")
        assert test_function._rate_limit.requests == 5  # type: ignore
        assert test_function._rate_limit.window == 300  # type: ignore


# ====================
# Integration Tests
# ====================

class TestRateLimitIntegration:
    """Integration tests for complete rate limiting flow"""
    
    def test_multiple_requests_within_limit(self, test_client, mock_redis):
        """Test multiple requests stay within limit"""
        # Simulate increasing count
        counts = [0, 1, 2, 3, 4]
        mock_redis.execute.side_effect = [
            [None, count, 1, True] for count in counts
        ]
        
        for i in range(5):
            response = test_client.get("/test")
            assert response.status_code == 200
            remaining = int(response.headers["X-RateLimit-Remaining"])
            assert remaining > 0
    
    def test_tier_based_limits(self, mock_redis):
        """Test different limits for different tiers"""
        app = FastAPI()
        
        @app.get("/api/v1/analyze")
        async def analyze(request: Request):
            # Will be set by test
            return {"message": "success"}
        
        app.add_middleware(
            RateLimitMiddleware,
            redis_client=mock_redis,
            enabled=True
        )
        
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        client = TestClient(app)
        response = client.get("/api/v1/analyze")
        
        assert response.status_code == 200
        # Free tier should have limit of 10
        assert int(response.headers["X-RateLimit-Limit"]) == 10


# ====================
# Performance Tests
# ====================

class TestRateLimitPerformance:
    """Test rate limiter performance"""
    
    def test_check_rate_limit_performance(self, sliding_window_counter, mock_redis):
        """Test rate limit check completes quickly"""
        mock_redis.execute.return_value = [None, 5, 1, True]
        
        start = time.time()
        for _ in range(100):
            sliding_window_counter.check_rate_limit(
                identifier="user:123",
                endpoint="/api/v1/test",
                limit=10,
                window=60
            )
        duration = time.time() - start
        
        # Should complete 100 checks in less than 1 second
        assert duration < 1.0
    
    def test_middleware_overhead(self, test_client, mock_redis):
        """Test middleware adds minimal overhead"""
        mock_redis.execute.return_value = [None, 0, 1, True]
        
        start = time.time()
        for _ in range(50):
            response = test_client.get("/test")
            assert response.status_code == 200
        duration = time.time() - start
        
        # Should handle 50 requests quickly
        assert duration < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])