"""
OpenTelemetry tracing configuration for SampleMind AI.

This module provides distributed tracing capabilities for tracking requests
across services and identifying performance bottlenecks.
"""

from typing import Optional, Callable, Any
import functools
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.trace import Status, StatusCode, Span
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from fastapi import FastAPI

# Global tracer instance
_tracer: Optional[trace.Tracer] = None
_tracer_provider: Optional[TracerProvider] = None


def init_tracing(
    service_name: str = "samplemind-ai",
    service_version: str = "0.6.0",
    otlp_endpoint: Optional[str] = None,
    enable_console: bool = False,
) -> None:
    """
    Initialize OpenTelemetry tracing.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        otlp_endpoint: OTLP collector endpoint (e.g., "http://localhost:4317")
        enable_console: Enable console span exporter for debugging
        
    Example:
        init_tracing(
            service_name="samplemind-ai",
            service_version="0.6.0",
            otlp_endpoint="http://localhost:4317"
        )
    """
    global _tracer, _tracer_provider
    
    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "service.instance.id": "samplemind-01",  # Can be made dynamic
        "deployment.environment": "production",  # Can be configured
    })
    
    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter if endpoint is provided
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(span_processor)
    
    # Add console exporter for debugging
    if enable_console:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        _tracer_provider.add_span_processor(console_processor)
    
    # Set as global tracer provider
    trace.set_tracer_provider(_tracer_provider)
    
    # Create tracer instance
    _tracer = trace.get_tracer(__name__)


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.
    
    Returns:
        OpenTelemetry Tracer instance
        
    Raises:
        RuntimeError: If tracing has not been initialized
    """
    if _tracer is None:
        raise RuntimeError("Tracing not initialized. Call init_tracing() first.")
    return _tracer


def instrument_fastapi(app: FastAPI) -> None:
    """
    Instrument FastAPI application with OpenTelemetry.
    
    This automatically creates spans for all HTTP requests.
    
    Args:
        app: FastAPI application instance
        
    Example:
        app = FastAPI()
        instrument_fastapi(app)
    """
    FastAPIInstrumentor.instrument_app(app)


def shutdown_tracing() -> None:
    """
    Shutdown tracing and flush remaining spans.
    
    Should be called during application shutdown.
    """
    global _tracer_provider
    if _tracer_provider:
        _tracer_provider.shutdown()


# ====================
# Span Management
# ====================


@contextmanager
def trace_span(
    name: str,
    attributes: Optional[dict[str, Any]] = None,
    set_status_on_exception: bool = True,
):
    """
    Context manager for creating a trace span.
    
    Args:
        name: Span name
        attributes: Optional span attributes
        set_status_on_exception: Automatically set error status on exception
        
    Example:
        with trace_span("audio.analyze", {"file_format": "wav"}):
            # Process audio file
            ...
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
        except Exception as e:
            if set_status_on_exception:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            raise


