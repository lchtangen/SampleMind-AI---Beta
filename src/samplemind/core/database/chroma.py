"""ChromaDB client for vector similarity search

Features:
- Semantic search with query result caching
- Fast duplicate detection via caching
- TTL-based cache invalidation
- Cache statistics and monitoring
"""

import logging
import os
import hashlib
from typing import Any, Dict, List, Optional

import chromadb

try:
    from chromadb.config import Settings
except ImportError:
    Settings = None

from samplemind.core.config import Settings as AppSettings

logger = logging.getLogger(__name__)

# Global ChromaDB client
_chroma_client = None
_collection = None
_settings = AppSettings()

# Query result cache
_query_cache = {}
_query_cache_hits = 0
_query_cache_misses = 0


def _cache_embedding_hash(embedding: List[float]) -> str:
    """Generate hash for embedding vector."""
    import json
    embedding_str = json.dumps(embedding, separators=(',', ':'))
    return hashlib.sha256(embedding_str.encode()).hexdigest()[:16]


def init_chromadb(
    persist_directory: str = "./data/chroma",
    collection_name: str = _settings.chroma_collection
):
    """Initialize ChromaDB client"""
    global _chroma_client, _collection

    try:
        logger.info(f"🔌 Initializing ChromaDB: {collection_name}")

        # Check environment for Chroma host (e.g. from Docker)
        host = os.getenv("CHROMA_HOST", _settings.chroma_host)
        port = int(os.getenv("CHROMA_PORT", _settings.chroma_port))

        # Determine client type
        if host and host != "localhost":
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            _chroma_client = chromadb.HttpClient(host=host, port=port)
        else:
            logger.info(f"Using local ChromaDB at {persist_directory}")
            # Use PersistentClient for local storage
            _chroma_client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        _collection = _chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Audio sample embeddings for similarity search"}
        )

        logger.info(f"✅ ChromaDB initialized with {_collection.count()} embeddings")
        return _chroma_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize ChromaDB: {e}")
        raise


def get_chroma_client():
    """Get ChromaDB client instance"""
    if _chroma_client is None:
        raise RuntimeError("ChromaDB not initialized. Call init_chromadb() first.")
    return _chroma_client


def get_collection():
    """Get ChromaDB collection"""
    if _collection is None:
        raise RuntimeError("ChromaDB collection not initialized")
    return _collection


async def add_embedding(
    file_id: str,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Add audio embedding to ChromaDB"""
    try:
        collection = get_collection()

        collection.add(
            ids=[file_id],
            embeddings=[embedding],
            metadatas=[metadata or {}]
        )

        logger.debug(f"Added embedding for file: {file_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to add embedding: {e}")
        return False


async def query_similar(
    embedding: List[float],
    n_results: int = 10,
    where: Optional[Dict[str, Any]] = None,
    use_cache: bool = True
) -> Dict[str, Any]:
    """
    Query similar audio samples with caching support.

    Args:
        embedding: Query embedding vector
        n_results: Number of results to return
        where: Optional metadata filter
        use_cache: Enable query result caching (default: True)

    Returns:
        Query results with ids, distances, and metadata
    """
    global _query_cache, _query_cache_hits, _query_cache_misses

    # Generate cache key
    cache_key = None
    if use_cache and where is None:  # Only cache queries without filters
        import json
        embedding_hash = _cache_embedding_hash(embedding)
        cache_key = f"query:{embedding_hash}:n{n_results}"

        # Check cache
        if cache_key in _query_cache:
            cached_result, timestamp = _query_cache[cache_key]

            # Check TTL (3600 seconds = 1 hour)
            import time
            if time.time() - timestamp < 3600:
                _query_cache_hits += 1
                logger.debug(f"Query cache hit (cached {len(cached_result.get('ids', []))} results)")
                return cached_result
            else:
                # Expired, remove from cache
                del _query_cache[cache_key]

    _query_cache_misses += 1

    try:
        collection = get_collection()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where
        )

        result = {
            "ids": results["ids"][0] if results["ids"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else []
        }

        # Cache result
        if use_cache and cache_key is not None:
            import time
            _query_cache[cache_key] = (result, time.time())
            logger.debug(f"Cached query result ({len(result.get('ids', []))} items)")

        return result

    except Exception as e:
        logger.error(f"Failed to query similar: {e}")
        return {"ids": [], "distances": [], "metadatas": []}


async def delete_embedding(file_id: str) -> bool:
    """Delete audio embedding from ChromaDB"""
    try:
        collection = get_collection()
        collection.delete(ids=[file_id])
        logger.debug(f"Deleted embedding for file: {file_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete embedding: {e}")
        return False


async def get_collection_stats() -> Dict[str, Any]:
    """Get collection statistics"""
    try:
        collection = get_collection()
        return {
            "count": collection.count(),
            "name": collection.name,
            "metadata": collection.metadata
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"count": 0, "name": "unknown", "metadata": {}}


def get_query_cache_stats() -> Dict[str, Any]:
    """Get query cache statistics."""
    global _query_cache, _query_cache_hits, _query_cache_misses

    total_requests = _query_cache_hits + _query_cache_misses
    hit_rate = (
        (_query_cache_hits / total_requests * 100) if total_requests > 0 else 0.0
    )

    return {
        "hits": _query_cache_hits,
        "misses": _query_cache_misses,
        "hit_rate_percent": round(hit_rate, 2),
        "cached_queries": len(_query_cache),
        "total_requests": total_requests
    }


def clear_query_cache() -> None:
    """Clear all cached query results."""
    global _query_cache, _query_cache_hits, _query_cache_misses

    cache_size = len(_query_cache)
    _query_cache.clear()
    _query_cache_hits = 0
    _query_cache_misses = 0

    logger.info(f"Cleared query cache ({cache_size} entries)")


def invalidate_query_cache_for_embedding(embedding: List[float]) -> None:
    """Invalidate cache entries for a specific embedding."""
    global _query_cache

    embedding_hash = _cache_embedding_hash(embedding)
    keys_to_delete = [
        key for key in _query_cache.keys()
        if embedding_hash in key
    ]

    for key in keys_to_delete:
        del _query_cache[key]

    if keys_to_delete:
        logger.debug(f"Invalidated {len(keys_to_delete)} cache entries")


async def invalidate_query_cache_on_add() -> None:
    """Invalidate query cache when new embeddings are added."""
    clear_query_cache()
