#!/usr/bin/env python3
"""
Analytics middleware for FastAPI
Automatically tracks API requests and performance
"""

import time
import logging
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from samplemind.integrations.analytics import get_analytics

logger = logging.getLogger(__name__)


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking API requests and performance metrics"""

    # Routes to exclude from tracking (health checks, etc.)
    EXCLUDE_PATHS = {
        "/api/v1/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/",
        "/favicon.ico",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track request metrics"""

        # Skip excluded paths
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        start_time = time.time()

        # Get user ID from headers if available
        user_id = request.headers.get("X-User-ID", request.headers.get("Authorization"))

        try:
            # Call the next middleware/route handler
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Track the request
            analytics = get_analytics()
            analytics.capture(
                "api_request",
                user_id=user_id,
                properties={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                    "client_host": request.client.host if request.client else None,
                }
            )

            return response

        except Exception as e:
            # Track errors
            duration_ms = (time.time() - start_time) * 1000

            analytics = get_analytics()
            analytics.capture(
                "api_error",
                user_id=user_id,
                properties={
                    "path": request.url.path,
                    "method": request.method,
                    "error": str(e),
                    "duration_ms": duration_ms,
                }
            )

            # Re-raise the exception
            raise
