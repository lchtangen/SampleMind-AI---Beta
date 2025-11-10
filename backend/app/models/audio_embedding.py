"""Audio embedding database model"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON, Index
from sqlalchemy.orm import relationship

from app.core.database import Base

try:  # pragma: no cover - optional dependency
    from pgvector.sqlalchemy import Vector  # type: ignore
except Exception:  # pragma: no cover
    Vector = None


def _embedding_column():
    if Vector is not None:
        return Vector(512)
    return JSON()


class AudioEmbedding(Base):
    """Stores audio embeddings for vector similarity search."""

    __tablename__ = "audio_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    model = Column(String(255), nullable=False, default="laion/clap-htsat-unfused")
    source = Column(String(128), nullable=True)
    embedding = Column(_embedding_column(), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    audio = relationship("Audio", back_populates="embedding")
    user = relationship("User", back_populates="embeddings")

    __table_args__ = (
        Index("ix_audio_embeddings_model", "model"),
    )

    def __repr__(self) -> str:
        return f"<AudioEmbedding(audio_id={self.audio_id}, model='{self.model}')>"
