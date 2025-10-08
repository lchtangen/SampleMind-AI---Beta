"""
SampleMind AI Monitoring Module

Provides comprehensive monitoring, tracing, and structured logging capabilities:

- Prometheus metrics for performance tracking
- OpenTelemetry tracing for distributed request tracking  
- Structured logging with JSON output

Usage:
    # Initialize monitoring
    from samplemind.monitoring import init_monitoring, get_logger
    
    init_monitoring(
        service_name="samplemind-ai",
        service_version="0.6.0",
        log_level="INFO",
        enable_tracing=True,
        enable_metrics=True
    )
    
    # Get structured logger
    logger = get_logger(__name__)
    logger.info("application_started", version="0.6.0")
    
    # Use tracing
    from samplemind.monitoring import trace_span
    with trace_span("audio.analyze"):
        # Process audio
        pass
"""

from typing import Optional

# Metrics
from .metrics import (
    PrometheusMiddleware,
    get_metrics,
    track_time,
    record_audio_processing,
    record_ai_request,
    record_db_operation,
    update_cache_metrics,
    set_app_info,
    update_uptime,
    # Metric instances for direct access
    http_requests_total,
    http_request_duration_seconds,
    audio_processing_duration_seconds,
    ai_api_duration_seconds,
    db_operation_duration_seconds,
    cache_hit_ratio,
)

# Tracing
from .tracing import (
    init_tracing,
    get_tracer,
    instrument_fastapi,
    shutdown_tracing,
    trace_span,
    trace_function,
    add_span_attribute,
    add_span_event,
    set_span_error,
    trace_audio_processing,
    trace_ai_request,
    trace_db_operation,
    trace_cache_operation,
    trace_batch_operation,
    record_ai_tokens,
    record_batch_progress,
)

# Logging
from .logging_config import (
    configure_structured_logging,
    get_logger,
    bind_context,
    unbind_context,
    clear_context,
    RequestLoggingMiddleware,
    log_audio_processing_start,
    log_audio_processing_complete,
    log_ai_request,
    log_ai_response,
    log_db_operation,
    log_cache_operation,
    log_error,
    PerformanceLogger,
    LogLevel,
)

__all__ = [
    # Core initialization
    "init_monitoring",
    # Metrics
    "PrometheusMiddleware",
    "get_metrics",
    "track_time",
    "record_audio_processing",
    "record_ai_request",
    "record_db_operation",
    "update_cache_metrics",
    "set_app_info",
    "update_uptime",
    "http_requests_total",
    "http_request_duration_seconds",
    "audio_processing_duration_seconds",
    "ai_api_duration_seconds",
    "db_operation_duration_seconds",
    "cache_hit_ratio",
    # Tracing
    "init_tracing",
    "get_tracer",
    "instrument_fastapi",
    "shutdown_tracing",
    "trace_span",
    "trace_function",
    "add_span_attribute",
    "add_span_event",
    "set_span_error",
    "trace_audio_processing",
    "trace_ai_request",
    "trace_db_operation",
    "trace_cache_operation",
    "trace_batch_operation",
    "record_ai_tokens",
    "record_batch_progress",
    # Logging
    "configure_structured_logging",
    "get_logger",
    "bind_context",
    "unbind_context",
    "clear_context",
    "RequestLoggingMiddleware",
    "log_audio_processing_start",
    "log_audio_processing_complete",
    "log_ai_request",
    "log_ai_response",
    "log_db_operation",
    "log_cache_operation",
    "log_error",
    "PerformanceLogger",
    "LogLevel",
]


def init_monitoring(
    service_name: str = "samplemind-ai",
    service_version: str = "0.6.0",
    environment: str = "production",
    log_level: str = "INFO",
    json_logs: bool = True,
    log_file: Optional[str] = None,
    enable_tracing: bool = False,
    otlp_endpoint: Optional[str] = None,
    enable_console_tracing: bool = False,
) -> None:
    """
    Initialize all monitoring components.
    
    This is a convenience function to set up metrics, tracing, and logging
    with a single call.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        environment: Environment name (production, development, etc.)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
        log_file: Optional log file path
        enable_tracing: Whether to enable OpenTelemetry tracing
        otlp_endpoint: OTLP collector endpoint for tracing
        enable_console_tracing: Enable console output for traces (debugging)
        
    Example:
        # Basic setup
        init_monitoring()
        
        # Full setup with tracing
        init_monitoring(
            service_name="samplemind-ai",
            service_version="0.6.0",
            environment="production",
            log_level="INFO",
            json_logs=True,
            log_file="/var/log/samplemind/app.log",
            enable_tracing=True,
            otlp_endpoint="http://localhost:4317"
        )
    """
    # Configure structured logging
    configure_structured_logging(
        level=log_level,
        json_logs=json_logs,
        log_file=log_file,
        service_name=service_name,
        environment=environment,
    )
    
    # Initialize tracing if enabled
    if enable_tracing:
        init_tracing(
            service_name=service_name,
            service_version=service_version,
            otlp_endpoint=otlp_endpoint,
            enable_console=enable_console_tracing,
        )
    
    # Set application info for metrics
    import sys
    set_app_info(
        version=service_version,
        environment=environment,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    
    # Log initialization
    logger = get_logger(__name__)
    logger.info(
        "monitoring_initialized",
        service=service_name,
        version=service_version,
        environment=environment,
        tracing_enabled=enable_tracing,
    )