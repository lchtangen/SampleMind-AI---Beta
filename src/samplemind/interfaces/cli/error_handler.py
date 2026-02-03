"""
Enhanced Error Handling System for SampleMind AI CLI

Provides:
- Detailed error categorization and context
- Interactive error recovery options
- Actionable error messages with suggestions
- Error diagnostics and troubleshooting
- Graceful degradation patterns
"""

import logging
import traceback
from typing import Optional, Callable, Any, Dict, List, TypeVar
from enum import Enum
from pathlib import Path
from functools import wraps

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import typer

logger = logging.getLogger(__name__)
console = Console()

T = TypeVar('T')


# ============================================================================
# ERROR SEVERITY LEVELS
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity classification"""
    INFO = "ℹ️"          # Informational, non-critical
    WARNING = "⚠️"       # Warning, operation completed with issues
    ERROR = "❌"         # Error, operation failed
    CRITICAL = "🔴"      # Critical, system cannot continue


# ============================================================================
# ERROR CATEGORIES
# ============================================================================

class ErrorCategory(Enum):
    """Error categorization for better UX"""

    # Audio file errors
    FILE_NOT_FOUND = "File not found"
    INVALID_FORMAT = "Invalid audio format"
    CORRUPTED_FILE = "Corrupted or unreadable file"
    FILE_TOO_LARGE = "File exceeds size limit"
    PERMISSION_DENIED = "Permission denied"

    # Analysis errors
    ANALYSIS_FAILED = "Analysis failed"
    ENGINE_UNAVAILABLE = "Audio engine unavailable"
    INSUFFICIENT_MEMORY = "Insufficient memory"
    TIMEOUT = "Operation timeout"

    # AI/Model errors
    MODEL_NOT_LOADED = "Model not loaded"
    AI_SERVICE_UNAVAILABLE = "AI service unavailable"
    API_ERROR = "API error"
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded"

    # System errors
    DISK_SPACE_LOW = "Insufficient disk space"
    DATABASE_ERROR = "Database error"
    NETWORK_ERROR = "Network error"
    CONFIG_ERROR = "Configuration error"

    # User input errors
    INVALID_INPUT = "Invalid input"
    MISSING_ARGUMENT = "Missing required argument"
    INVALID_OPTION = "Invalid option"
    AMBIGUOUS_INPUT = "Ambiguous input"

    # Unknown errors
    UNKNOWN = "Unknown error"


# ============================================================================
# CUSTOM EXCEPTION CLASSES
# ============================================================================

class SampleMindError(Exception):
    """Base exception for all SampleMind errors"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        recovery_options: Optional[Dict[str, Callable]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context
        self.suggestions = suggestions or []
        self.recovery_options = recovery_options or {}
        super().__init__(message)


class AudioFileError(SampleMindError):
    """Error loading or processing audio file"""

    def __init__(self, message: str, file_path: Optional[Path] = None, **kwargs) -> None:
        kwargs['category'] = ErrorCategory.FILE_NOT_FOUND
        kwargs['severity'] = ErrorSeverity.ERROR
        if file_path:
            kwargs['context'] = f"File: {file_path}"
        super().__init__(message, **kwargs)


class AnalysisError(SampleMindError):
    """Error during audio analysis"""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs['category'] = kwargs.get('category', ErrorCategory.ANALYSIS_FAILED)
        kwargs['severity'] = kwargs.get('severity', ErrorSeverity.ERROR)
        super().__init__(message, **kwargs)


class AIServiceError(SampleMindError):
    """Error with AI services"""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs['category'] = kwargs.get('category', ErrorCategory.AI_SERVICE_UNAVAILABLE)
        kwargs['severity'] = kwargs.get('severity', ErrorSeverity.ERROR)
        super().__init__(message, **kwargs)


class ValidationError(SampleMindError):
    """Error validating user input"""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs['category'] = kwargs.get('category', ErrorCategory.INVALID_INPUT)
        kwargs['severity'] = kwargs.get('severity', ErrorSeverity.ERROR)
        super().__init__(message, **kwargs)


class ResourceError(SampleMindError):
    """Error with system resources"""

    def __init__(self, message: str, **kwargs) -> None:
        kwargs['category'] = kwargs.get('category', ErrorCategory.UNKNOWN)
        kwargs['severity'] = kwargs.get('severity', ErrorSeverity.ERROR)
        super().__init__(message, **kwargs)


