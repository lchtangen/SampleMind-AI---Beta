"""
Rate limiting tests
"""

import pytest
from collections import defaultdict
from datetime import datetime, timedelta
from app.middleware.rate_limiter import RateLimiter


def test_rate_limiter_init():
    """Test rate limiter initialization"""
    limiter = RateLimiter(None, per_minute=60, per_hour=1000)
    assert limiter.per_minute == 60
    assert limiter.per_hour == 1000
    assert isinstance(limiter.requests, defaultdict)


def test_check_rate_limit_within_limits():
    """Test rate limit check when within limits"""
    limiter = RateLimiter(None, per_minute=5, per_hour=10)
    
    # First request should be allowed
    allowed, headers = limiter.check_rate_limit("test_user")
    assert allowed is True
    assert "X-RateLimit-Remaining-Minute" in headers


def test_check_rate_limit_exceeds_minute():
    """Test rate limit when exceeding per-minute limit"""
    limiter = RateLimiter(None, per_minute=2, per_hour=10)
    
    # Make requests up to limit
    for i in range(2):
        limiter.record_request("test_user")
    
    # Next request should be denied
    allowed, headers = limiter.check_rate_limit("test_user")
    assert allowed is False


def test_check_rate_limit_exceeds_hour():
    """Test rate limit when exceeding per-hour limit"""
    limiter = RateLimiter(None, per_minute=100, per_hour=2)
    
    # Make requests up to hour limit
    for i in range(2):
        limiter.record_request("test_user")
    
    # Next request should be denied
    allowed, headers = limiter.check_rate_limit("test_user")
    assert allowed is False


def test_rate_limit_headers():
    """Test rate limit response headers"""
    limiter = RateLimiter(None, per_minute=60, per_hour=1000)
    
    allowed, headers = limiter.check_rate_limit("test_user")
    
    assert "X-RateLimit-Limit-Minute" in headers
    assert "X-RateLimit-Limit-Hour" in headers
    assert "X-RateLimit-Remaining-Minute" in headers
    assert "X-RateLimit-Remaining-Hour" in headers
    assert "X-RateLimit-Reset" in headers
    
    assert headers["X-RateLimit-Limit-Minute"] == "60"
    assert headers["X-RateLimit-Limit-Hour"] == "1000"


def test_rate_limit_per_user():
    """Test rate limits are per user/IP"""
    limiter = RateLimiter(None, per_minute=2, per_hour=10)
    
    # User 1 makes requests
    limiter.record_request("user1")
    limiter.record_request("user1")
    
    # User 1 should be at limit
    allowed1, _ = limiter.check_rate_limit("user1")
    assert allowed1 is False
    
    # User 2 should still be allowed
    allowed2, _ = limiter.check_rate_limit("user2")
    assert allowed2 is True


def test_record_request():
    """Test recording a request"""
    limiter = RateLimiter(None, per_minute=60, per_hour=1000)
    
    # Record a request
    limiter.record_request("test_user")
    
    # Check that it was recorded
    assert "test_user" in limiter.requests
    assert len(limiter.requests["test_user"]) == 1
