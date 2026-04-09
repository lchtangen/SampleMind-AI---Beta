"""Health check endpoints for liveness and readiness probes.

These endpoints are used by Kubernetes, Docker, and load balancers to
determine if the service is alive and ready to handle requests.

Endpoints:
    GET /health        — Liveness probe (is the service up?)
    GET /health/ready  — Readiness probe (all dependencies working?)
    GET /health/live   — Alternative liveness probe (legacy)
    GET /health/deps   — Detailed dependency status (debugging)
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from samplemind.interfaces.api import __version__
from samplemind.interfaces.api.config import get_settings
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.interfaces.api.schemas.common import HealthCheckResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Liveness probe — service is up and responding.

    Returns:
        dict: Status indicator with version and component health
    """
    settings = get_settings()
    components: dict[str, Any] = {}

    # Check AudioEngine
    audio_engine = get_app_state("audio_engine")
    components["audio_engine"] = "healthy" if audio_engine else "unavailable"

    # Check AI Manager
    ai_manager = get_app_state("ai_manager")
    if ai_manager:
        try:
            providers = ai_manager.get_available_providers()
            components["ai_providers"] = f"{len(providers)} available"
        except Exception as e:
            logger.warning(f"Error checking AI providers: {e}")
            components["ai_providers"] = "error"
    else:
        components["ai_providers"] = "unavailable"

    return HealthCheckResponse(
        status="healthy",
        version=__version__,
        environment=settings.ENVIRONMENT,
        components=components,
    )


@router.get("/health/ready")
async def readiness_check():
    """Readiness probe — all critical dependencies working.

    Checks:
        - Audio Engine available
        - AI Manager initialized
        - At least one AI provider available

    Raises:
        HTTPException: 503 if dependencies not ready
    """
    audio_engine = get_app_state("audio_engine")
    ai_manager = get_app_state("ai_manager")

    if not audio_engine or not ai_manager:
        logger.warning("Readiness check failed: critical components unavailable")
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        providers = ai_manager.get_available_providers()
        if not providers:
            logger.warning("Readiness check failed: no AI providers available")
            raise HTTPException(status_code=503, detail="No AI providers available")
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

    return {"status": "ready", "version": __version__}


@router.get("/health/live")
async def liveness_check():
    """Liveness probe for Kubernetes (legacy endpoint).

    Always returns success unless service is completely crashed.
    """
    return {"status": "alive", "version": __version__}


@router.get("/health/deps")
async def dependency_check() -> dict[str, Any]:
    """Detailed dependency status (for debugging).

    Returns detailed info on all integrations for troubleshooting.
    """
    dep_status: dict[str, Any] = {
        "timestamp": None,
        "components": {},
    }

    # Audio Engine
    try:
        audio_engine = get_app_state("audio_engine")
        dep_status["components"]["audio_engine"] = {
            "status": "available" if audio_engine else "unavailable"
        }
    except Exception as e:
        dep_status["components"]["audio_engine"] = {"status": "error", "error": str(e)}

    # AI Manager
    try:
        ai_manager = get_app_state("ai_manager")
        if ai_manager:
            providers = ai_manager.get_available_providers()
            dep_status["components"]["ai_manager"] = {
                "status": "available",
                "providers": providers
            }
        else:
            dep_status["components"]["ai_manager"] = {"status": "unavailable"}
    except Exception as e:
        dep_status["components"]["ai_manager"] = {"status": "error", "error": str(e)}

    return dep_status
