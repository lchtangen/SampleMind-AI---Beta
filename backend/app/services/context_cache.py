"""Context cache service for recommendation engine"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import redis

from app.core.config import settings
from app.schemas.recommendations import SessionContext


class ContextCache:
    """Stores and retrieves session context per user"""

    def __init__(self) -> None:
        self._ttl = settings.CACHE_TTL
        self._local_cache: dict[int, dict] = {}
        self._redis: Optional[redis.Redis] = None

        if settings.ENABLE_CACHING:
            try:
                self._redis = redis.Redis.from_url(
                    settings.REDIS_URL,
                    password=settings.REDIS_PASSWORD,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    decode_responses=True,
                )
                self._redis.ping()
            except Exception:
                # Fallback to in-memory cache if Redis unavailable
                self._redis = None

    def set_context(self, user_id: int, context: SessionContext) -> None:
        payload = context.model_dump()
        payload["updated_at"] = datetime.utcnow().isoformat()

        if self._redis:
            key = self._redis_key(user_id)
            self._redis.set(key, json.dumps(payload), ex=self._ttl)
        else:
            self._local_cache[user_id] = payload

    def get_context(self, user_id: int) -> Optional[SessionContext]:
        data: Optional[dict]
        if self._redis:
            raw = self._redis.get(self._redis_key(user_id))
            data = json.loads(raw) if raw else None
        else:
            data = self._local_cache.get(user_id)

        if not data:
            return None

        return SessionContext(**data)

    def clear_context(self, user_id: int) -> None:
        if self._redis:
            self._redis.delete(self._redis_key(user_id))
        else:
            self._local_cache.pop(user_id, None)

    @staticmethod
    def _redis_key(user_id: int) -> str:
        return f"context:{user_id}"


_context_cache: Optional[ContextCache] = None


def get_context_cache() -> ContextCache:
    global _context_cache
    if _context_cache is None:
        _context_cache = ContextCache()
    return _context_cache
