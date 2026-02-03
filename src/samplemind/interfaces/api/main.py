#!/usr/bin/env python3
"""
SampleMind AI v6 - FastAPI Application
Main entry point for the REST API backend
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .config import get_settings
from .exceptions import SampleMindException
from .middleware.auth import SimpleAuthMiddleware
from .routes import (
    ai,
    audio,
    auth,
    batch,
    collections,
    health,
    sync,
    tasks,
    websocket,
)
from .routes import (
    settings as settings_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Import dependencies for state management
from .dependencies import set_app_state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan management"""
    logger.info("🚀 Starting SampleMind AI Backend...")

    settings = get_settings()

    # Create required directories
    for directory in [settings.UPLOAD_DIR, settings.ANALYSIS_DIR, settings.CACHE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

    # Initialize AudioEngine
    try:
        from samplemind.core.engine.audio_engine import AudioEngine
        audio_engine = AudioEngine(
            max_workers=settings.MAX_WORKERS,
            cache_size=settings.CACHE_SIZE
        )
        set_app_state("audio_engine", audio_engine)
        logger.info("✓ AudioEngine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize AudioEngine: {e}")
        raise

    # Initialize databases (optional, fail gracefully)
    try:
        from samplemind.core.database import init_mongodb, init_redis
        from samplemind.core.database.chroma import init_chromadb

        # MongoDB
        try:
            await init_mongodb(settings.MONGODB_URL, settings.MONGODB_DB_NAME)
            set_app_state("mongodb", True)
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}")
            set_app_state("mongodb", False)

        # Redis
        try:
            await init_redis(settings.REDIS_URL)
            set_app_state("redis", True)
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            set_app_state("redis", False)

        # ChromaDB
        try:
            init_chromadb(settings.CHROMA_PERSIST_DIR, settings.CHROMA_COLLECTION_NAME)
            set_app_state("chromadb", True)
        except Exception as e:
            logger.warning(f"ChromaDB not available: {e}")
            set_app_state("chromadb", False)

    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

    # Initialize AI Manager
    try:
        from samplemind.integrations.ai_manager import SampleMindAIManager
        ai_manager = SampleMindAIManager()
        set_app_state("ai_manager", ai_manager)
        logger.info("✓ SampleMindAIManager initialized")

        # Log available providers
        providers = ai_manager.get_available_providers()
        logger.info(f"✓ Available AI providers: {[p.value for p in providers]}")
    except Exception as e:
        logger.error(f"Failed to initialize AI Manager: {e}")
        # Don't raise, allow running without AI
        # raise

    # Initialize Sync Manager
    try:
        from samplemind.services.storage import (
            LocalStorageProvider,
            MockS3StorageProvider,
            S3StorageProvider,
        )
        from samplemind.services.sync import SyncManager

        storage_provider = None
        storage_info = ""

        if settings.STORAGE_PROVIDER == "s3":
            try:
                storage_provider = S3StorageProvider(
                    bucket_name=settings.S3_BUCKET,
                    region=settings.S3_REGION
                )
                storage_info = f"S3 ({settings.S3_BUCKET})"
            except ImportError:
                 logger.warning("Boto3 not installed, falling back to Mock S3")
                 storage_provider = MockS3StorageProvider(settings.S3_BUCKET, settings.S3_REGION)
                 storage_info = f"Mock S3 ({settings.S3_BUCKET})"
            except Exception as e:
                logger.error(f"Failed to init S3 provider: {e}. Falling back to local.")

        if settings.STORAGE_PROVIDER == "s3-mock":
             storage_provider = MockS3StorageProvider(settings.S3_BUCKET, settings.S3_REGION)
             storage_info = f"Mock S3 ({settings.S3_BUCKET})"

        if not storage_provider or settings.STORAGE_PROVIDER == "local":
            # Use local storage (default)
            storage_path = settings.CACHE_DIR / "cloud_storage_mock"
            storage_provider = LocalStorageProvider(storage_path)
            storage_info = f"Local ({storage_path})"

        sync_manager = SyncManager(storage_provider)
        set_app_state("sync_manager", sync_manager)
        logger.info(f"✓ SyncManager initialized ({storage_info})")
    except Exception as e:
        logger.error(f"Failed to initialize SyncManager: {e}")

    # Configure JWT authentication
    try:
        from samplemind.core.auth.jwt_handler import configure_jwt
        configure_jwt(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            access_expire=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_expire=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        logger.info("✓ JWT authentication configured")
    except Exception as e:
        logger.warning(f"JWT configuration warning: {e}")

    # Validate API keys
    if not settings.GOOGLE_AI_API_KEY and not settings.OPENAI_API_KEY:
        logger.warning("⚠️  No AI API keys configured. AI features will be limited.")

    logger.info(f"✅ SampleMind AI Backend v{__version__} ready!")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Max workers: {settings.MAX_WORKERS}")
    logger.info(f"💾 Upload dir: {settings.UPLOAD_DIR}")

    yield

    # Cleanup on shutdown
    logger.info("🛑 Shutting down SampleMind AI Backend...")

    from .dependencies import get_app_state

    # Close databases
    if get_app_state("mongodb"):
        try:
            from samplemind.core.database import close_mongodb
            await close_mongodb()
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")

    if get_app_state("redis"):
        try:
            from samplemind.core.database import close_redis
            await close_redis()
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")

    # Close audio engine and AI manager
    audio_engine = get_app_state("audio_engine")
    if audio_engine:
        audio_engine.shutdown()
        logger.info("✓ AudioEngine shutdown complete")

    ai_manager = get_app_state("ai_manager")
    if ai_manager:
        await ai_manager.close()
        logger.info("✓ AI Manager shutdown complete")

    logger.info("👋 Shutdown complete")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""

    settings = get_settings()

    app = FastAPI(
        title="SampleMind AI API",
        description="AI-powered music production and sample analysis API",
        version=__version__,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Register Custom Middleware
    # Note: Middleware is added in reverse order (last added runs first)
    # but since we want CORS to be outermost, we add this BEFORE CORS?
    # Actually add_middleware wraps. So last added = outer.
    # If we want CORS outer, we add it LAST.
    # So let's add Auth first here (inner), then CORS (outer).
    app.add_middleware(SimpleAuthMiddleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    @app.exception_handler(SampleMindException)
    async def samplemind_exception_handler(request, exc: SampleMindException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_type,
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.ENVIRONMENT == "development" else None
            }
        )

    # Register routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
    app.include_router(settings_router.router, prefix="/api/v1", tags=["Settings"])
    app.include_router(sync.router, prefix="/api/v1", tags=["Cloud Sync"])
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
    app.include_router(batch.router, prefix="/api/v1/batch", tags=["batch"])
    app.include_router(collections.router, prefix="/api/v1", tags=["collections"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])

    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint - redirect to docs"""
        return {
            "name": "SampleMind AI API",
            "version": __version__,
            "status": "operational",
            "docs": "/api/docs"
        }

    return app


# Create application instance
app = create_application()




if __name__ == "__main__":
    # Run with uvicorn for development
    uvicorn.run(
        "samplemind.interfaces.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
