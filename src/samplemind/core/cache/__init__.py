"""
SampleMind AI — Cache Package

Two-layer caching architecture:

  L1 — core/cache/backends/  (low-level drivers)
       RedisCache: async Redis KV driver with serialization, TTL, pool management

  L2 — core/caching/         (predictive intelligence layer, imported separately)
       AdvancedCacheManager: LRU-K eviction + adaptive TTL
       CacheWarmer:          Background preloading via Markov prediction
       SemanticCache:        Embedding + semantic search result caching
       UsagePatternTracker:  Workflow telemetry → transition matrices

Both layers are complementary. Import from here for the Redis driver;
import from core.caching for the full predictive system.
"""

# Re-export the Redis backend at the cache package level for backward compatibility
# (consumers can import from samplemind.core.cache directly)
from .backends.redis_backend import (
    AudioFeatureCache,
    CacheConfig,
    RateLimitCache,
    RedisCache,
    cache_key,
    cached,
    get_cache,
    init_cache,
)

__all__ = [
    "CacheConfig",
    "RedisCache",
    "AudioFeatureCache",
    "RateLimitCache",
    "cache_key",
    "cached",
    "init_cache",
    "get_cache",
]
