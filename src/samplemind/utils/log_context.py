"""
SampleMind AI - Contextual Logging

Provides request tracking and context injection for all logs using ContextVar.
Enables tracing of operations across async boundaries.

Usage:
    >>> from samplemind.utils.log_context import set_request_context, get_request_id
    >>> set_request_context(request_id="req_123", user_id="user_456")
    >>> logger.info("Processing request")  # Will include request_id and user_id
"""

from contextvars import ContextVar
from typing import Optional
import uuid
from loguru import logger


# ============================================================================
# Context Variables
# ============================================================================

request_id: ContextVar[str] = ContextVar("request_id", default="")
user_id: ContextVar[str] = ContextVar("user_id", default="")
command_name: ContextVar[str] = ContextVar("command_name", default="")
session_id: ContextVar[str] = ContextVar("session_id", default="")
operation_id: ContextVar[str] = ContextVar("operation_id", default="")
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


# ============================================================================
# Context Getters & Setters
# ============================================================================


def set_request_context(
    request_id_val: Optional[str] = None,
    user_id_val: Optional[str] = None,
    command_name_val: Optional[str] = None,
    session_id_val: Optional[str] = None,
    correlation_id_val: Optional[str] = None,
) -> str:
    """
    Set request context for tracing.

    Args:
        request_id_val: Request ID (auto-generated if not provided)
        user_id_val: User ID
        command_name_val: Command name
        session_id_val: Session ID
        correlation_id_val: Correlation ID for cross-service tracing

    Returns:
        Generated or provided request ID
    """
    # Generate request ID if not provided
    req_id = request_id_val or str(uuid.uuid4())
    request_id.set(req_id)

    if user_id_val:
        user_id.set(user_id_val)

    if command_name_val:
        command_name.set(command_name_val)

    if session_id_val:
        session_id.set(session_id_val)

    if correlation_id_val:
        correlation_id.set(correlation_id_val)
    else:
        # Use request_id as correlation_id if not set
        correlation_id.set(req_id)

    return req_id


def get_request_id() -> str:
    """Get current request ID."""
    return request_id.get()


def get_user_id() -> str:
    """Get current user ID."""
    return user_id.get()


def get_command_name() -> str:
    """Get current command name."""
    return command_name.get()


def get_session_id() -> str:
    """Get current session ID."""
    return session_id.get()


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id.get()


def get_all_context() -> dict:
    """Get all context variables as dictionary."""
    return {
        "request_id": request_id.get(),
        "user_id": user_id.get(),
        "command": command_name.get(),
        "session_id": session_id.get(),
        "correlation_id": correlation_id.get(),
    }


def clear_context() -> None:
    """Clear all context variables."""
    request_id.set("")
    user_id.set("")
    command_name.set("")
    session_id.set("")
    operation_id.set("")
    correlation_id.set("")


# ============================================================================
# Context Manager
# ============================================================================


