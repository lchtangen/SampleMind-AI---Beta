"""
SampleMind AI - Neural Audio Generation Module (Phase 4.3)

Provides AI-powered audio generation capabilities:
- Text-to-sample matching via CLAP embeddings
- Audio variation generation via stem recombination
- AI-assisted prompt-based sample suggestions
- Generation request management and queuing
"""

from .generation_manager import GenerationManager, GenerationRequest, GenerationResult

__all__ = [
    "GenerationManager",
    "GenerationRequest",
    "GenerationResult",
]