def trace_function(
    span_name: Optional[str] = None,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable:
    """
    Decorator to automatically trace a function.
    
    Args:
        span_name: Optional span name (defaults to function name)
        attributes: Optional span attributes
        
    Example:
        @trace_function("audio.transcode", {"operation": "wav_to_mp3"})
        async def transcode_audio(input_path: str, output_path: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        name = span_name or f"{func.__module__}.{func.__qualname__}"
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            with trace_span(name, attributes):
                return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            with trace_span(name, attributes):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ====================
# Span Attributes
# ====================


def add_span_attribute(key: str, value: Any) -> None:
    """
    Add an attribute to the current span.
    
    Args:
        key: Attribute key
        value: Attribute value
        
    Example:
        add_span_attribute("user.id", user_id)
        add_span_attribute("audio.duration", duration_seconds)
    """
    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict[str, Any]] = None) -> None:
    """
    Add an event to the current span.
    
    Args:
        name: Event name
        attributes: Optional event attributes
        
    Example:
        add_span_event("cache.hit", {"key": cache_key})
        add_span_event("ai.request.start", {"provider": "openai"})
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


def set_span_error(exception: Exception) -> None:
    """
    Mark the current span as an error and record the exception.
    
    Args:
        exception: Exception to record
        
    Example:
        try:
            process_audio(file_path)
        except Exception as e:
            set_span_error(e)
            raise
    """
    span = trace.get_current_span()
    if span:
        span.set_status(Status(StatusCode.ERROR, str(exception)))
        span.record_exception(exception)


# ====================
# Audio Processing Spans
# ====================


@contextmanager
def trace_audio_processing(
    operation: str,
    file_path: str,
    file_format: Optional[str] = None,
):
    """
    Context manager for tracing audio processing operations.
    
    Args:
        operation: Operation type (e.g., "analyze", "transcode", "stem_separation")
        file_path: Path to audio file
        file_format: Audio file format (optional)
        
    Example:
        with trace_audio_processing("analyze", file_path, "wav"):
            features = extract_features(file_path)
    """
    attributes = {
        "audio.operation": operation,
        "audio.file_path": file_path,
    }
    if file_format:
        attributes["audio.format"] = file_format
    
    with trace_span(f"audio.{operation}", attributes) as span:
        yield span


# ====================
# AI Provider Spans
# ====================


@contextmanager
def trace_ai_request(
    provider: str,
    operation: str,
    model: Optional[str] = None,
):
    """
    Context manager for tracing AI API requests.
    
    Args:
        provider: AI provider name (e.g., "openai", "anthropic", "google")
        operation: Operation type (e.g., "chat", "embedding", "completion")
        model: Model name (optional)
        
    Example:
        with trace_ai_request("openai", "chat", "gpt-4"):
            response = await client.chat.completions.create(...)
    """
    attributes = {
        "ai.provider": provider,
        "ai.operation": operation,
    }
    if model:
        attributes["ai.model"] = model
    
    with trace_span(f"ai.{provider}.{operation}", attributes) as span:
        yield span


def record_ai_tokens(prompt_tokens: int, completion_tokens: int) -> None:
    """
    Record token usage in the current span.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
    """
    add_span_attribute("ai.tokens.prompt", prompt_tokens)
    add_span_attribute("ai.tokens.completion", completion_tokens)
    add_span_attribute("ai.tokens.total", prompt_tokens + completion_tokens)


# ====================
# Database Spans
# ====================


@contextmanager
def trace_db_operation(
    database: str,
    operation: str,
    collection: Optional[str] = None,
):
    """
    Context manager for tracing database operations.
    
    Args:
        database: Database name (e.g., "mongodb", "redis", "chromadb")
        operation: Operation type (e.g., "query", "insert", "update", "delete")
        collection: Collection/table name (optional)
        
    Example:
        with trace_db_operation("mongodb", "query", "audio_files"):
            results = await collection.find(query).to_list()
    """
    attributes = {
        "db.system": database,
        "db.operation": operation,
    }
    if collection:
        attributes["db.collection"] = collection
    
    with trace_span(f"db.{database}.{operation}", attributes) as span:
        yield span


# ====================
# Cache Spans
# ====================


@contextmanager
def trace_cache_operation(
    operation: str,
    key: Optional[str] = None,
):
    """
    Context manager for tracing cache operations.
    
    Args:
        operation: Operation type (e.g., "get", "set", "delete")
        key: Cache key (optional)
        
    Example:
        with trace_cache_operation("get", cache_key) as span:
            value = await redis.get(cache_key)
            if value:
                add_span_attribute("cache.hit", True)
    """
    attributes = {"cache.operation": operation}
    if key:
        attributes["cache.key"] = key
    
    with trace_span(f"cache.{operation}", attributes) as span:
        yield span


# ====================
# Propagation Utilities
# ====================


def extract_trace_context(headers: dict[str, str]) -> dict:
    """
    Extract trace context from HTTP headers.
    
    Args:
        headers: HTTP headers dictionary
        
    Returns:
        Trace context dictionary
    """
    propagator = TraceContextTextMapPropagator()
    return propagator.extract(headers)


def inject_trace_context(headers: dict[str, str]) -> dict[str, str]:
    """
    Inject trace context into HTTP headers.
    
    Args:
        headers: HTTP headers dictionary
        
    Returns:
        Headers with trace context injected
    """
    propagator = TraceContextTextMapPropagator()
    propagator.inject(headers)
    return headers


# ====================
# Batch Tracing
# ====================


@contextmanager
def trace_batch_operation(
    operation: str,
    batch_size: int,
    batch_id: Optional[str] = None,
):
    """
    Context manager for tracing batch operations.
    
    Args:
        operation: Operation type (e.g., "batch_analyze", "batch_process")
        batch_size: Number of items in the batch
        batch_id: Optional batch identifier
        
    Example:
        with trace_batch_operation("batch_analyze", len(files), batch_id):
            for file in files:
                process_file(file)
    """
    attributes = {
        "batch.operation": operation,
        "batch.size": batch_size,
    }
    if batch_id:
        attributes["batch.id"] = batch_id
    
    with trace_span(f"batch.{operation}", attributes) as span:
        yield span


def record_batch_progress(processed: int, total: int) -> None:
    """
    Record batch processing progress.
    
    Args:
        processed: Number of items processed
        total: Total number of items
    """
    add_span_event("batch.progress", {
        "processed": processed,
        "total": total,
        "progress_pct": (processed / total) * 100 if total > 0 else 0,
    })