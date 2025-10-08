"""
SampleMind Audio Processing Module - Phase 2: Essentia Integration

This module provides high-performance audio analysis using Essentia,
with intelligent fallback to librosa when needed.

Key Features:
- 2-3x faster audio processing with Essentia
- 200+ audio features (vs librosa's ~50)
- Production-grade beat tracking and key detection
- Real-time capable analysis
- Automatic fallback system
- Comprehensive monitoring integration
"""

from .essentia_analyzer import EssentiaAnalyzer, EssentiaFeatures
from .hybrid_analyzer import HybridAnalyzer, AnalysisBackend

__all__ = [
    'EssentiaAnalyzer',
    'EssentiaFeatures',
    'HybridAnalyzer',
    'AnalysisBackend',
]

__version__ = '2.0.0'