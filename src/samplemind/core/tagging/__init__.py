#!/usr/bin/env python3
"""
AI-Powered Sample Tagging System

Complete tagging system for organizing and discovering audio samples.

Modules:
- tag_vocabulary: 200+ tag categories and validation
- ai_tagger: Hybrid AI + rule-based tagging engine
- tag_extractor: Extract tags from audio features
"""

from .tag_vocabulary import (
    TagVocabulary,
    TagConfidence,
    get_vocabulary,
    GENRES,
    MOODS,
    INSTRUMENTS,
    ENERGY_LEVELS,
    DESCRIPTORS,
)

from .ai_tagger import (
    AITagger,
    get_tagger,
)

__version__ = "1.0.0"

__all__ = [
    "TagVocabulary",
    "TagConfidence",
    "AITagger",
    "get_vocabulary",
    "get_tagger",
    "GENRES",
    "MOODS",
    "INSTRUMENTS",
    "ENERGY_LEVELS",
    "DESCRIPTORS",
]
