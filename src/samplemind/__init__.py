#!/usr/bin/env python3
"""
SampleMind AI v3.0 — Professional Music Production Suite
AI-powered music analysis and production platform

Main Components:
- Core Audio Engine: Advanced audio processing with LibROSA, Demucs, Basic Pitch
- AI Manager: Unified interface for Claude 3.7 Sonnet, GPT-4o, Gemini 2.0 Flash, Ollama
- Audio Loader: Professional-grade audio file loading (WAV, MP3, FLAC, OGG, AAC)
- CLI Interface: Interactive terminal interface (Rich / Typer)
- TUI Interface: Full Textual-based terminal UI (11+ screens)
- API Layer: FastAPI REST + WebSocket endpoints

Usage:
    from samplemind.core.engine import AudioEngine
    from samplemind.integrations.ai_manager import SampleMindAIManager
    from samplemind.interfaces.cli.menu import SampleMindCLI
"""
import logging
from typing import Any

__version__ = "3.0.0-alpha"
__codename__ = "Phoenix"
__status__ = "Alpha"
__release_date__ = "2026-03-07"
__author__ = "SampleMind AI Team"
__description__ = "Professional AI-powered music production suite"

# Lazy imports - import on demand to avoid loading heavy dependencies at startup
def __getattr__(name: str) -> Any:
    """Lazy load modules on demand"""
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

# Make key classes available at package level
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
    "__description__"
]

def get_version() -> str:
    """Get SampleMind AI version"""
    return __version__

def get_info() -> dict:
    """Get package information"""
    return {
        "name": "SampleMind AI",
        "version": __version__,
        "description": __description__,
        "author": __author__
    }
