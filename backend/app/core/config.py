"""
Configuration settings for SampleMind AI Backend
Enhanced with validation, logging, and performance tuning
"""

from pydantic_settings import BaseSettings
from pydantic import validator, Field
from typing import List, Optional
import secrets


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    
    All settings can be overridden via environment variables.
    See .env.example for complete configuration options.
    """
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="development, staging, or production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "SampleMind AI"
    VERSION: str = "0.1.0-beta"
    DESCRIPTION: str = "Revolutionary AI-powered music production platform"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://samplemind.ai",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Database - Using SQLite for development (no setup required!)
    DATABASE_URL: str = "sqlite:///./samplemind.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Security
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for JWT signing - CHANGE IN PRODUCTION"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # AI API Keys (from environment)
    GOOGLE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Recommendations / Embeddings
    RECS_USE_CLAP: bool = False
    RECS_EMBEDDING_DIM: int = 512
    RECS_EMBEDDING_FALLBACK: str = "fingerprint"
    RECS_RECOMMENDATION_MODE: str = "fusion"  # fusion or rules
    
    # File Upload
    UPLOAD_DIR: str = "uploads/audio"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_FORMATS: List[str] = ["mp3", "wav", "flac", "aiff", "ogg"]
    CHUNK_SIZE: int = 1024 * 1024  # 1MB chunks
    
    # Audio Processing
    AUDIO_SAMPLE_RATE: int = 44100
    AUDIO_CHANNELS: int = 2
    AUDIO_BIT_DEPTH: int = 16
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_TIME_LIMIT: int = 600  # 10 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 540  # 9 minutes
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    
    # Monitoring & Logging
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Performance
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    ENABLE_COMPRESSION: bool = True
    COMPRESSION_LEVEL: int = 6
    
    # Email (Optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@samplemind.ai"
    
    # AWS S3 (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Ensure environment is valid"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        """Warn about default secret key in production"""
        if values.get("ENVIRONMENT") == "production" and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


settings = Settings()
