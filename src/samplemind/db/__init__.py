"""
Database Module
Comprehensive database utilities and optimization tools

This module provides:
- Connection pooling (MongoDB sync/async)
- Query result caching (Redis-backed)
- Database monitoring and metrics
- Index management utilities
- Vector store integration
"""

from .connection_pool import (
    MongoConnectionPool,
    get_connection_pool,
    close_connection_pool
)

from .query_cache import (
    QueryCache,
    get_query_cache,
    cached_query
)

from .monitoring import (
    DatabaseMonitor,
    get_database_monitor,
    monitored_query
)

from .indexes import (
    IndexManager,
    INDEX_DEFINITIONS,
    create_indexes_sync,
    create_indexes_async
)

from .vector_store import (
    VectorStore,
    get_vector_store
)

from .optimized_config import (
    get_optimized_mongodb_client,
    get_optimized_redis_client,
    get_connection_pool_stats
)

from .vector_config import (
    get_optimized_chroma_settings,
    create_optimized_chroma_client,
    tune_hnsw_for_speed,
    tune_hnsw_for_accuracy
)

__all__ = [
    # Connection Pooling
    'MongoConnectionPool',
    'get_connection_pool',
    'close_connection_pool',
    
    # Query Caching
    'QueryCache',
    'get_query_cache',
    'cached_query',
    
    # Monitoring
    'DatabaseMonitor',
    'get_database_monitor',
    'monitored_query',
    
    # Index Management
    'IndexManager',
    'INDEX_DEFINITIONS',
    'create_indexes_sync',
    'create_indexes_async',
    
    # Vector Store
    'VectorStore',
    'get_vector_store',
    
    # Optimized Configs
    'get_optimized_mongodb_client',
    'get_optimized_redis_client',
    'get_connection_pool_stats',
    'get_optimized_chroma_settings',
    'create_optimized_chroma_client',
    'tune_hnsw_for_speed',
    'tune_hnsw_for_accuracy',
]