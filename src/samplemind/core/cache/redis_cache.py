"""
Production Redis Caching System
Multi-level caching with automatic invalidation
"""

import json
import pickle
from typing import Any, Optional, List, Dict, Callable
from functools import wraps
import hashlib
import asyncio
from datetime import timedelta
import logging
from redis import asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration"""
    DEFAULT_TTL = 3600  # 1 hour
    SHORT_TTL = 300  # 5 minutes
    LONG_TTL = 86400  # 24 hours
    
    # Cache key prefixes
    AUDIO_FEATURES = "audio:features:"
    AUDIO_METADATA = "audio:meta:"
    USER_DATA = "user:data:"
    SEARCH_RESULTS = "search:results:"
    API_RATE_LIMIT = "ratelimit:api:"
    SESSION_DATA = "session:"
    ANALYSIS_RESULTS = "analysis:results:"


class RedisCache:
    """
    Production-ready Redis cache manager
    Features:
    - Automatic serialization/deserialization
    - TTL management
    - Cache invalidation patterns
    - Batch operations
    - Cache statistics
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 3600,
        key_prefix: str = "samplemind:"
    ):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self._redis: Optional[Redis] = None
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.errors = 0
    
    async def connect(self):
        """Establish Redis connection"""
        try:
            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Handle binary data
                max_connections=50,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Test connection
            await self._redis.ping()
            logger.info(f"Redis cache connected: {self.redis_url}")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis cache disconnected")
    
    def _make_key(self, key: str) -> str:
        """Generate prefixed cache key"""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            full_key = self._make_key(key)
            data = await self._redis.get(full_key)
            
            if data is None:
                self.misses += 1
                return None
            
            self.hits += 1
            
            # Try to unpickle, fallback to JSON
            try:
                return pickle.loads(data)
            except (pickle.UnpicklingError, TypeError):
                return json.loads(data)
                
        except RedisError as e:
            self.errors += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            nx: Only set if key doesn't exist
            xx: Only set if key exists
            
        Returns:
            True if successful
        """
        try:
            full_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize value
            try:
                data = pickle.dumps(value)
            except (pickle.PicklingError, TypeError):
                data = json.dumps(value).encode()
            
            # Set with options
            result = await self._redis.set(
                full_key,
                data,
                ex=ttl,
                nx=nx,
                xx=xx
            )
            
            return bool(result)
            
        except RedisError as e:
            self.errors += 1
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            full_key = self._make_key(key)
            result = await self._redis.delete(full_key)
            return bool(result)
        except RedisError as e:
            self.errors += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            full_key = self._make_key(key)
            return bool(await self._redis.exists(full_key))
        except RedisError:
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            full_key = self._make_key(key)
            return bool(await self._redis.expire(full_key, ttl))
        except RedisError as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            full_key = self._make_key(key)
            return await self._redis.ttl(full_key)
        except RedisError:
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            full_key = self._make_key(key)
            return await self._redis.incrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement counter"""
        try:
            full_key = self._make_key(key)
            return await self._redis.decrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Cache decrement error for key {key}: {e}")
            return 0
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values at once"""
        try:
            full_keys = [self._make_key(k) for k in keys]
            values = await self._redis.mget(full_keys)
            
            result = {}
            for key, data in zip(keys, values):
                if data:
                    try:
                        result[key] = pickle.loads(data)
                    except:
                        try:
                            result[key] = json.loads(data)
                        except:
                            result[key] = data
            
            return result
            
        except RedisError as e:
            logger.error(f"Cache get_many error: {e}")
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values at once"""
        try:
            pipe = self._redis.pipeline()
            ttl = ttl or self.default_ttl
            
            for key, value in data.items():
                full_key = self._make_key(key)
                try:
                    serialized = pickle.dumps(value)
                except:
                    serialized = json.dumps(value).encode()
                
                pipe.set(full_key, serialized, ex=ttl)
            
            await pipe.execute()
            return True
            
        except RedisError as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            full_pattern = self._make_key(pattern)
            keys = []
            
            async for key in self._redis.scan_iter(match=full_pattern):
                keys.append(key)
            
            if keys:
                return await self._redis.delete(*keys)
            return 0
            
        except RedisError as e:
            logger.error(f"Cache delete_pattern error: {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear all cache entries (USE WITH CAUTION)"""
        try:
            await self._redis.flushdb()
            logger.warning("Cache cleared (flushdb)")
            return True
        except RedisError as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self._redis.info()
            
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "hits": self.hits,
                "misses": self.misses,
                "errors": self.errors,
                "hit_rate_percent": round(hit_rate, 2),
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": await self._redis.dbsize()
            }
            
        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