# ============================================================================
# ERROR RECOVERY STRATEGIES
# ============================================================================

class ErrorRecoveryStrategy:
    """Base class for error recovery strategies"""

    def __init__(self, error: SampleMindError) -> None:
        self.error = error

    def get_suggestions(self) -> List[str]:
        """Get actionable suggestions for this error"""
        return self.error.suggestions

    def get_recovery_options(self) -> Dict[str, Callable]:
        """Get recovery options for this error"""
        return self.error.recovery_options

    def auto_recover(self) -> bool:
        """Attempt automatic recovery if possible"""
        return False


class FileNotFoundRecovery(ErrorRecoveryStrategy):
    """Recovery for file not found errors"""

    def get_suggestions(self) -> List[str]:
        """Get recovery suggestions for file not found errors.
        
        Returns:
            List of actionable suggestions for the user
        """
        return [
            "Check the file path is correct",
            "Verify the file exists and is accessible",
            "Use --interactive flag to browse files",
            "Check file permissions (you may need sudo)",
        ]

    def get_recovery_options(self) -> Dict[str, Callable]:
        """Get interactive recovery options for file not found errors.
        
        Returns:
            Dictionary mapping option names to recovery functions
        """
        from samplemind.utils.file_picker import select_audio_file

        def pick_file():
            """Launch file picker to select audio file.
            
            Returns:
                Selected file path or None if cancelled
            """
            selected = select_audio_file(title="Select Audio File")
            if selected:
                console.print(f"[green]✓[/green] File selected: {selected}")
                return str(selected)
            return None

        return {
            "Browse for file": pick_file,
            "Cancel operation": lambda: None,
        }


class InsufficientMemoryRecovery(ErrorRecoveryStrategy):
    """Recovery for memory errors"""

    def get_suggestions(self) -> List[str]:
        """Get recovery suggestions for memory errors.
        
        Returns:
            List of actionable suggestions for the user
        """
        return [
            "Close other applications to free up memory",
            "Try analysis with lower detail level (--level basic)",
            "Process files in smaller batches",
            "Increase system virtual memory/swap",
        ]

    def auto_recover(self) -> bool:
        """Try to recover by clearing caches"""
        try:
            import gc
            gc.collect()
            console.print("[yellow]⚠[/yellow] Cleared memory caches, retrying...")
            return True
        except Exception:
            return False


class APIErrorRecovery(ErrorRecoveryStrategy):
    """Recovery for API/network errors"""

    def get_suggestions(self) -> List[str]:
        """Get recovery suggestions for API/network errors.
        
        Returns:
            List of actionable suggestions for the user
        """
        return [
            "Check your internet connection",
            "Verify API keys are configured correctly",
            "Check API service status",
            "Try offline mode (--offline) to use local models",
            "Wait a few seconds and retry",
        ]

    def get_recovery_options(self) -> Dict[str, Callable]:
        """Get interactive recovery options for API errors.
        
        Returns:
            Dictionary mapping option names to recovery functions
        """
        return {
            "Retry operation": lambda: True,
            "Use offline mode": lambda: False,
            "Cancel": lambda: None,
        }


# ============================================================================
# ERROR RECOVERY FACTORY
# ============================================================================

def get_recovery_strategy(error: SampleMindError) -> ErrorRecoveryStrategy:
    """Get appropriate recovery strategy for error"""

    if error.category == ErrorCategory.FILE_NOT_FOUND:
        return FileNotFoundRecovery(error)
    elif error.category == ErrorCategory.INSUFFICIENT_MEMORY:
        return InsufficientMemoryRecovery(error)
    elif error.category in [
        ErrorCategory.API_ERROR,
        ErrorCategory.NETWORK_ERROR,
        ErrorCategory.RATE_LIMIT_EXCEEDED,
    ]:
        return APIErrorRecovery(error)

    return ErrorRecoveryStrategy(error)


# ============================================================================
# ERROR DISPLAY AND HANDLING
# ============================================================================

