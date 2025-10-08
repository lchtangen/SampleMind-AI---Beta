"""
Rate Limiting Middleware for SampleMind AI
Protects API endpoints from abuse with per-endpoint, per-IP, and per-user limits

Features:
- Sliding window algorithm for accurate rate limiting
- Per-IP and per-user tracking
- Tiered limits (Free/Pro/Enterprise)
- Redis-backed storage for distributed systems
- Prometheus metrics integration
- Clear error responses with retry information
"""

import logging
import time
from typing import Optional, Dict, Callable, Tuple
from enum import Enum
from dataclasses import dataclass

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import redis
from redis.exceptions import RedisError

from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


# ====================
# Prometheus Metrics
# ====================

rate_limit_requests_total = Counter(
    "samplemind_rate_limit_requests_total",
    "Total rate limit checks",
    ["endpoint", "status"]
)

rate_limit_violations_total = Counter(
    "samplemind_rate_limit_violations_total",
    "Total rate limit violations",
    ["endpoint", "tier"]
)

rate_limit_check_duration_seconds = Histogram(
    "samplemind_rate_limit_check_duration_seconds",
    "Rate limit check duration",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1)
)

active_rate_limits = Gauge(
    "samplemind_active_rate_limits",
    "Number of active rate limit buckets",
    ["tier"]
)


# ====================
# Rate Limit Tiers
# ====================

class RateLimitTier(str, Enum):
    """User subscription tiers with different rate limits"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimitConfig:
    """Rate limit configuration for an endpoint"""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    
    def __str__(self) -> str:
        return f"{self.requests} requests per {self.window}s"


# ====================
# Rate Limit Definitions
# ====================

class RateLimitRules:
    """
    Define rate limits for different endpoints and tiers
    
    Format: {endpoint_pattern: {tier: RateLimitConfig}}
    """
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        "/api/v1/analyze": {
            RateLimitTier.FREE: RateLimitConfig(requests=10, window=60),
            RateLimitTier.PRO: RateLimitConfig(requests=100, window=60),
            RateLimitTier.ENTERPRISE: RateLimitConfig(requests=1000, window=60),
        },
        "/api/v1/upload": {
            RateLimitTier.FREE: RateLimitConfig(requests=5, window=60),
            RateLimitTier.PRO: RateLimitConfig(requests=50, window=60),
            RateLimitTier.ENTERPRISE: RateLimitConfig(requests=500, window=60),
        },
        "/api/v1/auth/login": {
            RateLimitTier.FREE: RateLimitConfig(requests=5, window=60),
            RateLimitTier.PRO: RateLimitConfig(requests=5, window=60),
            RateLimitTier.ENTERPRISE: RateLimitConfig(requests=10, window=60),
        },
        "/api/v1/auth/register": {
            RateLimitTier.FREE: RateLimitConfig(requests=3, window=3600),  # 3 per hour
            RateLimitTier.PRO: RateLimitConfig(requests=3, window=3600),
            RateLimitTier.ENTERPRISE: RateLimitConfig(requests=10, window=3600),
        },
    }
    
    # Default limits for unspecified endpoints
    DEFAULT_LIMITS = {
        RateLimitTier.FREE: RateLimitConfig(requests=100, window=60),
        RateLimitTier.PRO: RateLimitConfig(requests=1000, window=60),
        RateLimitTier.ENTERPRISE: RateLimitConfig(requests=10000, window=60),
    }
    
    @classmethod
    def get_limit(cls, endpoint: str, tier: RateLimitTier) -> RateLimitConfig:
        """Get rate limit configuration for endpoint and tier"""
        # Check exact match
        if endpoint in cls.ENDPOINT_LIMITS:
            return cls.ENDPOINT_LIMITS[endpoint][tier]
        
        # Check prefix match
        for pattern, limits in cls.ENDPOINT_LIMITS.items():
            if endpoint.startswith(pattern):
                return limits[tier]
        
        # Return default
        return cls.DEFAULT_LIMITS[tier]


# ====================
# Sliding Window Counter
# ====================

class SlidingWindowCounter:
    """
    Redis-backed sliding window rate limiter
    
    Uses Redis sorted sets for accurate sliding window counting.
    Each request is stored with its timestamp as the score.
    """
    
    def __init__(self, redis_client: redis.Redis, key_prefix: str = "ratelimit"):
        """
        Initialize sliding window counter
        
        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
    
    def _get_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for identifier and endpoint"""
        return f"{self.key_prefix}:{identifier}:{endpoint}"
    
    def check_rate_limit(
        self,
        identifier: str,
        endpoint: str,
        limit: int,
        window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit using sliding window
        
        Args:
            identifier: Unique identifier (IP or user ID)
            endpoint: API endpoint
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            Tuple of (allowed, current_count, retry_after_seconds)
        """
        start_time = time.time()
        key = self._get_key(identifier, endpoint)
        now = time.time()
        window_start = now - window
        
        try:
            # Pipeline operations for atomicity
            pipe = self.redis.pipeline()
            
            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            pipe.zcard(key)
            
            # Add current request with timestamp
            pipe.zadd(key, {str(now): now})
            
            # Set expiry on key
            pipe.expire(key, window + 10)  # Extra 10s buffer
            
            # Execute pipeline
            results = pipe.execute()
            current_count = results[1]  # Count before adding current request
            
            # Record metrics
            duration = time.time() - start_time
            rate_limit_check_duration_seconds.observe(duration)
            
            # Check if within limit
            if current_count < limit:
                rate_limit_requests_total.labels(endpoint=endpoint, status="allowed").inc()
                return True, current_count + 1, 0
            else:
                # Calculate retry-after
                # Get oldest request in window
                try:
                    oldest = self.redis.zrange(key, 0, 0, withscores=True)  # type: ignore
                    # Type cast for type checker
                    oldest_list = list(oldest) if oldest else []  # type: ignore
                    if oldest_list and len(oldest_list) > 0:
                        oldest_timestamp = float(oldest_list[0][1])
                        retry_after = int(window - (now - oldest_timestamp)) + 1
                    else:
                        retry_after = window
                except (IndexError, ValueError, TypeError):
                    retry_after = window
                
                rate_limit_requests_total.labels(endpoint=endpoint, status="blocked").inc()
                return False, current_count, retry_after
        
        except RedisError as e:
            logger.error(f"Redis error in rate limiting: {e}")
            # Fail open - allow request if Redis is down
            rate_limit_requests_total.labels(endpoint=endpoint, status="error").inc()
            return True, 0, 0
    
    def get_current_usage(self, identifier: str, endpoint: str, window: int) -> int:
        """Get current request count for identifier and endpoint"""
        key = self._get_key(identifier, endpoint)
        now = time.time()
        window_start = now - window
        
        try:
            # Remove old entries and count
            self.redis.zremrangebyscore(key, 0, window_start)
            count_result = self.redis.zcard(key)  # type: ignore
            # Type cast: zcard returns int
            return int(count_result) if count_result else 0  # type: ignore
        except (RedisError, ValueError, TypeError) as e:
            logger.error(f"Redis error getting usage: {e}")
            return 0
    
    def reset_limit(self, identifier: str, endpoint: str) -> bool:
        """Reset rate limit for identifier and endpoint"""
        key = self._get_key(identifier, endpoint)
        try:
            self.redis.delete(key)
            return True
        except RedisError as e:
            logger.error(f"Redis error resetting limit: {e}")
            return False


