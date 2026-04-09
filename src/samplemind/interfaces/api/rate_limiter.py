"""
Shared slowapi Limiter instance — import this in both main.py and route files.

Usage in routes::

    from samplemind.interfaces.api.rate_limiter import limit

    @router.post("/analyze")
    @limit("100/minute")
    async def my_endpoint(request: Request, ...):
        ...

``limit()`` is a no-op decorator when slowapi is not installed, so routes work
in any environment without conditional guards.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def _noop_decorator(*_: Any, **__: Any) -> Callable:
    """No-op rate-limit decorator used when slowapi is unavailable."""

    def decorator(func: Callable) -> Callable:
        return func

    return decorator


try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter: Limiter | None = Limiter(
        key_func=get_remote_address,
        default_limits=["200/minute"],
    )
    limit = limiter.limit  # type: ignore[assignment]
except ImportError:  # pragma: no cover
    limiter = None  # type: ignore[assignment]
    limit = _noop_decorator  # type: ignore[assignment]
