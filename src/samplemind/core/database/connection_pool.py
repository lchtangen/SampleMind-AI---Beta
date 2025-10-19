"""
Database Connection Pooling & Performance Monitoring
Production-optimized connection management
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import event, text
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import time
import logging
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class QueryStats:
    """Query performance statistics"""
    query: str
    duration_ms: float
    timestamp: datetime
    connection_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ConnectionPoolStats:
    """Connection pool statistics"""
    pool_size: int
    overflow: int
    checked_out: int
    checked_in: int
    total_connections: int
    idle_connections: int
    queries_executed: int = 0
    avg_query_time_ms: float = 0.0
    slow_queries: list = field(default_factory=list)


class DatabaseConnectionPool:
    """
    Production-ready database connection pool manager
    Features:
    - Automatic connection retry
    - Query performance tracking
    - Connection health checks
    - Pool statistics
    - Slow query logging
    """
    
    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 40,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
        slow_query_threshold_ms: float = 1000.0
    ):
        """
        Initialize connection pool
        
        Args:
            database_url: Database connection string
            pool_size: Number of persistent connections
            max_overflow: Maximum overflow connections
            pool_timeout: Seconds to wait for connection
            pool_recycle: Recycle connections after N seconds
            pool_pre_ping: Test connections before using
            echo: Log all SQL statements
            slow_query_threshold_ms: Log queries slower than this
        """
        self.database_url = database_url
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.query_stats: list[QueryStats] = []
        self.total_queries = 0
        self.total_query_time_ms = 0.0
        
        # Create async engine with optimized pool settings
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            echo=echo,
            echo_pool=False,
            # Connection arguments
            connect_args={
                "server_settings": {
                    "application_name": "samplemind_ai",
                    "jit": "off"  # Disable JIT for faster simple queries
                },
                "command_timeout": 60,  # Command timeout in seconds
                "timeout": 10,  # Connection timeout
            },
            # Performance optimizations
            execution_options={
                "isolation_level": "READ COMMITTED",
                "postgresql_readonly": False,
                "postgresql_deferrable": False
            }
        )
        
        # Session factory
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
        
        # Register event listeners for monitoring
        self._register_event_listeners()
        
        logger.info(
            f"Database pool initialized: size={pool_size}, "
            f"max_overflow={max_overflow}, timeout={pool_timeout}s"
        )
    
    def _register_event_listeners(self):
        """Register SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Track query start time"""
            conn.info.setdefault("query_start_time", []).append(time.time())
        
        @event.listens_for(self.engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """Track query execution time"""
            start_times = conn.info.get("query_start_time", [])
            if start_times:
                start_time = start_times.pop()
                duration_ms = (time.time() - start_time) * 1000
                
                # Update stats
                self.total_queries += 1
                self.total_query_time_ms += duration_ms
                
                # Log slow queries
                if duration_ms > self.slow_query_threshold_ms:
                    logger.warning(
                        f"Slow query detected: {duration_ms:.2f}ms\n"
                        f"Query: {statement[:200]}"
                    )
                    
                    stat = QueryStats(
                        query=statement[:500],
                        duration_ms=duration_ms,
                        timestamp=datetime.now()
                    )
                    self.query_stats.append(stat)
                    
                    # Keep only last 100 slow queries
                    if len(self.query_stats) > 100:
                        self.query_stats = self.query_stats[-100:]
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Configure connection on creation"""
            logger.debug("New database connection established")
            
            # Set session parameters for performance
            cursor = dbapi_conn.cursor()
            cursor.execute("SET random_page_cost = 1.1")  # SSD-optimized
            cursor.execute("SET effective_cache_size = '4GB'")
            cursor.execute("SET work_mem = '50MB'")
            cursor.execute("SET maintenance_work_mem = '256MB'")
            cursor.close()
        
        @event.listens_for(self.engine.sync_engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """Track connection checkout"""
            logger.debug(f"Connection checked out: {id(dbapi_conn)}")
        
        @event.listens_for(self.engine.sync_engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """Track connection checkin"""
            logger.debug(f"Connection checked in: {id(dbapi_conn)}")
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get database session with automatic cleanup
        
        Usage:
            async with pool.get_session() as session:
                result = await session.execute(query)
        """
        session = self.SessionLocal()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Session error: {e}")
            raise
        finally:
            await session.close()
    
    async def get_pool_stats(self) -> ConnectionPoolStats:
        """Get current connection pool statistics"""
        pool = self.engine.pool
        
        return ConnectionPoolStats(
            pool_size=pool.size(),
            overflow=pool.overflow(),
            checked_out=pool.checkedout(),
            checked_in=pool.checkedin(),
            total_connections=pool.size() + pool.overflow(),
            idle_connections=pool.size() - pool.checkedout(),
            queries_executed=self.total_queries,
            avg_query_time_ms=(
                self.total_query_time_ms / self.total_queries 
                if self.total_queries > 0 else 0.0
            ),
            slow_queries=self.query_stats[-10:]  # Last 10 slow queries
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check
        
        Returns:
            Health status dictionary
        """
        try:
            start_time = time.time()
            
            async with self.get_session() as session:
                # Simple query to test connection
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                # Check database version
                version_result = await session.execute(text("SELECT version()"))
                db_version = version_result.scalar()
                
                # Check active connections
                conn_result = await session.execute(text("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                active_connections = conn_result.scalar()
            
            response_time_ms = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time_ms,
                "database_version": db_version,
                "active_connections": active_connections,
                "pool_stats": (await self.get_pool_stats()).__dict__
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def optimize_connection(self, session: AsyncSession):
        """Apply connection-level optimizations"""
        # Set optimal parameters for this connection
        await session.execute(text("SET LOCAL enable_seqscan = off"))  # Prefer indexes
        await session.execute(text("SET LOCAL random_page_cost = 1.1"))  # SSD
        await session.execute(text("SET LOCAL effective_io_concurrency = 200"))  # SSD
    
    async def get_slow_queries(self, limit: int = 10) -> list[QueryStats]:
        """Get slowest queries"""
        return sorted(
            self.query_stats,
            key=lambda x: x.duration_ms,
            reverse=True
        )[:limit]
    
    async def get_query_analytics(self) -> Dict[str, Any]:
        """Get query performance analytics"""
        if not self.query_stats:
            return {
                "total_slow_queries": 0,
                "average_duration_ms": 0.0,
                "max_duration_ms": 0.0
            }
        
        durations = [s.duration_ms for s in self.query_stats]
        
        return {
            "total_slow_queries": len(self.query_stats),
            "average_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)]
        }
    
    async def close(self):
        """Close all connections and cleanup"""
        logger.info("Closing database connection pool")
        await self.engine.dispose()


# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None


async def init_connection_pool(database_url: str, **kwargs) -> DatabaseConnectionPool:
    """Initialize global connection pool"""
    global _connection_pool
    _connection_pool = DatabaseConnectionPool(database_url, **kwargs)
    return _connection_pool


def get_connection_pool() -> DatabaseConnectionPool:
    """Get global connection pool instance"""
    if _connection_pool is None:
        raise RuntimeError("Connection pool not initialized. Call init_connection_pool() first")
    return _connection_pool


# Example usage
"""
from src.samplemind.core.config import settings

async def main():
    # Initialize pool
    pool = await init_connection_pool(
        settings.database_url,
        pool_size=20,
        max_overflow=40,
        slow_query_threshold_ms=1000.0
    )
    
    # Use pool
    async with pool.get_session() as session:
        result = await session.execute(text("SELECT * FROM users LIMIT 10"))
        users = result.fetchall()
    
    # Check health
    health = await pool.health_check()
    print(health)
    
    # Get stats
    stats = await pool.get_pool_stats()
    print(f"Active connections: {stats.checked_out}")
    print(f"Average query time: {stats.avg_query_time_ms:.2f}ms")
    
    # Cleanup
    await pool.close()
"""