class RequestContext:
    """Context manager for request tracking."""

    def __init__(
        self,
        request_id_val: Optional[str] = None,
        user_id_val: Optional[str] = None,
        command_name_val: Optional[str] = None,
        **extra_context,
    ):
        """
        Initialize request context.

        Args:
            request_id_val: Request ID
            user_id_val: User ID
            command_name_val: Command name
            **extra_context: Additional context variables

        Example:
            >>> with RequestContext(command_name_val="analyze:full"):
            ...     logger.info("Starting analysis")
        """
        self.request_id_val = request_id_val
        self.user_id_val = user_id_val
        self.command_name_val = command_name_val
        self.extra_context = extra_context
        self._previous_context = None

    def __enter__(self):
        """Enter context."""
        # Save previous context
        self._previous_context = get_all_context()

        # Set new context
        set_request_context(
            request_id_val=self.request_id_val,
            user_id_val=self.user_id_val,
            command_name_val=self.command_name_val,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore previous context."""
        # Restore previous context
        if self._previous_context:
            set_request_context(
                request_id_val=self._previous_context.get("request_id"),
                user_id_val=self._previous_context.get("user_id"),
                command_name_val=self._previous_context.get("command"),
                session_id_val=self._previous_context.get("session_id"),
                correlation_id_val=self._previous_context.get("correlation_id"),
            )


# ============================================================================
# Contextual Logging Functions
# ============================================================================


def log_with_context(level: str, message: str, **kwargs) -> None:
    """
    Log message with automatic context injection.

    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context

    Example:
        >>> log_with_context("info", "Processing file", file="sample.wav")
    """
    context = {
        "request_id": request_id.get(),
        "user_id": user_id.get(),
        "command": command_name.get(),
        "session_id": session_id.get(),
        "correlation_id": correlation_id.get(),
        **kwargs,
    }

    # Remove empty context values
    context = {k: v for k, v in context.items() if v}

    level_lower = level.lower()
    if level_lower == "debug":
        logger.debug(message, extra=context)
    elif level_lower == "info":
        logger.info(message, extra=context)
    elif level_lower == "warning":
        logger.warning(message, extra=context)
    elif level_lower == "error":
        logger.error(message, extra=context)
    elif level_lower == "critical":
        logger.critical(message, extra=context)
    else:
        logger.info(message, extra=context)


def log_debug(message: str, **kwargs) -> None:
    """Log debug message with context."""
    log_with_context("debug", message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    """Log info message with context."""
    log_with_context("info", message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log warning message with context."""
    log_with_context("warning", message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """Log error message with context."""
    log_with_context("error", message, **kwargs)


def log_critical(message: str, **kwargs) -> None:
    """Log critical message with context."""
    log_with_context("critical", message, **kwargs)


# ============================================================================
# Structured Logging Helpers
# ============================================================================


class OperationTimer:
    """Timer for tracking operation duration."""

    def __init__(self, operation: str):
        """
        Initialize operation timer.

        Args:
            operation: Name of operation to track

        Example:
            >>> with OperationTimer("audio_analysis") as timer:
            ...     # Do work
            ...     pass
            >>> logger.info(f"Took {timer.duration_ms}ms")
        """
        self.operation = operation
        self.duration_ms = 0
        self._start_time = None

    def __enter__(self):
        """Enter context."""
        import time

        self._start_time = time.time()
        log_info(f"Operation started", operation=self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and log duration."""
        import time

        if self._start_time:
            self.duration_ms = (time.time() - self._start_time) * 1000

            if exc_type is None:
                log_info(
                    f"Operation completed",
                    operation=self.operation,
                    duration_ms=self.duration_ms,
                )
            else:
                log_error(
                    f"Operation failed",
                    operation=self.operation,
                    duration_ms=self.duration_ms,
                    error=str(exc_val),
                )


# ============================================================================
# Request Logging Decorators
# ============================================================================


def with_logging(
    operation_name: str = None,
    include_args: bool = False,
    include_result: bool = False,
):
    """
    Decorator for logging function calls with context.

    Args:
        operation_name: Name of operation (defaults to function name)
        include_args: Include function arguments in log
        include_result: Include function result in log

    Example:
        >>> @with_logging("user_authentication", include_result=True)
        ... def authenticate(username, password):
        ...     # Authentication logic
        ...     return user_id
    """

    def decorator(func):
        import functools
        import inspect

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            log_context = {"operation": name}

            if include_args:
                # Get function signature
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                log_context["args"] = str(dict(bound_args.arguments))

            log_info(f"Starting {name}", **log_context)

            try:
                result = func(*args, **kwargs)

                if include_result:
                    log_context["result"] = str(result)[:100]  # Limit length

                log_info(f"Completed {name}", **log_context)
                return result

            except Exception as e:
                log_context["error"] = str(e)
                log_error(f"Failed {name}", **log_context)
                raise

        return wrapper

    return decorator