def cache_key(*args, **kwargs) -> str:
    """Generate deterministic cache key from arguments"""
    key_data = f"{args}{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(
    ttl: int = CacheConfig.DEFAULT_TTL,
    key_prefix: str = "",
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=3600, key_prefix="audio:features")
        async def get_audio_features(audio_id: str):
            # Expensive operation
            return features
    """
    def decorator(func: Callable):
        """Decorator wrapper for caching"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache instance (assumes global cache)
            cache = get_cache()
            
            # Build cache key
            if key_builder:
                key = key_prefix + key_builder(*args, **kwargs)
            else:
                key = key_prefix + cache_key(*args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(key, result, ttl=ttl)
            logger.debug(f"Cache set: {key}")
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_instance: Optional[RedisCache] = None


async def init_cache(redis_url: str, **kwargs) -> RedisCache:
    """Initialize global cache instance"""
    global _cache_instance
    _cache_instance = RedisCache(redis_url, **kwargs)
    await _cache_instance.connect()
    return _cache_instance


def get_cache() -> RedisCache:
    """Get global cache instance"""
    if _cache_instance is None:
        raise RuntimeError("Cache not initialized. Call init_cache() first")
    return _cache_instance


# Specialized cache managers

class AudioFeatureCache:
    """Cache manager for audio features"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.prefix = CacheConfig.AUDIO_FEATURES
    
    async def get_features(self, audio_id: str) -> Optional[Dict[str, Any]]:
        """Get cached audio features"""
        return await self.cache.get(f"{self.prefix}{audio_id}")
    
    async def set_features(
        self,
        audio_id: str,
        features: Dict[str, Any],
        ttl: int = CacheConfig.LONG_TTL
    ) -> bool:
        """Cache audio features"""
        return await self.cache.set(f"{self.prefix}{audio_id}", features, ttl=ttl)
    
    async def invalidate(self, audio_id: str) -> bool:
        """Invalidate cached features"""
        return await self.cache.delete(f"{self.prefix}{audio_id}")


class RateLimitCache:
    """Cache-based rate limiting"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.prefix = CacheConfig.API_RATE_LIMIT
    
    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            identifier: User/API key identifier
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if allowed, False if rate limit exceeded
        """
        key = f"{self.prefix}{identifier}"
        
        # Get current count
        current = await self.cache.get(key)
        
        if current is None:
            # First request in window
            await self.cache.set(key, 1, ttl=window_seconds)
            return True
        
        if int(current) >= max_requests:
            # Rate limit exceeded
            return False
        
        # Increment counter
        await self.cache.increment(key)
        return True
    
    async def get_remaining(self, identifier: str, max_requests: int) -> int:
        """Get remaining requests in current window"""
        key = f"{self.prefix}{identifier}"
        current = await self.cache.get(key)
        
        if current is None:
            return max_requests
        
        return max(0, max_requests - int(current))


# Example usage
"""
from src.samplemind.core.config import settings

async def main():
    # Initialize cache
    cache = await init_cache(settings.redis_url)
    
    # Basic operations
    await cache.set("user:123", {"name": "John"}, ttl=3600)
    user = await cache.get("user:123")
    
    # Batch operations
    await cache.set_many({
        "audio:1": {"duration": 120},
        "audio:2": {"duration": 180}
    })
    
    # Pattern deletion
    await cache.delete_pattern("audio:*")
    
    # Statistics
    stats = await cache.get_stats()
    print(f"Hit rate: {stats['hit_rate_percent']}%")
    
    # Rate limiting
    rate_limiter = RateLimitCache(cache)
    allowed = await rate_limiter.check_rate_limit("user:123", max_requests=100, window_seconds=60)
    
    # Cached function
    @cached(ttl=3600, key_prefix="audio:features:")
    async def get_audio_features(audio_id: str):
        # Expensive operation
        return {"tempo": 120, "key": "C"}
    
    features = await get_audio_features("audio_123")
"""
