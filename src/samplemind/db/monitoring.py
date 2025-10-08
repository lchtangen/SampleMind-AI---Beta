"""
Database Monitoring & Metrics
Comprehensive monitoring for MongoDB and Redis performance

This module provides:
- Query execution time tracking
- Connection pool monitoring
- Cache hit/miss rates
- Index usage statistics
- Slow query logging
- Prometheus metrics export
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager, contextmanager

try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Prometheus client not available, metrics disabled")

logger = logging.getLogger(__name__)


# Prometheus Metrics (if available)
if PROMETHEUS_AVAILABLE:
    # MongoDB Query Metrics
    mongo_query_duration = Histogram(
        'mongodb_query_duration_seconds',
        'MongoDB query execution time',
        ['operation', 'collection']
    )

    mongo_query_total = Counter(
        'mongodb_queries_total',
        'Total number of MongoDB queries',
        ['operation', 'collection', 'status']
    )

    mongo_slow_queries = Counter(
        'mongodb_slow_queries_total',
        'Number of slow queries (>100ms)',
        ['operation', 'collection']
    )

    # Connection Pool Metrics
    mongo_pool_size = Gauge(
        'mongodb_pool_size',
        'MongoDB connection pool size'
    )

    mongo_pool_active = Gauge(
        'mongodb_pool_active_connections',
        'Active MongoDB connections'
    )

    mongo_pool_available = Gauge(
        'mongodb_pool_available_connections',
        'Available MongoDB connections'
    )

    # Redis Cache Metrics
    redis_cache_hits = Counter(
        'redis_cache_hits_total',
        'Total cache hits',
        ['prefix']
    )

    redis_cache_misses = Counter(
        'redis_cache_misses_total',
        'Total cache misses',
        ['prefix']
    )

    redis_cache_errors = Counter(
        'redis_cache_errors_total',
        'Total cache errors',
        ['prefix']
    )

    redis_memory_usage = Gauge(
        'redis_memory_usage_bytes',
        'Redis memory usage in bytes'
    )

    # Index Usage Metrics
    mongo_index_usage = Counter(
        'mongodb_index_usage_total',
        'MongoDB index usage count',
        ['collection', 'index_name']
    )


class DatabaseMonitor:
    """
    Monitor database performance and collect metrics
    """

    def __init__(
        self,
        slow_query_threshold_ms: float = 100.0,
        enable_metrics: bool = True
    ):
        """
        Initialize database monitor

        Args:
            slow_query_threshold_ms: Threshold for slow query logging (default: 100ms)
            enable_metrics: Whether to enable Prometheus metrics
        """
        self.slow_query_threshold = slow_query_threshold_ms / 1000.0  # Convert to seconds
        self.enable_metrics = enable_metrics and PROMETHEUS_AVAILABLE

        # In-memory slow query log
        self.slow_queries: List[Dict[str, Any]] = []
        self.max_slow_queries = 100  # Keep last 100 slow queries

        logger.info(
            f"DatabaseMonitor initialized "
            f"(threshold: {slow_query_threshold_ms}ms, metrics: {self.enable_metrics})"
        )

    @asynccontextmanager
    async def track_query_async(
        self,
        operation: str,
        collection: str,
        query: Optional[Dict[str, Any]] = None
    ):
        """
        Async context manager to track query execution time

        Args:
            operation: Operation type (find, update, delete, etc.)
            collection: Collection name
            query: Optional query parameters for logging

        Example:
            async with monitor.track_query_async('find', 'users', {'email': email}):
                result = await db.users.find_one({'email': email})
        """
        start_time = time.time()
        status = 'success'

        try:
            yield
        except Exception as e:
            status = 'error'
            logger.error(f"Query failed: {operation} on {collection}: {e}")
            raise
        finally:
            duration = time.time() - start_time

            # Log slow queries
            if duration >= self.slow_query_threshold:
                self._log_slow_query(operation, collection, duration, query)

            # Update metrics
            if self.enable_metrics:
                mongo_query_duration.labels(
                    operation=operation,
                    collection=collection
                ).observe(duration)

                mongo_query_total.labels(
                    operation=operation,
                    collection=collection,
                    status=status
                ).inc()

                if duration >= self.slow_query_threshold:
                    mongo_slow_queries.labels(
                        operation=operation,
                        collection=collection
                    ).inc()

    @contextmanager
    def track_query_sync(
        self,
        operation: str,
        collection: str,
        query: Optional[Dict[str, Any]] = None
    ):
        """
        Sync context manager to track query execution time

        Args:
            operation: Operation type (find, update, delete, etc.)
            collection: Collection name
            query: Optional query parameters for logging

        Example:
            with monitor.track_query_sync('find', 'users', {'email': email}):
                result = db.users.find_one({'email': email})
        """
        start_time = time.time()
        status = 'success'

        try:
            yield
        except Exception as e:
            status = 'error'
            logger.error(f"Query failed: {operation} on {collection}: {e}")
            raise
        finally:
            duration = time.time() - start_time

            # Log slow queries
            if duration >= self.slow_query_threshold:
                self._log_slow_query(operation, collection, duration, query)

            # Update metrics
            if self.enable_metrics:
                mongo_query_duration.labels(
                    operation=operation,
                    collection=collection
                ).observe(duration)

                mongo_query_total.labels(
                    operation=operation,
                    collection=collection,
                    status=status
                ).inc()

                if duration >= self.slow_query_threshold:
                    mongo_slow_queries.labels(
                        operation=operation,
                        collection=collection
                    ).inc()

    def _log_slow_query(
        self,
        operation: str,
        collection: str,
        duration: float,
        query: Optional[Dict[str, Any]]
    ):
        """Log slow query for analysis"""
        slow_query = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'collection': collection,
            'duration_ms': duration * 1000,
            'query': str(query) if query else None
        }

        self.slow_queries.append(slow_query)

        # Keep only last N queries
        if len(self.slow_queries) > self.max_slow_queries:
            self.slow_queries = self.slow_queries[-self.max_slow_queries:]

        logger.warning(
            f"SLOW QUERY: {operation} on {collection} "
            f"took {duration*1000:.2f}ms"
        )

    def update_pool_metrics(self, pool_stats: Dict[str, Any]):
        """
        Update connection pool metrics

        Args:
            pool_stats: Pool statistics from MongoConnectionPool
        """
        if not self.enable_metrics:
            return

        mongo_pool_size.set(pool_stats.get('pool_size', 0))
        mongo_pool_active.set(pool_stats.get('active_connections', 0))
        mongo_pool_available.set(pool_stats.get('available_connections', 0))

    def update_cache_metrics(
        self,
        prefix: str,
        hits: int = 0,
        misses: int = 0,
        errors: int = 0
    ):
        """
        Update cache metrics

        Args:
            prefix: Cache key prefix
            hits: Number of cache hits
            misses: Number of cache misses
            errors: Number of cache errors
        """
        if not self.enable_metrics:
            return

        if hits > 0:
            redis_cache_hits.labels(prefix=prefix).inc(hits)
        if misses > 0:
            redis_cache_misses.labels(prefix=prefix).inc(misses)
        if errors > 0:
            redis_cache_errors.labels(prefix=prefix).inc(errors)

    def update_redis_memory(self, memory_bytes: int):
        """
        Update Redis memory usage metric

        Args:
            memory_bytes: Memory usage in bytes
        """
        if self.enable_metrics:
            redis_memory_usage.set(memory_bytes)

    def record_index_usage(self, collection: str, index_name: str):
        """
        Record index usage

        Args:
            collection: Collection name
            index_name: Index name
        """
        if self.enable_metrics:
            mongo_index_usage.labels(
                collection=collection,
                index_name=index_name
            ).inc()

    def get_slow_queries(
        self,
        limit: int = 10,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent slow queries

        Args:
            limit: Maximum number of queries to return
            since: Only return queries after this time

        Returns:
            List of slow query records
        """
        queries = self.slow_queries

        if since:
            queries = [
                q for q in queries
                if datetime.fromisoformat(q['timestamp']) >= since
            ]

        # Return most recent first
        return list(reversed(queries[-limit:]))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get monitoring statistics

        Returns:
            Dictionary with monitoring stats
        """
        total_slow = len(self.slow_queries)

        # Calculate average slow query duration
        avg_slow_duration = 0.0
        if total_slow > 0:
            avg_slow_duration = sum(
                q['duration_ms'] for q in self.slow_queries
            ) / total_slow

        return {
            'slow_query_threshold_ms': self.slow_query_threshold * 1000,
            'total_slow_queries': total_slow,
            'avg_slow_query_duration_ms': round(avg_slow_duration, 2),
            'metrics_enabled': self.enable_metrics,
            'prometheus_available': PROMETHEUS_AVAILABLE
        }

    def print_statistics(self):
        """Print formatted monitoring statistics"""
        stats = self.get_statistics()
        print("\n" + "="*60)
        print("📊 DATABASE MONITORING STATISTICS")
        print("="*60)
        print(f"  Slow Query Threshold:  {stats['slow_query_threshold_ms']:.0f}ms")
        print(f"  Total Slow Queries:    {stats['total_slow_queries']:,}")
        print(f"  Avg Slow Duration:     {stats['avg_slow_query_duration_ms']:.2f}ms")
        print(f"  Metrics Enabled:       {stats['metrics_enabled']}")
        print(f"  Prometheus Available:  {stats['prometheus_available']}")
        print("="*60)

        # Print recent slow queries
        if stats['total_slow_queries'] > 0:
            print("\n📝 RECENT SLOW QUERIES (Last 5):")
            print("-" * 60)
            for query in self.get_slow_queries(limit=5):
                print(f"  {query['timestamp'][:19]}")
                print(f"  Operation: {query['operation']} on {query['collection']}")
                print(f"  Duration:  {query['duration_ms']:.2f}ms")
                if query['query']:
                    print(f"  Query:     {query['query'][:100]}")
                print("-" * 60)

        print()


# Singleton instance
_monitor_instance: Optional[DatabaseMonitor] = None


def get_database_monitor(slow_query_threshold_ms: float = 100.0) -> DatabaseMonitor:
    """
    Get or create DatabaseMonitor singleton instance

    Args:
        slow_query_threshold_ms: Threshold for slow query logging

    Returns:
        DatabaseMonitor instance
    """
    global _monitor_instance

    if _monitor_instance is None:
        _monitor_instance = DatabaseMonitor(slow_query_threshold_ms)

    return _monitor_instance


def monitored_query(operation: str, collection: str):
    """
    Decorator for automatic query monitoring

    Args:
        operation: Operation type
        collection: Collection name

    Example:
        @monitored_query('find', 'users')
        async def get_user_by_email(email: str):
            return await db.users.find_one({'email': email})
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = get_database_monitor()
            async with monitor.track_query_async(operation, collection):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = get_database_monitor()
            with monitor.track_query_sync(operation, collection):
                return func(*args, **kwargs)

        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator