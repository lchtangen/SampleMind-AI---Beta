"""MongoDB connection and models using Beanie ODM"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import Field
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

# Global MongoDB client
_mongo_client: Optional[AsyncIOMotorClient] = None
_database = None


class AudioFile(Document):
    """Audio file metadata model"""
    file_id: str = Field(..., unique=True, index=True)
    filename: str
    file_path: str
    file_size: int
    duration: float
    sample_rate: int
    channels: int
    format: str
    user_id: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        """MongoDB collection settings"""
        name = "audio_files"
        indexes = [
            "file_id",
            "user_id",
            "uploaded_at",
        ]


class Analysis(Document):
    """Audio analysis results model"""
    analysis_id: str = Field(..., unique=True, index=True)
    file_id: str = Field(..., index=True)
    user_id: Optional[str] = None

    # Audio features
    tempo: float
    key: str
    mode: str
    time_signature: List[int]
    duration: float

    # Spectral features
    spectral_features: Optional[Dict[str, Any]] = None

    # AI analysis
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_detailed: Optional[Dict[str, Any]] = None
    production_tips: List[str] = Field(default_factory=list)
    creative_ideas: List[str] = Field(default_factory=list)
    fl_studio_recommendations: List[str] = Field(default_factory=list)

    # Metadata
    analysis_level: str
    processing_time: float
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """MongoDB collection settings"""
        name = "analyses"
        indexes = [
            "analysis_id",
            "file_id",
            "user_id",
            "analyzed_at",
        ]


class BatchJob(Document):
    """Batch processing job model"""
    batch_id: str = Field(..., unique=True, index=True)
    user_id: Optional[str] = None
    status: str  # pending, processing, completed, failed
    total_files: int
    completed: int = 0
    failed: int = 0
    file_ids: List[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """MongoDB collection settings"""
        name = "batch_jobs"
        indexes = [
            "batch_id",
            "user_id",
            "status",
            "created_at",
        ]


class Favorite(Document):
    """User favorite analysis model"""
    favorite_id: str = Field(..., unique=True, index=True)
    user_id: Optional[str] = None
    analysis_id: str = Field(..., index=True)
    file_name: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    rating: int = Field(default=0, ge=0, le=5)

    class Settings:
        """MongoDB collection settings"""
        name = "favorites"
        indexes = [
            "favorite_id",
            "user_id",
            "analysis_id",
            "added_at",
        ]


class UserSettings(Document):
    """User settings and preferences model"""
    settings_id: str = Field(..., unique=True, index=True)
    user_id: Optional[str] = None

    # Feature preferences
    default_analysis_level: str = "STANDARD"
    auto_save_results: bool = False
    cache_enabled: bool = True

    # Export preferences
    export_format: str = "JSON"  # JSON, CSV, YAML, Markdown
    export_path: Optional[str] = None

    # Display preferences
    theme: str = "dark"  # dark, light, cyberpunk, etc.
    show_advanced_stats: bool = False

    # Performance
    max_cache_size: int = 100
    batch_parallel_workers: int = 4

    # UI preferences
    show_waveform: bool = True
    waveform_height: int = 10
    auto_preview: bool = False

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """MongoDB collection settings"""
        name = "user_settings"
        indexes = [
            "settings_id",
            "user_id",
            "updated_at",
        ]


class User(Document):
    """User model (for future authentication)"""
    user_id: str = Field(..., unique=True, index=True)
    email: str = Field(..., unique=True, index=True)
    username: str = Field(..., unique=True, index=True)
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # User profile
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    # Usage tracking
    total_analyses: int = 0
    total_uploads: int = 0
    storage_used_mb: float = 0.0
    storage_quota_mb: float = 1000.0
    last_cleanup: Optional[datetime] = None

    # User preferences
    preferences: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        """MongoDB collection settings"""
        name = "users"
        indexes = [
            "user_id",
            "email",
            "username",
        ]


class AudioCollection(Document):
    """Audio collection/playlist model"""
    collection_id: str = Field(..., unique=True, index=True)
    user_id: str = Field(..., index=True)
    name: str
    description: Optional[str] = None
    is_public: bool = False
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Stats (denormalized for performance)
    file_count: int = 0
    total_duration: float = 0.0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        """MongoDB collection settings"""
        name = "audio_collections"
        indexes = [
            "collection_id",
            "user_id",
            "name",
        ]


class APIKey(Document):
    """API key model for external access"""
    key_id: str = Field(..., unique=True, index=True)
    user_id: str = Field(..., index=True)
    name: str
    provider: str
    key_hash: str = Field(..., unique=True)
    permissions: List[str] = Field(default_factory=lambda: ["read"])
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None

    class Settings:
        """MongoDB collection settings"""
        name = "api_keys"
        indexes = [
            "key_id",
            "user_id",
            "is_active",
            "created_at",
        ]


async def init_mongodb(mongodb_url: str, database_name: str = "samplemind"):
    """Initialize MongoDB connection and Beanie ODM"""
    global _mongo_client, _database

    try:
        logger.info(f"🔌 Connecting to MongoDB: {database_name}")

        _mongo_client = AsyncIOMotorClient(
            mongodb_url,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1,
        )

        # Test connection
        await _mongo_client.admin.command('ping')

        _database = _mongo_client[database_name]

        # Initialize Beanie with document models
        await init_beanie(
            database=_database,
            document_models=[AudioFile, Analysis, BatchJob, User, APIKey, Favorite, UserSettings, AudioCollection]
        )

        logger.info("✅ MongoDB connected and Beanie initialized")
        return _database

    except ConnectionFailure as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB: {e}")
        raise


async def close_mongodb():
    """Close MongoDB connection"""
    global _mongo_client

    if _mongo_client:
        _mongo_client.close()
        logger.info("✅ MongoDB connection closed")
        _mongo_client = None


def get_database() -> Any:
    """Get MongoDB database instance"""
    if _database is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return _database


async def health_check() -> bool:
    """Check MongoDB connection health"""
    try:
        if _mongo_client:
            await _mongo_client.admin.command('ping')
            return True
    except Exception:
        pass
    return False
