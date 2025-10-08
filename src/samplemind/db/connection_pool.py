"""
MongoDB Connection Pool Manager
Efficient connection reuse for high throughput

This module provides production-grade connection pooling for MongoDB with:
- Configurable pool sizes
- Automatic reconnection handling
- Health checks
- Connection metrics
- Thread-safe operations
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import time
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoConnectionPool:
    """
    MongoDB connection pool manager with health checks and metrics
    """

    def __init__(
        self,
        uri: str,
        pool_size: int = 50,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 30000,
        wait_queue_timeout_ms: int = 5000,
        server_selection_timeout_ms: int = 5000,
        connect_timeout_ms: int = 10000,
        socket_timeout_ms: int = 30000,
        database_name: str = "samplemind"
    ):
        """
        Initialize MongoDB connection pool

        Args:
            uri: MongoDB connection URI
            pool_size: Maximum number of connections (default: 50)
            min_pool_size: Minimum number of connections to maintain (default: 10)
            max_idle_time_ms: Max time a connection can be idle (default: 30s)
            wait_queue_timeout_ms: Max time to wait for connection (default: 5s)
            server_selection_timeout_ms: Server selection timeout (default: 5s)
            connect_timeout_ms: Initial connection timeout (default: 10s)
            socket_timeout_ms: Socket operation timeout (default: 30s)
            database_name: Database name to use (default: 'samplemind')
        """
        self.uri = uri
        self.pool_size = pool_size
        self.min_pool_size = min_pool_size
        self.database_name = database_name

        # Connection metrics
        self._connection_attempts = 0
        self._connection_failures = 0
        self._last_health_check = None
        self._health_check_failures = 0

        # Create async client (for FastAPI/async operations)
        self.async_client = AsyncIOMotorClient(
            uri,
            maxPoolSize=pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms,
            waitQueueTimeoutMS=wait_queue_timeout_ms,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
            connectTimeoutMS=connect_timeout_ms,
            socketTimeoutMS=socket_timeout_ms,
            retryWrites=True,
            retryReads=True,
            w='majority',
            readPreference='primaryPreferred',
        )

        # Create sync client (for scripts/background tasks)
        self.sync_client = MongoClient(
            uri,
            maxPoolSize=pool_size,
            minPoolSize=min_pool_size,
            maxIdleTimeMS=max_idle_time_ms,
            waitQueueTimeoutMS=wait_queue_timeout_ms,
            serverSelectionTimeoutMS=server_selection_timeout_ms,
            connectTimeoutMS=connect_timeout_ms,
            socketTimeoutMS=socket_timeout_ms,
            retryWrites=True,
            retryReads=True,
            w='majority',
            readPreference='primaryPreferred',
        )

        logger.info(
            f"MongoConnectionPool initialized "
            f"(pool: {min_pool_size}-{pool_size}, db: {database_name})"
        )

    def get_async_database(self) -> AsyncIOMotorDatabase:
        """
        Get async database instance for FastAPI/async operations

        Returns:
            AsyncIOMotorDatabase instance
        """
        return self.async_client[self.database_name]

    def get_sync_database(self) -> Database:
        """
        Get sync database instance for scripts/background tasks

        Returns:
            Database instance
        """
        return self.sync_client[self.database_name]

    async def health_check_async(self) -> bool:
        """
        Perform async health check on MongoDB connection

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            start_time = time.time()
            db = self.get_async_database()
            await db.command('ping')
            elapsed = (time.time() - start_time) * 1000  # Convert to ms

            self._last_health_check = datetime.now()
            self._health_check_failures = 0

            logger.debug(f"MongoDB health check passed ({elapsed:.2f}ms)")
            return True

        except Exception as e:
            self._health_check_failures += 1
            logger.error(f"MongoDB health check failed: {e}")
            return False

    def health_check_sync(self) -> bool:
        """
        Perform sync health check on MongoDB connection

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            start_time = time.time()
            db = self.get_sync_database()
            db.command('ping')
            elapsed = (time.time() - start_time) * 1000  # Convert to ms

            self._last_health_check = datetime.now()
            self._health_check_failures = 0

            logger.debug(f"MongoDB health check passed ({elapsed:.2f}ms)")
            return True

        except Exception as e:
            self._health_check_failures += 1
            logger.error(f"MongoDB health check failed: {e}")
            return False

    def get_pool_statistics(self) -> Dict[str, Any]:
        """
        Get connection pool statistics

        Returns:
            Dictionary with pool metrics
        """
        try:
            # Get server info
            db = self.get_sync_database()
            server_info = db.command('serverStatus')

            # Extract connection info
            connections = server_info.get('connections', {})

            return {
                'pool_size': self.pool_size,
                'min_pool_size': self.min_pool_size,
                'current_connections': connections.get('current', 0),
                'available_connections': connections.get('available', 0),
                'total_created': connections.get('totalCreated', 0),
                'active_connections': connections.get('active', 0),
                'connection_attempts': self._connection_attempts,
                'connection_failures': self._connection_failures,
                'health_check_failures': self._health_check_failures,
                'last_health_check': self._last_health_check.isoformat() if self._last_health_check else None,
                'database_name': self.database_name
            }

        except Exception as e:
            logger.error(f"Error getting pool statistics: {e}")
            return {
                'pool_size': self.pool_size,
                'min_pool_size': self.min_pool_size,
                'error': str(e)
            }

    def print_statistics(self):
        """Print formatted pool statistics"""
        stats = self.get_pool_statistics()
        print("\n" + "="*60)
        print("🔗 MONGODB CONNECTION POOL STATISTICS")
        print("="*60)
        print(f"  Database:           {stats['database_name']}")
        print(f"  Pool Size:          {stats['min_pool_size']}-{stats['pool_size']}")
        print(f"  Current:            {stats.get('current_connections', 'N/A')}")
        print(f"  Available:          {stats.get('available_connections', 'N/A')}")
        print(f"  Active:             {stats.get('active_connections', 'N/A')}")
        print(f"  Total Created:      {stats.get('total_created', 'N/A')}")
        print(f"  Health Failures:    {stats['health_check_failures']}")
        print(f"  Last Health Check:  {stats['last_health_check'] or 'Never'}")
        print("="*60 + "\n")

    def close(self):
        """Close all connections gracefully"""
        try:
            self.async_client.close()
            self.sync_client.close()
            logger.info("MongoDB connections closed successfully")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# Singleton instance
_connection_pool_instance: Optional[MongoConnectionPool] = None


def get_connection_pool(uri: Optional[str] = None, **kwargs) -> MongoConnectionPool:
    """
    Get or create MongoConnectionPool singleton instance

    Args:
        uri: MongoDB connection URI (required for first initialization)
        **kwargs: Additional pool configuration parameters

    Returns:
        MongoConnectionPool instance
    """
    global _connection_pool_instance

    if _connection_pool_instance is None:
        if uri is None:
            raise ValueError("uri required for first initialization")
        _connection_pool_instance = MongoConnectionPool(uri, **kwargs)

    return _connection_pool_instance


def close_connection_pool():
    """Close the singleton connection pool"""
    global _connection_pool_instance

    if _connection_pool_instance is not None:
        _connection_pool_instance.close()
        _connection_pool_instance = None
        logger.info("Connection pool closed")