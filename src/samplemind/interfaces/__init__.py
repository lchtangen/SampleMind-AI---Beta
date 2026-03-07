"""
SampleMind AI v3.0 — Interfaces Package

Provides three user-facing interfaces:
- CLI: Interactive terminal menu (Rich / Typer), primary product
- TUI: Full Textual-based terminal UI with 11+ screens
- API: FastAPI REST + WebSocket endpoints (served via uvicorn)

Usage:
    # Start interactive CLI menu
    from samplemind.interfaces.cli.menu import SampleMindCLI

    # Start Textual TUI
    from samplemind.interfaces.tui.app import SampleMindTUI
"""

__all__ = ["SampleMindCLI", "SampleMindTUI"]


def __getattr__(name: str):
    """Lazy-load interface classes to avoid pulling heavy deps at import time."""
    if name == "SampleMindCLI":
        from samplemind.interfaces.cli.menu import SampleMindCLI
        return SampleMindCLI
    if name == "SampleMindTUI":
        from samplemind.interfaces.tui.app import SampleMindTUI  # type: ignore[attr-defined]
        return SampleMindTUI
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
