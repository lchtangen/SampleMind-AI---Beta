"""AI-powered audio classification and auto-tagging.

Phase 4.1A: Implements intelligent sample classification using rule-based
and optional ML-based approaches for offline-first capability.
"""

from .classifier import AIClassifier, ClassificationResult

__all__ = ["AIClassifier", "ClassificationResult"]
