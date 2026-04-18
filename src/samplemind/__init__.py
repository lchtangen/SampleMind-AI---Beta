#!/usr/bin/env python3
"""
SampleMind AI — Root Package
=============================

Top-level package for the SampleMind AI music production platform.

This ``__init__.py`` exposes:
  1. **Version metadata** — ``__version__``, ``__codename__``, ``__author__``, etc.
  2. **Lazy imports** via a custom ``__getattr__`` so that heavy dependencies
     (torch, librosa, faiss) are only loaded when the caller actually accesses
     ``AudioEngine``, ``AdvancedAudioLoader``, or other core classes.

Quick start::

    import samplemind
    print(samplemind.__version__)        # "2.1.0-beta"
    engine = samplemind.AudioEngine()    # lazy-imported on first access
"""

from typing import Any

# ── Package metadata ──────────────────────────────────────────────────────────

__version__ = "2.1.0-beta"
__codename__ = "Phoenix"
__status__ = "Beta"
__release_date__ = "2025-10-04"
__author__ = "SampleMind AI Team"
__description__ = "Professional AI-powered music production suite"


# ── Lazy imports ──────────────────────────────────────────────────────────────
# Each branch below defers the heavy import until the attribute is first used.
# This keeps ``import samplemind`` near-instant even when torch/librosa are installed.


def __getattr__(name: str) -> Any:
    """Resolve package-level names on first access (PEP 562 lazy imports)."""
    if name == "AudioEngine":
        from .core.engine.audio_engine import AudioEngine

        return AudioEngine
    elif name == "AudioFeatures":
        from .core.engine.audio_engine import AudioFeatures

        return AudioFeatures
    elif name == "AnalysisLevel":
        from .core.engine.audio_engine import AnalysisLevel

        return AnalysisLevel
    elif name == "AdvancedAudioLoader":
        from .core.loader import AdvancedAudioLoader

        return AdvancedAudioLoader
    elif name == "LoadingStrategy":
        from .core.loader import LoadingStrategy

        return LoadingStrategy
    elif name == "AudioFormat":
        from .core.loader import AudioFormat

        return AudioFormat
    elif name == "SampleMindAIManager":
        from .integrations.ai_manager import SampleMindAIManager

        return SampleMindAIManager
    elif name == "AnalysisType":
        from .integrations.ai_manager import AnalysisType

        return AnalysisType
    elif name == "AIProvider":
        from .integrations.ai_manager import AIProvider

        return AIProvider
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# ── Public API ────────────────────────────────────────────────────────────────
# Everything listed here is importable from the package root.

__all__ = [
    # Core classes
    "AudioEngine",
    "AudioFeatures",
    "AnalysisLevel",
    "AdvancedAudioLoader",
    "LoadingStrategy",
    "AudioFormat",
    # AI classes
    "SampleMindAIManager",
    "AnalysisType",
    "AIProvider",
    # Package info
    "__version__",
    "__author__",
    "__description__",
]


# ── Convenience helpers ───────────────────────────────────────────────────────


def get_version() -> str:
    """Return the current SampleMind AI version string."""
    return __version__


def get_info() -> dict:
    """Return a dict of basic package metadata (name, version, description, author)."""
    return {
        "name": "SampleMind AI",
        "version": __version__,
        "description": __description__,
        "author": __author__,
    }
