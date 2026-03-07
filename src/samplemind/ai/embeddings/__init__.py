"""SampleMind AI — audio embeddings sub-package.

Provides three complementary embedding / classification services:

- :class:`~samplemind.ai.embeddings.beats_encoder.BEATsEncoder`
    Microsoft BEATs — 768-dim embeddings, AudioSet-trained.

- :class:`~samplemind.ai.embeddings.ast_classifier.ASTClassifier`
    MIT AST — 527-class AudioSet classification with confidence scores.

- :class:`~samplemind.ai.embeddings.music_embedder.MusicEmbedder`
    music2vec — 768-dim music-domain embeddings + ChromaDB storage.
"""

from .ast_classifier import ASTClassifier, AudioLabel
from .beats_encoder import BEATsEncoder
from .music_embedder import MusicEmbedder

__all__ = [
    "BEATsEncoder",
    "ASTClassifier",
    "AudioLabel",
    "MusicEmbedder",
]
