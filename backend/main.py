"""
SampleMind AI - FastAPI Backend
Revolutionary AI-powered music production platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1 import auth, audio, websocket

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 SampleMind AI API starting up...")
    print("📊 Initializing monitoring...")
    print("🔌 Connecting to databases...")
    yield
    # Shutdown
    print("👋 SampleMind AI API shutting down...")

app = FastAPI(
    title="SampleMind AI API",
    description="Revolutionary AI-powered music production platform with neurologic quantum audio processing",
    version="0.1.0-beta",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://localhost:3001",
        "https://samplemind.ai",  # Production (future)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(audio.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "SampleMind AI API",
        "version": "0.1.0-beta",
        "status": "operational",
        "environment": "development",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health",
        "theme": "cyberpunk-glassmorphism",
        "features": [
            "JWT Authentication",
            "Audio Upload & Analysis", 
            "Real-time WebSocket Updates",
            "AI-Powered Music Production",
            "Multi-format Audio Support",
            "Advanced Feature Extraction"
        ],
        "endpoints": {
            "auth": 5,
            "audio": 5,
            "websocket": 1,
            "system": 3
        },
        "support": {
            "formats": ["mp3", "wav", "flac", "aiff", "ogg"],
            "max_upload": "100MB",
            "ai_models": ["tempo", "key", "genre", "mood", "instruments"]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "samplemind-api",
        "checks": {
            "api": "ok",
            "database": "not_configured",  # TODO: Add DB health check
            "redis": "not_configured",      # TODO: Add Redis health check
            "celery": "not_configured"      # TODO: Add Celery health check
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "active",
        "endpoints": {
            "auth": "active",
            "audio": "active",
            "analysis": "active",
            "search": "pending"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
