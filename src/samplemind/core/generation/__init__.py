"""
AI Music Generation Module

Provides AI-powered music generation capabilities using:
- Google Gemini Lyria RealTime
- Style transfer
- Prompt-based generation
"""

from .lyria_engine import (
    LyriaRealTimeEngine,
    MusicGenerationRequest,
    MusicGenerationResult,
    MusicStyle,
    MusicMood,
)

__all__ = [
    'LyriaRealTimeEngine',
    'MusicGenerationRequest',
    'MusicGenerationResult',
    'MusicStyle',
    'MusicMood',
]
