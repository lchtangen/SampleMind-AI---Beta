"""
Prometheus metrics collection for SampleMind AI.

This module provides comprehensive metrics for monitoring API performance,
audio processing, AI API calls, database queries, and cache performance.
"""

from typing import Callable, Optional
import time
import functools
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Create a custom registry for better control
registry = CollectorRegistry()

# ====================
# API Metrics
# ====================

# HTTP Request metrics
http_requests_total = Counter(
    "samplemind_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "samplemind_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

http_requests_in_progress = Gauge(
    "samplemind_http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=registry,
)

# Error metrics
http_exceptions_total = Counter(
    "samplemind_http_exceptions_total",
    "Total HTTP exceptions",
    ["method", "endpoint", "exception_type"],
    registry=registry,
)

# ====================
# Audio Processing Metrics
# ====================

audio_files_processed_total = Counter(
    "samplemind_audio_files_processed_total",
    "Total audio files processed",
    ["status", "format"],
    registry=registry,
)

audio_processing_duration_seconds = Histogram(
    "samplemind_audio_processing_duration_seconds",
    "Audio processing duration in seconds",
    ["operation"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
    registry=registry,
)

audio_file_size_bytes = Histogram(
    "samplemind_audio_file_size_bytes",
    "Audio file size in bytes",
    ["format"],
    buckets=(100_000, 500_000, 1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000),
    registry=registry,
)

# ====================
# AI Provider Metrics
# ====================

ai_api_requests_total = Counter(
    "samplemind_ai_api_requests_total",
    "Total AI API requests",
    ["provider", "operation", "status"],
    registry=registry,
)

ai_api_duration_seconds = Histogram(
    "samplemind_ai_api_duration_seconds",
    "AI API request duration in seconds",
    ["provider", "operation"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
    registry=registry,
)

ai_api_tokens_used = Counter(
    "samplemind_ai_api_tokens_used_total",
    "Total AI API tokens used",
    ["provider", "token_type"],
    registry=registry,
)

ai_api_cost_dollars = Counter(
    "samplemind_ai_api_cost_dollars_total",
    "Total AI API cost in dollars",
    ["provider"],
    registry=registry,
)

# ====================
# Database Metrics
# ====================

db_operations_total = Counter(
    "samplemind_db_operations_total",
    "Total database operations",
    ["database", "operation", "status"],
    registry=registry,
)

db_operation_duration_seconds = Histogram(
    "samplemind_db_operation_duration_seconds",
    "Database operation duration in seconds",
    ["database", "operation"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
    registry=registry,
)

db_connections_active = Gauge(
    "samplemind_db_connections_active",
    "Number of active database connections",
    ["database"],
    registry=registry,
)

# ====================
# Cache Metrics
# ====================

cache_operations_total = Counter(
    "samplemind_cache_operations_total",
    "Total cache operations",
    ["operation", "result"],
    registry=registry,
)

cache_hit_ratio = Gauge(
    "samplemind_cache_hit_ratio",
    "Cache hit ratio (0-1)",
    registry=registry,
)

cache_size_bytes = Gauge(
    "samplemind_cache_size_bytes",
    "Current cache size in bytes",
    registry=registry,
)

# ====================
# System Metrics
# ====================

app_info = Info(
    "samplemind_app",
    "Application information",
    registry=registry,
)

uptime_seconds = Gauge(
    "samplemind_uptime_seconds",
    "Application uptime in seconds",
    registry=registry,
)

# ====================
# Middleware
# ====================


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic Prometheus metrics collection.
    
    Tracks HTTP request duration, status codes, and errors.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        method = request.method
        path = request.url.path

        # Skip metrics endpoint
        if path == "/metrics":
            return await call_next(request)

        # Normalize path (remove IDs, etc.)
        endpoint = self._normalize_path(path)

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        start_time = time.time()
        status_code = 500
        exception_name = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            exception_name = type(e).__name__
            http_exceptions_total.labels(
                method=method, endpoint=endpoint, exception_type=exception_name
            ).inc()
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=method, endpoint=endpoint, status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method, endpoint=endpoint
            ).observe(duration)
            
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize path to reduce cardinality.
        Replace UUIDs, IDs, and other variable parts with placeholders.
        """
        parts = path.split("/")
        normalized = []
        
        for part in parts:
            if not part:
                continue
            # Replace UUIDs and numeric IDs
            if len(part) > 20 or part.isdigit():
                normalized.append("{id}")
            else:
                normalized.append(part)
        
        return "/" + "/".join(normalized)


# ====================
# Decorator for Function Timing
# ====================


def track_time(
    metric: Histogram,
    labels: Optional[dict] = None,
) -> Callable:
    """
    Decorator to track function execution time.
    
    Args:
        metric: Histogram metric to record duration
        labels: Optional labels for the metric
        
    Example:
        @track_time(audio_processing_duration_seconds, {"operation": "analyze"})
        async def analyze_audio(file_path: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ====================
# Metrics Endpoint
# ====================


def get_metrics() -> tuple[bytes, str]:
    """
    Get current metrics in Prometheus format.
    
    Returns:
        Tuple of (metrics_data, content_type)
    """
    return generate_latest(registry), CONTENT_TYPE_LATEST


# ====================
# Helper Functions
# ====================


def record_audio_processing(
    duration: float,
    operation: str,
    status: str = "success",
    file_format: str = "unknown",
    file_size: Optional[int] = None,
) -> None:
    """
    Record audio processing metrics.
    
    Args:
        duration: Processing duration in seconds
        operation: Type of operation (e.g., "analyze", "transcode")
        status: Operation status ("success", "error")
        file_format: Audio file format (e.g., "wav", "mp3")
        file_size: File size in bytes (optional)
    """
    audio_processing_duration_seconds.labels(operation=operation).observe(duration)
    audio_files_processed_total.labels(status=status, format=file_format).inc()
    
    if file_size is not None:
        audio_file_size_bytes.labels(format=file_format).observe(file_size)


def record_ai_request(
    provider: str,
    operation: str,
    duration: float,
    status: str = "success",
    tokens_used: Optional[int] = None,
    cost: Optional[float] = None,
) -> None:
    """
    Record AI API request metrics.
    
    Args:
        provider: AI provider name (e.g., "openai", "anthropic", "google")
        operation: Operation type (e.g., "chat", "embedding", "completion")
        duration: Request duration in seconds
        status: Request status ("success", "error", "timeout")
        tokens_used: Number of tokens used (optional)
        cost: Request cost in dollars (optional)
    """
    ai_api_requests_total.labels(
        provider=provider, operation=operation, status=status
    ).inc()
    
    ai_api_duration_seconds.labels(provider=provider, operation=operation).observe(
        duration
    )
    
    if tokens_used is not None:
        ai_api_tokens_used.labels(provider=provider, token_type="total").inc(
            tokens_used
        )
    
    if cost is not None:
        ai_api_cost_dollars.labels(provider=provider).inc(cost)


def record_db_operation(
    database: str,
    operation: str,
    duration: float,
    status: str = "success",
) -> None:
    """
    Record database operation metrics.
    
    Args:
        database: Database name (e.g., "mongodb", "redis", "chromadb")
        operation: Operation type (e.g., "query", "insert", "update", "delete")
        duration: Operation duration in seconds
        status: Operation status ("success", "error")
    """
    db_operations_total.labels(
        database=database, operation=operation, status=status
    ).inc()
    
    db_operation_duration_seconds.labels(database=database, operation=operation).observe(
        duration
    )


def update_cache_metrics(hits: int, misses: int, size_bytes: Optional[int] = None) -> None:
    """
    Update cache metrics.
    
    Args:
        hits: Number of cache hits
        misses: Number of cache misses
        size_bytes: Current cache size in bytes (optional)
    """
    total = hits + misses
    if total > 0:
        hit_ratio = hits / total
        cache_hit_ratio.set(hit_ratio)
    
    cache_operations_total.labels(operation="get", result="hit").inc(hits)
    cache_operations_total.labels(operation="get", result="miss").inc(misses)
    
    if size_bytes is not None:
        cache_size_bytes.set(size_bytes)


def set_app_info(version: str, environment: str, python_version: str) -> None:
    """
    Set application information metrics.
    
    Args:
        version: Application version
        environment: Environment name (e.g., "production", "development")
        python_version: Python version
    """
    app_info.info({
        "version": version,
        "environment": environment,
        "python_version": python_version,
    })


def update_uptime(seconds: float) -> None:
    """
    Update application uptime metric.
    
    Args:
        seconds: Uptime in seconds
    """
    uptime_seconds.set(seconds)