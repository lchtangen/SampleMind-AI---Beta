"""
Configuration management for SampleMind AI Backend
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    ENVIRONMENT: str = "development"
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    MAX_WORKERS: int = 4

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]

    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    ANALYSIS_DIR: Path = DATA_DIR / "analysis"
    CACHE_DIR: Path = DATA_DIR / "cache"

    # File handling
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_AUDIO_FORMATS: List[str] = [
        "audio/wav",
        "audio/x-wav",
        "audio/mpeg",
        "audio/mp3",
        "audio/flac",
        "audio/aiff",
        "audio/x-aiff",
        "audio/ogg",
    ]
    ALLOWED_EXTENSIONS: List[str] = [".wav", ".mp3", ".flac", ".aiff", ".ogg"]

    # Audio processing
    CACHE_SIZE: int = 100
    DEFAULT_SAMPLE_RATE: int = 44100

    # Storage
    STORAGE_PROVIDER: str = "local"  # Options: "local", "s3", "s3-mock"
    S3_BUCKET: str = "samplemind-storage"
    S3_REGION: str = "us-east-1"

    # AI Providers
    GOOGLE_AI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "google_ai"

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "samplemind"
    REDIS_URL: str = "redis://localhost:6379/0"
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "data" / "chroma")
    CHROMA_COLLECTION_NAME: str = "audio_embeddings"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True

    # Timeouts
    REQUEST_TIMEOUT: int = 300  # 5 minutes
    AI_TIMEOUT: int = 120  # 2 minutes

    # Analytics (PostHog)
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"
    POSTHOG_ENABLED: bool = True

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
