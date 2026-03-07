"""AI-powered features for SampleMind.

Phase 4: Advanced AI capabilities including:
- Sample classification and auto-tagging
- AI-powered mastering
- Smart caching and prediction
"""

__version__ = "0.1.0"

from .classification import AIClassifier, ClassificationResult
from .classification.auto_tagger import AutoTagger
from .mastering import MasteringEngine, MasteringProfile, ReferenceAnalyzer
from .mastering.processing_chain import MasteringChain, ProcessingStep

__all__ = [
    # Classification
    "AIClassifier",
    "ClassificationResult",
    "AutoTagger",
    # Mastering
    "MasteringEngine",
    "MasteringProfile",
    "ReferenceAnalyzer",
    "MasteringChain",
    "ProcessingStep",
]
