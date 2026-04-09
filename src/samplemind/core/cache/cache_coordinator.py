"""
Cache Coordinator — Unified access to L1/L2/L3 cache layers.

Architecture:
- L1: In-memory LRU (ultra-fast, 512MB, 1 hour TTL)
- L2: Redis (distributed, persistent, 24 hour TTL)
- L3: S3 cold storage (archival, <7 days old samples, opt-in)

Strategy:
- READ: Check L1 → L2 → compute (populate on miss)
- WRITE: Write-through L1 + L2 simultaneously
- INVALIDATE: Clear L1 + L2 + S3 on updates
- PROMOTE: Auto-promote L2 → L1 on cache hits
"""

import asyncio
import jsonpickle
import logging
from typing import Any, Awaitable, Callable, TypeVar

from samplemind.core.cache.lru_cache import get_l1_cache
from samplemind.core.cache.redis_cache import RedisCache
from samplemind.integrations.s3_provider import S3Provider

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CacheCoordinator:
    """
    Multi-layer cache coordinator with write-through and L2→L1 promotion.

    Ensures fast L1 hits for hot data while maintaining distributed cache
    via L2 Redis and cold storage via L3 S3.
    """

    def __init__(
        self,
        redis_cache: RedisCache | None = None,
        s3_provider: S3Provider | None = None,
        enable_l3: bool = False,
    ):
        """
        Initialize cache coordinator.

        Args:
            redis_cache: L2 Redis cache instance
            s3_provider: L3 S3 storage provider
            enable_l3: Enable L3 S3 cold storage (opt-in, default False)
        """
        self.l1_cache = get_l1_cache()
        self.l2_cache = redis_cache
        self.l3_provider = s3_provider
        self.enable_l3 = enable_l3

        logger.info(
            f"Cache coordinator initialized "
            f"(L1=in-memory, L2={'redis' if redis_cache else 'disabled'}, "
            f"L3={'s3' if enable_l3 and s3_provider else 'disabled'})"
        )

    async def get(
        self,
        key: str,
        compute_fn: Callable[[], Awaitable[T]] | None = None,
        ttl_seconds: int | None = None,
    ) -> T | None:
        """
        Get value from cache with automatic fallthrough and population.

        Strategy: L1 → L2 → compute (if compute_fn provided)

        Args:
            key: Cache key
            compute_fn: Optional async function to compute value on miss
            ttl_seconds: Optional TTL override (all layers use same TTL)

        Returns:
            Cached value or computed value
        """
        # L1: Check in-memory LRU (fastest)
        value = self.l1_cache.get(key)
        if value is not None:
            logger.debug(f"Cache hit (L1): {key}")
            return value

        # L2: Check Redis (fast, distributed)
        if self.l2_cache:
            try:
                value = await self.l2_cache.get(key)
                if value is not None:
                    logger.debug(f"Cache hit (L2): {key}, promoting to L1")
                    # Promote to L1 for next access
                    self.l1_cache.set(key, value, ttl_seconds=ttl_seconds or 3600)
                    return value
            except Exception as e:
                logger.warning(f"L2 cache get failed for {key}: {e}")

        # L3: Check S3 (slow, cold storage) - only if explicitly looking for old data
        if self.enable_l3 and self.l3_provider:
            try:
                value = await self.l3_provider.get_async(f"cache/{key}")
                if value is not None:
                    # Deserialize
                    value = jsonpickle.decode(value)
                    logger.debug(f"Cache hit (L3): {key}, restoring to L1/L2")
                    # Promote back to L1 + L2
                    await self.set(key, value, ttl_seconds=ttl_seconds)
                    return value
            except Exception as e:
                logger.debug(f"L3 cache get failed for {key}: {e}")

        # Miss: Compute if function provided
        if compute_fn:
            logger.debug(f"Cache miss: {key}, computing...")
            value = await compute_fn()
            if value is not None:
                await self.set(key, value, ttl_seconds=ttl_seconds)
            return value

        logger.debug(f"Cache miss: {key}, no compute function")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
        promote_to_l1: bool = True,
    ) -> None:
        """
        Set value in cache with write-through strategy.

        Strategy: Write L1 + L2 simultaneously, optionally L3 for archival

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override (default: 1hr for features, 24hr for analysis)
            promote_to_l1: Always promote to L1 (default True)
        """
        # Determine TTL based on key prefix if not provided
        if ttl_seconds is None:
            ttl_seconds = self._determine_ttl(key)

        # Write L1 (always, synchronous)
        if promote_to_l1:
            self.l1_cache.set(key, value, ttl_seconds=ttl_seconds)
            logger.debug(f"Cache set (L1): {key}")

        # Write L2 (Redis, async)
        if self.l2_cache:
            try:
                await self.l2_cache.set(key, value, ttl=ttl_seconds)
                logger.debug(f"Cache set (L2): {key}")
            except Exception as e:
                logger.warning(f"L2 cache set failed for {key}: {e}")

        # Write L3 (S3, async, only for specific patterns)
        if self.enable_l3 and self.l3_provider and self._should_archive(key):
            try:
                serialized = jsonpickle.encode(value)
                await self.l3_provider.put_async(f"cache/{key}", serialized)
                logger.debug(f"Cache set (L3): {key}")
            except Exception as e:
                logger.debug(f"L3 cache set failed for {key}: {e}")

    async def invalidate(self, key: str | None = None) -> None:
        """
        Invalidate cache entries across all layers.

        Args:
            key: Specific key to invalidate (None = clear all)
        """
        if key is None:
            # Clear all
            self.l1_cache.clear()
            if self.l2_cache:
                try:
                    await self.l2_cache.clear()
                except Exception as e:
                    logger.warning(f"L2 cache clear failed: {e}")
            logger.info("Cache cleared (all layers)")
        else:
            # Invalidate specific key
            self.l1_cache.delete(key)
            if self.l2_cache:
                try:
                    await self.l2_cache.delete(key)
                except Exception as e:
                    logger.warning(f"L2 cache delete failed for {key}: {e}")
            if self.enable_l3 and self.l3_provider:
                try:
                    await self.l3_provider.delete_async(f"cache/{key}")
                except Exception as e:
                    logger.debug(f"L3 cache delete failed for {key}: {e}")
            logger.debug(f"Cache invalidated: {key}")

    async def invalidate_pattern(self, pattern: str) -> None:
        """
        Invalidate all keys matching pattern (e.g., 'audio:features:*').

        Args:
            pattern: Key pattern to match (Unix glob)
        """
        # L1: Iterate and match
        l1_keys = [k for k in self.l1_cache._cache.keys() if self._match_pattern(k, pattern)]
        for key in l1_keys:
            self.l1_cache.delete(key)

        # L2: Use Redis pattern matching
        if self.l2_cache:
            try:
                await self.l2_cache.delete_pattern(pattern)
            except Exception as e:
                logger.warning(f"L2 cache pattern delete failed: {e}")

        logger.debug(f"Cache invalidated pattern: {pattern} ({len(l1_keys)} keys)")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics across all layers."""
        l1_stats = self.l1_cache.get_stats()

        l2_stats = {}
        if self.l2_cache:
            try:
                l2_stats = asyncio.run(self.l2_cache.get_stats())
            except Exception as e:
                logger.warning(f"L2 stats retrieval failed: {e}")
                l2_stats = {"error": str(e)}

        return {
            "l1_memory": l1_stats,
            "l2_redis": l2_stats,
            "l3_enabled": self.enable_l3,
            "total_hits": l1_stats.get("hits", 0) + l2_stats.get("hits", 0),
            "total_misses": l1_stats.get("misses", 0) + l2_stats.get("misses", 0),
        }

    def _determine_ttl(self, key: str) -> int:
        """Determine TTL based on key prefix."""
        # Short-lived: search results, recommendations
        if key.startswith(("search:", "recommend:")):
            return 300  # 5 minutes

        # Medium-lived: feature extractions, classifications
        if key.startswith(("feature:", "class:", "tag:")):
            return 3600  # 1 hour

        # Long-lived: analysis results, embeddings
        if key.startswith(("analysis:", "embed:")):
            return 86400  # 24 hours

        # Embeddings are often cached longer
        if key.startswith("clap:"):
            return 604800  # 7 days

        # Default: 1 hour
        return 3600

    def _should_archive(self, key: str) -> bool:
        """Determine if key should be archived to S3."""
        # Archive long-lived, non-volatile data
        # Skip: search results, recommendations, temporary data
        skip_patterns = ["search:", "recommend:", "temp:", "session:"]
        return not any(key.startswith(pattern) for pattern in skip_patterns)

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches glob pattern."""
        import fnmatch

        return fnmatch.fnmatch(key, pattern)


# Global singleton
_COORDINATOR_INSTANCE: CacheCoordinator | None = None


async def get_cache_coordinator(
    enable_l3: bool = False,
) -> CacheCoordinator:
    """
    Get or create cache coordinator singleton.

    Args:
        enable_l3: Enable S3 cold storage layer (opt-in)

    Returns:
        Singleton CacheCoordinator instance
    """
    global _COORDINATOR_INSTANCE

    if _COORDINATOR_INSTANCE is None:
        # Lazy load Redis and S3 providers
        try:
            from samplemind.core.cache.redis_cache import RedisCache

            l2_cache = RedisCache()
        except Exception as e:
            logger.warning(f"Failed to initialize L2 Redis cache: {e}")
            l2_cache = None

        if enable_l3:
            try:
                from samplemind.integrations.s3_provider import S3Provider

                l3_provider = S3Provider()
            except Exception as e:
                logger.warning(f"Failed to initialize L3 S3 provider: {e}")
                l3_provider = None
        else:
            l3_provider = None

        _COORDINATOR_INSTANCE = CacheCoordinator(
            redis_cache=l2_cache,
            s3_provider=l3_provider,
            enable_l3=enable_l3,
        )

    return _COORDINATOR_INSTANCE
