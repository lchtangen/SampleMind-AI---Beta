"""
RecommendationAgent — Similarity search to find related samples.

Queries the ChromaDB vector store using audio embeddings to find
samples that are harmonically or spectrally similar to the input.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


def recommendation_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Find similar samples via vector similarity search.
    """
    file_path = state.get("file_path", "")
    features = state.get("audio_features", {})

    updates: Dict[str, Any] = {
        "current_stage": "recommendations",
        "progress_pct": 82,
        "messages": state.get("messages", []) + ["🔍 Finding similar samples…"],
    }

    similar: List[Dict[str, Any]] = []

    try:
        from samplemind.core.similarity.similarity import AudioEmbeddingEngine

        embedding_engine = AudioEmbeddingEngine()
        results = embedding_engine.find_similar(file_path, top_k=5)
        similar = [
            {
                "path": str(r.path),
                "score": round(r.score, 4),
                "bpm": r.metadata.get("bpm"),
                "key": r.metadata.get("key"),
            }
            for r in (results or [])
        ]
    except Exception as exc:
        logger.warning("Similarity search unavailable: %s", exc)
        # Fall back to tag-based heuristic match description
        tags = state.get("tags", {}) or {}
        genre = tags.get("genre", ["unknown"])
        similar = [
            {
                "note": f"ChromaDB unavailable. Search manually for {genre[0]} samples.",
                "score": 0.0,
            }
        ]
        updates["errors"] = state.get("errors", []) + [f"RecommendationAgent: {exc}"]

    updates["similar_samples"] = similar
    updates["messages"] = state.get("messages", []) + [
        f"✅ Found {len(similar)} similar sample(s)"
    ]
    updates["progress_pct"] = 88

    return updates
