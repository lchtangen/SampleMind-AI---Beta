"""
Unit tests for L1 in-memory LRU cache.

Tests:
- Basic get/set operations
- TTL expiration
- LRU eviction (max entries and memory)
- Statistics tracking
- Cache invalidation
"""

import pytest
import time
from samplemind.core.cache.lru_cache import L1LRUCache, L1CacheEntry, get_l1_cache


class TestL1CacheEntry:
    """Test L1CacheEntry data structure"""

    def test_entry_creation(self):
        """Test entry is created with correct metadata"""
        entry = L1CacheEntry(
            key="test:key",
            value={"data": "value"},
            created_at=time.time(),
            last_accessed=time.time(),
            ttl_seconds=3600,
            size_bytes=128,
        )

        assert entry.key == "test:key"
        assert entry.value == {"data": "value"}
        assert entry.ttl_seconds == 3600
        assert entry.access_count == 0

    def test_entry_expiration(self):
        """Test entry expiration check"""
        now = time.time()
        entry = L1CacheEntry(
            key="test:key",
            value="test",
            created_at=now - 3700,  # 3700 seconds ago
            last_accessed=now,
            ttl_seconds=3600,  # expires after 1 hour
        )

        assert entry.is_expired() is False  # Just created, need to check time

    def test_entry_is_expired(self):
        """Test entry that has expired"""
        now = time.time()
        entry = L1CacheEntry(
            key="test:key",
            value="test",
            created_at=now - 7200,  # 7200 seconds (2 hours) ago
            last_accessed=now,
            ttl_seconds=3600,  # expires after 1 hour
        )

        assert entry.is_expired() is True


