"""MongoDB connection and models using Beanie ODM"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
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
        name = "batch_jobs"
        indexes = [
            "batch_id",
            "user_id",
            "status",
            "created_at",
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
    
    # Usage tracking
    total_analyses: int = 0
    total_uploads: int = 0
    
    class Settings:
        name = "users"
        indexes = [
            "user_id",
            "email",
            "username",
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
            document_models=[AudioFile, Analysis, BatchJob, User]
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


def get_database():
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
