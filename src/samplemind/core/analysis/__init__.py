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
    SCALE_DEGREES,
    NOTE_NAMES,
    get_chord_template,
    get_roman_numeral,
)
from .music_theory import (
    ChordEvent,
    HarmonicAnalysis,
    MusicTheoryAnalyzer,
)

__all__ = [
    "CHORD_TEMPLATES",
    "SCALE_DEGREES",
    "NOTE_NAMES",
    "get_chord_template",
    "get_roman_numeral",
    "ChordEvent",
    "HarmonicAnalysis",
    "MusicTheoryAnalyzer",
]
