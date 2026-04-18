"""
Sonic Relationship Graph — FAISS-powered sample similarity network.

Endpoints:
  GET /api/v1/graph/sonic-map    — Nodes + edges for force-directed graph
  GET /api/v1/graph/cluster/{id} — Cluster of similar samples around a node
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class GraphNode(BaseModel):
    id: str
    filename: str
    bpm: float | None = None
    key: str | None = None
    energy: str | None = None
    genre: list[str] = []
    mood: list[str] = []
    x: float = 0.0
    y: float = 0.0


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity")


class SonicMapResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    clusters: list[dict[str, Any]] = []


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/sonic-map")
@rate_limit("30/minute")
async def get_sonic_map(
    request: Request,
    limit: int = Query(200, ge=10, le=500, description="Max nodes"),
    similarity_threshold: float = Query(
        0.6, ge=0.1, le=0.99, description="Min similarity for edges"
    ),
) -> SonicMapResponse:
    """
    Build a force-directed graph of sonic relationships between samples.
    Nodes are samples, edges represent FAISS cosine similarity above threshold.
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return SonicMapResponse(nodes=[], edges=[], clusters=[])

        entries = idx._entries[:limit]
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        # Build nodes
        for i, entry in enumerate(entries):
            nodes.append(
                GraphNode(
                    id=str(i),
                    filename=entry.filename,
                    bpm=entry.bpm,
                    key=entry.key,
                    energy=entry.energy,
                    genre=entry.genre_labels or [],
                    mood=entry.mood_labels or [],
                )
            )

        # Build edges from pairwise similarity (sampled for performance)
        # For each node, find its top-K similar nodes
        import numpy as np

        if hasattr(idx, "_index") and idx._index is not None and len(entries) > 1:
            vectors = idx._index.reconstruct_n(0, min(len(entries), limit))
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1
            normalized = vectors / norms

            # Compute similarity matrix in batches to limit memory
            batch_size = 50
            for start in range(0, len(normalized), batch_size):
                end = min(start + batch_size, len(normalized))
                batch = normalized[start:end]
                sim_matrix = batch @ normalized.T

                for i_local in range(len(batch)):
                    i_global = start + i_local
                    for j in range(i_global + 1, len(normalized)):
                        score = float(sim_matrix[i_local, j])
                        if score >= similarity_threshold:
                            edges.append(
                                GraphEdge(
                                    source=str(i_global),
                                    target=str(j),
                                    weight=round(score, 3),
                                )
                            )

        # Auto-detect clusters via genre grouping
        genre_groups: dict[str, list[str]] = {}
        for node in nodes:
            primary_genre = node.genre[0] if node.genre else "uncategorized"
            genre_groups.setdefault(primary_genre, []).append(node.id)

        clusters = [
            {"label": genre, "node_ids": node_ids, "count": len(node_ids)}
            for genre, node_ids in sorted(
                genre_groups.items(), key=lambda x: len(x[1]), reverse=True
            )[:15]
        ]

        return SonicMapResponse(nodes=nodes, edges=edges, clusters=clusters)

    except Exception as exc:
        logger.error("Sonic map generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Graph generation failed")


@router.get("/cluster/{sample_id}")
@rate_limit("60/minute")
async def get_cluster(
    request: Request,
    sample_id: str,
    top_k: int = Query(10, ge=1, le=50),
) -> dict[str, Any]:
    """
    Get the N most similar samples to a specific sample with relationship explanations.
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            raise HTTPException(status_code=404, detail="No samples indexed")

        # Find the source entry
        source_entry = None
        for entry in idx._entries:
            if entry.filename == sample_id or entry.path == sample_id:
                source_entry = entry
                break

        if not source_entry:
            raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found")

        # Search for similar samples using audio embedding
        results = idx.search_audio(source_entry.path, top_k=top_k + 1)

        # Filter out the source itself
        similar = [
            {
                "filename": r.filename,
                "score": round(r.score, 3),
                "bpm": r.metadata.get("bpm"),
                "key": r.metadata.get("key"),
                "energy": r.metadata.get("energy"),
                "genre": r.metadata.get("genre_labels", []),
                "mood": r.metadata.get("mood_labels", []),
            }
            for r in results
            if r.filename != source_entry.filename
        ][:top_k]

        return {
            "source": {
                "filename": source_entry.filename,
                "bpm": source_entry.bpm,
                "key": source_entry.key,
                "energy": source_entry.energy,
            },
            "similar": similar,
            "total": len(similar),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Cluster query failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Cluster query failed")
