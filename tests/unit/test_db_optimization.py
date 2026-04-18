"""
Unit tests for database optimization (query caching and pool tuning).

Modules under test:
    samplemind.core.database.db_optimization
        — ConnectionPoolConfig, DatabaseOptimizationManager,
          BatchOperationHelper, get_database_optimizer,
          STRATEGIC_INDEXES, CACHE_PRIORITY_QUERIES
    samplemind.core.database.query_cache
        — cached_query, QueryCacheManager, _build_cache_key,
          get_query_cache_manager

Tests:
    TestConnectionPoolConfig
        - Default and custom pool configuration values.
        - Conversion to SQLAlchemy kwargs (to_dict).
    TestDatabaseOptimizationManager
        - Singleton pattern (get_database_optimizer).
        - Pool config retrieval.
        - Index definitions: all models, single model, metadata validation.
        - Migration SQL generation for SQLite and PostgreSQL dialects.
        - Query optimization hints (recent_samples, by_genre, by_bpm_and_key).
        - Pool stats query for PostgreSQL.
    TestStrategicIndexes
        - Sample, user, and library indexes are defined with required
          metadata (name, columns, unique, description).
    TestCacheQueryDecorator
        - Decorator can be applied and stores ``_cache_prefix``.
        - Cache key building from positional and keyword arguments.
        - Different arguments produce different keys.
    TestQueryCacheManager
        - Manager initialisation sets a coordinator.
        - Invalidation rules exist for TortoiseSample and TortoiseLibrary.
        - ``invalidate_on_model_update`` and ``get_cache_stats`` run
          without error.
    TestBatchOperationHelper
        - bulk_create_samples and bulk_update_samples function signatures.
    TestCachePriorityQueries
        - Important queries have defined cache priorities (TTL + reason).
    TestDatabaseOptimizationIntegration
        - Full workflow: pool config → migration SQL → query hints.
    TestDatabaseOptimizationSingleton
        - Optimizer and query-cache-manager singleton patterns.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from samplemind.core.database.db_optimization import (
    ConnectionPoolConfig,
    DatabaseOptimizationManager,
    BatchOperationHelper,
    get_database_optimizer,
    STRATEGIC_INDEXES,
    CACHE_PRIORITY_QUERIES,
)
from samplemind.core.database.query_cache import (
    cached_query,
    QueryCacheManager,
    _build_cache_key,
    get_query_cache_manager,
)


class TestConnectionPoolConfig:
    """Test connection pool configuration"""

    def test_default_config(self):
        """Test default pool configuration"""
        config = ConnectionPoolConfig()

        assert config.pool_size == 40  # Phase 7.2: increased
        assert config.max_overflow == 80  # Phase 7.2: increased
        assert config.recycle_seconds == 1800  # Phase 7.2: decreased
        assert config.connect_timeout == 10

    def test_custom_config(self):
        """Test custom pool configuration"""
        config = ConnectionPoolConfig(
            pool_size=50,
            max_overflow=100,
            recycle_seconds=900,
        )

        assert config.pool_size == 50
        assert config.max_overflow == 100
        assert config.recycle_seconds == 900

    def test_to_dict(self):
        """Test conversion to SQLAlchemy kwargs"""
        config = ConnectionPoolConfig(pool_size=30, max_overflow=60)
        pool_kwargs = config.to_dict()

        assert pool_kwargs["pool_size"] == 30
        assert pool_kwargs["max_overflow"] == 60
        assert pool_kwargs["pool_recycle"] == 1800
        assert pool_kwargs["pool_pre_ping"] is True


class TestDatabaseOptimizationManager:
    """Test database optimization manager"""

    def test_manager_creation(self):
        """Test manager singleton creation"""
        manager = get_database_optimizer()
        manager2 = get_database_optimizer()

        assert manager is manager2

    def test_get_pool_config(self):
        """Test pool config retrieval"""
        manager = DatabaseOptimizationManager()
        config = manager.get_pool_config()

        assert isinstance(config, ConnectionPoolConfig)
        assert config.pool_size == 40

    def test_get_index_definitions_all(self):
        """Test getting all index definitions"""
        manager = DatabaseOptimizationManager()
        indexes = manager.get_index_definitions()

        assert "tortoise_sample" in indexes
        assert "tortoise_user" in indexes
        assert "tortoise_library" in indexes

    def test_get_index_definitions_model(self):
        """Test getting indexes for specific model"""
        manager = DatabaseOptimizationManager()
        indexes = manager.get_index_definitions("tortoise_sample")

        assert len(indexes) > 0
        assert indexes[0]["name"] == "idx_samples_bpm_key"

    def test_migration_sql_sqlite(self):
        """Test generating SQLite migration SQL"""
        manager = DatabaseOptimizationManager()
        statements = manager.get_migration_sql("sqlite")

        assert len(statements) > 0
        # Check SQLite syntax
        for stmt in statements:
            assert "CREATE" in stmt
            assert "INDEX" in stmt
            assert "IF NOT EXISTS" in stmt
            assert stmt.endswith(";")

    def test_migration_sql_postgresql(self):
        """Test generating PostgreSQL migration SQL"""
        manager = DatabaseOptimizationManager()
        statements = manager.get_migration_sql("postgresql")

        assert len(statements) > 0
        # Check PostgreSQL syntax
        for stmt in statements:
            assert "CREATE" in stmt
            assert "INDEX" in stmt
            assert "CONCURRENTLY" in stmt

    def test_query_optimization_hints(self):
        """Test query optimization hints"""
        manager = DatabaseOptimizationManager()
        hints = manager.get_query_optimization_hints()

        assert "recent_samples" in hints
        assert "by_genre" in hints
        assert "by_bpm_and_key" in hints

    def test_pool_stats_query_postgresql(self):
        """Test pool stats query for PostgreSQL"""
        manager = DatabaseOptimizationManager()
        query = manager.get_pool_stats_query("postgresql")

        assert "pg_stat_activity" in query
        assert "datname" in query


class TestStrategicIndexes:
    """Test index definitions"""

    def test_sample_indexes_exist(self):
        """Test sample indexes are defined"""
        assert "tortoise_sample" in STRATEGIC_INDEXES
        sample_indexes = STRATEGIC_INDEXES["tortoise_sample"]

        # Should have: bpm_key, genre, created_at, owner
        assert len(sample_indexes) >= 4

        index_names = [idx["name"] for idx in sample_indexes]
        assert "idx_samples_bpm_key" in index_names
        assert "idx_samples_created_at" in index_names

    def test_index_metadata(self):
        """Test index definitions have required metadata"""
        for model, indexes in STRATEGIC_INDEXES.items():
            for index in indexes:
                assert "name" in index
                assert "columns" in index
                assert "unique" in index
                assert "description" in index
                assert isinstance(index["columns"], list)


class TestCacheQueryDecorator:
    """Test cached_query decorator"""

    @pytest.mark.asyncio
    async def test_decorator_creation(self):
        """Test decorator can be applied"""

        @cached_query(cache_key_prefix="test:query")
        async def test_query(param1: str):
            return f"result_{param1}"

        assert hasattr(test_query, "_cache_prefix")
        assert test_query._cache_prefix == "test:query"

    def test_cache_key_building(self):
        """Test cache key generation from args"""
        key = _build_cache_key("samples", ("genre", 50), {})
        assert "samples" in key
        assert "genre" in key
        assert "50" in key

    def test_cache_key_with_kwargs(self):
        """Test cache key with keyword arguments"""
        key = _build_cache_key(
            "search", ("trap",), {"limit": 20, "offset": 0}
        )
        assert "search" in key
        assert "trap" in key
        assert "limit=20" in key

    def test_cache_key_uniqueness(self):
        """Test different args produce different keys"""
        key1 = _build_cache_key("query", ("a",), {})
        key2 = _build_cache_key("query", ("b",), {})

        assert key1 != key2


class TestQueryCacheManager:
    """Test query cache manager"""

    @pytest.mark.asyncio
    async def test_manager_init(self):
        """Test manager initialization"""
        manager = QueryCacheManager()
        await manager.init()

        assert manager.coordinator is not None

    def test_invalidation_rules_exist(self):
        """Test invalidation rules are defined"""
        assert "TortoiseSample" in QueryCacheManager.INVALIDATION_RULES
        assert "TortoiseLibrary" in QueryCacheManager.INVALIDATION_RULES

    @pytest.mark.asyncio
    async def test_invalidate_on_model_update(self):
        """Test cache invalidation on model update"""
        manager = QueryCacheManager()
        await manager.init()

        # Should not raise
        await manager.invalidate_on_model_update("TortoiseSample", model_id="sample123")

    @pytest.mark.asyncio
    async def test_get_cache_stats(self):
        """Test getting cache statistics"""
        manager = QueryCacheManager()
        await manager.init()

        stats = await manager.get_cache_stats()

        assert isinstance(stats, dict)


class TestBatchOperationHelper:
    """Test batch operation helpers"""

    @pytest.mark.asyncio
    async def test_bulk_create_samples(self):
        """Test bulk create function signature"""
        # Just test that it's callable and handles errors gracefully
        samples = [
            {"filename": "s1.wav", "bpm": 120},
            {"filename": "s2.wav", "bpm": 128},
        ]

        # Mock TortoiseSample
        with patch("samplemind.core.database.db_optimization.TortoiseSample"):
            result = await BatchOperationHelper.bulk_create_samples(samples)
            # Should complete without error (even if mock fails)

    @pytest.mark.asyncio
    async def test_bulk_update_samples(self):
        """Test bulk update function signature"""
        updates = [
            ("sample1", {"bpm": 125}),
            ("sample2", {"key": "A minor"}),
        ]

        # Should complete without raising
        with patch("samplemind.core.database.db_optimization.TortoiseSample"):
            result = await BatchOperationHelper.bulk_update_samples(updates)


class TestCachePriorityQueries:
    """Test cache priority definitions"""

    def test_priority_queries_defined(self):
        """Test important queries have cache priorities"""
        assert "get_user_library" in CACHE_PRIORITY_QUERIES
        assert "search_by_genre" in CACHE_PRIORITY_QUERIES

    def test_priority_query_metadata(self):
        """Test priority query has TTL and reason"""
        for query_name, priority_info in CACHE_PRIORITY_QUERIES.items():
            assert "ttl" in priority_info
            assert "reason" in priority_info
            assert priority_info["ttl"] > 0


class TestDatabaseOptimizationIntegration:
    """Integration tests for database optimization"""

    def test_index_coverage(self):
        """Test all essential models have indexes"""
        indexed_models = list(STRATEGIC_INDEXES.keys())

        # Core models that should be indexed
        required_models = [
            "tortoise_sample",
            "tortoise_user",
            "tortoise_library",
        ]

        for model in required_models:
            assert model in indexed_models, f"Missing indexes for {model}"

    def test_optimization_manager_workflow(self):
        """Test typical optimization workflow"""
        manager = DatabaseOptimizationManager()

        # Get pool config for SQLAlchemy
        pool_kwargs = manager.get_pool_config().to_dict()
        assert "pool_size" in pool_kwargs

        # Get migration SQL for deployment
        migrations = manager.get_migration_sql("postgresql")
        assert len(migrations) > 0

        # Get query hints for developers
        hints = manager.get_query_optimization_hints()
        assert len(hints) > 0


class TestDatabaseOptimizationSingleton:
    """Test singleton pattern"""

    def test_get_optimizer_returns_same_instance(self):
        """Test optimizer singleton"""
        opt1 = get_database_optimizer()
        opt2 = get_database_optimizer()

        assert opt1 is opt2

    @pytest.mark.asyncio
    async def test_get_query_cache_manager_singleton(self):
        """Test query cache manager singleton"""
        manager1 = await get_query_cache_manager()
        manager2 = await get_query_cache_manager()

        assert manager1 is manager2
