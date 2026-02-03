"""
SampleMind AI - Sample Similarity Module

This module provides audio similarity search capabilities using:
- Audio feature extraction for embedding generation
- ChromaDB vector database for similarity storage
- Efficient querying with filters (BPM, key, genre)
"""

from .embedding_engine import AudioEmbeddingEngine, AudioEmbedding
from .similarity_db import SimilarityDatabase, SimilarityResult

__all__ = [
    "AudioEmbeddingEngine",
    "AudioEmbedding",
    "SimilarityDatabase",
    "SimilarityResult",
]
