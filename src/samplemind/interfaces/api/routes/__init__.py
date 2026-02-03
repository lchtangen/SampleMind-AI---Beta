"""API routes"""

from . import (
    ai,
    audio,
    auth,
    batch,
    collections,
    health,
    settings,
    sync,
    tasks,
    websocket,
)

__all__ = ["health", "audio", "ai", "batch", "websocket", "auth", "settings", "tasks", "sync", "collections"]
