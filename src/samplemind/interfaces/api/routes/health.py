"""Health check endpoints"""

from fastapi import APIRouter, Depends
from samplemind.interfaces.api.schemas.common import HealthCheckResponse
from samplemind.interfaces.api.config import get_settings
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.interfaces.api import __version__

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Basic health check"""
    settings = get_settings()
    
    components = {}
    
    # Check AudioEngine
    audio_engine = get_app_state("audio_engine")
    components["audio_engine"] = "healthy" if audio_engine else "unavailable"
    
    # Check AI Manager
    ai_manager = get_app_state("ai_manager")
    if ai_manager:
        try:
            providers = ai_manager.get_available_providers()
            components["ai_providers"] = f"{len(providers)} available"
        except:
            components["ai_providers"] = "error"
    else:
        components["ai_providers"] = "unavailable"
    
    return HealthCheckResponse(
        status="healthy",
        version=__version__,
        environment=settings.ENVIRONMENT,
        components=components
    )


@router.get("/health/ready")
async def readiness_check():
    """Readiness probe for K8s"""
    audio_engine = get_app_state("audio_engine")
    ai_manager = get_app_state("ai_manager")
    
    if not audio_engine or not ai_manager:
        return {"status": "not_ready"}
    
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check():
    """Liveness probe for K8s"""
    return {"status": "alive"}
