"""
Unit tests for Cache Coordinator (L1/L2/L3 unified access).

Module under test:
    samplemind.core.cache.cache_coordinator
        — CacheCoordinator, get_cache_coordinator

Tests:
    TestCacheCoordinatorRead
        - Multi-layer fallthrough (L1 → L2 → compute).
        - L2 → L1 promotion on cache hits.
        - Compute function populates L1 on miss.
        - L2 errors fall back to compute gracefully.
        - Custom TTL passed through to compute.
    TestCacheCoordinatorWrite
        - Write-through strategy (L1 + L2 simultaneous).
        - TTL determination by key prefix (search, feature, analysis,
          clap, unknown).
        - Custom TTL override, promote_to_l1 flag, L2 error isolation.
        - S3 archival for long-lived data; skip for short-lived data.
    TestCacheCoordinatorInvalidation
        - Specific key invalidation (L1 + L2).
        - Full cache clear.
        - Pattern-based invalidation (glob-style, e.g. ``feature:*``).
        - L2 delete error does not break L1 invalidation.
    TestCacheCoordinatorStatistics
        - Statistics aggregation across L1/L2/L3.
        - ``_should_archive`` decision logic.
        - Glob pattern matching helper.
    TestCacheCoordinatorIntegration
        - Audio analysis caching workflow.
        - Search with compute fallback (miss → compute → hit).
        - Invalidation-on-update pattern (``*:sample1``).
        - Concurrent reads with L2 promotion.
    TestCacheCoordinatorSingleton
        - get_cache_coordinator returns same instance on repeated calls.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

# Mock imports to avoid dependency issues during testing
import sys
from unittest.mock import MagicMock

sys_modules_backup = {}


@pytest.fixture(autouse=True)
def mock_imports(monkeypatch):
    """Mock optional imports that might not be installed"""
    # Mock jsonpickle if not available
    mock_jsonpickle = MagicMock()
    mock_jsonpickle.encode = lambda x: str(x)
    mock_jsonpickle.decode = lambda x: x
    sys.modules["jsonpickle"] = mock_jsonpickle

    monkeypatch.setitem(sys.modules, "jsonpickle", mock_jsonpickle)


@pytest.fixture
def mock_redis_cache():
    """Create mock Redis cache"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    cache.delete = AsyncMock(return_value=True)
    cache.clear = AsyncMock(return_value=True)
    cache.delete_pattern = AsyncMock(return_value=0)
    cache.get_stats = AsyncMock(return_value={"hits": 0, "misses": 0})
    return cache


@pytest.fixture
def mock_s3_provider():
    """Create mock S3 provider"""
    provider = AsyncMock()
    provider.get_async = AsyncMock(return_value=None)
    provider.put_async = AsyncMock(return_value=True)
    provider.delete_async = AsyncMock(return_value=True)
    return provider


@pytest.fixture
def coordinator(mock_redis_cache, mock_s3_provider):
    """Create cache coordinator with mocks"""
    from samplemind.core.cache.cache_coordinator import CacheCoordinator

    coordinator = CacheCoordinator(
        redis_cache=mock_redis_cache,
        s3_provider=mock_s3_provider,
        enable_l3=False,
    )
    yield coordinator
    # Cleanup
    coordinator.l1_cache.clear()


class TestCacheCoordinatorRead:
    """Test read operations (get)"""

    @pytest.mark.asyncio
    async def test_get_from_l1(self, coordinator):
        """Test getting value from L1 cache"""
        coordinator.l1_cache.set("test:key", "value_from_l1")

        result = await coordinator.get("test:key")

        assert result == "value_from_l1"

    @pytest.mark.asyncio
    async def test_get_from_l2_promotes_to_l1(self, coordinator):
        """Test getting from L2 promotes to L1"""
        coordinator.l2_cache.get.return_value = "value_from_l2"

        result = await coordinator.get("test:key")

        assert result == "value_from_l2"
        # Value should now be in L1
        assert coordinator.l1_cache.get("test:key") == "value_from_l2"

    @pytest.mark.asyncio
    async def test_get_with_compute_function(self, coordinator):
        """Test get with compute function on miss"""

        async def compute():
            return "computed_value"

        result = await coordinator.get("test:key", compute_fn=compute)

        assert result == "computed_value"
        # Should be cached in L1
        assert coordinator.l1_cache.get("test:key") == "computed_value"

    @pytest.mark.asyncio
    async def test_get_miss_without_compute(self, coordinator):
        """Test get miss without compute function"""
        result = await coordinator.get("nonexistent:key")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_fallthrough_l1_miss_l2_hit(self, coordinator):
        """Test complete fallthrough: L1 miss → L2 hit"""
        coordinator.l2_cache.get.return_value = "redis_value"

        result = await coordinator.get("test:key")

        assert result == "redis_value"
        coordinator.l2_cache.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_l2_error_fallback(self, coordinator):
        """Test L2 error doesn't break get"""
        coordinator.l2_cache.get.side_effect = Exception("Redis error")

        async def compute():
            return "fallback_value"

        result = await coordinator.get("test:key", compute_fn=compute)

        assert result == "fallback_value"

    @pytest.mark.asyncio
    async def test_get_custom_ttl(self, coordinator):
        """Test get with custom TTL passed to compute"""

        async def compute():
            return "value"

        await coordinator.get("test:key", compute_fn=compute, ttl_seconds=1800)

        # Value should be in L1 with correct TTL
        # Can't directly check TTL, but we can verify it was set
        assert coordinator.l1_cache.get("test:key") == "value"
        coordinator.l2_cache.set.assert_called_once()


