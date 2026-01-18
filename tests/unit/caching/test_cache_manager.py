"""Unit tests for advanced cache manager."""

import pytest
import asyncio
import time

from samplemind.core.caching.cache_manager import (
    CacheEntry,
    AdvancedCacheManager,
)


class TestCacheEntry:
    """Test CacheEntry dataclass"""

    def test_entry_creation(self):
        """Test creating a cache entry"""
        entry = CacheEntry(
            key="test_key",
            value={"data": "value"},
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=3600
        )

        assert entry.key == "test_key"
        assert entry.value == {"data": "value"}
        assert entry.access_count == 0

    def test_entry_not_expired(self):
        """Test non-expired entry"""
        now = time.time()
        entry = CacheEntry(
            key="test_key",
            value="value",
            created_at=now,
            last_accessed=now,
            ttl=3600
        )

        assert entry.is_expired() is False

    def test_entry_expired(self):
        """Test expired entry"""
        past = time.time() - 7200  # 2 hours ago
        entry = CacheEntry(
            key="test_key",
            value="value",
            created_at=past,
            last_accessed=past,
            ttl=3600
        )

        assert entry.is_expired() is True

    def test_entry_recency_score(self):
        """Test recency score calculation"""
        now = time.time()
        entry = CacheEntry(
            key="test_key",
            value="value",
            created_at=now,
            last_accessed=now,
            ttl=3600
        )

        recency = entry.get_recency()
        assert recency == pytest.approx(1.0)

        # Older entry
        entry.last_accessed = now - 1800  # 30 min ago
        recency = entry.get_recency()
        assert 0.4 < recency < 0.6

    def test_entry_frequency_score(self):
        """Test frequency score calculation"""
        entry = CacheEntry(
            key="test_key",
            value="value",
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=3600,
            access_count=0
        )

        assert entry.get_frequency() == 0.0

        entry.access_count = 50
        frequency = entry.get_frequency()
        assert frequency == pytest.approx(0.5)

        entry.access_count = 150
        frequency = entry.get_frequency()
        assert frequency == 1.0

    def test_update_access(self):
        """Test updating access information"""
        entry = CacheEntry(
            key="test_key",
            value="value",
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=3600
        )

        assert entry.access_count == 0
        assert len(entry.access_history) == 0

        entry.update_access()

        assert entry.access_count == 1
        assert len(entry.access_history) == 1


