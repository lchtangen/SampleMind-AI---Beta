"""
Core Analysis Module

Advanced audio analysis capabilities including BPM/key detection,
loop segmentation, and harmonic analysis.
"""

from .bpm_key_detector import BPMKeyDetector, quick_bpm, quick_key, quick_label
from .loop_segmenter import LoopSegmenter, quick_segment, quick_best_loop
from .stem_separator import MultiStemSeparator, StemResult, quick_separate, quick_separate_4stem, quick_separate_6stem
from .music_tagger import MusicAutoTagger, TaggingResult, TagPrediction, quick_tag, quick_tag_genres, quick_tag_instruments

__all__ = [
    'BPMKeyDetector',
    'quick_bpm',
    'quick_key',
    'quick_label',
    'LoopSegmenter',
    'quick_segment',
    'quick_best_loop',
    'MultiStemSeparator',
    'StemResult',
    'quick_separate',
    'quick_separate_4stem',
    'quick_separate_6stem',
    'MusicAutoTagger',
    'TaggingResult',
    'TagPrediction',
    'quick_tag',
    'quick_tag_genres',
    'quick_tag_instruments',
    'AudioEmbedder',
    'AudioEmbedding',
    'SimilarityResult',
    'quick_extract_embedding',
    'quick_find_similar',
    'quick_build_library',
    'HarmonicAnalyzer',
    'Chord',
    'ChordProgression',
    'HarmonicAnalysis',
    'quick_analyze_harmonics',
    'quick_detect_key',
    'quick_detect_chords',
]
