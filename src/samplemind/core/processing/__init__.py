"""
Advanced Audio Processing Module

This module contains advanced audio processing capabilities including:
- Stem separation (vocals, drums, bass, instruments)
- Audio-to-MIDI conversion
- Real-time audio streaming
- Advanced analysis features
"""

from .stem_separation import StemSeparationEngine, StemType
from .audio_to_midi import AudioToMIDIConverter, MIDIConversionMode

__all__ = [
    'StemSeparationEngine',
    'StemType',
    'AudioToMIDIConverter',
    'MIDIConversionMode',
]
