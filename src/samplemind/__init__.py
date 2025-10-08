#!/usr/bin/env python3
"""
SampleMind AI v1.0.0 Phoenix Beta - Professional Music Production Suite

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

__version__ = "1.0.0-phoenix-beta"
__status__ = "Phoenix Beta"

"""
SampleMind AI Beta v2.0 Phoenix
================================
AI-Powered Music Production Platform

Version: Beta 2.0 (Phoenix)
Codename: Phoenix - Rising from the ashes of v6
"""

__version__ = "0.6.0-beta"  # Beta v0.6.0 - Core Features Stable
__codename__ = "Phoenix"
__status__ = "Beta"
__release_date__ = "2025-10-04"
__author__ = "SampleMind AI Team"
__description__ = "Professional AI-powered music production suite"

# Core imports
from .core.engine.audio_engine import AudioEngine, AudioFeatures, AnalysisLevel
from .core.loader import AdvancedAudioLoader, LoadingStrategy, AudioFormat
from .integrations.ai_manager import SampleMindAIManager, AnalysisType, AIProvider

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

def get_version():
    """Get SampleMind AI version"""
    return __version__

def get_info():
    """Get package information"""
    return {
        "name": "SampleMind AI",
        "version": __version__,
        "description": __description__,
        "author": __author__
    }