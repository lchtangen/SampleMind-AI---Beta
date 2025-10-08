"""
Structured logging configuration for SampleMind AI.

This module provides structured logging using structlog with JSON output
for better log aggregation and analysis in production environments.
"""

import logging
import sys
from typing import Any, Optional
from pathlib import Path

import structlog
from structlog.types import Processor
from pythonjsonlogger import jsonlogger


# ====================
# Log Levels
# ====================


class LogLevel:
    """Log level constants."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ====================
# Structured Logging Configuration
# ====================


def configure_structured_logging(
    level: str = "INFO",
    json_logs: bool = True,
    log_file: Optional[str] = None,
    service_name: str = "samplemind-ai",
    environment: str = "production",
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
        log_file: Optional log file path
        service_name: Service name to include in logs
        environment: Environment name (production, development, etc.)
        
    Example:
        configure_structured_logging(
            level="INFO",
            json_logs=True,
            log_file="/var/log/samplemind/app.log",
            service_name="samplemind-ai",
            environment="production"
        )
    """
    # Define processors for structlog
    processors: list[Processor] = [
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add log level
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        # Add stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.processors.format_exc_info,
        # Add context information
        structlog.processors.CallsiteParameterAdder(
            parameters={
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]
    
    # Add common context
    structlog.contextvars.bind_contextvars(
        service=service_name,
        environment=environment,
    )
    
    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.extend([
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ])
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    log_level = getattr(logging, level.upper())
    
    # Create handlers
    handlers: list[logging.Handler] = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        # JSON formatter for console
        json_formatter = jsonlogger.JsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Human-readable formatter
        console_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Always use JSON for file logs
        json_formatter = jsonlogger.JsonFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )
        file_handler.setFormatter(json_formatter)
        
        handlers.append(file_handler)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("anthropic").setLevel(logging.INFO)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)


