"""
Phase 4.1C: Smart Caching & Predictive Preloading System

This module implements intelligent caching with predictive preloading to achieve:
- 80%+ cache hit ratio through Markov chain prediction
- <200ms perceived latency for cached operations
- 4x performance improvement vs basic caching

Components:
- UsagePatternTracker: Real-time workflow analysis
- MarkovPredictor: Order-2 state transition prediction
- CacheWarmer: Background preloading service
- AdvancedCacheManager: LRU-K eviction and adaptive TTL
"""

from .usage_patterns import UsagePatternTracker
from .markov_predictor import MarkovPredictor
from .cache_warmer import CacheWarmer
from .cache_manager import AdvancedCacheManager

__all__ = [
    "UsagePatternTracker",
    "MarkovPredictor",
    "CacheWarmer",
    "AdvancedCacheManager",
]