# ====================
# Rate Limit Middleware
# ====================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting
    
    Enforces per-endpoint, per-IP, and per-user rate limits with
    tiered subscription support.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        redis_client: redis.Redis,
        enabled: bool = True,
        key_prefix: str = "ratelimit"
    ):
        """
        Initialize rate limit middleware
        
        Args:
            app: FastAPI application
            redis_client: Redis client for rate limit storage
            enabled: Enable/disable rate limiting
            key_prefix: Redis key prefix
        """
        super().__init__(app)
        self.enabled = enabled
        self.counter = SlidingWindowCounter(redis_client, key_prefix)
        
        logger.info(f"RateLimitMiddleware initialized (enabled={enabled})")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce rate limits"""
        
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip certain paths
        path = request.url.path
        if self._should_skip_path(path):
            return await call_next(request)
        
        # Get identifier (IP or user ID)
        identifier = self._get_identifier(request)
        
        # Get user tier
        tier = self._get_user_tier(request)
        
        # Normalize endpoint for rate limiting
        endpoint = self._normalize_endpoint(path)
        
        # Get rate limit config
        limit_config = RateLimitRules.get_limit(endpoint, tier)
        
        # Check rate limit
        allowed, current_count, retry_after = self.counter.check_rate_limit(
            identifier=identifier,
            endpoint=endpoint,
            limit=limit_config.requests,
            window=limit_config.window
        )
        
        # Add rate limit headers to response
        headers = {
            "X-RateLimit-Limit": str(limit_config.requests),
            "X-RateLimit-Remaining": str(max(0, limit_config.requests - current_count)),
            "X-RateLimit-Reset": str(int(time.time() + limit_config.window)),
        }
        
        if not allowed:
            # Rate limit exceeded
            rate_limit_violations_total.labels(endpoint=endpoint, tier=tier.value).inc()
            
            headers["Retry-After"] = str(retry_after)
            
            logger.warning(
                f"Rate limit exceeded: {identifier} on {endpoint} "
                f"({current_count}/{limit_config.requests} in {limit_config.window}s)"
            )
            
            # Return 429 Too Many Requests
            return Response(
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit_config}",
                    "retry_after": retry_after,
                    "current_usage": current_count,
                    "limit": limit_config.requests,
                    "window": limit_config.window,
                },
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers=headers,
                media_type="application/json"
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to successful response
        for key, value in headers.items():
            response.headers[key] = value
        
        return response
    
    def _should_skip_path(self, path: str) -> bool:
        """Check if path should skip rate limiting"""
        skip_paths = [
            "/metrics",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        return any(path.startswith(skip) for skip in skip_paths)
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting
        
        Priority:
        1. Authenticated user ID
        2. API key
        3. Client IP address
        """
        # Check for authenticated user
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "id"):
            return f"user:{user.id}"
        
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"apikey:{api_key[:8]}"  # Use first 8 chars
        
        # Fallback to IP address
        # Check for proxy headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP from list
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        return f"ip:{ip}"
    
    def _get_user_tier(self, request: Request) -> RateLimitTier:
        """
        Get user's subscription tier
        
        Default to FREE if not authenticated or no tier found
        """
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "tier"):
            try:
                return RateLimitTier(user.tier)
            except ValueError:
                pass
        
        return RateLimitTier.FREE
    
    def _normalize_endpoint(self, path: str) -> str:
        """
        Normalize endpoint path for rate limiting
        
        Removes variable parts like IDs to group similar endpoints
        """
        # Remove trailing slash
        path = path.rstrip("/")
        
        # Simple normalization - replace UUIDs and numeric IDs
        parts = path.split("/")
        normalized = []
        
        for part in parts:
            if not part:
                continue
            # Replace UUIDs (36 chars with hyphens) and long IDs
            if len(part) > 20 or (len(part) > 10 and part.replace("-", "").isalnum()):
                normalized.append("{id}")
            elif part.isdigit():
                normalized.append("{id}")
            else:
                normalized.append(part)
        
        return "/" + "/".join(normalized)


