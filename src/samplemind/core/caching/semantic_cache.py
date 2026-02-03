"""
Semantic Search & Embedding Result Caching

Implements multi-level caching strategy for:
1. Neural embeddings - cache CLAP model outputs
2. Semantic search results - cache ChromaDB queries
3. Feature extraction - cache audio feature analysis
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import asyncio
from functools import lru_cache

import numpy as np

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Multi-level semantic search cache with embedding and query result caching.

    Features:
    - Embedding cache: Store neural embeddings to avoid recomputation
    - Query cache: Cache semantic search results with TTL
    - Feature cache: Disk-based audio feature caching
    - Memory limits: Automatic eviction of least-used entries
    """

    def __init__(self, max_embeddings: int = 10000, cache_dir: str = ".semantic_cache") -> None:
        """
        Initialize semantic cache.

        Args:
            max_embeddings: Maximum embeddings to store in memory
            cache_dir: Directory for disk-based caching
        """
        self.max_embeddings = max_embeddings
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory embedding cache (file_hash -> embedding)
        self.embeddings_cache: Dict[str, List[float]] = {}

        # Query result cache (query_hash -> (results, timestamp))
        self.query_cache: Dict[str, Tuple[List[Dict], float]] = {}

        # Access tracking for LRU eviction
        self.access_count: Dict[str, int] = {}

        # Statistics
        self.embedding_hits = 0
        self.embedding_misses = 0
        self.query_hits = 0
        self.query_misses = 0

        logger.info(
            f"Semantic cache initialized (max_embeddings={max_embeddings}, "
            f"cache_dir={self.cache_dir.absolute()})"
        )

    def _hash_audio_file(self, audio_path: str) -> str:
        """
        Generate deterministic hash for audio file.
        Uses file content hash for cache key.

        Args:
            audio_path: Path to audio file

        Returns:
            SHA256 hash of file content
        """
        try:
            with open(audio_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash audio file {audio_path}: {e}")
            return hashlib.sha256(str(audio_path).encode()).hexdigest()

    def _hash_query(self, query_text: str, n_results: int = 5, metadata_filter: Optional[Dict] = None) -> str:
        """
        Generate deterministic hash for semantic query.

        Args:
            query_text: Query text
            n_results: Number of results
            metadata_filter: Optional metadata filter

        Returns:
            Deterministic hash of query
        """
        key_data = {
            "query": query_text,
            "n_results": n_results,
            "filter": metadata_filter
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    async def get_embedding(self, audio_path: str) -> Optional[List[float]]:
        """
        Get cached embedding for audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Cached embedding or None if not found
        """
        file_hash = self._hash_audio_file(audio_path)

        # Check in-memory cache
        if file_hash in self.embeddings_cache:
            self.embedding_hits += 1
            self.access_count[file_hash] = self.access_count.get(file_hash, 0) + 1
            logger.debug(f"Embedding cache hit for {audio_path}")
            return self.embeddings_cache[file_hash]

        # Check disk cache
        disk_path = self.cache_dir / f"{file_hash}.npy"
        if disk_path.exists():
            try:
                embedding = np.load(disk_path).tolist()
                self.embeddings_cache[file_hash] = embedding
                self.embedding_hits += 1
                self.access_count[file_hash] = self.access_count.get(file_hash, 0) + 1
                logger.debug(f"Embedding cache hit (from disk) for {audio_path}")
                return embedding
            except Exception as e:
                logger.warning(f"Failed to load embedding from disk: {e}")

        self.embedding_misses += 1
        return None

    async def set_embedding(self, audio_path: str, embedding: List[float]) -> bool:
        """
        Cache embedding for audio file.

        Args:
            audio_path: Path to audio file
            embedding: Embedding vector

        Returns:
            True if successful
        """
        try:
            file_hash = self._hash_audio_file(audio_path)

            # Check memory limit
            if len(self.embeddings_cache) >= self.max_embeddings:
                await self._evict_embedding()

            # Store in memory
            self.embeddings_cache[file_hash] = embedding
            self.access_count[file_hash] = 0

            # Store on disk
            disk_path = self.cache_dir / f"{file_hash}.npy"
            np.save(disk_path, np.array(embedding))

            logger.debug(f"Cached embedding for {audio_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache embedding: {e}")
            return False

    async def get_query_result(
        self,
        query_text: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None,
        ttl: int = 3600
    ) -> Optional[List[Dict]]:
        """
        Get cached semantic search results.

        Args:
            query_text: Query text
            n_results: Number of results
            metadata_filter: Optional metadata filter
            ttl: Time-to-live in seconds

        Returns:
            Cached results or None if expired/not found
        """
        query_hash = self._hash_query(query_text, n_results, metadata_filter)

        if query_hash in self.query_cache:
            results, timestamp = self.query_cache[query_hash]

            # Check TTL
            import time
            if time.time() - timestamp > ttl:
                del self.query_cache[query_hash]
                self.query_misses += 1
                return None

            self.query_hits += 1
            self.access_count[query_hash] = self.access_count.get(query_hash, 0) + 1
            logger.debug(f"Query cache hit: {query_text}")
            return results

        self.query_misses += 1
        return None

    async def set_query_result(
        self,
        query_text: str,
        results: List[Dict],
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None
    ) -> bool:
        """
        Cache semantic search results.

        Args:
            query_text: Query text
            results: Search results
            n_results: Number of results
            metadata_filter: Optional metadata filter

        Returns:
            True if successful
        """
        try:
            import time
            query_hash = self._hash_query(query_text, n_results, metadata_filter)
            self.query_cache[query_hash] = (results, time.time())
            logger.debug(f"Cached query result: {query_text}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache query result: {e}")
            return False

    async def _evict_embedding(self) -> None:
        """Evict least-used embedding from cache."""
        if not self.embeddings_cache:
            return

        # Find least accessed embedding
        min_key = min(
            self.embeddings_cache.keys(),
            key=lambda k: self.access_count.get(k, 0)
        )

        del self.embeddings_cache[min_key]
        del self.access_count[min_key]

        logger.debug(f"Evicted embedding cache entry: {min_key}")

    def get_hit_ratio(self) -> Dict[str, float]:
        """Get cache hit ratios."""
        embedding_total = self.embedding_hits + self.embedding_misses
        query_total = self.query_hits + self.query_misses

        return {
            "embedding_hit_ratio": (
                self.embedding_hits / embedding_total if embedding_total > 0 else 0.0
            ),
            "query_hit_ratio": (
                self.query_hits / query_total if query_total > 0 else 0.0
            ),
            "overall_hit_ratio": (
                (self.embedding_hits + self.query_hits) /
                (embedding_total + query_total) if (embedding_total + query_total) > 0 else 0.0
            )
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "embedding_hits": self.embedding_hits,
            "embedding_misses": self.embedding_misses,
            "query_hits": self.query_hits,
            "query_misses": self.query_misses,
            "hit_ratios": self.get_hit_ratio(),
            "cached_embeddings": len(self.embeddings_cache),
            "max_embeddings": self.max_embeddings,
            "cached_queries": len(self.query_cache),
            "cache_dir": str(self.cache_dir.absolute())
        }

    def clear(self) -> None:
        """Clear all caches."""
        self.embeddings_cache.clear()
        self.query_cache.clear()
        self.access_count.clear()
        self.embedding_hits = 0
        self.embedding_misses = 0
        self.query_hits = 0
        self.query_misses = 0
        logger.info("Semantic cache cleared")


# Global semantic cache instance
_semantic_cache: Optional[SemanticCache] = None


def init_semantic_cache(**kwargs) -> SemanticCache:
    """Initialize global semantic cache instance"""
    global _semantic_cache
    _semantic_cache = SemanticCache(**kwargs)
    return _semantic_cache


def get_semantic_cache() -> SemanticCache:
    """Get global semantic cache instance"""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache


# Cached wrappers for neural and semantic operations

async def cached_embedding(neural_extractor, audio_path: str) -> List[float]:
    """
    Generate embedding with caching.

    Args:
        neural_extractor: NeuralFeatureExtractor instance
        audio_path: Path to audio file

    Returns:
        Embedding vector
    """
    cache = get_semantic_cache()

    # Try to get from cache
    cached = await cache.get_embedding(audio_path)
    if cached is not None:
        return cached

    # Generate embedding
    embedding = neural_extractor.generate_embedding(audio_path)

    # Cache result
    await cache.set_embedding(audio_path, embedding)

    return embedding


async def cached_query(
    chroma_collection,
    query_text: str,
    n_results: int = 5,
    metadata_filter: Optional[Dict] = None,
    ttl: int = 3600
) -> List[Dict]:
    """
    Perform semantic search with caching.

    Args:
        chroma_collection: ChromaDB collection
        query_text: Query text
        n_results: Number of results
        metadata_filter: Optional metadata filter
        ttl: Cache time-to-live

    Returns:
        Search results
    """
    cache = get_semantic_cache()

    # Try to get from cache
    cached = await cache.get_query_result(
        query_text, n_results, metadata_filter, ttl
    )
    if cached is not None:
        return cached

    # Execute query
    results = chroma_collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=metadata_filter
    )

    # Format results
    formatted_results = []
    if results and results['ids'] and len(results['ids']) > 0:
        for i, sample_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': sample_id,
                'distance': results.get('distances', [[]])[0][i] if i < len(results.get('distances', [[]])[0]) else 0,
                'metadata': results['metadatas'][0][i] if i < len(results['metadatas'][0]) else {}
            })

    # Cache result
    await cache.set_query_result(
        query_text, formatted_results, n_results, metadata_filter
    )

    return formatted_results
