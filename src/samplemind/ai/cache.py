"""Ultra-fast AI response caching with Redis and prompt fingerprinting

This module provides intelligent caching for AI API responses using:
- Redis for distributed caching
- Blake3 for ultra-fast hashing (faster than SHA-256)
- Content-based fingerprinting for deduplication
- 7-day TTL for cost optimization

Expected benefits:
- 60-80% cost reduction on repeated prompts
- <2ms cache lookup overhead
- Deterministic cache keys for consistency
"""

import orjson
from blake3 import blake3
from aiocache import caches, Cache
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

# Redis configuration from environment
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "604800"))  # 7 days default

# Configure Redis cache
caches.set_config({
    "default": {
        "cache": "aiocache.RedisCache",
        "endpoint": REDIS_HOST,
        "port": REDIS_PORT,
        "timeout": 1,
        "serializer": {
            "class": "aiocache.serializers.PickleSerializer"
        },
        "ttl": CACHE_TTL,
        "namespace": "samplemind:ai"
    }
})


def prompt_fingerprint(payload: Dict[str, Any]) -> str:
    """Generate deterministic hash from AI request payload
    
    Uses Blake3 for ultra-fast hashing (10x faster than SHA-256).
    Canonicalizes JSON with sorted keys for consistency.
    
    Args:
        payload: AI request payload (prompt, model, params)
        
    Returns:
        64-character hex hash
    """
    # Canonicalize JSON with sorted keys
    blob = orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)
    return blake3(blob).hexdigest()


def cache_key(provider: str, payload: Dict[str, Any]) -> str:
    """Generate cache key with namespace
    
    Format: ai:v2:{provider}:{fingerprint}
    Version prefix (v2) allows cache invalidation if needed.
    
    Args:
        provider: AI provider name (ollama, gemini, claude, openai)
        payload: Request payload
        
    Returns:
        Cache key string
    """
    return f"ai:v2:{provider}:{prompt_fingerprint(payload)}"


async def get_cached_response(
    provider: str,
    payload: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Get cached AI response if exists
    
    Args:
        provider: AI provider name
        payload: Request payload
        
    Returns:
        Cached response dict or None if cache miss
    """
    key = cache_key(provider, payload)
    cache = caches.get("default")
    
    try:
        result = await cache.get(key)
        if result:
            logger.info(
                f"🎯 Cache HIT for {provider}: {key[:24]}... "
                f"(saved API call)"
            )
            return result
        else:
            logger.debug(f"Cache MISS for {provider}: {key[:24]}...")
            return None
    except Exception as e:
        logger.error(f"Cache error: {e}")
        return None


async def cache_response(
    provider: str,
    payload: Dict[str, Any],
    response: Dict[str, Any],
    ttl: Optional[int] = None
) -> None:
    """Cache AI response with optional custom TTL
    
    Args:
        provider: AI provider name
        payload: Request payload
        response: AI response to cache
        ttl: Optional custom TTL in seconds (default: 7 days)
    """
    key = cache_key(provider, payload)
    cache = caches.get("default")
    cache_ttl = ttl or CACHE_TTL
    
    try:
        await cache.set(key, response, ttl=cache_ttl)
        logger.info(
            f"💾 Cached {provider} response: {key[:24]}... "
            f"(TTL: {cache_ttl}s)"
        )
    except Exception as e:
        logger.error(f"Failed to cache response: {e}")


async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring
    
    Returns:
        Dict with hit rate, size, etc.
    """
    cache = caches.get("default")
    
    try:
        # Get Redis info
        redis_client = cache.client
        info = await redis_client.info("stats")
        
        hits = int(info.get("keyspace_hits", 0))
        misses = int(info.get("keyspace_misses", 0))
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0
        
        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total,
            "redis_host": REDIS_HOST,
            "ttl": CACHE_TTL
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"error": str(e)}


async def clear_provider_cache(provider: str) -> int:
    """Clear all cached responses for a specific provider
    
    Useful for debugging or when provider behavior changes.
    
    Args:
        provider: Provider name to clear
        
    Returns:
        Number of keys deleted
    """
    cache = caches.get("default")
    pattern = f"samplemind:ai:ai:v2:{provider}:*"
    
    try:
        redis_client = cache.client
        keys = await redis_client.keys(pattern)
        if keys:
            deleted = await redis_client.delete(*keys)
            logger.info(f"Cleared {deleted} cached responses for {provider}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return 0


async def warm_cache(
    common_prompts: list[Dict[str, Any]],
    provider: str = "ollama"
) -> int:
    """Pre-warm cache with common prompts
    
    Useful for reducing cold-start latency on common queries.
    Run this during off-peak hours.
    
    Args:
        common_prompts: List of common prompt payloads
        provider: Provider to use for warming
        
    Returns:
        Number of prompts warmed
    """
    from .http_client import make_ai_request
    from .router import get_provider_url
    
    warmed = 0
    url = get_provider_url(Provider[provider.upper()])
    
    for prompt in common_prompts:
        # Check if already cached
        cached = await get_cached_response(provider, prompt)
        if cached:
            continue
            
        try:
            # Make request and cache
            response = await make_ai_request(url, prompt)
            await cache_response(provider, prompt, response)
            warmed += 1
        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            
    logger.info(f"Cache warming complete: {warmed} new entries")
    return warmed
