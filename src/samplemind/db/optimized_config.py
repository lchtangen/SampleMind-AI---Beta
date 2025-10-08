"""Optimized database connection configurations"""

import socket
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import redis


def get_optimized_mongodb_client(url: str) -> AsyncIOMotorClient:
    """
    Create MongoDB client with optimized connection pooling.
    
    Args:
        url: MongoDB connection URL
        
    Returns:
        Configured AsyncIOMotorClient
    """
    return AsyncIOMotorClient(
        url,
        maxPoolSize=100,
        minPoolSize=10,
        socketTimeoutMS=30000,
        connectTimeoutMS=5000,
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
        retryReads=True,
        w='majority',
        readPreference='primaryPreferred',
    )


def get_optimized_redis_client(host: str = 'redis', port: int = 6379, db: int = 0) -> redis.Redis:
    """
    Create Redis client with optimized connection pooling.
    
    Args:
        host: Redis host
        port: Redis port
        db: Database number
        
    Returns:
        Configured Redis client
    """
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        max_connections=100,
        socket_connect_timeout=5,
        socket_timeout=30,
        socket_keepalive=True,
        socket_keepalive_options={
            socket.TCP_KEEPIDLE: 60,
            socket.TCP_KEEPINTVL: 10,
            socket.TCP_KEEPCNT: 3,
        },
        decode_responses=False,
        health_check_interval=30,
    )


def get_connection_pool_stats(redis_client: redis.Redis) -> Dict[str, Any]:
    """Get Redis connection pool statistics"""
    pool = redis_client.connection_pool
    return {
        'max_connections': pool.max_connections,
        'available_connections': len(pool._available_connections),
        'in_use_connections': len(pool._in_use_connections),
    }
