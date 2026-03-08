"""AI-powered features for SampleMind.

Phase 4: Advanced AI capabilities including:
- Sample classification and auto-tagging
- AI-powered mastering
- Smart caching and prediction
"""

__version__ = "0.1.0"

from .classification import AIClassifier, ClassificationResult
from .classification.auto_tagger import AutoTagger
from .embeddings import ASTClassifier, AudioLabel, BEATsEncoder, MusicEmbedder
from .mastering import MasteringEngine, MasteringProfile, ReferenceAnalyzer
from .mastering.processing_chain import MasteringChain, ProcessingStep
from .midi import MidiConversionResult, MidiConverter
from .separation import SeparationResult, StemSeparator
from .transcription import TranscriptionResult, WhisperTranscriber

__all__ = [
    # Classification
    "AIClassifier",
    "ClassificationResult",
    "AutoTagger",
    # Embeddings
    "BEATsEncoder",
    "ASTClassifier",
    "AudioLabel",
    "MusicEmbedder",
    # Mastering
    "MasteringEngine",
    "MasteringProfile",
    "ReferenceAnalyzer",
    "MasteringChain",
    "ProcessingStep",
    # MIDI
    "MidiConverter",
    "MidiConversionResult",
    # Separation
    "StemSeparator",
    "SeparationResult",
    # Transcription
    "WhisperTranscriber",
    "TranscriptionResult",
]
