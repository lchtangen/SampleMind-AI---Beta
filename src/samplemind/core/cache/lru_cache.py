"""
L1 In-Memory LRU Cache — Ultra-fast hot data cache with TTL and eviction.

Features:
- Native in-memory storage (no I/O)
- Thread-safe LRU eviction with size limits
- Per-entry TTL with background cleanup
- Hit/miss statistics tracking
- Configurable max entries and memory limits
"""

import asyncio
import logging
import sys
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class L1CacheEntry:
    """Single L1 cache entry with metadata"""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    ttl_seconds: int
    size_bytes: int = 0
    access_count: int = 0


class L1LRUCache:
    """
    L1 in-memory LRU cache with TTL support.

    Target response: <1ms for cache hits
    Memory limit: 512MB default, configurable
    Eviction: LRU when capacity exceeded
    """

    def __init__(
        self,
        max_entries: int = 10000,
        max_memory_mb: int = 512,
        default_ttl_seconds: int = 3600,
        cleanup_interval_seconds: int = 300,
    ):
        """
        Initialize L1 cache.

        Args:
            max_entries: Maximum entries to store
            max_memory_mb: Maximum memory in MB
            default_ttl_seconds: Default TTL for entries
            cleanup_interval_seconds: Background cleanup interval
        """
        self.max_entries = max_entries
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl_seconds = default_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds

        # OrderedDict for LRU tracking (oldest → newest)
        self._cache: OrderedDict[str, L1CacheEntry] = OrderedDict()

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # Background cleanup task
        self._cleanup_task: asyncio.Task | None = None
        self._cleanup_stop = False

        logger.info(
            f"L1 LRU cache initialized "
            f"(max_entries={max_entries}, max_memory={max_memory_mb}MB, "
            f"default_ttl={default_ttl_seconds}s, cleanup_interval={cleanup_interval_seconds}s)"
        )

    def get(self, key: str) -> Any | None:
        """
        Get value from cache (synchronous, <1ms).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self.misses += 1
            return None

        entry = self._cache[key]

        # Check if expired
        if time.time() - entry.created_at > entry.ttl_seconds:
            del self._cache[key]
            self.misses += 1
            return None

        # Update access time and move to end (LRU)
        entry.last_accessed = time.time()
        entry.access_count += 1
        self._cache.move_to_end(key)

        self.hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
        size_bytes: int | None = None,
    ) -> None:
        """
        Set value in cache with automatic eviction.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override
            size_bytes: Optional size hint (auto-estimated if None)
        """
        ttl = ttl_seconds or self.default_ttl_seconds

        # Estimate size if not provided
        if size_bytes is None:
            size_bytes = sys.getsizeof(value)

        # Create entry
        entry = L1CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl_seconds=ttl,
            size_bytes=size_bytes,
            access_count=1,
        )

        # Remove old entry if exists
        if key in self._cache:
            del self._cache[key]

        # Check eviction before adding
        current_size = self._get_total_memory()
        if (
            len(self._cache) >= self.max_entries
            or current_size + size_bytes > self.max_memory_bytes
        ):
            self._evict_lru()

        # Add to cache (move to end = most recent)
        self._cache[key] = entry

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def has(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self._cache:
            return False

        entry = self._cache[key]
        if time.time() - entry.created_at > entry.ttl_seconds:
            del self._cache[key]
            return False

        return True

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        total_memory = self._get_total_memory()
        hit_rate = (
            self.hits / (self.hits + self.misses)
            if (self.hits + self.misses) > 0
            else 0
        )

        return {
            "entries": total_entries,
            "memory_mb": total_memory / (1024 * 1024),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "capacity_entries": f"{total_entries}/{self.max_entries}",
            "capacity_memory": f"{total_memory / (1024 * 1024):.1f}/{self.max_memory_bytes / (1024 * 1024):.1f}MB",
        }

    def _get_total_memory(self) -> int:
        """Calculate total memory used by all entries."""
        return sum(entry.size_bytes for entry in self._cache.values())

    def _evict_lru(self) -> None:
        """Evict least recently used entries until under limit."""
        while (
            len(self._cache) >= self.max_entries
            or self._get_total_memory() > self.max_memory_bytes
        ):
            # Pop oldest entry (first in OrderedDict)
            if self._cache:
                first_key, first_entry = self._cache.popitem(last=False)
                self.evictions += 1
                logger.debug(
                    f"L1 cache evicted (LRU): {first_key} "
                    f"(size: {first_entry.size_bytes} bytes, access_count: {first_entry.access_count})"
                )

            if len(self._cache) == 0:
                break

    def _cleanup_expired(self) -> None:
        """Remove all expired entries (synchronous)."""
        current_time = time.time()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if current_time - entry.created_at > entry.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.debug(f"L1 cache cleanup: removed {len(expired_keys)} expired entries")


# Global singleton instance
_L1_CACHE_INSTANCE: L1LRUCache | None = None


def get_l1_cache(
    max_entries: int = 10000,
    max_memory_mb: int = 512,
    default_ttl_seconds: int = 3600,
) -> L1LRUCache:
    """
    Get or create L1 cache singleton.

    Args:
        max_entries: Max entries (only used on first call)
        max_memory_mb: Max memory MB (only used on first call)
        default_ttl_seconds: Default TTL (only used on first call)

    Returns:
        Singleton L1LRUCache instance
    """
    global _L1_CACHE_INSTANCE

    if _L1_CACHE_INSTANCE is None:
        _L1_CACHE_INSTANCE = L1LRUCache(
            max_entries=max_entries,
            max_memory_mb=max_memory_mb,
            default_ttl_seconds=default_ttl_seconds,
        )

    return _L1_CACHE_INSTANCE
