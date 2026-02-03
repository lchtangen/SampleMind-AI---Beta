"""
SQLAlchemy Database Models
Complete data relationships for SampleMind AI
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

Base = declarative_base()


class User(Base):
    """User model with role-based permissions"""
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String(100), primary_key=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Role & Status
    role = Column(String(50), nullable=False, default="free", index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    
    # Usage Tracking
    total_uploads = Column(Integer, nullable=False, default=0)
    storage_used_mb = Column(Float, nullable=False, default=0.0)
    api_calls_today = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Metadata
    metadata_json = Column("metadata", JSONB, default={})
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    collections = relationship("AudioCollection", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class APIKey(Base):
    """API keys for external developer access"""
    __tablename__ = "api_keys"
    
    key_id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Key Info
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    prefix = Column(String(20), nullable=False, index=True)
    
    # Permissions & Limits
    permissions = Column(JSONB, nullable=False)
    rate_limit_per_minute = Column(Integer, nullable=False, default=60)
    ip_whitelist = Column(JSONB, default=[])
    
    # Status & Usage
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Metadata
    description = Column(Text)
    environment = Column(String(50), nullable=False, default="production")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        Index('idx_api_keys_user_active', 'user_id', 'is_active'),
    )


class OAuthAccount(Base):
    """OAuth provider accounts linked to users"""
    __tablename__ = "oauth_accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Provider Info
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    
    # Tokens
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    
    # Metadata
    linked_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json = Column("metadata", JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="oauth_accounts")
    
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user'),
    )


class UserSession(Base):
    """User sessions for refresh token management"""
    __tablename__ = "user_sessions"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Token
    refresh_token_hash = Column(String(255), unique=True, nullable=False)
    
    # Device Info
    device_info = Column(JSONB, default={})
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class AudioCollection(Base):
    """Audio file collections/playlists"""
    __tablename__ = "audio_collections"
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Collection Info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, nullable=False, default=False, index=True)
    
    # Stats
    file_count = Column(Integer, nullable=False, default=0)
    total_duration = Column(Float, nullable=False, default=0.0)
    
    # Tags & Metadata
    tags = Column(JSONB, default=[])
    metadata_json = Column("metadata", JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="collections")
    
    __table_args__ = (
        Index('idx_collections_user_public', 'user_id', 'is_public'),
    )


class AuditLog(Base):
    """Audit log for security and compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # Action Info
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100))
    resource_id = Column(String(100))
    
    # Request Info
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Details
    details = Column(JSONB, default={})
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_action_timestamp', 'action', 'timestamp'),
    )


# MongoDB Models (using Beanie ODM)
from beanie import Document
from pydantic import Field
from typing import Optional, List


class AudioFile(Document):
    """Audio file metadata (MongoDB)"""
    file_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    
    # File Info
    filename: str
    file_path: str
    file_size: int
    duration: float
    sample_rate: int
    channels: int
    format: str
    
    # Audio Features
    tempo: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    
    # Metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    
    # Status
    processing_status: str = "pending"  # pending, processing, completed, failed
    is_public: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    
    # Collections
    collection_ids: List[str] = Field(default_factory=list)
    
    # Additional metadata
    metadata: dict = Field(default_factory=dict)
    
    class Settings:
        """MongoDB collection settings for AudioFile"""
        name = "audio_files"
        indexes = [
            "user_id",
            "file_id",
            "created_at",
            "processing_status",
            [("user_id", 1), ("created_at", -1)],
        ]


class AnalysisResult(Document):
    """Audio analysis results (MongoDB)"""
    analysis_id: str = Field(..., index=True, unique=True)
    audio_id: str = Field(..., index=True)
    user_id: str = Field(..., index=True)
    
    # Analysis Type
    analysis_type: str  # spectral, harmonic, rhythm, ml_features
    
    # Results
    results: dict
    
    # Processing Info
    model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    
    # Status
    status: str = "completed"  # pending, processing, completed, failed
    error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        """MongoDB collection settings for AnalysisResult"""
        name = "analysis_results"
        indexes = [
            "audio_id",
            "user_id",
            "analysis_type",
            [("audio_id", 1), ("analysis_type", 1)],
        ]


class BatchJob(Document):
    """Batch processing jobs (MongoDB)"""
    job_id: str = Field(..., index=True, unique=True)
    user_id: str = Field(..., index=True)
    
    # Job Info
    job_type: str  # batch_upload, batch_analysis, batch_export
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    
    # Status
    status: str = "pending"  # pending, running, completed, failed, cancelled
    progress_percent: float = 0.0
    
    # Results
    results: List[dict] = Field(default_factory=list)
    errors: List[dict] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Settings:
        """MongoDB collection settings for BatchJob"""
        name = "batch_jobs"
        indexes = [
            "user_id",
            "status",
            "created_at",
            [("user_id", 1), ("status", 1)],
        ]


# Initialize MongoDB models
async def init_mongodb_models():
    """Initialize Beanie with MongoDB models"""
    from beanie import init_beanie
    from motor.motor_asyncio import AsyncIOMotorClient
    from src.samplemind.core.config import settings
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client.get_database()
    
    await init_beanie(
        database=database,
        document_models=[
            AudioFile,
            AnalysisResult,
            BatchJob,
        ]
    )


# Repository pattern for cleaner data access
class UserRepository:
    """User data access layer"""
    
    @staticmethod
    async def get_by_id(session, user_id: str) -> Optional[User]:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(session, email: str) -> Optional[User]:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(session, user_data: dict) -> User:
        user = User(**user_data)
        session.add(user)
        await session.flush()
        return user
    
    @staticmethod
    async def update_usage(session, user_id: str, uploads: int = 0, storage_mb: float = 0):
        from sqlalchemy import update
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                total_uploads=User.total_uploads + uploads,
                storage_used_mb=User.storage_used_mb + storage_mb
            )
        )


class AudioFileRepository:
    """Audio file data access layer"""
    
    @staticmethod
    async def get_by_id(audio_id: str) -> Optional[AudioFile]:
        return await AudioFile.find_one(AudioFile.file_id == audio_id)
    
    @staticmethod
    async def get_by_user(user_id: str, skip: int = 0, limit: int = 50) -> List[AudioFile]:
        return await AudioFile.find(
            AudioFile.user_id == user_id,
            AudioFile.deleted_at == None
        ).sort(-AudioFile.created_at).skip(skip).limit(limit).to_list()
    
    @staticmethod
    async def create(audio_data: dict) -> AudioFile:
        audio = AudioFile(**audio_data)
        await audio.insert()
        return audio
    
    @staticmethod
    async def soft_delete(audio_id: str):
        audio = await AudioFile.find_one(AudioFile.file_id == audio_id)
        if audio:
            audio.deleted_at = datetime.utcnow()
            await audio.save()


# Example usage
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.samplemind.core.config import settings

async def main():
    # PostgreSQL (SQLAlchemy)
    engine = create_async_engine(settings.database_url_async)
    
    async with AsyncSession(engine) as session:
        # Create user
        user = await UserRepository.create(session, {
            "id": "user_123",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "...",
            "role": "free"
        })
        
        await session.commit()
    
    # MongoDB (Beanie)
    await init_mongodb_models()
    
    # Create audio file
    audio = await AudioFileRepository.create({
        "file_id": "audio_123",
        "user_id": "user_123",
        "filename": "track.mp3",
        "file_path": "/storage/audio_123.mp3",
        "file_size": 5242880,
        "duration": 180.5,
        "sample_rate": 44100,
        "channels": 2,
        "format": "mp3"
    })
"""
