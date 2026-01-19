"""
SampleMind AI - Error Handler Decorators

Provides graceful error handling for CLI commands with:
- Automatic error logging
- User-friendly error messages
- Actionable suggestions
- Error recovery strategies
- Exit code management

Usage:
    >>> @handle_errors(fallback_message="Analysis failed", exit_on_error=True)
    ... async def analyze_command(file: Path):
    ...     # Command logic
    ...     pass
"""

import asyncio
import sys
from functools import wraps
from typing import Callable, Optional, Any
from rich.console import Console
from rich.panel import Panel
from loguru import logger

from samplemind.exceptions import SampleMindError, UserInterruptedError


console = Console()


# ============================================================================
# Error Display
# ============================================================================


def display_error(
    error: Exception,
    command_name: str = "operation",
    include_suggestion: bool = True,
    verbose: bool = False,
) -> None:
    """
    Display error in user-friendly format.

    Args:
        error: Exception to display
        command_name: Name of command that failed
        include_suggestion: Whether to show suggestions
        verbose: Show verbose/debug information
    """
    if isinstance(error, SampleMindError):
        # SampleMind error - show user message and suggestion
        console.print(f"[red]❌ {error.user_message}[/red]")

        if include_suggestion and error.suggestion:
            console.print(f"[yellow]💡 {error.suggestion}[/yellow]")

        if verbose and error.context:
            console.print(
                Panel(
                    str(error.context),
                    title="[dim]Debug Context[/dim]",
                    expand=False,
                )
            )

    else:
        # Generic error - show message
        console.print(f"[red]❌ {command_name} failed[/red]")
        console.print(f"[dim]{str(error)}[/dim]")

        if verbose:
            console.print(
                Panel(
                    f"{error.__class__.__name__}: {str(error)}",
                    title="[dim]Exception Details[/dim]",
                    expand=False,
                )
            )


def display_success(message: str, details: Optional[dict] = None) -> None:
    """Display success message."""
    console.print(f"[green]✅ {message}[/green]")

    if details:
        for key, value in details.items():
            console.print(f"[cyan]{key}:[/cyan] {value}")


# ============================================================================
# Error Handler Decorator
# ============================================================================