class TestL1LRUCache:
    """Test L1LRUCache functionality"""

    def test_cache_creation(self):
        """Test cache is initialized correctly"""
        cache = L1LRUCache(
            max_entries=1000,
            max_memory_mb=256,
            default_ttl_seconds=1800,
        )

        assert cache.max_entries == 1000
        assert cache.max_memory_bytes == 256 * 1024 * 1024
        assert cache.default_ttl_seconds == 1800
        assert len(cache._cache) == 0

    def test_set_and_get(self):
        """Test basic set/get operations"""
        cache = L1LRUCache(max_entries=100)

        cache.set("test:key", {"value": 123})
        result = cache.get("test:key")

        assert result == {"value": 123}
        assert cache.hits == 1
        assert cache.misses == 0

    def test_get_nonexistent_key(self):
        """Test getting nonexistent key"""
        cache = L1LRUCache()

        result = cache.get("nonexistent:key")

        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_ttl_expiration(self):
        """Test entry expires after TTL"""
        cache = L1LRUCache(default_ttl_seconds=1)

        cache.set("expiring:key", "value")
        assert cache.get("expiring:key") == "value"

        # Sleep past TTL
        time.sleep(1.1)

        result = cache.get("expiring:key")
        assert result is None

    def test_lru_eviction_by_count(self):
        """Test LRU eviction when max entries exceeded"""
        cache = L1LRUCache(max_entries=3, max_memory_mb=1024)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # This should trigger eviction of key1 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        assert cache.evictions >= 1

    def test_lru_eviction_promotes_on_access(self):
        """Test accessing old entry makes it LRU-proof"""
        cache = L1LRUCache(max_entries=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        _ = cache.get("key1")

        # This should evict key2, not key1
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None

    def test_delete(self):
        """Test explicit key deletion"""
        cache = L1LRUCache()

        cache.set("test:key", "value")
        assert cache.get("test:key") == "value"

        deleted = cache.delete("test:key")
        assert deleted is True
        assert cache.get("test:key") is None

    def test_delete_nonexistent(self):
        """Test deleting nonexistent key"""
        cache = L1LRUCache()
        deleted = cache.delete("nonexistent:key")
        assert deleted is False

    def test_clear(self):
        """Test clearing entire cache"""
        cache = L1LRUCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.hits = 10
        cache.misses = 5

        cache.clear()

        assert len(cache._cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_has(self):
        """Test key existence check"""
        cache = L1LRUCache()

        cache.set("exists:key", "value")

        assert cache.has("exists:key") is True
        assert cache.has("nonexistent:key") is False

    def test_has_expired_key(self):
        """Test has() with expired key"""
        cache = L1LRUCache(default_ttl_seconds=1)

        cache.set("expiring:key", "value")
        assert cache.has("expiring:key") is True

        time.sleep(1.1)
        assert cache.has("expiring:key") is False

    def test_statistics(self):
        """Test cache statistics"""
        cache = L1LRUCache(max_entries=100, max_memory_mb=256)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # hit
        cache.get("key3")  # miss

        stats = cache.get_stats()

        assert stats["entries"] == 2
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert 0.0 <= stats["hit_rate"] <= 1.0

    def test_custom_ttl(self):
        """Test custom TTL per entry"""
        cache = L1LRUCache(default_ttl_seconds=3600)

        cache.set("slow", "value", ttl_seconds=1)
        cache.set("fast", "value", ttl_seconds=3600)

        time.sleep(1.1)

        assert cache.get("slow") is None
        assert cache.get("fast") == "value"

    def test_memory_limit(self):
        """Test eviction by memory limit"""
        cache = L1LRUCache(max_entries=1000, max_memory_mb=1)  # 1MB limit

        # Add entries until we exceed memory limit
        for i in range(100):
            large_value = "x" * 20000  # ~20KB per entry
            cache.set(f"key{i}", large_value)

        # Cache should have evicted entries
        stats = cache.get_stats()
        assert cache.evictions > 0

    def test_singleton_pattern(self):
        """Test get_l1_cache returns same instance"""
        cache1 = get_l1_cache()
        cache2 = get_l1_cache()

        assert cache1 is cache2

    def test_singleton_with_config(self):
        """Test singleton returns existing instance with config params ignored"""
        # Reset singleton for this test
        import samplemind.core.cache.lru_cache as lru_module

        lru_module._L1_CACHE_INSTANCE = None

        cache1 = get_l1_cache(max_entries=100)
        cache2 = get_l1_cache(max_entries=5000)

        # cache2 should use cache1's config (100 entries), not 5000
        assert cache1.max_entries == 100
        assert cache2.max_entries == 100
        assert cache1 is cache2


class TestL1CacheIntegration:
    """Integration tests with realistic usage patterns"""

    def test_audio_features_cache(self):
        """Test caching audio features"""
        cache = L1LRUCache(max_entries=1000, default_ttl_seconds=3600)

        # Simulate feature extraction
        features = {
            "bpm": 140.5,
            "key": "A minor",
            "energy": 0.85,
            "mfcc": [0.1, 0.2, 0.3],
        }

        cache.set("audio:features:file1.wav", features)
        cached = cache.get("audio:features:file1.wav")

        assert cached == features

    def test_search_results_cache(self):
        """Test caching search results with short TTL"""
        cache = L1LRUCache(default_ttl_seconds=5)

        results = [
            {"id": "s1", "bpm": 120},
            {"id": "s2", "bpm": 128},
        ]

        cache.set("search:trap:bpm>120", results, ttl_seconds=300)
        cached = cache.get("search:trap:bpm>120")

        assert cached == results
        assert cache.hits == 1

    def test_multiple_access_pattern(self):
        """Test realistic access pattern with varying frequencies"""
        cache = L1LRUCache(max_entries=10)

        # Hot data accessed frequently
        hot_data = {"type": "hot"}
        cache.set("hot:data", hot_data)

        # Access hot data 5 times
        for _ in range(5):
            cache.get("hot:data")

        # Set cold data
        cache.set("cold:data", {"type": "cold"})

        # Trigger eviction - should evict cold data, not hot
        cache.set("new:data", {"type": "new"})

        assert cache.get("hot:data") == hot_data
        assert cache.get("cold:data") is None

    def test_cache_invalidation_pattern(self):
        """Test invalidating cache after sample update"""
        cache = L1LRUCache()

        cache.set("feature:sample1", {"bpm": 120})
        cache.set("tag:sample1", ["trap", "drum"])

        # Simulate sample update - invalidate related cache
        cache.delete("feature:sample1")
        cache.delete("tag:sample1")

        assert cache.get("feature:sample1") is None
        assert cache.get("tag:sample1") is None


class TestL1CachePerformance:
    """Performance tests"""

    def test_get_latency(self):
        """Test get() latency is <1ms for hits"""
        cache = L1LRUCache(max_entries=1000)

        cache.set("test:key", {"data": 123})

        import time

        start = time.perf_counter()
        for _ in range(1000):
            cache.get("test:key")
        elapsed = time.perf_counter() - start

        # Average latency per get
        avg_latency_ms = (elapsed / 1000) * 1000

        assert avg_latency_ms < 1.0, f"Expected <1ms, got {avg_latency_ms:.4f}ms"

    def test_throughput(self):
        """Test cache throughput for sets and gets"""
        cache = L1LRUCache(max_entries=10000)

        import time

        start = time.perf_counter()
        for i in range(1000):
            cache.set(f"key{i}", {"value": i})
            cache.get(f"key{i}")
        elapsed = time.perf_counter() - start

        # 2000 operations (1000 set + 1000 get)
        throughput_ops_per_sec = 2000 / elapsed

        assert throughput_ops_per_sec > 50000, f"Expected >50k ops/sec, got {throughput_ops_per_sec:.0f}"
