"""
Query Result Caching — Ultra-fast database query results via multi-layer cache.

Pattern:
- Wrap common queries with @cached_query decorator
- Automatic L1/L2 caching with TTL
- Pattern-based invalidation on model updates
- Lazy loading with background cache warming
"""

import asyncio
import functools
import logging
from typing import Any, Awaitable, Callable, TypeVar, ParamSpec

from samplemind.core.cache.cache_coordinator import get_cache_coordinator

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

# Predefined query cache TTLs
QUERY_CACHE_TTLS = {
    "library:samples": 300,  # 5 minutes - frequently changing
    "library:list": 600,  # 10 minutes
    "library:stats": 3600,  # 1 hour
    "user:profile": 3600,  # 1 hour
    "user:preferences": 7200,  # 2 hours
    "sample:metadata": 1800,  # 30 minutes
    "sample:search": 300,  # 5 minutes
    "pack:list": 1800,  # 30 minutes
    "pack:published": 3600,  # 1 hour
}


def cached_query(
    cache_key_prefix: str = "",
    ttl_seconds: int | None = None,
    invalidate_patterns: list[str] | None = None,
):
    """
    Decorator to cache async query results automatically.

    Usage:
        @cached_query(cache_key_prefix="samples:by_genre", ttl_seconds=3600)
        async def get_samples_by_genre(genre: str, limit: int = 50):
            return await TortoiseSample.filter(genre_labels__contains=genre).limit(limit)

    Args:
        cache_key_prefix: Prefix for cache key (required)
        ttl_seconds: TTL override (uses QUERY_CACHE_TTLS if None)
        invalidate_patterns: Patterns to invalidate on update

    Returns:
        Decorated async function
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Build cache key from prefix + args
            cache_key = _build_cache_key(cache_key_prefix, args, kwargs)

            # Determine TTL
            ttl = ttl_seconds or QUERY_CACHE_TTLS.get(cache_key_prefix, 3600)

            # Get from cache coordinator
            coordinator = await get_cache_coordinator()

            # Return cached if exists, else compute and cache
            return await coordinator.get(cache_key, compute_fn=lambda: func(*args, **kwargs), ttl_seconds=ttl)

        # Store metadata for invalidation
        wrapper._cache_prefix = cache_key_prefix
        wrapper._invalidate_patterns = invalidate_patterns or []
        wrapper._original_func = func

        return wrapper

    return decorator


class QueryCacheManager:
    """
    Manages query result caching and invalidation patterns.

    Maps database model updates to invalidate relevant query caches.
    """

    # Map of invalidation patterns by model class
    INVALIDATION_RULES = {
        "TortoiseSample": [
            "sample:*",
            "search:*",
            "library:stats",
            "recommendation:*",
        ],
        "TortoiseLibrary": [
            "library:*",
            "library:stats",
        ],
        "TortoiseUser": [
            "user:*",
            "library:*",
        ],
        "TortoisePack": [
            "pack:*",
            "pack:list",
            "pack:published",
        ],
    }

    def __init__(self):
        """Initialize query cache manager"""
        self.coordinator: Any = None
        logger.info("Query cache manager initialized")

    async def init(self) -> None:
        """Initialize with cache coordinator"""
        self.coordinator = await get_cache_coordinator()

    async def invalidate_on_model_update(
        self,
        model_name: str,
        model_id: str | None = None,
    ) -> None:
        """
        Invalidate query caches after model update.

        Args:
            model_name: Name of updated model (e.g., "TortoiseSample")
            model_id: Optional specific model instance ID
        """
        if not self.coordinator:
            await self.init()

        patterns = self.INVALIDATION_RULES.get(model_name, [])

        if model_id:
            # Invalidate specific instance patterns
            specific_patterns = [f"{p.rstrip('*')}{model_id}" for p in patterns if "*" in p]
            patterns = specific_patterns + [p for p in patterns if "*" not in p]

        for pattern in patterns:
            try:
                await self.coordinator.invalidate_pattern(pattern)
                logger.debug(f"Invalidated cache pattern: {pattern} (model: {model_name}, id: {model_id})")
            except Exception as e:
                logger.warning(f"Failed to invalidate pattern {pattern}: {e}")

    async def invalidate_search_cache(self, query: str) -> None:
        """Invalidate search results for specific query"""
        if not self.coordinator:
            await self.init()

        # Hash the query for cache key
        import hashlib

        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        await self.coordinator.invalidate(f"search:{query_hash}")

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get current cache statistics"""
        if not self.coordinator:
            await self.init()

        return self.coordinator.get_stats()


