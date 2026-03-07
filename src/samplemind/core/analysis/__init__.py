"""
SampleMind AI - Music Theory Analysis Module

Advanced harmonic analysis including:
- Chord progression detection
- Key and modulation detection
- Roman numeral functional analysis
- Scale/mode identification
"""

from .chord_templates import (
    CHORD_TEMPLATES,
    NOTE_NAMES,
    SCALE_DEGREES,
    get_chord_template,
    get_roman_numeral,
)
from .fingerprinter import AudioFingerprinter, FingerprintResult
from .genre_classifier import GENRE_TAXONOMY, GenreClassifier, GenreResult
from .harmonic_analyzer import CAMELOT_WHEEL, HarmonicAnalyzer, HarmonicFeatures
from .loop_detector import LoopDetector, LoopResult
from .music_theory import (
    ChordEvent,
    HarmonicAnalysis,
    MusicTheoryAnalyzer,
)
from .quality_scorer import AudioQualityScorer, QualityMetrics
from .rhythmic_analyzer import RhythmicAnalyzer, RhythmicFeatures
from .spectral_analyzer import SpectralAnalyzer, SpectralFeatures
from .timbral_analyzer import TimbralAnalyzer, TimbralFeatures

__all__ = [
    # Chord / theory
    "CHORD_TEMPLATES",
    "SCALE_DEGREES",
    "NOTE_NAMES",
    "get_chord_template",
    "get_roman_numeral",
    "ChordEvent",
    "HarmonicAnalysis",
    "MusicTheoryAnalyzer",
    # Spectral
    "SpectralFeatures",
    "SpectralAnalyzer",
    # Rhythmic
    "RhythmicFeatures",
    "RhythmicAnalyzer",
    # Harmonic
    "CAMELOT_WHEEL",
    "HarmonicFeatures",
    "HarmonicAnalyzer",
    # Timbral
    "TimbralFeatures",
    "TimbralAnalyzer",
    # Quality
    "QualityMetrics",
    "AudioQualityScorer",
    # Genre
    "GENRE_TAXONOMY",
    "GenreResult",
    "GenreClassifier",
    # Loop
    "LoopResult",
    "LoopDetector",
    # Fingerprint
    "FingerprintResult",
    "AudioFingerprinter",
]
