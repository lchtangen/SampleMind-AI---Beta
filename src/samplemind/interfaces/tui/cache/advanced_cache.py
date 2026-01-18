"""Advanced multi-level caching system (L1/L2/L3) for TUI"""

import asyncio
import logging
import hashlib
import json
from collections import OrderedDict
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdvancedCache:
    """Multi-level cache with L1 (memory), L2 (Redis), L3 (MongoDB)"""

    def __init__(
        self,
        l1_max_size: int = 100,
        l2_enabled: bool = True,
        l3_enabled: bool = True,
        ttl_minutes: int = 60,
    ):
        """
        Initialize advanced cache

        Args:
            l1_max_size: Maximum items in L1 memory cache
            l2_enabled: Enable Redis L2 cache
            l3_enabled: Enable MongoDB L3 cache
            ttl_minutes: Time-to-live in minutes
        """
        # L1: Memory cache (LRU)
        self.l1_cache: OrderedDict[str, Any] = OrderedDict()
        self.l1_max_size = l1_max_size

        # Cache configuration
        self.l2_enabled = l2_enabled
        self.l3_enabled = l3_enabled
        self.ttl = timedelta(minutes=ttl_minutes)

        # Statistics
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l3_hits": 0,
            "l3_misses": 0,
            "total_requests": 0,
        }

        # Redis/MongoDB references (will be set externally)
        self.redis_cache: Optional[Any] = None
        self.mongo_db: Optional[Any] = None

    # ============================================================================
    # KEY MANAGEMENT
    # ============================================================================

    @staticmethod
    def _generate_key(namespace: str, identifier: str) -> str:
        """Generate cache key"""
        return f"{namespace}:{identifier}"

    @staticmethod
    def _generate_hash(data: Any) -> str:
        """Generate hash of data for cache validation"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    # ============================================================================
    # L1 CACHE (MEMORY)
    # ============================================================================

    def _l1_get(self, key: str) -> Optional[Any]:
        """Get from L1 memory cache"""
        if key in self.l1_cache:
            # Move to end (LRU pattern)
            self.l1_cache.move_to_end(key)
            self.stats["l1_hits"] += 1
            logger.debug(f"💾 L1 HIT: {key}")
            return self.l1_cache[key]
        self.stats["l1_misses"] += 1
        return None

    def _l1_set(self, key: str, value: Any) -> None:
        """Set in L1 memory cache"""
        # Remove if already exists
        if key in self.l1_cache:
            del self.l1_cache[key]

        # Add to cache
        self.l1_cache[key] = value

        # Evict oldest if over capacity
        while len(self.l1_cache) > self.l1_max_size:
            evicted_key, _ = self.l1_cache.popitem(last=False)
            logger.debug(f"💾 L1 EVICT: {evicted_key}")

        logger.debug(f"💾 L1 SET: {key} (size: {len(self.l1_cache)}/{self.l1_max_size})")

    def _l1_clear(self) -> None:
        """Clear L1 cache"""
        self.l1_cache.clear()
        logger.info("💾 L1 cache cleared")

    def _l1_size(self) -> int:
        """Get L1 cache size"""
        return len(self.l1_cache)

    # ============================================================================
    # MULTI-LEVEL CACHE OPERATIONS
    # ============================================================================

    async def get(self, namespace: str, identifier: str) -> Optional[Any]:
        """Get value from cache (L1 → L2 → L3)"""
        self.stats["total_requests"] += 1
        key = self._generate_key(namespace, identifier)

        # Try L1
        value = self._l1_get(key)
        if value is not None:
            return value

        # Try L2 (Redis)
        if self.l2_enabled and self.redis_cache:
            try:
                value = await self._l2_get(key)
                if value is not None:
                    # Promote to L1
                    self._l1_set(key, value)
                    self.stats["l2_hits"] += 1
                    logger.debug(f"📡 L2 HIT → L1: {key}")
                    return value
                self.stats["l2_misses"] += 1
            except Exception as e:
                logger.warning(f"⚠️  L2 error: {e}")

        # Try L3 (MongoDB)
        if self.l3_enabled and self.mongo_db:
            try:
                value = await self._l3_get(key)
                if value is not None:
                    # Promote to L1 and L2
                    self._l1_set(key, value)
                    if self.l2_enabled and self.redis_cache:
                        await self._l2_set(key, value)
                    self.stats["l3_hits"] += 1
                    logger.debug(f"🗄️  L3 HIT → L1/L2: {key}")
                    return value
                self.stats["l3_misses"] += 1
            except Exception as e:
                logger.warning(f"⚠️  L3 error: {e}")

        logger.debug(f"❌ MISS: {key}")
        return None

    async def set(
        self, namespace: str, identifier: str, value: Any, tags: Optional[List[str]] = None
    ) -> None:
        """Set value in cache (L1 + L2 + L3)"""
        key = self._generate_key(namespace, identifier)

        # Set L1
        self._l1_set(key, value)

        # Set L2 (Redis) - non-blocking
        if self.l2_enabled and self.redis_cache:
            try:
                await self._l2_set(key, value, tags=tags)
            except Exception as e:
                logger.warning(f"⚠️  Failed to set L2: {e}")

        # Set L3 (MongoDB) - non-blocking
        if self.l3_enabled and self.mongo_db:
            try:
                await self._l3_set(key, value, tags=tags)
            except Exception as e:
                logger.warning(f"⚠️  Failed to set L3: {e}")

        logger.debug(f"✅ SET: {key}")

    async def delete(self, namespace: str, identifier: str) -> None:
        """Delete from all cache levels"""
        key = self._generate_key(namespace, identifier)

        # Delete L1
        if key in self.l1_cache:
            del self.l1_cache[key]

        # Delete L2
        if self.l2_enabled and self.redis_cache:
            try:
                await self._l2_delete(key)
            except Exception as e:
                logger.warning(f"⚠️  Failed to delete from L2: {e}")

        # Delete L3
        if self.l3_enabled and self.mongo_db:
            try:
                await self._l3_delete(key)
            except Exception as e:
                logger.warning(f"⚠️  Failed to delete from L3: {e}")

        logger.debug(f"🗑️  DELETE: {key}")

    async def clear(self) -> None:
        """Clear all cache levels"""
        # Clear L1
        self._l1_clear()

        # Clear L2
        if self.l2_enabled and self.redis_cache:
            try:
                await self._l2_clear()
            except Exception as e:
                logger.warning(f"⚠️  Failed to clear L2: {e}")

        # Clear L3
        if self.l3_enabled and self.mongo_db:
            try:
                await self._l3_clear()
            except Exception as e:
                logger.warning(f"⚠️  Failed to clear L3: {e}")

        logger.info("🧹 All cache levels cleared")

    # ============================================================================
    # L2 CACHE (REDIS) - Stub methods
    # ============================================================================

    async def _l2_get(self, key: str) -> Optional[Any]:
        """Get from Redis (requires external setup)"""
        if not self.redis_cache:
            return None
        # Implementation would use self.redis_cache.get(key)
        return None

    async def _l2_set(
        self, key: str, value: Any, tags: Optional[List[str]] = None
    ) -> None:
        """Set in Redis (requires external setup)"""
        if not self.redis_cache:
            return
        # Implementation would use self.redis_cache.set(key, value, ttl=self.ttl)

    async def _l2_delete(self, key: str) -> None:
        """Delete from Redis (requires external setup)"""
        if not self.redis_cache:
            return
        # Implementation would use self.redis_cache.delete(key)

    async def _l2_clear(self) -> None:
        """Clear Redis (requires external setup)"""
        if not self.redis_cache:
            return
        # Implementation would use self.redis_cache.clear()

    # ============================================================================
    # L3 CACHE (MONGODB) - Stub methods
    # ============================================================================

    async def _l3_get(self, key: str) -> Optional[Any]:
        """Get from MongoDB (requires external setup)"""
        if not self.mongo_db:
            return None
        # Implementation would query MongoDB for cached_key
        return None

    async def _l3_set(
        self, key: str, value: Any, tags: Optional[List[str]] = None
    ) -> None:
        """Set in MongoDB (requires external setup)"""
        if not self.mongo_db:
            return
        # Implementation would insert/update in MongoDB

    async def _l3_delete(self, key: str) -> None:
        """Delete from MongoDB (requires external setup)"""
        if not self.mongo_db:
            return
        # Implementation would delete from MongoDB

    async def _l3_clear(self) -> None:
        """Clear MongoDB (requires external setup)"""
        if not self.mongo_db:
            return
        # Implementation would clear collection in MongoDB

    # ============================================================================
    # STATISTICS
    # ============================================================================

    def get_hit_rate(self) -> float:
        """Get overall cache hit rate"""
        if self.stats["total_requests"] == 0:
            return 0.0

        total_hits = (
            self.stats["l1_hits"] + self.stats["l2_hits"] + self.stats["l3_hits"]
        )
        return round((total_hits / self.stats["total_requests"]) * 100, 1)

    def get_l1_hit_rate(self) -> float:
        """Get L1 hit rate"""
        total_l1 = self.stats["l1_hits"] + self.stats["l1_misses"]
        if total_l1 == 0:
            return 0.0
        return round((self.stats["l1_hits"] / total_l1) * 100, 1)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_requests": self.stats["total_requests"],
            "l1_hits": self.stats["l1_hits"],
            "l1_misses": self.stats["l1_misses"],
            "l1_hit_rate": self.get_l1_hit_rate(),
            "l1_size": self._l1_size(),
            "l1_max_size": self.l1_max_size,
            "l2_hits": self.stats["l2_hits"],
            "l2_misses": self.stats["l2_misses"],
            "l3_hits": self.stats["l3_hits"],
            "l3_misses": self.stats["l3_misses"],
            "overall_hit_rate": self.get_hit_rate(),
            "l2_enabled": self.l2_enabled,
            "l3_enabled": self.l3_enabled,
        }

    def reset_stats(self) -> None:
        """Reset cache statistics"""
        for key in self.stats:
            self.stats[key] = 0
        logger.info("📊 Cache statistics reset")

    def print_stats(self) -> str:
        """Print formatted cache statistics"""
        stats = self.get_stats()
        lines = [
            "╔════════════════════════════════════════╗",
            "║       CACHE STATISTICS                 ║",
            "╠════════════════════════════════════════╣",
            f"║ Total Requests:        {stats['total_requests']:>20} ║",
            f"║ Overall Hit Rate:      {stats['overall_hit_rate']:>19}% ║",
            "╠════════════════════════════════════════╣",
            f"║ L1 (Memory):           {stats['l1_size']:>4}/{stats['l1_max_size']} "
            f"({stats['l1_hit_rate']:>5}% hit)  ║",
            f"║ L2 (Redis):            "
            f"{'Enabled' if stats['l2_enabled'] else 'Disabled':>20} ║",
            f"║ L3 (MongoDB):          "
            f"{'Enabled' if stats['l3_enabled'] else 'Disabled':>20} ║",
            "╠════════════════════════════════════════╣",
            f"║ L1: {stats['l1_hits']:>5} hits, {stats['l1_misses']:>5} misses           ║",
            f"║ L2: {stats['l2_hits']:>5} hits, {stats['l2_misses']:>5} misses           ║",
            f"║ L3: {stats['l3_hits']:>5} hits, {stats['l3_misses']:>5} misses           ║",
            "╚════════════════════════════════════════╝",
        ]
        return "\n".join(lines)


# Global singleton instance
_advanced_cache: Optional[AdvancedCache] = None


def get_advanced_cache(
    l1_max_size: int = 100, l2_enabled: bool = True, l3_enabled: bool = True
) -> AdvancedCache:
    """Get or create advanced cache singleton"""
    global _advanced_cache
    if _advanced_cache is None:
        _advanced_cache = AdvancedCache(
            l1_max_size=l1_max_size, l2_enabled=l2_enabled, l3_enabled=l3_enabled
        )
    return _advanced_cache
