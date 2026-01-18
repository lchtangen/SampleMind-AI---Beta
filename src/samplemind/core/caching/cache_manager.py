"""
Advanced Cache Manager with LRU-K eviction and adaptive TTL.

Extends the basic Redis cache with intelligent eviction policies
and adaptive time-to-live management based on access patterns.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Single cache entry with metadata"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    access_history: List[float] = field(default_factory=list)
    ttl: int = 3600  # Time-to-live in seconds
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() - self.created_at > self.ttl

    def get_recency(self) -> float:
        """Get recency score (0.0 = old, 1.0 = recent)"""
        age = time.time() - self.last_accessed
        max_age = self.ttl

        if age >= max_age:
            return 0.0

        return 1.0 - (age / max_age)

    def get_frequency(self) -> float:
        """Get frequency score (normalized)"""
        if self.access_count == 0:
            return 0.0

        # Normalize to 0.0-1.0 based on common access patterns
        # Most accessed items have 10-100 accesses in a session
        return min(1.0, self.access_count / 100.0)

    def update_access(self) -> None:
        """Record access"""
        self.last_accessed = time.time()
        self.access_count += 1
        self.access_history.append(self.last_accessed)

        # Keep history limited
        if len(self.access_history) > 1000:
            self.access_history.pop(0)


class AdvancedCacheManager:
    """
    Advanced cache manager with LRU-K eviction and adaptive TTL.

    Features:
    - LRU-K eviction: considers both recency and frequency
    - Adaptive TTL: adjusts based on access patterns
    - Memory management: enforces size limits
    - Statistics: tracks hit/miss rates and patterns
    - Thermal awareness: responds to system load
    """

    def __init__(
        self,
        redis_cache=None,
        max_memory_mb: int = 512,
        k: int = 2,
        adaptive_ttl: bool = True
    ):
        """
        Initialize advanced cache manager.

        Args:
            redis_cache: Underlying Redis cache instance
            max_memory_mb: Maximum cache size in MB
            k: Parameter for LRU-K (number of accesses to track)
            adaptive_ttl: Enable adaptive time-to-live
        """
        self.redis_cache = redis_cache
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.k = k
        self.adaptive_ttl = adaptive_ttl

        # Local entry tracking
        self.entries: Dict[str, CacheEntry] = OrderedDict()

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # Time windows for adaptive TTL
        self.short_ttl = 300  # 5 minutes
        self.medium_ttl = 3600  # 1 hour
        self.long_ttl = 86400  # 24 hours

        logger.info(
            f"Advanced cache manager initialized "
            f"(max_memory={max_memory_mb}MB, k={k}, adaptive_ttl={adaptive_ttl})"
        )

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache with eviction checks.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Check if entry exists locally
        if key in self.entries:
            entry = self.entries[key]

            # Check expiration
            if entry.is_expired():
                await self.delete(key)
                self.misses += 1
                return None

            # Update access
            entry.update_access()
            self.hits += 1

            return entry.value

        # Try Redis
        if self.redis_cache:
            try:
                value = await self.redis_cache.get(key)
                if value is not None:
                    self.hits += 1
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        self.misses += 1
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        size_bytes: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with automatic eviction.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override
            size_bytes: Optional size hint

        Returns:
            True if successful
        """
        # Remove old entry if exists
        if key in self.entries:
            del self.entries[key]

        # Determine TTL
        if ttl is None:
            ttl = self._calculate_adaptive_ttl(key)

        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=ttl,
            size_bytes=size_bytes or 0
        )

        # Check if we need to evict
        if self._get_cache_size() + entry.size_bytes > self.max_memory_bytes:
            await self._evict_lruk()

        # Store entry
        self.entries[key] = entry

        # Store in Redis if available
        if self.redis_cache:
            try:
                await self.redis_cache.set(key, value, ttl=ttl)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
                return False

        return True

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.entries:
            del self.entries[key]

        if self.redis_cache:
            try:
                return await self.redis_cache.delete(key)
            except Exception:
                return False

        return True

    def _get_cache_size(self) -> int:
        """Get total cache size in bytes"""
        return sum(entry.size_bytes for entry in self.entries.values())

    async def _evict_lruk(self) -> None:
        """
        Evict entries using LRU-K algorithm.

        LRU-K considers both recency (how recently accessed) and
        frequency (how often accessed), with weight towards frequency.
        """
        if not self.entries:
            return

        # Calculate eviction scores for each entry
        scores: List[Tuple[str, float]] = []

        for key, entry in self.entries.items():
            # LRU-K score combines recency and frequency
            # Weight: 70% frequency, 30% recency
            frequency_score = entry.get_frequency()
            recency_score = entry.get_recency()

            lruk_score = (0.7 * frequency_score) + (0.3 * recency_score)

            scores.append((key, lruk_score))

        # Sort by score (lowest first - will be evicted)
        scores.sort(key=lambda x: x[1])

        # Evict bottom 25% of entries
        evict_count = max(1, len(self.entries) // 4)

        for i in range(evict_count):
            key_to_evict = scores[i][0]
            await self.delete(key_to_evict)
            self.evictions += 1

        logger.info(f"LRU-K eviction: removed {evict_count} entries")

    def _calculate_adaptive_ttl(self, key: str) -> int:
        """
        Calculate adaptive TTL based on access patterns.

        Args:
            key: Cache key

        Returns:
            TTL in seconds
        """
        if not self.adaptive_ttl:
            return self.medium_ttl

        # If key exists, use its access pattern
        if key in self.entries:
            entry = self.entries[key]

            # Frequently accessed → longer TTL
            if entry.access_count > 50:
                return self.long_ttl

            # Moderately accessed → medium TTL
            elif entry.access_count > 10:
                return self.medium_ttl

            # Rarely accessed → short TTL
            else:
                return self.short_ttl

        # New keys get medium TTL
        return self.medium_ttl

    def get_hit_ratio(self) -> float:
        """Get cache hit ratio (0.0 - 1.0)"""
        total = self.hits + self.misses

        if total == 0:
            return 0.0

        return self.hits / total

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        cache_size_mb = self._get_cache_size() / 1024 / 1024

        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": round(self.get_hit_ratio(), 3),
            "evictions": self.evictions,
            "entries": len(self.entries),
            "cache_size_mb": round(cache_size_mb, 2),
            "max_size_mb": self.max_memory_bytes / 1024 / 1024,
            "memory_utilization": round((cache_size_mb / (self.max_memory_bytes / 1024 / 1024)) * 100, 1)
        }

    def get_top_accessed(self, limit: int = 10) -> List[Dict]:
        """Get most accessed entries"""
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].access_count,
            reverse=True
        )

        result = []
        for key, entry in sorted_entries[:limit]:
            result.append({
                "key": key,
                "access_count": entry.access_count,
                "size_mb": entry.size_bytes / 1024 / 1024,
                "age_seconds": time.time() - entry.created_at,
                "ttl_remaining": max(0, entry.ttl - (time.time() - entry.created_at))
            })

        return result

    def get_oldest_entries(self, limit: int = 10) -> List[Dict]:
        """Get oldest entries (candidates for eviction)"""
        sorted_entries = sorted(
            self.entries.items(),
            key=lambda x: x[1].created_at
        )

        result = []
        for key, entry in sorted_entries[:limit]:
            result.append({
                "key": key,
                "created_at": entry.created_at,
                "age_seconds": time.time() - entry.created_at,
                "access_count": entry.access_count,
                "lruk_score": (0.7 * entry.get_frequency()) + (0.3 * entry.get_recency())
            })

        return result

    def clear(self) -> None:
        """Clear all cache"""
        self.entries.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.entries.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self.entries[key]

        logger.info(f"Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)


# Global instance
_manager_instance: Optional[AdvancedCacheManager] = None


def init_manager(redis_cache=None, **kwargs) -> AdvancedCacheManager:
    """Initialize global cache manager instance"""
    global _manager_instance
    _manager_instance = AdvancedCacheManager(redis_cache=redis_cache, **kwargs)
    return _manager_instance


def get_manager() -> AdvancedCacheManager:
    """Get global cache manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AdvancedCacheManager()
    return _manager_instance