def display_error(error: SampleMindError, verbose: bool = False) -> None:
    """Display error with context and suggestions"""

    # Create error panel
    error_msg = f"{error.severity.value} {error.category.value}\n\n{error.message}"

    if error.context:
        error_msg += f"\n\n[dim]{error.context}[/dim]"

    console.print(Panel(
        error_msg,
        title="[bold red]Error[/bold red]",
        border_style="red",
        expand=False
    ))

    # Display suggestions
    if error.suggestions:
        suggestions_text = "\n".join(
            f"  • {suggestion}"
            for suggestion in error.suggestions
        )
        console.print(Panel(
            suggestions_text,
            title="[bold yellow]Suggestions[/bold yellow]",
            border_style="yellow",
            expand=False
        ))

    # Display traceback in verbose mode
    if verbose and hasattr(error, '__traceback__'):
        console.print("[dim]Traceback:[/dim]")
        console.print(Syntax(
            traceback.format_exc(),
            "python",
            theme="monokai",
            line_numbers=False
        ))


def handle_error_interactive(error: SampleMindError) -> Optional[Any]:
    """Handle error interactively with recovery options"""

    display_error(error)

    # Get recovery strategy
    recovery = get_recovery_strategy(error)

    # Try auto-recovery if available
    if recovery.auto_recover():
        return True

    # Get and display recovery options
    options = recovery.get_recovery_options()

    if not options:
        return None

    if len(options) == 1:
        # Only one option, don't ask
        func = list(options.values())[0]
        return func()

    # Present options to user
    console.print("\n[bold]Recovery Options:[/bold]")
    for i, option_name in enumerate(options.keys(), 1):
        console.print(f"  [{i}] {option_name}")
    console.print(f"  [0] Cancel")

    try:
        choice = typer.prompt("Select option", type=int)
        if choice == 0:
            return None

        option_names = list(options.keys())
        if 1 <= choice <= len(option_names):
            func = options[option_names[choice - 1]]
            return func()
    except (ValueError, KeyError):
        console.print("[red]Invalid selection[/red]")

    return None


# ============================================================================
# ERROR DECORATORS
# ============================================================================

