"""
Application Configuration
Loads all environment variables and provides type-safe settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Optional
import secrets
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ========================================================================
    # APPLICATION SETTINGS
    # ========================================================================
    app_name: str = "SampleMind AI"
    app_version: str = "2.0.0-beta"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    frontend_url: str = Field(default="http://localhost:3000", env="FRONTEND_URL")
    
    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        env="ALLOWED_ORIGINS"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # ========================================================================
    # SECURITY & AUTHENTICATION
    # ========================================================================
    
    # JWT Configuration
    jwt_secret_key: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Session
    session_secret_key: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        env="SESSION_SECRET_KEY"
    )
    session_max_age_seconds: int = Field(default=2592000, env="SESSION_MAX_AGE_SECONDS")
    
    # Password Hashing
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    # ========================================================================
    # OAUTH2 PROVIDERS
    # ========================================================================
    
    # Google OAuth2
    google_client_id: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:3000/auth/google/callback",
        env="GOOGLE_REDIRECT_URI"
    )
    
    # GitHub OAuth2
    github_client_id: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    github_client_secret: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    github_redirect_uri: str = Field(
        default="http://localhost:3000/auth/github/callback",
        env="GITHUB_REDIRECT_URI"
    )
    
    # Spotify OAuth2
    spotify_client_id: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: Optional[str] = Field(default=None, env="SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri: str = Field(
        default="http://localhost:3000/auth/spotify/callback",
        env="SPOTIFY_REDIRECT_URI"
    )
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    
    # PostgreSQL
    database_url: str = Field(
        default="postgresql://samplemind:samplemind123@localhost:5432/samplemind",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=40, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")
    
    # MongoDB
    mongodb_url: str = Field(
        default="mongodb://localhost:27017/samplemind",
        env="MONGODB_URL"
    )
    mongodb_max_pool_size: int = Field(default=50, env="MONGODB_MAX_POOL_SIZE")
    
    # ChromaDB
    chroma_host: str = Field(default="localhost", env="CHROMA_HOST")
    chroma_port: int = Field(default=8000, env="CHROMA_PORT")
    chroma_collection: str = Field(default="audio_embeddings", env="CHROMA_COLLECTION")
    
    # ========================================================================
    # CLOUD STORAGE
    # ========================================================================
    
    storage_provider: str = Field(default="local", env="STORAGE_PROVIDER")
    
    # Google Cloud Storage
    gcs_bucket_name: Optional[str] = Field(default=None, env="GCS_BUCKET_NAME")
    gcs_project_id: Optional[str] = Field(default=None, env="GCS_PROJECT_ID")
    gcs_credentials_path: Optional[str] = Field(default=None, env="GCS_CREDENTIALS_PATH")
    
    # AWS S3
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-west-2", env="AWS_REGION")
    s3_bucket_name: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    
    # CDN
    cdn_enabled: bool = Field(default=False, env="CDN_ENABLED")
    cdn_url: Optional[str] = Field(default=None, env="CDN_URL")
    
    # ========================================================================
    # AI/ML PROVIDERS
    # ========================================================================
    
    # Google Gemini
    google_ai_api_key: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")
    google_ai_model: str = Field(default="gemini-pro", env="GOOGLE_AI_MODEL")
    
    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    
    # Anthropic Claude
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    
    # Ollama
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3.1:8b", env="OLLAMA_MODEL")
    
    # Hugging Face
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # ========================================================================
    # CELERY TASK QUEUE
    # ========================================================================
    
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    celery_worker_concurrency: int = Field(default=4, env="CELERY_WORKER_CONCURRENCY")
    celery_task_soft_time_limit: int = Field(default=300, env="CELERY_TASK_SOFT_TIME_LIMIT")
    celery_task_time_limit: int = Field(default=600, env="CELERY_TASK_TIME_LIMIT")
    
    # ========================================================================
    # EMAIL CONFIGURATION
    # ========================================================================
    
    smtp_host: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="noreply@samplemind.ai", env="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="SampleMind AI", env="SMTP_FROM_NAME")
    
    email_verification_enabled: bool = Field(default=True, env="EMAIL_VERIFICATION_ENABLED")
    email_verification_expire_hours: int = Field(default=24, env="EMAIL_VERIFICATION_EXPIRE_HOURS")
    password_reset_expire_hours: int = Field(default=1, env="PASSWORD_RESET_EXPIRE_HOURS")
    
    # ========================================================================
    # MONITORING & LOGGING
    # ========================================================================
    
    # Sentry
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    sentry_environment: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.1, env="SENTRY_TRACES_SAMPLE_RATE")
    
    # Prometheus
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    
    # ========================================================================
    # STRIPE PAYMENT PROCESSING
    # ========================================================================
    
    stripe_publishable_key: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    stripe_secret_key: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Subscription Price IDs
    stripe_price_free: str = Field(default="price_free", env="STRIPE_PRICE_FREE")
    stripe_price_pro: Optional[str] = Field(default=None, env="STRIPE_PRICE_PRO")
    stripe_price_studio: Optional[str] = Field(default=None, env="STRIPE_PRICE_STUDIO")
    stripe_price_enterprise: Optional[str] = Field(default=None, env="STRIPE_PRICE_ENTERPRISE")
    
    # ========================================================================
    # ANALYTICS & TRACKING
    # ========================================================================
    
    ga_tracking_id: Optional[str] = Field(default=None, env="GA_TRACKING_ID")
    mixpanel_token: Optional[str] = Field(default=None, env="MIXPANEL_TOKEN")
    posthog_api_key: Optional[str] = Field(default=None, env="POSTHOG_API_KEY")
    posthog_host: str = Field(default="https://app.posthog.com", env="POSTHOG_HOST")
    
    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    
    feature_oauth_enabled: bool = Field(default=True, env="FEATURE_OAUTH_ENABLED")
    feature_api_keys_enabled: bool = Field(default=True, env="FEATURE_API_KEYS_ENABLED")
    feature_batch_processing: bool = Field(default=True, env="FEATURE_BATCH_PROCESSING")
    feature_ai_generation: bool = Field(default=False, env="FEATURE_AI_GENERATION")
    
    # Rate Limits per Role
    rate_limit_free: int = Field(default=10, env="RATE_LIMIT_FREE")
    rate_limit_pro: int = Field(default=100, env="RATE_LIMIT_PRO")
    rate_limit_studio: int = Field(default=500, env="RATE_LIMIT_STUDIO")
    rate_limit_enterprise: int = Field(default=2000, env="RATE_LIMIT_ENTERPRISE")
    
    # Storage Limits (MB)
    storage_limit_free: int = Field(default=100, env="STORAGE_LIMIT_FREE")
    storage_limit_pro: int = Field(default=5000, env="STORAGE_LIMIT_PRO")
    storage_limit_studio: int = Field(default=50000, env="STORAGE_LIMIT_STUDIO")
    storage_limit_enterprise: int = Field(default=-1, env="STORAGE_LIMIT_ENTERPRISE")
    
    # ========================================================================
    # WEBSOCKET CONFIGURATION
    # ========================================================================
    
    ws_enabled: bool = Field(default=True, env="WS_ENABLED")
    ws_port: int = Field(default=8001, env="WS_PORT")
    ws_max_connections: int = Field(default=1000, env="WS_MAX_CONNECTIONS")
    
    # ========================================================================
    # AUDIO PROCESSING
    # ========================================================================
    
    audio_max_size_mb: int = Field(default=500, env="AUDIO_MAX_SIZE_MB")
    audio_max_duration_seconds: int = Field(default=1800, env="AUDIO_MAX_DURATION_SECONDS")
    audio_sample_rate: int = Field(default=44100, env="AUDIO_SAMPLE_RATE")
    audio_bit_depth: int = Field(default=16, env="AUDIO_BIT_DEPTH")
    
    # ========================================================================
    # BACKUP & RECOVERY
    # ========================================================================
    
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    # ========================================================================
    # LEGAL & COMPLIANCE
    # ========================================================================
    
    gdpr_enabled: bool = Field(default=True, env="GDPR_ENABLED")
    data_retention_days: int = Field(default=365, env="DATA_RETENTION_DAYS")
    cookie_consent_required: bool = Field(default=True, env="COOKIE_CONSENT_REQUIRED")
    
    # ========================================================================
    # VALIDATORS
    # ========================================================================
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values"""
        allowed = ['development', 'staging', 'production', 'testing']
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator('jwt_secret_key', 'session_secret_key')
    @classmethod
    def validate_secret_keys(cls, v: str, info) -> str:
        """Ensure secret keys are secure in production"""
        env = info.data.get('environment', 'development')
        if env == 'production' and len(v) < 32:
            raise ValueError(f"{info.field_name} must be at least 32 characters in production")
        return v
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL for SQLAlchemy"""
        return self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": self.allowed_origins_list,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    def get_oauth_config(self, provider: str) -> dict:
        """Get OAuth configuration for a provider"""
        configs = {
            "google": {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "redirect_uri": self.google_redirect_uri,
            },
            "github": {
                "client_id": self.github_client_id,
                "client_secret": self.github_client_secret,
                "redirect_uri": self.github_redirect_uri,
            },
            "spotify": {
                "client_id": self.spotify_client_id,
                "client_secret": self.spotify_client_secret,
                "redirect_uri": self.spotify_redirect_uri,
            },
        }
        return configs.get(provider, {})
    
    class Config:
        """Pydantic configuration for Settings model"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Configuration display (safe for logging)
def get_config_summary() -> dict:
    """Get configuration summary (hides secrets)"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "api_base_url": settings.api_base_url,
        "frontend_url": settings.frontend_url,
        "debug": settings.debug,
        "features": {
            "oauth": settings.feature_oauth_enabled,
            "api_keys": settings.feature_api_keys_enabled,
            "batch_processing": settings.feature_batch_processing,
        },
        "database": {
            "type": "PostgreSQL",
            "pool_size": settings.database_pool_size,
        },
        "cache": {
            "type": "Redis",
            "max_connections": settings.redis_max_connections,
        },
        "storage": {
            "provider": settings.storage_provider,
            "cdn_enabled": settings.cdn_enabled,
        },
    }
