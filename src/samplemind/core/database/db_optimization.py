"""
Database Optimization Configuration and Management.

Handles:
- Connection pool tuning (size, overflow, recycling)
- Strategic index definitions
- Migration strategies
- Performance monitoring
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Connection pool tuning configuration"""

    # Pool size: number of persistent connections to keep
    # Phase 7.2: Increase from 20 to 40 for higher concurrency
    pool_size: int = 40

    # Max overflow: additional connections allowed beyond pool_size
    # Phase 7.2: Increase from 40 to 80 (2x pool_size for burst capacity)
    max_overflow: int = 80

    # Recycle interval (seconds): how often to recycle stale connections
    # Phase 7.2: Decrease from 3600 to 1800 for faster stale cleanup
    recycle_seconds: int = 1800

    # Connection timeout
    connect_timeout: int = 10

    # Query timeout
    query_timeout: int = 30

    # Echo SQL for debugging (disable in production)
    echo: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to SQLAlchemy pool_kwargs compatible dict"""
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_recycle": self.recycle_seconds,
            "pool_pre_ping": True,  # Verify connection before use
            "echo_pool": self.echo,
        }


# Strategic indexes for Phase 7.2
STRATEGIC_INDEXES = {
    "tortoise_sample": [
        {
            "name": "idx_samples_bpm_key",
            "columns": ["bpm", "key"],
            "unique": False,
            "description": "Composite index for BPM + key filtering",
        },
        {
            "name": "idx_samples_genre",
            "columns": ["genre_labels"],
            "unique": False,
            "description": "Genre filtering (if using JSON array)",
        },
        {
            "name": "idx_samples_created_at",
            "columns": ["created_at"],
            "unique": False,
            "order": "DESC",
            "description": "Recent samples query",
        },
        {
            "name": "idx_samples_owner",
            "columns": ["owner_id", "created_at"],
            "unique": False,
            "description": "User's samples with date order",
        },
    ],
    "tortoise_user": [
        {
            "name": "idx_user_tier_active",
            "columns": ["tier", "is_active"],
            "unique": False,
            "description": "Tier-based user filtering",
        },
    ],
    "tortoise_library": [
        {
            "name": "idx_library_owner_created",
            "columns": ["owner_id", "created_at"],
            "unique": False,
            "order": "DESC",
            "description": "User's libraries by creation date",
        },
    ],
    "tortoise_pack": [
        {
            "name": "idx_pack_status_published",
            "columns": ["status", "published_at"],
            "unique": False,
            "order": "DESC",
            "description": "Published packs (for marketplace)",
        },
    ],
}

# Query patterns that benefit most from caching
CACHE_PRIORITY_QUERIES = {
    "get_user_library": {
        "ttl": 3600,
        "reason": "User profile rarely changes, high access",
    },
    "list_recent_samples": {
        "ttl": 600,
        "reason": "Recently added samples with frequent queries",
    },
    "search_by_genre": {
        "ttl": 1800,
        "reason": "Genre filtering is common, changes infrequent",
    },
    "get_pack_metadata": {
        "ttl": 3600,
        "reason": "Pack info stable, high reads",
    },
    "count_library_stats": {
        "ttl": 3600,
        "reason": "Stats queries expensive, don't change frequently",
    },
}


class DatabaseOptimizationManager:
    """
    Manages database optimization including indexing and connection pooling.
    """

    def __init__(self):
        self.pool_config = ConnectionPoolConfig()
        self.indexes_applied: dict[str, list[str]] = {}

    def get_pool_config(self) -> ConnectionPoolConfig:
        """Get optimized connection pool configuration"""
        return self.pool_config

    def get_index_definitions(self, model: str = "") -> dict[str, Any]:
        """
        Get index definitions for a model or all.

        Args:
            model: Model name (e.g., "tortoise_sample"), empty = all

        Returns:
            Index definitions
        """
        if model:
            return STRATEGIC_INDEXES.get(model.lower(), [])

        return STRATEGIC_INDEXES

    def get_migration_sql(self, db_type: str = "sqlite") -> list[str]:
        """
        Generate SQL for creating indexes.

        Args:
            db_type: Database type ("sqlite", "postgresql", etc.)

        Returns:
            List of CREATE INDEX SQL statements
        """
        statements = []

        for model, indexes in STRATEGIC_INDEXES.items():
            table_name = self._model_to_table(model)

            for index_def in indexes:
                columns = ", ".join(index_def["columns"])
                order_clause = f" {index_def.get('order', '')}".rstrip()
                unique_clause = "UNIQUE " if index_def.get("unique") else ""
                name = index_def["name"]

                # SQLite syntax
                if db_type.lower() == "sqlite":
                    sql = f"CREATE {unique_clause}INDEX IF NOT EXISTS {name} ON {table_name} ({columns}{order_clause});"

                # PostgreSQL syntax
                elif db_type.lower() in ("postgres", "postgresql"):
                    sql = f"CREATE {unique_clause}INDEX CONCURRENTLY IF NOT EXISTS {name} ON {table_name} ({columns}{order_clause});"

                else:
                    sql = f"CREATE {unique_clause}INDEX IF NOT EXISTS {name} ON {table_name} ({columns}{order_clause});"

                statements.append(sql)

        return statements

    def get_query_optimization_hints(self) -> dict[str, str]:
        """
        Get hints for optimizing common query patterns.

        Returns:
            Dict of query type → optimization hint
        """
        return {
            "recent_samples": "Use idx_samples_created_at DESC to get latest first",
            "by_genre": "Use idx_samples_genre for genre filtering",
            "by_bpm_and_key": "Use idx_samples_bpm_key composite for both filters",
            "user_library": "Use idx_library_owner_created for user lookup",
            "published_packs": "Use idx_pack_status_published for marketplace queries",
        }

    def _model_to_table(self, model: str) -> str:
        """Convert model name to table name"""
        # e.g., "tortoise_sample" → "samplemind_sample"
        return model.replace("tortoise_", "samplemind_")

    def get_pool_stats_query(self, db_type: str = "postgresql") -> str:
        """
        Get query to monitor connection pool.

        Args:
            db_type: Database type

        Returns:
            SQL query for pool stats
        """
        if db_type.lower() in ("postgres", "postgresql"):
            return """
                SELECT
                    datname,
                    usename,
                    application_name,
                    state,
                    count(*) as connection_count
                FROM pg_stat_activity
                WHERE datname IS NOT NULL
                GROUP BY datname, usename, application_name, state
                ORDER BY connection_count DESC;
            """
        else:
            # SQLite doesn't have built-in connection monitoring
            return "-- SQLite doesn't support connection pool monitoring"


# Batch operation helpers
class BatchOperationHelper:
    """Helpers for batch database operations"""

    @staticmethod
    async def bulk_create_samples(
        samples: list[dict[str, Any]],
        chunk_size: int = 1000,
    ) -> int:
        """
        Bulk create samples in batches.

        Args:
            samples: List of sample data dicts
            chunk_size: Number of samples per batch

        Returns:
            Total created
        """
        from samplemind.core.database.tortoise_models import TortoiseSample

        total_created = 0

        # Process in chunks to avoid memory issues
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i : i + chunk_size]

            try:
                # Use bulk_create if available (ORM-specific)
                created = await TortoiseSample.bulk_create(
                    [TortoiseSample(**s) for s in chunk]
                )
                total_created += len(created)
                logger.info(f"Bulk created {len(created)} samples (chunk {i // chunk_size + 1})")
            except Exception as e:
                logger.error(f"Bulk create failed for chunk {i // chunk_size + 1}: {e}")

        return total_created

    @staticmethod
    async def bulk_update_samples(
        updates: list[tuple[str, dict[str, Any]]],
        chunk_size: int = 1000,
    ) -> int:
        """
        Bulk update samples in batches.

        Args:
            updates: List of (sample_id, update_dict) tuples
            chunk_size: Number per batch

        Returns:
            Total updated
        """
        from samplemind.core.database.tortoise_models import TortoiseSample

        total_updated = 0

        for i in range(0, len(updates), chunk_size):
            chunk = updates[i : i + chunk_size]

            for sample_id, update_dict in chunk:
                try:
                    sample = await TortoiseSample.get(id=sample_id)
                    for key, value in update_dict.items():
                        setattr(sample, key, value)
                    await sample.save()
                    total_updated += 1
                except Exception as e:
                    logger.error(f"Bulk update failed for sample {sample_id}: {e}")

        return total_updated


# Global instance
_DB_OPTIMIZE_MANAGER: DatabaseOptimizationManager | None = None


def get_database_optimizer() -> DatabaseOptimizationManager:
    """Get or create database optimization manager singleton"""
    global _DB_OPTIMIZE_MANAGER

    if _DB_OPTIMIZE_MANAGER is None:
        _DB_OPTIMIZE_MANAGER = DatabaseOptimizationManager()
        logger.info("Database optimization manager initialized")

    return _DB_OPTIMIZE_MANAGER
