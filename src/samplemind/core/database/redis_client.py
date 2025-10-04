"""Redis client for caching, sessions, and rate limiting"""

import logging
import json
from typing import Optional, Any, Dict
from functools import wraps
import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def init_redis(redis_url: str = "redis://localhost:6379"):
    """Initialize Redis connection"""
    global _redis_client
    
    try:
        logger.info("🔌 Connecting to Redis...")
        
        _redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
        
        # Test connection
        await _redis_client.ping()
        
        logger.info("✅ Redis connected")
        return _redis_client
        
    except RedisError as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis: {e}")
        raise


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        logger.info("✅ Redis connection closed")
        _redis_client = None


def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


# Caching utilities

async def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """Set a value in cache with TTL"""
    try:
        client = get_redis()
        serialized = json.dumps(value)
        await client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache"""
    try:
        client = get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_delete(key: str) -> bool:
    """Delete a value from cache"""
    try:
        client = get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache"""
    try:
        client = get_redis()
        return await client.exists(key) > 0
    except Exception:
        return False


# Rate limiting

async def rate_limit_check(key: str, limit: int = 60, window: int = 60) -> bool:
    """
    Check rate limit using sliding window
    
    Args:
        key: Unique identifier (e.g., user_id, ip_address)
        limit: Maximum requests allowed
        window: Time window in seconds
        
    Returns:
        True if within limit, False if exceeded
    """
    try:
        client = get_redis()
        current_count = await client.incr(key)
        
        if current_count == 1:
            await client.expire(key, window)
        
        return current_count <= limit
        
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error


async def rate_limit_reset(key: str):
    """Reset rate limit for a key"""
    try:
        client = get_redis()
        await client.delete(key)
    except Exception as e:
        logger.error(f"Rate limit reset error: {e}")


# Session management

async def session_set(session_id: str, data: Dict[str, Any], ttl: int = 86400) -> bool:
    """Set session data (default 24 hour TTL)"""
    return await cache_set(f"session:{session_id}", data, ttl)


async def session_get(session_id: str) -> Optional[Dict[str, Any]]:
    """Get session data"""
    return await cache_get(f"session:{session_id}")


async def session_delete(session_id: str) -> bool:
    """Delete session"""
    return await cache_delete(f"session:{session_id}")


# Decorator for caching function results

def redis_cache(ttl: int = 3600, key_prefix: str = "cache"):
    """
    Decorator to cache function results in Redis
    
    Usage:
        @redis_cache(ttl=600, key_prefix="analysis")
        async def expensive_operation(param1, param2):
            # ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_set(cache_key, result, ttl)
            logger.debug(f"Cache miss, stored: {cache_key}")
            
            return result
        return wrapper
    return decorator


async def health_check() -> bool:
    """Check Redis connection health"""
    try:
        if _redis_client:
            await _redis_client.ping()
            return True
    except Exception:
        pass
    return False
