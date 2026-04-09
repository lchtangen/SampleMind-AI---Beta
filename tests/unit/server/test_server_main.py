"""
Tests for src/samplemind/server/main.py — the Docker entrypoint module (Step 1).
"""

from __future__ import annotations

import pytest


def test_app_importable():
    """samplemind.server.main must export `app` without crashing."""
    from samplemind.server import main  # noqa: F401
    assert hasattr(main, "app"), "server/main.py must expose `app`"


def test_app_is_asgi_callable():
    """The `app` object should be an ASGI app (callable)."""
    from samplemind.server.main import app

    assert callable(app), "`app` must be callable (ASGI interface)"


def test_app_routes_present():
    """FastAPI app should have at least a health route registered."""
    try:
        from samplemind.server.main import app
        from fastapi import FastAPI

        if not isinstance(app, FastAPI):
            pytest.skip("app is not a FastAPI instance — skipping route check")

        route_paths = [r.path for r in app.routes]
        # Health endpoint must exist (from interfaces/api/main.py)
        assert any("/health" in p for p in route_paths), (
            f"No /health route found. Routes: {route_paths}"
        )
    except ImportError:
        pytest.skip("FastAPI not installed")