class TestAdvancedCacheManager:
    """Test advanced cache manager"""

    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test manager initialization"""
        manager = AdvancedCacheManager(max_memory_mb=512, k=2, adaptive_ttl=True)

        assert len(manager.entries) == 0
        assert manager.hits == 0
        assert manager.misses == 0
        assert manager.evictions == 0

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test basic set and get operations"""
        manager = AdvancedCacheManager()

        await manager.set("key1", {"data": "value1"}, size_bytes=1024)

        value = await manager.get("key1")
        assert value == {"data": "value1"}
        assert manager.hits == 1

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss"""
        manager = AdvancedCacheManager()

        value = await manager.get("nonexistent")
        assert value is None
        assert manager.misses == 1

    @pytest.mark.asyncio
    async def test_entry_expiration(self):
        """Test entry expiration"""
        manager = AdvancedCacheManager()

        # Add entry with short TTL
        await manager.set("key1", "value", ttl=1, size_bytes=100)

        # Should exist immediately
        value = await manager.get("key1")
        assert value is not None

        # Wait for expiration
        await asyncio.sleep(1.1)

        # Should be expired
        value = await manager.get("key1")
        assert value is None

    @pytest.mark.asyncio
    async def test_hit_ratio(self):
        """Test hit ratio calculation"""
        manager = AdvancedCacheManager()

        await manager.set("key1", "value1", size_bytes=100)
        await manager.set("key2", "value2", size_bytes=100)

        # Get hits
        await manager.get("key1")
        await manager.get("key1")
        await manager.get("key2")

        # Get misses
        await manager.get("nonexistent")
        await manager.get("nonexistent")

        ratio = manager.get_hit_ratio()
        assert ratio == pytest.approx(0.6)  # 3 hits / 5 total

    @pytest.mark.asyncio
    async def test_adaptive_ttl_frequency_based(self):
        """Test adaptive TTL based on frequency"""
        manager = AdvancedCacheManager(adaptive_ttl=True)

        # New entry should get medium TTL
        ttl1 = manager._calculate_adaptive_ttl("new_key")
        assert ttl1 == manager.medium_ttl

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting entries"""
        manager = AdvancedCacheManager()

        await manager.set("key1", "value", size_bytes=100)
        assert "key1" in manager.entries

        await manager.delete("key1")
        assert "key1" not in manager.entries

    @pytest.mark.asyncio
    async def test_cache_size_tracking(self):
        """Test tracking cache size"""
        manager = AdvancedCacheManager()

        await manager.set("key1", "value1", size_bytes=1000)
        await manager.set("key2", "value2", size_bytes=2000)

        size = manager._get_cache_size()
        assert size == 3000

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """Test cleaning up expired entries"""
        manager = AdvancedCacheManager()

        # Add entries with different TTLs
        await manager.set("key1", "value1", ttl=1, size_bytes=100)
        await manager.set("key2", "value2", ttl=3600, size_bytes=100)

        assert len(manager.entries) == 2

        # Wait for first to expire
        await asyncio.sleep(1.1)

        # Cleanup
        cleaned = manager.cleanup_expired()

        assert cleaned == 1
        assert len(manager.entries) == 1

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting cache statistics"""
        manager = AdvancedCacheManager(max_memory_mb=512)

        await manager.set("key1", "value1", size_bytes=1000)
        await manager.set("key2", "value2", size_bytes=2000)

        await manager.get("key1")
        await manager.get("nonexistent")

        stats = manager.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["entries"] == 2
        assert "hit_ratio" in stats
        assert "memory_utilization" in stats

    @pytest.mark.asyncio
    async def test_get_top_accessed(self):
        """Test getting top accessed entries"""
        manager = AdvancedCacheManager()

        await manager.set("key1", "value1", size_bytes=100)
        await manager.set("key2", "value2", size_bytes=100)
        await manager.set("key3", "value3", size_bytes=100)

        # Access key1 multiple times
        for _ in range(5):
            await manager.get("key1")

        # Access key2 twice
        for _ in range(2):
            await manager.get("key2")

        top = manager.get_top_accessed(limit=3)

        assert len(top) == 3
        # key1 should be first
        assert top[0]["key"] == "key1"
        assert top[0]["access_count"] == 5

    @pytest.mark.asyncio
    async def test_get_oldest_entries(self):
        """Test getting oldest entries"""
        manager = AdvancedCacheManager()

        # Add entries at different times
        await manager.set("key1", "value1", size_bytes=100)
        await asyncio.sleep(0.1)
        await manager.set("key2", "value2", size_bytes=100)
        await asyncio.sleep(0.1)
        await manager.set("key3", "value3", size_bytes=100)

        oldest = manager.get_oldest_entries(limit=3)

        assert len(oldest) == 3
        # key1 should be oldest
        assert oldest[0]["key"] == "key1"

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test clearing cache"""
        manager = AdvancedCacheManager()

        await manager.set("key1", "value1", size_bytes=100)
        await manager.set("key2", "value2", size_bytes=100)

        assert len(manager.entries) == 2

        manager.clear()

        assert len(manager.entries) == 0
        assert manager.hits == 0
        assert manager.misses == 0

    @pytest.mark.asyncio
    async def test_lruk_eviction_triggers(self):
        """Test LRU-K eviction under memory pressure"""
        manager = AdvancedCacheManager(max_memory_mb=1)  # 1MB limit

        # Add entries until eviction is triggered
        # 1MB = 1024*1024 = 1,048,576 bytes
        # Each entry is 10,000 bytes, so ~104 entries fit
        for i in range(150):  # More than can fit
            await manager.set(f"key_{i}", f"value_{i}", size_bytes=10000)

        # Should have evicted some entries
        assert manager.evictions > 0
        # Cache size should be under or near limit
        cache_size_bytes = manager._get_cache_size()
        assert cache_size_bytes <= manager.max_memory_bytes * 1.5  # Allow 50% overshoot

    @pytest.mark.asyncio
    async def test_global_instance(self):
        """Test global manager instance"""
        from samplemind.core.caching.cache_manager import init_manager, get_manager

        # Initialize
        manager1 = init_manager(max_memory_mb=512)
        assert manager1 is not None

        # Get same instance
        manager2 = get_manager()
        assert manager1 is manager2
