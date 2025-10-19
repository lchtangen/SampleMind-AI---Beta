"""
Audio database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class AudioStatus(str, enum.Enum):
    """Audio processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Audio(Base):
    """Audio file model"""
    
    __tablename__ = "audio_files"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_format = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    
    # Audio properties
    duration = Column(Float, nullable=True)  # seconds
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    bit_depth = Column(Integer, nullable=True)
    
    # Processing status
    status = Column(SQLEnum(AudioStatus), default=AudioStatus.UPLOADED, nullable=False, index=True)
    error_message = Column(String, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audio_files")
    analysis = relationship("AudioAnalysis", back_populates="audio", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Audio(id={self.id}, filename='{self.filename}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "format": self.file_format,
            "size": self.file_size,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "status": self.status.value if isinstance(self.status, AudioStatus) else self.status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "error_message": self.error_message,
        }


class AudioAnalysis(Base):
    """Audio analysis results model"""
    
    __tablename__ = "audio_analysis"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Audio relationship
    audio_id = Column(Integer, ForeignKey("audio_files.id"), nullable=False, unique=True, index=True)
    
    # Basic features
    tempo = Column(Float, nullable=True)  # BPM
    key = Column(String, nullable=True)  # Musical key
    time_signature = Column(String, nullable=True)  # e.g., "4/4"
    loudness = Column(Float, nullable=True)  # dB
    
    # Advanced features
    energy = Column(Float, nullable=True)  # 0.0 - 1.0
    danceability = Column(Float, nullable=True)  # 0.0 - 1.0
    valence = Column(Float, nullable=True)  # 0.0 - 1.0 (positivity)
    acousticness = Column(Float, nullable=True)  # 0.0 - 1.0
    instrumentalness = Column(Float, nullable=True)  # 0.0 - 1.0
    liveness = Column(Float, nullable=True)  # 0.0 - 1.0
    speechiness = Column(Float, nullable=True)  # 0.0 - 1.0
    
    # Spectral features
    spectral_centroid = Column(Float, nullable=True)
    spectral_rolloff = Column(Float, nullable=True)
    zero_crossing_rate = Column(Float, nullable=True)
    
    # AI Analysis (JSON fields)
    genres = Column(JSON, nullable=True)  # ["Electronic", "House"]
    moods = Column(JSON, nullable=True)  # ["Energetic", "Uplifting"]
    instruments = Column(JSON, nullable=True)  # ["Synthesizer", "Drums"]
    tags = Column(JSON, nullable=True)  # ["Summer", "Festival"]
    
    # AI-generated description
    description = Column(String, nullable=True)
    similarity_score = Column(Float, nullable=True)  # Confidence score
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    audio = relationship("Audio", back_populates="analysis")
    
    def __repr__(self):
        return f"<AudioAnalysis(id={self.id}, audio_id={self.audio_id}, tempo={self.tempo})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "audio_id": self.audio_id,
            "features": {
                "tempo": self.tempo,
                "key": self.key,
                "time_signature": self.time_signature,
                "duration": self.audio.duration if self.audio else None,
                "loudness": self.loudness,
                "energy": self.energy,
                "danceability": self.danceability,
                "valence": self.valence,
                "acousticness": self.acousticness,
                "instrumentalness": self.instrumentalness,
                "liveness": self.liveness,
                "speechiness": self.speechiness,
                "spectral_centroid": self.spectral_centroid,
                "spectral_rolloff": self.spectral_rolloff,
                "zero_crossing_rate": self.zero_crossing_rate,
            },
            "ai_analysis": {
                "genres": self.genres or [],
                "moods": self.moods or [],
                "instruments": self.instruments or [],
                "tags": self.tags or [],
                "description": self.description,
                "similarity_score": self.similarity_score,
            },
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
        }
