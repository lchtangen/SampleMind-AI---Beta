"""Embedding service for audio recommendations"""

from __future__ import annotations

import hashlib
import logging
import math
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Audio, AudioEmbedding

_CLAP_MODEL_NAME = "laion/clap-htsat-unfused"
_FALLBACK_MODEL_NAME = "fingerprint-derived"


class EmbeddingService:
    """Generate and persist audio embeddings for recommendation workflows."""

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.dim = max(32, settings.RECS_EMBEDDING_DIM)

    def ensure_embedding(self, audio: Audio, force: bool = False) -> Optional[AudioEmbedding]:
        """Ensure an embedding exists for the given audio record."""
        existing = audio.embedding
        if existing and not force:
            return existing

        vector = self._generate_embedding(audio)
        if vector is None:
            self.logger.warning("No embedding generated for audio_id=%s", audio.id)
            return existing

        model_name, source = self._descriptor()
        if existing is None:
            embedding = AudioEmbedding(
                audio_id=audio.id,
                user_id=audio.user_id,
                model=model_name,
                source=source,
                embedding=vector,
            )
            self.db.add(embedding)
            self.db.commit()
            self.db.refresh(embedding)
            audio.embedding = embedding
            return embedding

        existing.embedding = vector
        existing.model = model_name
        existing.source = source
        self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def _generate_embedding(self, audio: Audio) -> Optional[List[float]]:
        if settings.RECS_USE_CLAP:
            vector = self._clap_embedding(audio)
            if vector:
                return vector
        return self._fingerprint_embedding(audio)

    def _descriptor(self) -> tuple[str, str]:
        if settings.RECS_USE_CLAP:
            return _CLAP_MODEL_NAME, "clap"
        return _FALLBACK_MODEL_NAME, settings.RECS_EMBEDDING_FALLBACK

    def _clap_embedding(self, audio: Audio) -> Optional[List[float]]:
        """Attempt to generate a CLAP embedding. Falls back if provider unavailable."""
        try:
            from samplemind.core.embeddings import clap  # type: ignore
        except Exception:  # pragma: no cover - optional dependency
            self.logger.info("CLAP embedding provider unavailable; using fallback")
            return None

        try:
            client = getattr(clap, "ClapEmbeddingClient", None)
            if client is None:
                self.logger.info("CLAP client missing; using fallback")
                return None
            runner = client()
            vector = runner.embed_audio(audio.file_path)
            if not vector:
                return None
            return self._normalize(vector)
        except Exception as exc:  # pragma: no cover - runtime safeguard
            self.logger.exception("CLAP embedding failed for audio_id=%s: %s", audio.id, exc)
            return None

    def _fingerprint_embedding(self, audio: Audio) -> List[float]:
        """Deterministic hash-based embedding for environments without CLAP."""
        seed_source = audio.fingerprint or f"{audio.user_id}:{audio.filename}:{audio.id}"
        digest = hashlib.sha256(seed_source.encode("utf-8")).digest()
        values: List[float] = []

        while len(values) < self.dim:
            for byte in digest:
                values.append((byte / 255.0) * 2 - 1)
                if len(values) == self.dim:
                    break
            digest = hashlib.sha256(digest + seed_source.encode("utf-8")).digest()

        return self._normalize(values)

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(v * v for v in vector))
        if norm == 0:
            return vector
        return [v / norm for v in vector]
