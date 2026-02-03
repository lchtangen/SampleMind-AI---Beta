"""
SampleMind AI - Structured Logging Configuration

Provides comprehensive logging using Loguru with:
- Console output (pretty, color-coded)
- File output (detailed, with rotation)
- JSON output (for log aggregation)
- Request tracing and context injection
- Automatic log rotation and compression
"""

import sys
from pathlib import Path
from typing import Optional, Any
from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = False,
    log_format: str = "standard",
) -> Path:
    """
    Configure structured logging for SampleMind AI.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ~/.samplemind/logs)
        enable_console: Enable console output
        enable_file: Enable file output
        enable_json: Enable JSON output for log aggregation
        log_format: Log format ('standard', 'detailed', 'minimal')

    Returns:
        Path to the logs directory

    Example:
        >>> log_dir = setup_logging("DEBUG", enable_json=True)
        >>> logger.info("Application started", extra={"user_id": 123})
    """

    # Determine log directory
    if log_dir is None:
        log_dir = Path.home() / ".samplemind" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default logger
    logger.remove()

    # ========================================================================
    # Console Output (User-Facing)
    # ========================================================================

    if enable_console:
        if log_format == "minimal":
            console_format = "<level>{level: <8}</level> | {message}"
        elif log_format == "detailed":
            console_format = (
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "{message}"
            )
        else:  # standard
            console_format = (
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan> | "
                "{message}"
            )

        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # ========================================================================
    # File Output (Detailed Logging)
    # ========================================================================

    if enable_file:
        log_file = log_dir / "samplemind.log"

        logger.add(
            str(log_file),
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
            level="DEBUG",  # Always log DEBUG level to file
            rotation="10 MB",  # Rotate when file reaches 10MB
            retention="7 days",  # Keep logs for 7 days
            compression="zip",  # Compress rotated logs
            backtrace=True,
            diagnose=True,
        )

    # ========================================================================
    # JSON Output (Log Aggregation)
    # ========================================================================

    if enable_json:
        json_file = log_dir / "samplemind.json"

        def json_formatter(record: Any) -> dict:
            """Format log record as JSON for aggregation services."""
            return {
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "message": record["message"],
                "exception": record["exception"] is not None,
                "extra": record["extra"],
            }

        logger.add(
            str(json_file),
            format="{message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            serialize=True,  # Output as JSON
            backtrace=False,
            diagnose=False,
        )

    logger.info(
        f"Logging initialized",
        extra={
            "level": log_level,
            "log_dir": str(log_dir),
            "console": enable_console,
            "file": enable_file,
            "json": enable_json,
        },
    )

    return log_dir


def get_logger(name: str) -> Any:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)


def configure_log_level(level: str) -> None:
    """Change logging level at runtime."""
    logger.remove()
    setup_logging(log_level=level)


class LogContext:
    """Context manager for adding context to logs."""

    def __init__(self, **context) -> None:
        """
        Initialize log context.

        Args:
            **context: Key-value pairs to add to all logs in this context

        Example:
            >>> with LogContext(user_id=123, request_id="req_456"):
            ...     logger.info("Processing request")
        """
        self.context = context
        self._token = None

    def __enter__(self) -> "LogContext":
        """Enter context."""
        self._token = logger.contextualize(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        if self._token:
            self._token.__exit__(exc_type, exc_val, exc_tb)


# ============================================================================
# Pre-configured Loggers
# ============================================================================


class CLILogger:
    """Logger for CLI operations."""

    @staticmethod
    def command_start(command: str, **kwargs) -> None:
        """Log start of command."""
        logger.info(f"Command started: {command}", extra=kwargs)

    @staticmethod
    def command_complete(command: str, duration_ms: float, **kwargs) -> None:
        """Log successful command completion."""
        logger.info(
            f"Command completed: {command}",
            extra={"duration_ms": duration_ms, **kwargs},
        )

    @staticmethod
    def command_error(command: str, error: str, **kwargs) -> None:
        """Log command error."""
        logger.error(
            f"Command failed: {command}",
            extra={"error": error, **kwargs},
        )


class AudioLogger:
    """Logger for audio processing operations."""

    @staticmethod
    def analysis_start(file_path: str, level: str) -> None:
        """Log start of audio analysis."""
        logger.info(
            f"Audio analysis started",
            extra={"file_path": file_path, "level": level},
        )

    @staticmethod
    def analysis_complete(file_path: str, duration_ms: float, features: dict) -> None:
        """Log completed audio analysis."""
        logger.info(
            f"Audio analysis completed",
            extra={
                "file_path": file_path,
                "duration_ms": duration_ms,
                "features_count": len(features),
            },
        )

    @staticmethod
    def analysis_error(file_path: str, error: str) -> None:
        """Log audio analysis error."""
        logger.error(
            f"Audio analysis failed",
            extra={"file_path": file_path, "error": error},
        )


class AILogger:
    """Logger for AI operations."""

    @staticmethod
    def request_start(provider: str, model: str, **kwargs) -> None:
        """Log start of AI request."""
        logger.info(
            f"AI request started",
            extra={"provider": provider, "model": model, **kwargs},
        )

    @staticmethod
    def request_complete(
        provider: str, response_time_ms: float, tokens_used: int, **kwargs
    ) -> None:
        """Log completed AI request."""
        logger.info(
            f"AI request completed",
            extra={
                "provider": provider,
                "response_time_ms": response_time_ms,
                "tokens_used": tokens_used,
                **kwargs,
            },
        )

    @staticmethod
    def request_error(provider: str, error: str, **kwargs) -> None:
        """Log AI request error."""
        logger.error(
            f"AI request failed",
            extra={"provider": provider, "error": error, **kwargs},
        )

    @staticmethod
    def fallback_triggered(original_provider: str, fallback_provider: str) -> None:
        """Log fallback to different AI provider."""
        logger.warning(
            f"Falling back to {fallback_provider}",
            extra={
                "original_provider": original_provider,
                "fallback_provider": fallback_provider,
            },
        )


class DatabaseLogger:
    """Logger for database operations."""

    @staticmethod
    def query_start(operation: str, **kwargs) -> None:
        """Log start of database query."""
        logger.debug(f"Database query started", extra={"operation": operation, **kwargs})

    @staticmethod
    def query_complete(operation: str, duration_ms: float, rows: int = 0) -> None:
        """Log completed database query."""
        logger.debug(
            f"Database query completed",
            extra={"operation": operation, "duration_ms": duration_ms, "rows": rows},
        )

    @staticmethod
    def query_error(operation: str, error: str) -> None:
        """Log database query error."""
        logger.error(
            f"Database query failed",
            extra={"operation": operation, "error": error},
        )


class CacheLogger:
    """Logger for cache operations."""

    @staticmethod
    def hit(key: str, size_bytes: int) -> None:
        """Log cache hit."""
        logger.debug(
            f"Cache hit",
            extra={"key": key, "size_bytes": size_bytes},
        )

    @staticmethod
    def miss(key: str) -> None:
        """Log cache miss."""
        logger.debug(f"Cache miss", extra={"key": key})

    @staticmethod
    def store(key: str, size_bytes: int) -> None:
        """Log cache store."""
        logger.debug(f"Cache store", extra={"key": key, "size_bytes": size_bytes})

    @staticmethod
    def evict(reason: str, freed_bytes: int) -> None:
        """Log cache eviction."""
        logger.info(
            f"Cache eviction: {reason}",
            extra={"freed_bytes": freed_bytes},
        )


# ============================================================================
# Initialization
# ============================================================================

# Initialize logging on module import
_log_dir = setup_logging()