def with_error_recovery(
    interactive: bool = True,
    verbose: bool = False,
    exit_on_error: bool = True
):
    """Decorator to add error recovery to commands

    Args:
        interactive: Show interactive recovery options
        verbose: Show detailed error information
        exit_on_error: Exit program on error (default) or continue
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator function that wraps the target function with error handling.
        
        Args:
            func: Function to wrap with error handling
            
        Returns:
            Wrapped function with error handling
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            """Wrapper function that executes the target function with error handling.
            
            Args:
                *args: Positional arguments for the wrapped function
                **kwargs: Keyword arguments for the wrapped function
                
            Returns:
                Result from the wrapped function
                
            Raises:
                SystemExit: If error occurs and exit_on_error is True
            """
            try:
                return func(*args, **kwargs)

            except SampleMindError as e:
                logger.error(f"SampleMind error: {e.message}", exc_info=True)

                if interactive:
                    result = handle_error_interactive(e)
                    if result is None and exit_on_error:
                        raise typer.Exit(code=1)
                    return result
                else:
                    display_error(e, verbose=verbose)
                    if exit_on_error:
                        raise typer.Exit(code=1)

            except KeyboardInterrupt:
                console.print("\n[yellow]⏸ Operation cancelled by user[/yellow]")
                raise typer.Exit(code=0)

            except Exception as e:
                logger.exception("Unexpected error")

                # Try to convert to SampleMindError
                error = SampleMindError(
                    message=str(e),
                    category=ErrorCategory.UNKNOWN,
                    severity=ErrorSeverity.ERROR
                )

                if interactive:
                    handle_error_interactive(error)
                else:
                    display_error(error, verbose=verbose)

                if exit_on_error:
                    raise typer.Exit(code=1)

        return wrapper
    return decorator


# ============================================================================
# CONTEXT MANAGERS FOR ERROR HANDLING
# ============================================================================

class ErrorContext:
    """Context manager for graceful error handling"""

    def __init__(
        self,
        operation: str,
        recovery_options: Optional[Dict[str, Callable]] = None,
        fallback_value: Any = None
    ):
        self.operation = operation
        self.recovery_options = recovery_options or {}
        self.fallback_value = fallback_value
        self.error: Optional[Exception] = None

    def __enter__(self) -> None:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            return False

        self.error = exc_val

        # Log error
        logger.error(f"Error in {self.operation}: {exc_val}", exc_info=True)

        # Display error
        if isinstance(exc_val, SampleMindError):
            display_error(exc_val)
        else:
            error = SampleMindError(
                message=str(exc_val),
                context=f"Operation: {self.operation}",
                category=ErrorCategory.UNKNOWN
            )
            display_error(error)

        # Handle recovery
        if self.recovery_options:
            result = handle_error_interactive(exc_val)
            return True  # Suppress exception

        return False  # Re-raise exception


# ============================================================================
# ERROR HELPERS
# ============================================================================

def ensure_file_exists(file_path: Path) -> Path:
    """Ensure file exists, raise error if not"""
    if not file_path.exists():
        raise AudioFileError(
            message=f"File not found: {file_path.name}",
            file_path=file_path,
            suggestions=[
                f"Check path: {file_path}",
                "Use --interactive to browse files",
                "Verify file has read permissions"
            ]
        )
    return file_path


def ensure_audio_format(file_path: Path) -> Path:
    """Ensure file is valid audio format"""
    valid_formats = {'.wav', '.mp3', '.flac', '.aiff', '.ogg', '.m4a'}

    if file_path.suffix.lower() not in valid_formats:
        raise AudioFileError(
            message=f"Invalid audio format: {file_path.suffix}",
            file_path=file_path,
            category=ErrorCategory.INVALID_FORMAT,
            suggestions=[
                f"Supported formats: {', '.join(valid_formats)}",
                "Convert file using: ffmpeg -i input.{old} output.wav",
            ]
        )
    return file_path


def ensure_readable(file_path: Path) -> Path:
    """Ensure file is readable"""
    try:
        if not file_path.is_file():
            raise AudioFileError(
                message=f"Not a file: {file_path}",
                file_path=file_path
            )

        if not file_path.stat().st_size > 0:
            raise AudioFileError(
                message=f"File is empty: {file_path}",
                file_path=file_path
            )

        # Try opening
        with open(file_path, 'rb') as f:
            f.read(1024)

        return file_path

    except PermissionError:
        raise AudioFileError(
            message=f"Permission denied: {file_path}",
            file_path=file_path,
            category=ErrorCategory.PERMISSION_DENIED,
            suggestions=[
                "Check file permissions (chmod +r file.wav)",
                "Run with appropriate privileges if needed",
            ]
        )
    except Exception as e:
        raise AudioFileError(
            message=f"Cannot read file: {e}",
            file_path=file_path,
            category=ErrorCategory.CORRUPTED_FILE,
            suggestions=[
                "File may be corrupted",
                "Try opening with audio player to verify",
                "Try converting: ffmpeg -i input.mp3 -c copy output.mp3"
            ]
        )


# ============================================================================
# ERROR DIAGNOSTICS
# ============================================================================

def diagnose_system() -> Dict[str, Any]:
    """Diagnose system capabilities"""
    import sys
    import platform
    import shutil

    return {
        "platform": platform.system(),
        "python_version": sys.version,
        "disk_space_free_gb": shutil.disk_usage("/").free / (1024**3),
        "encoders_available": {
            "ffmpeg": bool(shutil.which("ffmpeg")),
            "sox": bool(shutil.which("sox")),
        },
    }


def display_diagnostics() -> None:
    """Display system diagnostics"""
    diag = diagnose_system()

    table = Table(title="System Diagnostics")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")

    for key, value in diag.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                status = "✓" if sub_value else "✗"
                table.add_row(f"  {sub_key}", status)
        else:
            table.add_row(key, str(value))

    console.print(table)


# ============================================================================
# GRACEFUL DEGRADATION
# ============================================================================

class GracefulDegradation:
    """Handle missing features gracefully"""

    @staticmethod
    def with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        error_message: str = ""
    ) -> Any:
        """Try primary function, fall back to secondary"""
        try:
            return primary_func()
        except Exception as e:
            logger.warning(f"Primary function failed: {e}, using fallback")
            if error_message:
                console.print(f"[yellow]⚠[/yellow] {error_message}")
                console.print("[dim]Using fallback...[/dim]")
            return fallback_func()

    @staticmethod
    def optional_feature(
        feature_func: Callable,
        feature_name: str
    ) -> Optional[Any]:
        """Try optional feature, continue if unavailable"""
        try:
            return feature_func()
        except Exception as e:
            logger.warning(f"Optional feature '{feature_name}' unavailable: {e}")
            console.print(f"[yellow]⚠[/yellow] Feature unavailable: {feature_name}")
            return None


# ============================================================================
# SETUP ERROR LOGGING
# ============================================================================

def setup_error_logging(log_file: Optional[Path] = None) -> None:
    """Setup comprehensive error logging"""

    if log_file:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