class TestCacheCoordinatorWrite:
    """Test write operations (set)"""

    @pytest.mark.asyncio
    async def test_set_writes_to_l1_and_l2(self, coordinator):
        """Test set writes to both L1 and L2"""
        await coordinator.set("test:key", "test_value")

        # Check L1
        assert coordinator.l1_cache.get("test:key") == "test_value"

        # Check L2 was called
        coordinator.l2_cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_determines_ttl_by_prefix(self, coordinator):
        """Test TTL determination by key prefix"""
        test_cases = [
            ("search:query", 300),  # 5 minutes
            ("feature:extraction", 3600),  # 1 hour
            ("analysis:result", 86400),  # 24 hours
            ("clap:embedding", 604800),  # 7 days
            ("unknown:key", 3600),  # default 1 hour
        ]

        for key, expected_ttl in test_cases:
            ttl = coordinator._determine_ttl(key)
            assert ttl == expected_ttl, f"Key {key} should use TTL {expected_ttl}, got {ttl}"

    @pytest.mark.asyncio
    async def test_set_with_custom_ttl(self, coordinator):
        """Test set with explicit TTL override"""
        await coordinator.set("test:key", "value", ttl_seconds=7200)

        coordinator.l2_cache.set.assert_called_once()
        call_args = coordinator.l2_cache.set.call_args
        assert call_args.kwargs["ttl"] == 7200

    @pytest.mark.asyncio
    async def test_set_promotes_to_l1(self, coordinator):
        """Test promote_to_l1 parameter"""
        await coordinator.set("test:key", "value", promote_to_l1=True)

        assert coordinator.l1_cache.get("test:key") == "value"

    @pytest.mark.asyncio
    async def test_set_without_l1_promotion(self, coordinator):
        """Test set with promote_to_l1=False"""
        await coordinator.set("test:key", "value", promote_to_l1=False)

        # Still in L2
        coordinator.l2_cache.set.assert_called_once()

        # Not in L1 (unless L2 promoted it)
        # L1 should not have it from set operation
        # (it's only populated on get from L1 cache operation)

    @pytest.mark.asyncio
    async def test_set_l2_error_doesnt_fail_l1(self, coordinator):
        """Test L2 error doesn't prevent L1 write"""
        coordinator.l2_cache.set.side_effect = Exception("Redis error")

        await coordinator.set("test:key", "value")

        # L1 should still be written
        assert coordinator.l1_cache.get("test:key") == "value"

    @pytest.mark.asyncio
    async def test_set_archives_to_s3(self, coordinator):
        """Test set archives long-lived data to S3"""
        coordinator.enable_l3 = True

        await coordinator.set("analysis:results", {"data": "test"})

        # Check that S3 put was called for archival
        coordinator.l3_provider.put_async.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_skips_s3_for_short_lived(self, coordinator):
        """Test set skips S3 for short-lived data"""
        coordinator.enable_l3 = True
        coordinator.l3_provider.reset_mock()

        await coordinator.set("search:results", {"data": "test"})

        # S3 should not be called for search results
        coordinator.l3_provider.put_async.assert_not_called()


class TestCacheCoordinatorInvalidation:
    """Test cache invalidation operations"""

    @pytest.mark.asyncio
    async def test_invalidate_specific_key(self, coordinator):
        """Test invalidating specific key"""
        coordinator.l1_cache.set("test:key", "value")

        await coordinator.invalidate("test:key")

        assert coordinator.l1_cache.get("test:key") is None
        coordinator.l2_cache.delete.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_invalidate_all(self, coordinator):
        """Test invalidating entire cache"""
        coordinator.l1_cache.set("key1", "v1")
        coordinator.l1_cache.set("key2", "v2")

        await coordinator.invalidate()

        assert len(coordinator.l1_cache._cache) == 0
        coordinator.l2_cache.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, coordinator):
        """Test pattern-based invalidation"""
        coordinator.l1_cache.set("feature:file1", "v1")
        coordinator.l1_cache.set("feature:file2", "v2")
        coordinator.l1_cache.set("tag:file1", "v3")

        await coordinator.invalidate_pattern("feature:*")

        assert coordinator.l1_cache.get("feature:file1") is None
        assert coordinator.l1_cache.get("feature:file2") is None
        assert coordinator.l1_cache.get("tag:file1") == "v3"

    @pytest.mark.asyncio
    async def test_invalidate_with_l2_error(self, coordinator):
        """Test L2 delete error doesn't break invalidation"""
        coordinator.l2_cache.delete.side_effect = Exception("Redis error")
        coordinator.l1_cache.set("test:key", "value")

        # Should not raise
        await coordinator.invalidate("test:key")

        assert coordinator.l1_cache.get("test:key") is None


