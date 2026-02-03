"""API routes"""

from . import (
    ai,
    audio,
    auth,
    batch,
    collections,
    health,
    search,
    settings,
    sync,
    tasks,
    websocket,
)

__all__ = ["health", "audio", "ai", "batch", "websocket", "auth", "settings", "tasks", "sync", "collections", "search"]
