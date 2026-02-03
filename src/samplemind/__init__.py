#!/usr/bin/env python3
"""
SampleMind AI v6 - Professional Music Production Suite
The ultimate AI-powered music analysis and production platform

This package provides comprehensive audio analysis, AI-powered insights,
and professional music production tools through a beautiful CLI interface.

Main Components:
- Core Audio Engine: Advanced audio processing with LibROSA
- AI Manager: Unified interface for OpenAI GPT-5 and Google AI
- Audio Loader: Professional-grade audio file loading
- CLI Interface: Beautiful interactive terminal interface

Usage:
    from samplemind.core.engine import AudioEngine
    from samplemind.integrations.ai_manager import SampleMindAIManager
    from samplemind.interfaces.cli.menu import SampleMindCLI
"""
import logging
import sys
import warnings

# --- MONKEY PATCH START ---
# Fix for Librosa 0.10.1 compability with Scipy 1.14+ (removal of signal.hann)
try:
    import scipy.signal
    if not hasattr(scipy.signal, 'hann'):
        import scipy.signal.windows
        scipy.signal.hann = scipy.signal.windows.hann
except ImportError:
    pass
# --- MONKEY PATCH END ---

from typing import Any

"""
SampleMind AI Beta v2.0 Phoenix
================================
AI-Powered Music Production Platform

Version: Beta 2.0 (Phoenix)
Codename: Phoenix - Rising from the ashes of v6
"""

__version__ = "2.1.0-beta"
__codename__ = "Phoenix"
__status__ = "Beta"
__release_date__ = "2025-10-04"
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
