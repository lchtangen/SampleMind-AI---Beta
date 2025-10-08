"""
Query Caching Layer
Redis-backed cache for frequent database queries

This module provides intelligent query result caching to reduce database load
and improve response times. Features include:
- Automatic cache key generation
- Configurable TTL (Time To Live)
- Cache invalidation patterns
- Hit/miss metrics tracking
- Compression for large results
"""

import logging
import json
import hashlib
import zlib
from typing import Optional, Dict, Any, List, Callable
from datetime import timedelta
from functools import wraps
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class QueryCache:
    """Redis-backed query result cache with compression and metrics"""

    def __init__(
        self,
        redis_client: redis.Redis,
        default_ttl: int = 300,
        compression_threshold: int = 1024,
        enable_compression: bool = True
    ):
        """
        Initialize query cache

        Args:
            redis_client: Configured Redis client
            default_ttl: Default cache TTL in seconds (5 minutes)
            compression_threshold: Compress values larger than this (bytes)
            enable_compression: Whether to enable compression
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression

        # Metrics tracking
        self._hits = 0
        self._misses = 0
        self._errors = 0

        logger.info(f"QueryCache initialized (TTL: {default_ttl}s, compression: {enable_compression})")

    def _generate_cache_key(self, prefix: str, query_params: Dict[str, Any]) -> str:
        """
        Generate cache key from query parameters

        Args:
            prefix: Cache key prefix (e.g., 'user:', 'audio:')
            query_params: Query parameters to hash

        Returns:
            Cache key string
        """
        # Sort params for consistent hashing
        param_str = json.dumps(query_params, sort_keys=True)
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"cache:{prefix}:{param_hash}"

    def _compress_value(self, value: str) -> bytes:
        """Compress value if above threshold"""
        value_bytes = value.encode('utf-8')
        if self.enable_compression and len(value_bytes) > self.compression_threshold:
            compressed = zlib.compress(value_bytes, level=6)
            # Prefix with marker to indicate compression
            return b'COMPRESSED:' + compressed
        return value_bytes

    def _decompress_value(self, value: bytes) -> str:
        """Decompress value if needed"""
        if value.startswith(b'COMPRESSED:'):
            compressed = value[11:]  # Remove marker
            return zlib.decompress(compressed).decode('utf-8')
        return value.decode('utf-8')

    def get(self, prefix: str, query_params: Dict[str, Any]) -> Optional[Dict]:
        """
        Retrieve cached query result

        Args:
            prefix: Cache key prefix
            query_params: Query parameters

        Returns:
            Cached result or None if not found
        """
        try:
            cache_key = self._generate_cache_key(prefix, query_params)
            cached_value = self.redis.get(cache_key)

            if cached_value:
                self._hits += 1
                result = json.loads(self._decompress_value(cached_value))
                logger.debug(f"Cache HIT: {cache_key}")
                return result
            else:
                self._misses += 1
                logger.debug(f"Cache MISS: {cache_key}")
                return None

        except RedisError as e:
            self._errors += 1
            logger.error(f"Redis error during get: {e}")
            return None
        except Exception as e:
            self._errors += 1
            logger.error(f"Error retrieving from cache: {e}")
            return None

    def set(
        self,
        prefix: str,
        query_params: Dict[str, Any],
        data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache query result

        Args:
            prefix: Cache key prefix
            query_params: Query parameters
            data: Data to cache
            ttl: Time to live in seconds (uses default if None)

        Returns:
            Success status
        """
        try:
            cache_key = self._generate_cache_key(prefix, query_params)
            value = json.dumps(data)
            compressed = self._compress_value(value)

            ttl = ttl or self.default_ttl
            self.redis.setex(cache_key, ttl, compressed)

            logger.debug(f"Cached: {cache_key} (TTL: {ttl}s, size: {len(compressed)} bytes)")
            return True

        except RedisError as e:
            self._errors += 1
            logger.error(f"Redis error during set: {e}")
            return False
        except Exception as e:
            self._errors += 1
            logger.error(f"Error caching result: {e}")
            return False

    def invalidate(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern

        Args:
            pattern: Redis key pattern (e.g., 'cache:user:*')

        Returns:
            Number of keys deleted
        """
        try:
            keys = list(self.redis.scan_iter(match=pattern))
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Invalidated {deleted} cache entries matching: {pattern}")
                return deleted
            return 0

        except RedisError as e:
            self._errors += 1
            logger.error(f"Redis error during invalidation: {e}")
            return 0
        except Exception as e:
            self._errors += 1
            logger.error(f"Error invalidating cache: {e}")
            return 0

    def invalidate_prefix(self, prefix: str) -> int:
        """
        Invalidate all entries with given prefix

        Args:
            prefix: Cache key prefix (e.g., 'user', 'audio')

        Returns:
            Number of keys deleted
        """
        pattern = f"cache:{prefix}:*"
        return self.invalidate(pattern)

    def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            self.redis.flushdb()
            logger.info("Cache cleared successfully")
            return True
        except RedisError as e:
            self._errors += 1
            logger.error(f"Error clearing cache: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache performance statistics

        Returns:
            Dictionary with hit rate, misses, etc.
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0.0

        try:
            info = self.redis.info('stats')
            memory_info = self.redis.info('memory')

            return {
                'hits': self._hits,
                'misses': self._misses,
                'errors': self._errors,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests,
                'redis_keys': self.redis.dbsize(),
                'memory_used': memory_info.get('used_memory_human', 'N/A'),
                'memory_peak': memory_info.get('used_memory_peak_human', 'N/A'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'hits': self._hits,
                'misses': self._misses,
                'errors': self._errors,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }

    def print_statistics(self):
        """Print formatted cache statistics"""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("📊 QUERY CACHE STATISTICS")
        print("="*60)
        print(f"  Hit Rate:        {stats['hit_rate']:.2f}%")
        print(f"  Hits:            {stats['hits']:,}")
        print(f"  Misses:          {stats['misses']:,}")
        print(f"  Errors:          {stats['errors']:,}")
        print(f"  Total Requests:  {stats['total_requests']:,}")
        print(f"  Cached Keys:     {stats['redis_keys']:,}")
        print(f"  Memory Used:     {stats.get('memory_used', 'N/A')}")
        print(f"  Memory Peak:     {stats.get('memory_peak', 'N/A')}")
        print("="*60 + "\n")


def cached_query(
    cache: QueryCache,
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for automatic query result caching

    Args:
        cache: QueryCache instance
        prefix: Cache key prefix
        ttl: Cache TTL in seconds
        key_builder: Custom function to build cache key from args

    Example:
        @cached_query(cache, 'user', ttl=600)
        async def get_user_by_id(user_id: str):
            return await db.users.find_one({"_id": user_id})
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_params = key_builder(*args, **kwargs)
            else:
                cache_params = {'args': args, 'kwargs': kwargs}

            # Try to get from cache
            cached = cache.get(prefix, cache_params)
            if cached is not None:
                return cached

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                cache.set(prefix, cache_params, result, ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_params = key_builder(*args, **kwargs)
            else:
                cache_params = {'args': args, 'kwargs': kwargs}

            # Try to get from cache
            cached = cache.get(prefix, cache_params)
            if cached is not None:
                return cached

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            if result is not None:
                cache.set(prefix, cache_params, result, ttl)

            return result

        # Return appropriate wrapper based on function type
        import asyncio
        import inspect
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Singleton instance
_query_cache_instance: Optional[QueryCache] = None


def get_query_cache(redis_client: Optional[redis.Redis] = None) -> QueryCache:
    """
    Get or create QueryCache singleton instance

    Args:
        redis_client: Redis client (required for first initialization)

    Returns:
        QueryCache instance
    """
    global _query_cache_instance

    if _query_cache_instance is None:
        if redis_client is None:
            raise ValueError("redis_client required for first initialization")
        _query_cache_instance = QueryCache(redis_client)

    return _query_cache_instance