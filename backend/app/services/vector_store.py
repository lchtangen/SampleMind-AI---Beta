"""Lightweight vector store facade for sample recommendations"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import exp, sqrt
from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Audio, AudioAnalysis, AudioEmbedding
from app.schemas import SessionContext


def _to_list(value: Optional[object]) -> Optional[List[float]]:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [float(x) for x in value]
    if isinstance(value, memoryview):
        return [float(x) for x in value]
    return None


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    # Ensure same dimensionality
    length = min(len(a), len(b))
    if length == 0:
        return 0.0
    dot = sum(a[i] * b[i] for i in range(length))
    norm_a = sqrt(sum(a[i] * a[i] for i in range(length)))
    norm_b = sqrt(sum(b[i] * b[i] for i in range(length)))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return max(min(dot / (norm_a * norm_b), 1.0), -1.0)


@dataclass
class VectorEntry:
    audio_id: int
    user_id: int
    filename: str
    tempo: Optional[float]
    key: Optional[str]
    genres: List[str]
    moods: List[str]
    embedding: Optional[List[float]]
    uploaded_at: datetime


@dataclass
class VectorMatch:
    audio_id: int
    entry: VectorEntry
    base_score: float
    components: Dict[str, float]


class VectorStore:
    """Simplified in-memory vector search with optional embedding similarity."""

    def __init__(self) -> None:
        self._entries: List[VectorEntry] = []

    def refresh(self, db: Session) -> None:
        entries: List[VectorEntry] = []
        query = (
            db.query(Audio)
            .options(joinedload(Audio.analysis), joinedload(Audio.embedding))
        )
        for audio in query.all():
            analysis: Optional[AudioAnalysis] = audio.analysis
            embedding_model: Optional[AudioEmbedding] = audio.embedding
            entries.append(
                VectorEntry(
                    audio_id=audio.id,
                    user_id=audio.user_id,
                    filename=audio.filename,
                    tempo=analysis.tempo if analysis else None,
                    key=analysis.key if analysis else None,
                    genres=list(analysis.genres) if analysis and analysis.genres else [],
                    moods=list(analysis.moods) if analysis and analysis.moods else [],
                    embedding=_to_list(embedding_model.embedding) if embedding_model else None,
                    uploaded_at=audio.uploaded_at,
                )
            )
        self._entries = entries

    def query(self, context: SessionContext, top_k: int = 10) -> List[VectorMatch]:
        if not self._entries:
            return []

        target_embedding = getattr(context, 'target_embedding', None)
        if target_embedding:
            target_embedding = [float(x) for x in target_embedding]

        ranked: List[VectorMatch] = []
        target_tempo = context.bpm
        target_key = context.key
        target_moods = set(context.mood_tags or [])
        target_genre = context.genre

        for entry in self._entries:
            score = 0.0
            components: Dict[str, float] = {}

            if target_embedding and entry.embedding:
                embedding_score = _cosine_similarity(target_embedding, entry.embedding)
                if embedding_score > 0:
                    components['embedding'] = embedding_score
                    score += embedding_score

            if target_tempo and entry.tempo:
                diff = abs(entry.tempo - target_tempo)
                tempo_score = exp(-diff / 12.0)
                components['tempo_hint'] = tempo_score
                score += 0.2 * tempo_score

            if target_key and entry.key and entry.key == target_key:
                components['key_match'] = 0.15
                score += 0.15

            if target_genre and target_genre in entry.genres:
                components['genre_match'] = 0.1
                score += 0.1

            if target_moods and entry.moods:
                overlap = target_moods.intersection(entry.moods)
                if overlap:
                    mood_score = min(len(overlap) * 0.05, 0.15)
                    components['mood_overlap'] = mood_score
                    score += mood_score

            ranked.append(VectorMatch(audio_id=entry.audio_id, entry=entry, base_score=score, components=components))

        ranked.sort(key=lambda item: item.base_score, reverse=True)
        return ranked[:top_k]


_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