def handle_errors(
    fallback_message: str = "An error occurred",
    log_level: str = "ERROR",
    exit_on_error: bool = False,
    include_suggestion: bool = True,
    verbose_errors: bool = False,
):
    """
    Decorator for handling errors in CLI commands.

    Features:
    - Catches and logs all exceptions
    - Displays user-friendly error messages
    - Provides actionable suggestions
    - Handles keyboard interrupts gracefully
    - Manages exit codes

    Args:
        fallback_message: Message for non-SampleMind errors
        log_level: Logging level for errors
        exit_on_error: Whether to exit on error
        include_suggestion: Whether to show suggestions
        verbose_errors: Show detailed error information

    Example:
        >>> @handle_errors(
        ...     fallback_message="Analysis failed",
        ...     exit_on_error=True
        ... )
        ... async def analyze_command(file: Path):
        ...     # Command logic
        ...     pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)

            except KeyboardInterrupt:
                # User interrupted (Ctrl+C)
                command_name = kwargs.get("command", func.__name__)
                logger.info(f"Operation cancelled by user: {command_name}")
                console.print("\n[yellow]⚠️  Operation cancelled[/yellow]")

                if exit_on_error:
                    raise SystemExit(0)
                return None

            except UserInterruptedError as e:
                # Custom interruption error
                logger.info(f"Operation interrupted: {e.operation}")
                console.print(f"[yellow]⚠️  {e.user_message}[/yellow]")

                if exit_on_error:
                    raise SystemExit(0)
                return None

            except SampleMindError as e:
                # SampleMind error - log and display
                logger.log(log_level, e.message, extra=e.context)
                display_error(
                    e,
                    command_name=func.__name__,
                    include_suggestion=include_suggestion,
                    verbose=verbose_errors,
                )

                if exit_on_error:
                    raise SystemExit(1)
                return None

            except asyncio.CancelledError:
                # Task cancelled
                logger.info(f"Task cancelled: {func.__name__}")
                console.print("[yellow]⚠️  Task cancelled[/yellow]")
                raise

            except Exception as e:
                # Unexpected error - log full traceback
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                display_error(
                    e,
                    command_name=func.__name__,
                    include_suggestion=False,
                    verbose=verbose_errors,
                )
                console.print(f"[dim]Run with --verbose for details[/dim]")

                if exit_on_error:
                    raise SystemExit(1)
                return None

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)

            except KeyboardInterrupt:
                command_name = kwargs.get("command", func.__name__)
                logger.info(f"Operation cancelled by user: {command_name}")
                console.print("\n[yellow]⚠️  Operation cancelled[/yellow]")

                if exit_on_error:
                    raise SystemExit(0)
                return None

            except UserInterruptedError as e:
                logger.info(f"Operation interrupted: {e.operation}")
                console.print(f"[yellow]⚠️  {e.user_message}[/yellow]")

                if exit_on_error:
                    raise SystemExit(0)
                return None

            except SampleMindError as e:
                logger.log(log_level, e.message, extra=e.context)
                display_error(
                    e,
                    command_name=func.__name__,
                    include_suggestion=include_suggestion,
                    verbose=verbose_errors,
                )

                if exit_on_error:
                    raise SystemExit(1)
                return None

            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}: {e}")
                display_error(
                    e,
                    command_name=func.__name__,
                    include_suggestion=False,
                    verbose=verbose_errors,
                )
                console.print(f"[dim]Run with --verbose for details[/dim]")

                if exit_on_error:
                    raise SystemExit(1)
                return None

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ============================================================================
# Context Manager Error Handler
# ============================================================================


class ErrorHandling:
    """Context manager for error handling."""

    def __init__(
        self,
        operation: str,
        on_error: Callable[[Exception], None] = None,
        suppress: bool = False,
    ):
        """
        Initialize error handler context.

        Args:
            operation: Name of operation
            on_error: Callback for errors
            suppress: Whether to suppress exceptions

        Example:
            >>> with ErrorHandling("file_processing"):
            ...     process_file(path)
        """
        self.operation = operation
        self.on_error = on_error
        self.suppress = suppress

    def __enter__(self):
        """Enter context."""
        logger.debug(f"Starting operation: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and handle errors."""
        if exc_type is None:
            logger.debug(f"Operation completed: {self.operation}")
            return False

        if exc_val is not None:
            logger.error(
                f"Operation failed: {self.operation}",
                extra={"error": str(exc_val)},
            )

            if self.on_error:
                self.on_error(exc_val)

        return self.suppress


# ============================================================================
# Error Reporting
# ============================================================================


def report_error(
    error: Exception,
    context: Optional[dict] = None,
    suggest_report: bool = False,
) -> None:
    """
    Report error to user with option to submit feedback.

    Args:
        error: Exception to report
        context: Additional context
        suggest_report: Whether to suggest reporting the issue
    """
    error_code = getattr(error, "error_code", "UNKNOWN")

    console.print(
        Panel(
            f"[bold]Error Code:[/bold] {error_code}\n"
            f"[bold]Error:[/bold] {str(error)}\n"
            f"[dim]This error was logged for debugging purposes.[/dim]",
            title="[red]Error Report[/red]",
            expand=False,
        )
    )

    if suggest_report:
        console.print(
            "[yellow]📧 To help improve SampleMind, consider reporting this issue:[/yellow]"
        )
        console.print("[dim]   https://github.com/samplemind/issues[/dim]")
        console.print(f"[dim]   Include error code: {error_code}[/dim]")


def safe_execute(
    func: Callable,
    *args,
    default: Any = None,
    log_errors: bool = True,
    **kwargs,
) -> Any:
    """
    Safely execute function with error handling.

    Args:
        func: Function to execute
        *args: Positional arguments
        default: Default return value on error
        log_errors: Whether to log errors
        **kwargs: Keyword arguments

    Returns:
        Function result or default value

    Example:
        >>> result = safe_execute(process_file, path, default={})
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.exception(f"Error executing {func.__name__}")
        return default
