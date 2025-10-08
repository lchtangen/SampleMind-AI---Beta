#!/usr/bin/env python3
"""
SampleMind AI v6 - FastAPI Application
Main entry point for the REST API backend
"""

import asyncio
import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, ORJSONResponse
import uvicorn

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Enable uvloop for high-performance async I/O
try:
    import uvloop
    uvloop.install()
    logger.info("✅ uvloop enabled for high-performance async I/O")
except ImportError:
    logger.warning("⚠️ uvloop not available - using default asyncio")

from . import __version__
from .config import get_settings
from .exceptions import SampleMindException
from .routes import audio, ai, batch, health, websocket, auth, tasks, stems, midi, streaming, generation, analysis, vector_search

# Import dependencies for state management
from .dependencies import set_app_state

# Track startup time for uptime metrics
_startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan management"""
    logger.info("🚀 Starting SampleMind AI Backend...")

    settings = get_settings()

    # Initialize monitoring (Phase 1)
    try:
        from samplemind.monitoring import (
            init_monitoring,
            get_logger as get_structured_logger,
            update_uptime
        )

        # Determine log level from environment
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Initialize monitoring with structured logging
        init_monitoring(
            service_name="samplemind-ai",
            service_version=__version__,
            environment=settings.ENVIRONMENT,
            log_level=log_level,
            json_logs=settings.ENVIRONMENT == "production",
            enable_tracing=False,  # Can be enabled via env var later
        )

        # Switch to structured logger
        global logger
        logger = get_structured_logger(__name__)
        logger.info("monitoring_initialized", version=__version__, environment=settings.ENVIRONMENT)

        # Store monitoring availability
        set_app_state("monitoring_enabled", True)
    except ImportError as e:
        logger.warning(f"Monitoring not available: {e}. Install monitoring dependencies to enable.")
        set_app_state("monitoring_enabled", False)
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")
        set_app_state("monitoring_enabled", False)

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
        raise

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

    # Initialize high-performance HTTP client for AI requests
    try:
        from samplemind.ai import get_http_client
        http_client = await get_http_client()
        set_app_state("http_client", http_client)
        logger.info("✓ HTTP/2 client initialized for AI requests")
    except Exception as e:
        logger.warning(f"HTTP client initialization warning: {e}")

    # Log cache availability
    try:
        from samplemind.ai import get_cache_stats
        cache_stats = await get_cache_stats()
        if cache_stats:
            logger.info(f"✓ AI cache ready - Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
    except Exception as e:
        logger.warning(f"Cache stats unavailable: {e}")

    if hasattr(logger, 'bind'):
        # Structured logger
        logger.info(
            "backend_ready",
            version=__version__,
            environment=settings.ENVIRONMENT,
            max_workers=settings.MAX_WORKERS,
            upload_dir=str(settings.UPLOAD_DIR),
        )
    else:
        # Standard logger
        logger.info(f"✅ SampleMind AI Backend v{__version__} ready!")
        logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
        logger.info(f"🔧 Max workers: {settings.MAX_WORKERS}")
        logger.info(f"💾 Upload dir: {settings.UPLOAD_DIR}")

    # Start uptime tracking
    from .dependencies import get_app_state as get_state_for_uptime
    if get_state_for_uptime("monitoring_enabled"):
        async def update_uptime_metric():
            """Background task to update uptime metric"""
            from samplemind.monitoring import update_uptime
            while True:
                try:
                    uptime = time.time() - _startup_time
                    update_uptime(uptime)
                    await asyncio.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    if hasattr(logger, 'bind'):
                        logger.error("uptime_metric_error", error=str(e))
                    else:
                        logger.error(f"Uptime metric error: {e}")
                    await asyncio.sleep(30)

        # Start background task
        uptime_task = asyncio.create_task(update_uptime_metric())
        set_app_state("uptime_task", uptime_task)

    yield

    # Cleanup on shutdown
    if hasattr(logger, 'bind'):
        logger.info("backend_shutdown", message="Shutting down SampleMind AI Backend...")
    else:
        logger.info("🛑 Shutting down SampleMind AI Backend...")

    from .dependencies import get_app_state

    # Cancel uptime task
    uptime_task = get_app_state("uptime_task")
    if uptime_task:
        uptime_task.cancel()
        try:
            await uptime_task
        except asyncio.CancelledError:
            pass

    # Close databases
    if get_app_state("mongodb"):
        try:
            from samplemind.core.database import close_mongodb
            await close_mongodb()
        except Exception as e:
            if hasattr(logger, 'bind'):
                logger.error("mongodb_close_error", error=str(e))
            else:
                logger.error(f"Error closing MongoDB: {e}")

    if get_app_state("redis"):
        try:
            from samplemind.core.database import close_redis
            await close_redis()
        except Exception as e:
            if hasattr(logger, 'bind'):
                logger.error("redis_close_error", error=str(e))
            else:
                logger.error(f"Error closing Redis: {e}")

    # Close HTTP client
    if get_app_state("http_client"):
        try:
            from samplemind.ai import close_http_client
            await close_http_client()
            if hasattr(logger, 'bind'):
                logger.info("http_client_closed")
            else:
                logger.info("✓ HTTP client closed")
        except Exception as e:
            if hasattr(logger, 'bind'):
                logger.error("http_client_close_error", error=str(e))
            else:
                logger.error(f"Error closing HTTP client: {e}")

    # Close audio engine and AI manager
    audio_engine = get_app_state("audio_engine")
    if audio_engine:
        audio_engine.shutdown()
        if hasattr(logger, 'bind'):
            logger.info("audio_engine_shutdown")
        else:
            logger.info("✓ AudioEngine shutdown complete")

    ai_manager = get_app_state("ai_manager")
    if ai_manager:
        await ai_manager.close()
        if hasattr(logger, 'bind'):
            logger.info("ai_manager_shutdown")
        else:
            logger.info("✓ AI Manager shutdown complete")

    # Shutdown monitoring
    if get_app_state("monitoring_enabled"):
        try:
            from samplemind.monitoring import shutdown_tracing
            shutdown_tracing()
            if hasattr(logger, 'bind'):
                logger.info("monitoring_shutdown")
            else:
                logger.info("✓ Monitoring shutdown")
        except Exception as e:
            if hasattr(logger, 'bind'):
                logger.error("monitoring_shutdown_error", error=str(e))
            else:
                logger.error(f"Error shutting down monitoring: {e}")

    if hasattr(logger, 'bind'):
        logger.info("shutdown_complete")
    else:
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
        default_response_class=ORJSONResponse,  # High-performance JSON serialization
    )

    # Add monitoring middleware (Phase 1)
    try:
        from samplemind.monitoring import PrometheusMiddleware
        app.add_middleware(PrometheusMiddleware)
        logger.info("✓ Prometheus metrics middleware enabled")
    except ImportError:
        logger.warning("⚠️ Prometheus middleware not available")

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
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(audio.router, prefix="/api/v1/audio", tags=["audio"])
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
    app.include_router(batch.router, prefix="/api/v1/batch", tags=["batch"])
    app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
    app.include_router(stems.router, prefix="/api/v1", tags=["Stem Separation"])
    app.include_router(midi.router, prefix="/api/v1", tags=["MIDI Conversion"])
    app.include_router(streaming.router, prefix="/api/v1", tags=["Audio Streaming"])
    app.include_router(generation.router, prefix="/api/v1", tags=["Music Generation"])
    app.include_router(analysis.router, tags=["Analysis"])  # Includes /api/v1/analysis prefix
    app.include_router(vector_search.router, tags=["Vector Search"])  # Includes /api/v1/vector prefix

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
