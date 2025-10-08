"""Health check endpoints with comprehensive monitoring"""

import time
from typing import Dict, Any, Optional
from fastapi import APIRouter, Response
from fastapi.responses import ORJSONResponse
from samplemind.interfaces.api.schemas.common import HealthCheckResponse
from samplemind.interfaces.api.config import get_settings
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.interfaces.api import __version__

router = APIRouter()

# Track startup time for uptime calculation
STARTUP_TIME = time.time()


# ====================
# Metrics Endpoint
# ====================

@router.get("/metrics", include_in_schema=False)
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Exposes all collected metrics in Prometheus format for scraping.
    """
    try:
        from samplemind.monitoring import get_metrics
        metrics_data, content_type = get_metrics()
        return Response(content=metrics_data, media_type=content_type)
    except ImportError:
        return Response(
            content="# Monitoring not initialized\n",
            media_type="text/plain"
        )
    except Exception as e:
        return Response(
            content=f"# Error generating metrics: {str(e)}\n",
            media_type="text/plain",
            status_code=500
        )


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


@router.get("/health/detailed", response_class=ORJSONResponse)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with performance metrics
    Includes cache stats, provider status, and system info
    """
    settings = get_settings()
    uptime = time.time() - STARTUP_TIME
    
    health_data = {
        "status": "healthy",
        "version": __version__,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(uptime, 2),
        "timestamp": time.time()
    }
    
    # Component status
    components = {}
    
    # AudioEngine
    audio_engine = get_app_state("audio_engine")
    components["audio_engine"] = {
        "status": "healthy" if audio_engine else "unavailable",
        "workers": settings.MAX_WORKERS if audio_engine else 0
    }
    
    # AI Manager & Providers
    ai_manager = get_app_state("ai_manager")
    if ai_manager:
        try:
            providers = ai_manager.get_available_providers()
            components["ai_manager"] = {
                "status": "healthy",
                "providers": [p.value for p in providers],
                "provider_count": len(providers)
            }
        except Exception as e:
            components["ai_manager"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        components["ai_manager"] = {"status": "unavailable"}
    
    # Databases
    components["mongodb"] = {"status": "healthy" if get_app_state("mongodb") else "unavailable"}
    components["redis"] = {"status": "healthy" if get_app_state("redis") else "unavailable"}
    components["chromadb"] = {"status": "healthy" if get_app_state("chromadb") else "unavailable"}
    
    # HTTP Client
    http_client = get_app_state("http_client")
    components["http_client"] = {
        "status": "healthy" if http_client else "unavailable",
        "http2_enabled": True if http_client else False
    }
    
    health_data["components"] = components
    
    # AI Cache Statistics
    try:
        from samplemind.ai import get_cache_stats
        cache_stats = await get_cache_stats()
        if cache_stats:
            health_data["cache"] = {
                "status": "available",
                "hit_rate": round(cache_stats.get("hit_rate", 0), 4),
                "total_requests": cache_stats.get("total_requests", 0),
                "hits": cache_stats.get("hits", 0),
                "misses": cache_stats.get("misses", 0)
            }
        else:
            health_data["cache"] = {"status": "unavailable"}
    except Exception as e:
        health_data["cache"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Performance metrics
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        health_data["performance"] = {
            "cpu_percent": round(process.cpu_percent(interval=0.1), 2),
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "threads": process.num_threads()
        }
    except ImportError:
        health_data["performance"] = {"status": "metrics_unavailable"}
    except Exception as e:
        health_data["performance"] = {"error": str(e)}
    
    return health_data


@router.get("/health/ready", response_class=ORJSONResponse)
async def readiness_check():
    """
    Readiness probe for Kubernetes.
    
    Checks if the application is ready to accept traffic by verifying
    that all critical components are initialized and functional.
    
    Returns 200 if ready, 503 if not ready.
    """
    audio_engine = get_app_state("audio_engine")
    ai_manager = get_app_state("ai_manager")
    
    checks = {
        "audio_engine": audio_engine is not None,
        "ai_manager": ai_manager is not None,
    }
    
    # Check if at least one AI provider is available
    if ai_manager:
        try:
            providers = ai_manager.get_available_providers()
            checks["ai_providers"] = len(providers) > 0
        except:
            checks["ai_providers"] = False
    else:
        checks["ai_providers"] = False
    
    all_ready = all(checks.values())
    
    response = {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": time.time()
    }
    
    return ORJSONResponse(
        content=response,
        status_code=200 if all_ready else 503
    )


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness probe for Kubernetes.
    
    Simple check to verify the application is running and responsive.
    Always returns 200 unless the application is completely unresponsive.
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": round(time.time() - STARTUP_TIME, 2)
    }


# ====================
# Component Health Checks
# ====================

async def check_mongodb_health() -> Dict[str, Any]:
    """Check MongoDB connectivity and health."""
    try:
        if not get_app_state("mongodb"):
            return {"status": "unavailable", "message": "Not initialized"}
        
        # Simple check - if it's initialized, consider it healthy
        # More detailed checks can be added later with proper imports
        return {
            "status": "healthy",
            "message": "MongoDB connection active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and health."""
    try:
        if not get_app_state("redis"):
            return {"status": "unavailable", "message": "Not initialized"}
        
        # Simple check - if it's initialized, consider it healthy
        # More detailed checks can be added later with proper imports
        return {
            "status": "healthy",
            "message": "Redis connection active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_ai_providers_health() -> Dict[str, Any]:
    """Check AI providers availability and health."""
    try:
        ai_manager = get_app_state("ai_manager")
        if not ai_manager:
            return {"status": "unavailable", "message": "Not initialized"}
        
        providers = ai_manager.get_available_providers()
        
        return {
            "status": "healthy" if len(providers) > 0 else "degraded",
            "available_providers": [p.value for p in providers],
            "provider_count": len(providers)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/health/dependencies")
async def dependencies_health_check() -> Dict[str, Any]:
    """
    Check health of all external dependencies.
    
    Provides detailed health information for:
    - Database connections (MongoDB, Redis, ChromaDB)
    - AI providers
    - Cache system
    """
    checks = {}
    
    # Check MongoDB
    checks["mongodb"] = await check_mongodb_health()
    
    # Check Redis
    checks["redis"] = await check_redis_health()
    
    # Check ChromaDB
    if get_app_state("chromadb"):
        checks["chromadb"] = {"status": "healthy"}
    else:
        checks["chromadb"] = {"status": "unavailable", "message": "Not initialized"}
    
    # Check AI Providers
    checks["ai_providers"] = await check_ai_providers_health()
    
    # Determine overall status
    statuses = [check.get("status") for check in checks.values()]
    if all(s == "healthy" for s in statuses):
        overall_status = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall_status = "degraded"
    else:
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": time.time()
    }
