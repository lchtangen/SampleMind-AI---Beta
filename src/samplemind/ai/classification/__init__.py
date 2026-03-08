"""AI-powered audio classification and auto-tagging.

Phase 4.1A: Implements intelligent sample classification using rule-based
and optional ML-based approaches for offline-first capability.
"""

from .auto_tagger import AutoTagger
from .classifier import AIClassifier, ClassificationResult
from .cnn_classifier import MUSIC_CLASSES, CNNAudioClassifier, CNNClassificationResult

__all__ = [
    "AIClassifier",
    "ClassificationResult",
    "AutoTagger",
    "CNNAudioClassifier",
    "CNNClassificationResult",
    "MUSIC_CLASSES",
]