# Global instance
_QUERY_CACHE_MANAGER: QueryCacheManager | None = None


async def get_query_cache_manager() -> QueryCacheManager:
    """Get or create query cache manager singleton"""
    global _QUERY_CACHE_MANAGER

    if _QUERY_CACHE_MANAGER is None:
        _QUERY_CACHE_MANAGER = QueryCacheManager()
        await _QUERY_CACHE_MANAGER.init()

    return _QUERY_CACHE_MANAGER


def _build_cache_key(
    prefix: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Build cache key from function prefix and arguments"""
    # Include relevant args/kwargs in key (skip self/cls for methods)
    # Example: "samples:by_genre:trap:limit=50"
    key_parts = [prefix]

    # Add positional args (skip first if it's self/cls)
    for i, arg in enumerate(args):
        if i == 0 and isinstance(arg, (type, object)) and hasattr(arg, "__class__"):
            continue  # Skip self/cls
        if not isinstance(arg, (int, str, float, bool)):
            arg = str(arg)[:20]  # Truncate complex types
        key_parts.append(str(arg))

    # Add kwargs
    for key, val in sorted(kwargs.items()):
        if not isinstance(val, (int, str, float, bool)):
            val = str(val)[:20]
        key_parts.append(f"{key}={val}")

    return ":".join(key_parts)


# Pre-built cached query templates
async def get_samples_by_genre_cached(
    genre: str,
    limit: int = 50,
) -> list[Any]:
    """
    Get samples by genre with caching.

    Args:
        genre: Genre label to filter by
        limit: Max results

    Returns:
        List of samples
    """
    coordinator = await get_cache_coordinator()
    cache_key = f"sample:genre:{genre}:limit={limit}"

    async def query():
        from samplemind.core.database.tortoise_models import TortoiseSample

        try:
            return await TortoiseSample.filter(genre_labels__contains=genre).limit(limit).values()
        except Exception as e:
            logger.error(f"Query failed for genre {genre}: {e}")
            return []

    return await coordinator.get(
        cache_key,
        compute_fn=query,
        ttl_seconds=QUERY_CACHE_TTLS.get("sample:metadata", 1800),
    )


async def get_user_library_cached(
    user_id: str,
) -> dict[str, Any]:
    """
    Get user's library with caching.

    Args:
        user_id: User ID

    Returns:
        Library metadata dict
    """
    coordinator = await get_cache_coordinator()
    cache_key = f"library:user={user_id}"

    async def query():
        from samplemind.core.database.tortoise_models import TortoiseLibrary

        try:
            library = await TortoiseLibrary.get(owner_id=user_id)
            return {
                "id": library.id,
                "name": library.name,
                "samples_count": await library.samples.all().count(),
                "created_at": library.created_at,
            }
        except Exception as e:
            logger.error(f"Library query failed for user {user_id}: {e}")
            return {}

    return await coordinator.get(
        cache_key,
        compute_fn=query,
        ttl_seconds=QUERY_CACHE_TTLS.get("library:stats", 3600),
    )


async def search_samples_cached(
    query: str,
    filters: dict[str, Any] | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Search samples with caching.

    Args:
        query: Search query
        filters: Optional filters (bpm range, key, etc.)
        limit: Max results

    Returns:
        List of search results
    """
    coordinator = await get_cache_coordinator()

    # Build cache key with query + filters hash
    import hashlib

    filter_str = str(sorted((filters or {}).items()))
    combined = f"{query}:{filter_str}:limit={limit}"
    cache_key = f"search:q={hashlib.md5(combined.encode()).hexdigest()[:8]}"

    async def query_fn():
        from samplemind.core.search.faiss_index import get_index

        try:
            index = get_index(auto_load=True)
            results = index.search_text(query, top_k=limit)

            # Apply additional filters if provided
            if filters:
                results = [r for r in results if _matches_filters(r, filters)]

            return results
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []

    return await coordinator.get(
        cache_key,
        compute_fn=query_fn,
        ttl_seconds=QUERY_CACHE_TTLS.get("sample:search", 300),
    )


def _matches_filters(
    sample: dict[str, Any],
    filters: dict[str, Any],
) -> bool:
    """Check if sample matches filter criteria"""
    for key, value in filters.items():
        if key == "bpm_min" and sample.get("bpm", 0) < value:
            return False
        if key == "bpm_max" and sample.get("bpm", 0) > value:
            return False
        if key == "key" and sample.get("key") != value:
            return False
        if key == "genre" and value not in sample.get("genre_labels", []):
            return False

    return True