class TestCacheCoordinatorStatistics:
    """Test statistics and monitoring"""

    @pytest.mark.asyncio
    async def test_get_stats(self, coordinator):
        """Test statistics aggregation"""
        coordinator.l1_cache.set("key1", "value1")
        coordinator.l1_cache.get("key1")  # hit
        coordinator.l1_cache.get("key2")  # miss

        coordinator.l2_cache.get_stats.return_value = {"hits": 5, "misses": 2}

        stats = coordinator.get_stats()

        assert "l1_memory" in stats
        assert "l2_redis" in stats
        assert stats["l3_enabled"] is False

    def test_should_archive(self, coordinator):
        """Test archive decision logic"""
        assert coordinator._should_archive("analysis:results") is True
        assert coordinator._should_archive("clap:embeddings") is True
        assert coordinator._should_archive("search:query") is False
        assert coordinator._should_archive("recommend:playlist") is False
        assert coordinator._should_archive("temp:staging") is False

    def test_match_pattern(self, coordinator):
        """Test glob pattern matching"""
        assert coordinator._match_pattern("feature:file1.wav", "feature:*") is True
        assert coordinator._match_pattern("feature:file1.wav", "tag:*") is False
        assert coordinator._match_pattern("analysis:deep:v1", "analysis:*") is True


class TestCacheCoordinatorIntegration:
    """Integration tests with realistic patterns"""

    @pytest.mark.asyncio
    async def test_audio_analysis_workflow(self, coordinator):
        """Test realistic audio analysis caching workflow"""
        # Simulate analysis
        analysis_result = {
            "bpm": 140.5,
            "key": "A minor",
            "features": {"mfcc": [0.1, 0.2]},
        }

        # Store analysis result
        await coordinator.set("analysis:file1", analysis_result, ttl_seconds=86400)

        # Later, retrieve it
        cached = await coordinator.get("analysis:file1")

        assert cached == analysis_result

    @pytest.mark.asyncio
    async def test_search_with_compute_fallback(self, coordinator):
        """Test search with fallback computation"""

        async def search_compute():
            # Simulate search computation
            return [
                {"id": "s1", "score": 0.95},
                {"id": "s2", "score": 0.87},
            ]

        # First call - misses, computes
        results1 = await coordinator.get(
            "search:trap:bpm>120", compute_fn=search_compute, ttl_seconds=300
        )

        # Second call - hits L1
        results2 = await coordinator.get("search:trap:bpm>120")

        assert results1 == results2
        assert results2[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_cache_invalidation_on_update(self, coordinator):
        """Test cache invalidation after sample update"""
        # Cache initial data
        await coordinator.set("analysis:sample1", {"bpm": 120})
        await coordinator.set("tag:sample1", ["trap"])

        # Verify cached
        assert await coordinator.get("analysis:sample1") is not None

        # Update happens - invalidate cache
        await coordinator.invalidate_pattern("*:sample1")

        # Cache should be cleared
        assert await coordinator.get("analysis:sample1") is None

    @pytest.mark.asyncio
    async def test_concurrent_reads_after_l2_write(self, coordinator):
        """Test concurrent reads with L2 promotion"""
        value = {"data": "shared"}
        coordinator.l2_cache.get.return_value = value

        # Simulate concurrent reads
        tasks = [coordinator.get("shared:key") for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # All should get the value
        assert all(r == value for r in results)

        # L2 should only be called for first actual get (L1 miss)
        # Subsequent calls hit L1


class TestCacheCoordinatorSingleton:
    """Test singleton pattern"""

    @pytest.mark.asyncio
    async def test_get_coordinator_singleton(self):
        """Test get_cache_coordinator returns same instance"""
        from samplemind.core.cache.cache_coordinator import (
            get_cache_coordinator,
        )

        # Reset singleton for testing
        import samplemind.core.cache.cache_coordinator as coord_module

        coord_module._COORDINATOR_INSTANCE = None

        coord1 = await get_cache_coordinator()
        coord2 = await get_cache_coordinator()

        assert coord1 is coord2