# ====================
# Helper Functions
# ====================

def create_rate_limiter(
    redis_url: str,
    enabled: bool = True,
    key_prefix: str = "ratelimit"
) -> Callable[[ASGIApp], RateLimitMiddleware]:
    """
    Create rate limiter middleware factory with Redis connection
    
    Args:
        redis_url: Redis connection URL
        enabled: Enable/disable rate limiting
        key_prefix: Redis key prefix
    
    Returns:
        Middleware factory function
    
    Example:
        app = FastAPI()
        redis_url = "redis://localhost:6379/0"
        app.add_middleware(create_rate_limiter(redis_url))
    """
    redis_client: Optional[redis.Redis] = None
    
    try:
        redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        redis_client.ping()
        logger.info(f"Rate limiter connected to Redis: {redis_url}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis for rate limiting: {e}")
        logger.warning("Rate limiting will be disabled")
        enabled = False
    
    def middleware_factory(app: ASGIApp) -> RateLimitMiddleware:
        # If redis_client is None, create a dummy redis client or handle gracefully
        actual_redis: redis.Redis
        if redis_client is None:
            # Create a dummy Redis client that won't be used (disabled mode)
            actual_redis = redis.Redis()
        else:
            actual_redis = redis_client
            
        return RateLimitMiddleware(
            app=app,
            redis_client=actual_redis,
            enabled=enabled and redis_client is not None,
            key_prefix=key_prefix
        )
    
    return middleware_factory


# ====================
# Decorator for Route-Level Limits
# ====================

def rate_limit(
    requests: int,
    window: int,
    tier: Optional[RateLimitTier] = None
):
    """
    Decorator for custom rate limits on specific routes
    
    Args:
        requests: Number of requests allowed
        window: Time window in seconds
        tier: Specific tier (optional)
    
    Example:
        @app.get("/api/v1/expensive-operation")
        @rate_limit(requests=5, window=300)  # 5 requests per 5 minutes
        async def expensive_operation():
            ...
    """
    def decorator(func):
        # Store rate limit metadata on function
        func._rate_limit = RateLimitConfig(requests=requests, window=window)
        func._rate_limit_tier = tier
        return func
    return decorator