# ====================
# Logger Creation
# ====================


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Structured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("processing_audio", file_path=path, duration=duration)
    """
    return structlog.get_logger(name)


# ====================
# Context Management
# ====================


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables that will be included in all subsequent logs.
    
    Args:
        **kwargs: Context key-value pairs
        
    Example:
        bind_context(user_id="user123", request_id="req456")
        logger.info("user_action")  # Will include user_id and request_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """
    Unbind context variables.
    
    Args:
        *keys: Context keys to unbind
        
    Example:
        unbind_context("user_id", "request_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """
    Clear all context variables.
    
    Example:
        clear_context()
    """
    structlog.contextvars.clear_contextvars()


# ====================
# Request Logging Middleware
# ====================


class RequestLoggingMiddleware:
    """
    Middleware for logging HTTP requests with structured data.
    
    Automatically logs request and response information including:
    - Request method, path, headers
    - Response status code, duration
    - Request ID for tracing
    """
    
    def __init__(self, app, logger: Optional[structlog.BoundLogger] = None):
        self.app = app
        self.logger = logger or get_logger("samplemind.api.requests")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        import time
        import uuid
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Bind request context
        bind_context(
            request_id=request_id,
            method=scope["method"],
            path=scope["path"],
            client=f"{scope['client'][0]}:{scope['client'][1]}" if scope.get("client") else None,
        )
        
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "request_started",
            method=scope["method"],
            path=scope["path"],
        )
        
        status_code = 500
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            self.logger.error(
                "request_failed",
                error=str(e),
                exception_type=type(e).__name__,
                exc_info=True,
            )
            raise
        finally:
            duration = time.time() - start_time
            
            # Log response
            self.logger.info(
                "request_completed",
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
            )
            
            # Clear request context
            clear_context()


# ====================
# Common Log Messages
# ====================


def log_audio_processing_start(
    logger: structlog.BoundLogger,
    file_path: str,
    operation: str,
    **kwargs: Any,
) -> None:
    """
    Log the start of audio processing.
    
    Args:
        logger: Logger instance
        file_path: Path to audio file
        operation: Operation type (e.g., "analyze", "transcode")
        **kwargs: Additional context
    """
    logger.info(
        "audio_processing_started",
        file_path=file_path,
        operation=operation,
        **kwargs,
    )


def log_audio_processing_complete(
    logger: structlog.BoundLogger,
    file_path: str,
    operation: str,
    duration: float,
    **kwargs: Any,
) -> None:
    """
    Log the completion of audio processing.
    
    Args:
        logger: Logger instance
        file_path: Path to audio file
        operation: Operation type
        duration: Processing duration in seconds
        **kwargs: Additional context
    """
    logger.info(
        "audio_processing_completed",
        file_path=file_path,
        operation=operation,
        duration_seconds=round(duration, 3),
        **kwargs,
    )


def log_ai_request(
    logger: structlog.BoundLogger,
    provider: str,
    operation: str,
    model: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log an AI API request.
    
    Args:
        logger: Logger instance
        provider: AI provider name
        operation: Operation type
        model: Model name (optional)
        **kwargs: Additional context
    """
    logger.info(
        "ai_request",
        provider=provider,
        operation=operation,
        model=model,
        **kwargs,
    )


def log_ai_response(
    logger: structlog.BoundLogger,
    provider: str,
    operation: str,
    duration: float,
    tokens_used: Optional[int] = None,
    cost: Optional[float] = None,
    **kwargs: Any,
) -> None:
    """
    Log an AI API response.
    
    Args:
        logger: Logger instance
        provider: AI provider name
        operation: Operation type
        duration: Request duration in seconds
        tokens_used: Number of tokens used (optional)
        cost: Request cost in dollars (optional)
        **kwargs: Additional context
    """
    logger.info(
        "ai_response",
        provider=provider,
        operation=operation,
        duration_seconds=round(duration, 3),
        tokens_used=tokens_used,
        cost_dollars=round(cost, 4) if cost else None,
        **kwargs,
    )


def log_db_operation(
    logger: structlog.BoundLogger,
    database: str,
    operation: str,
    duration: float,
    **kwargs: Any,
) -> None:
    """
    Log a database operation.
    
    Args:
        logger: Logger instance
        database: Database name
        operation: Operation type
        duration: Operation duration in seconds
        **kwargs: Additional context
    """
    logger.info(
        "db_operation",
        database=database,
        operation=operation,
        duration_seconds=round(duration, 3),
        **kwargs,
    )


def log_cache_operation(
    logger: structlog.BoundLogger,
    operation: str,
    hit: bool,
    key: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log a cache operation.
    
    Args:
        logger: Logger instance
        operation: Operation type
        hit: Whether the operation was a cache hit
        key: Cache key (optional)
        **kwargs: Additional context
    """
    logger.info(
        "cache_operation",
        operation=operation,
        cache_hit=hit,
        key=key,
        **kwargs,
    )


def log_error(
    logger: structlog.BoundLogger,
    error_type: str,
    message: str,
    **kwargs: Any,
) -> None:
    """
    Log an error with structured data.
    
    Args:
        logger: Logger instance
        error_type: Type/category of error
        message: Error message
        **kwargs: Additional context
    """
    logger.error(
        message,
        error_type=error_type,
        **kwargs,
    )


# ====================
# Performance Logging
# ====================


class PerformanceLogger:
    """
    Context manager for logging operation performance.
    
    Example:
        logger = get_logger(__name__)
        with PerformanceLogger(logger, "audio_analysis"):
            analyze_audio(file_path)
    """
    
    def __init__(
        self,
        logger: structlog.BoundLogger,
        operation: str,
        **context: Any,
    ):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.info(
            f"{self.operation}_started",
            **self.context,
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time if self.start_time else 0
        
        if exc_type is None:
            self.logger.info(
                f"{self.operation}_completed",
                duration_seconds=round(duration, 3),
                **self.context,
            )
        else:
            self.logger.error(
                f"{self.operation}_failed",
                duration_seconds=round(duration, 3),
                error=str(exc_val),
                exception_type=exc_type.__name__,
                **self.context,
            )
        
        return False  # Don't suppress exceptions