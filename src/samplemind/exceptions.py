"""
SampleMind AI - Custom Exception Hierarchy

Provides structured error handling with user-friendly messages and actionable suggestions.

Exception Hierarchy:
  SampleMindError (base)
    ├── AudioFileError
    │   ├── FileNotFoundError
    │   ├── UnsupportedFormatError
    │   ├── CorruptedAudioError
    │   └── AudioProcessingError
    ├── AIServiceError
    │   ├── APIKeyMissingError
    │   ├── RateLimitError
    │   ├── NetworkError
    │   ├── AuthenticationError
    │   └── APIError
    ├── DatabaseError
    ├── CacheError
    ├── ConfigurationError
    ├── ValidationError
    └── ResourceError
        ├── DiskFullError
        ├── OutOfMemoryError
        └── CacheLimitError
"""

from typing import Optional, Dict, Any
from pathlib import Path


class SampleMindError(Exception):
    """
    Base exception for all SampleMind errors.

    All SampleMind exceptions include:
    - message: Technical error message for logging
    - user_message: User-friendly message for CLI display
    - suggestion: Actionable suggestion to fix the issue
    - error_code: Error code for programmatic handling
    - context: Additional context for debugging
    """

    def __init__(
        self,
        message: str,
        user_message: Optional[str] = None,
        suggestion: Optional[str] = None,
        error_code: Optional[str] = None,
        **context
    ):
        super().__init__(message)
        self.message = message
        self.user_message = user_message or message
        self.suggestion = suggestion
        self.error_code = error_code or self.__class__.__name__
        self.context = context

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON output."""
        return {
            "error_code": self.error_code,
            "message": self.user_message,
            "suggestion": self.suggestion,
            "context": self.context,
        }

    def __str__(self) -> str:
        """Return user-friendly error message."""
        return self.user_message


# ============================================================================
# Audio File Errors
# ============================================================================


class AudioFileError(SampleMindError):
    """Base exception for audio file-related errors."""
    pass


class FileNotFoundError(AudioFileError):
    """Audio file not found."""

    def __init__(self, file_path: Path) -> None:
        super().__init__(
            message=f"Audio file not found: {file_path}",
            user_message=f"Could not find audio file: {file_path.name}",
            suggestion="Check that the file path is correct and the file exists.",
            error_code="FILE_NOT_FOUND",
            file_path=str(file_path),
        )


class UnsupportedFormatError(AudioFileError):
    """Audio format not supported."""

    def __init__(self, file_path: Path, format: str) -> None:
        super().__init__(
            message=f"Unsupported audio format: {format}",
            user_message=f"File format '.{format}' is not supported",
            suggestion="Supported formats: .wav, .mp3, .flac, .ogg, .m4a, .aiff",
            error_code="UNSUPPORTED_FORMAT",
            file_path=str(file_path),
            format=format,
        )


class CorruptedAudioError(AudioFileError):
    """Audio file is corrupted."""

    def __init__(self, file_path: Path, reason: Optional[str] = None) -> None:
        super().__init__(
            message=f"Corrupted audio file: {file_path}" + (f" ({reason})" if reason else ""),
            user_message=f"Audio file appears to be corrupted: {file_path.name}",
            suggestion="Try re-downloading or re-exporting the file. If the issue persists, the file may be permanently damaged.",
            error_code="CORRUPTED_AUDIO",
            file_path=str(file_path),
            reason=reason,
        )


class EmptyAudioFileError(AudioFileError):
    """Audio file is empty."""

    def __init__(self, file_path: Path) -> None:
        super().__init__(
            message=f"Empty audio file: {file_path}",
            user_message=f"Audio file is empty: {file_path.name}",
            suggestion="Check that the file was properly exported and contains audio data.",
            error_code="EMPTY_AUDIO_FILE",
            file_path=str(file_path),
        )


class AudioProcessingError(AudioFileError):
    """Error during audio processing."""

    def __init__(self, file_path: Path, operation: str, reason: str) -> None:
        super().__init__(
            message=f"Audio processing error in {operation}: {reason}",
            user_message=f"Could not process audio file during {operation}",
            suggestion="Try analyzing a different file or check the file integrity.",
            error_code="AUDIO_PROCESSING_ERROR",
            file_path=str(file_path),
            operation=operation,
            reason=reason,
        )


# ============================================================================
# AI Service Errors
# ============================================================================


class AIServiceError(SampleMindError):
    """Base exception for AI service-related errors."""
    pass


class APIKeyMissingError(AIServiceError):
    """API key not configured."""

    def __init__(self, provider: str) -> None:
        super().__init__(
            message=f"API key missing for {provider}",
            user_message=f"API key not configured for {provider}",
            suggestion=f"Run: samplemind ai:key --provider {provider} --key YOUR_KEY",
            error_code="API_KEY_MISSING",
            provider=provider,
        )


class RateLimitError(AIServiceError):
    """API rate limit exceeded."""

    def __init__(self, provider: str, retry_after: Optional[int] = None) -> None:
        super().__init__(
            message=f"Rate limit exceeded for {provider}",
            user_message=f"Too many requests to {provider} API",
            suggestion=f"Please wait {retry_after or 60} seconds and try again.",
            error_code="RATE_LIMIT_EXCEEDED",
            provider=provider,
            retry_after=retry_after,
        )


class NetworkError(AIServiceError):
    """Network connectivity error."""

    def __init__(self, provider: str, reason: Optional[str] = None) -> None:
        super().__init__(
            message=f"Network error connecting to {provider}: {reason or 'Connection failed'}",
            user_message="Could not connect to AI service",
            suggestion="Check your internet connection and try again. The application can continue offline with local AI models.",
            error_code="NETWORK_ERROR",
            provider=provider,
            reason=reason,
        )


class AuthenticationError(AIServiceError):
    """API authentication failed."""

    def __init__(self, provider: str) -> None:
        super().__init__(
            message=f"Authentication failed for {provider}",
            user_message=f"Invalid credentials for {provider}",
            suggestion=f"Check that your API key is correct. Run: samplemind ai:key --provider {provider}",
            error_code="AUTHENTICATION_ERROR",
            provider=provider,
        )


class APIError(AIServiceError):
    """General API error."""

    def __init__(self, provider: str, status_code: int, reason: str) -> None:
        super().__init__(
            message=f"API error from {provider}: {status_code} {reason}",
            user_message=f"Error from {provider} API (HTTP {status_code})",
            suggestion="The service may be temporarily unavailable. Try again in a moment.",
            error_code=f"API_ERROR_{status_code}",
            provider=provider,
            status_code=status_code,
            reason=reason,
        )


# ============================================================================
# Database Errors
# ============================================================================


class DatabaseError(SampleMindError):
    """Base exception for database-related errors."""

    def __init__(self, message: str, operation: str) -> None:
        super().__init__(
            message=message,
            user_message="Database operation failed",
            suggestion="Check the database connection and try again.",
            error_code="DATABASE_ERROR",
            operation=operation,
        )


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to database."""

    def __init__(self) -> None:
        super().__init__(
            message="Failed to connect to MongoDB",
            operation="connect",
        )
        self.user_message = "Could not connect to the database"
        self.suggestion = "Ensure MongoDB is running and accessible."


# ============================================================================
# Cache Errors
# ============================================================================


class CacheError(SampleMindError):
    """Base exception for cache-related errors."""

    def __init__(self, message: str, operation: str) -> None:
        super().__init__(
            message=message,
            user_message="Cache operation failed",
            suggestion="Try clearing the cache: samplemind cache:clear",
            error_code="CACHE_ERROR",
            operation=operation,
        )


class CacheLimitError(CacheError):
    """Cache limit exceeded."""

    def __init__(self, current_size: int, limit: int) -> None:
        super().__init__(
            message=f"Cache limit exceeded: {current_size}MB / {limit}MB",
            operation="store",
        )
        self.user_message = "Cache is full"
        self.suggestion = "Cache will be automatically cleared. Increase cache size if needed: samplemind config:set cache_size_mb 500"
        self.context = {"current_size": current_size, "limit": limit}


# ============================================================================
# Configuration Errors
# ============================================================================


class ConfigurationError(SampleMindError):
    """Configuration-related error."""

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            user_message="Configuration error",
            suggestion="Check your configuration settings: samplemind config:show",
            error_code="CONFIGURATION_ERROR",
            config_key=config_key,
        )


class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration value."""

    def __init__(self, key: str, value: Any, reason: str) -> None:
        super().__init__(
            message=f"Invalid configuration value for {key}: {value} ({reason})",
            config_key=key,
        )
        self.user_message = f"Invalid value for setting '{key}': {reason}"
        self.suggestion = f"Update the configuration: samplemind config:set {key} <valid_value>"


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing."""

    def __init__(self, key: str) -> None:
        super().__init__(
            message=f"Missing required configuration: {key}",
            config_key=key,
        )
        self.user_message = f"Required configuration is missing: {key}"
        self.suggestion = f"Set the configuration: samplemind config:set {key} <value>"


# ============================================================================
# Validation Errors
# ============================================================================


class ValidationError(SampleMindError):
    """Input validation error."""

    def __init__(self, message: str, field: Optional[str] = None) -> None:
        super().__init__(
            message=message,
            user_message="Invalid input",
            suggestion="Check your input and try again.",
            error_code="VALIDATION_ERROR",
            field=field,
        )


class InvalidFormatError(ValidationError):
    """Invalid format specification."""

    def __init__(self, format: str, supported_formats: list) -> None:
        super().__init__(
            message=f"Invalid format: {format}",
            field="format",
        )
        self.user_message = f"Invalid format: {format}"
        self.suggestion = f"Use one of: {', '.join(supported_formats)}"


class InvalidRangeError(ValidationError):
    """Invalid range specification."""

    def __init__(self, field: str, min_val: Any, max_val: Any) -> None:
        super().__init__(
            message=f"Invalid range for {field}: min ({min_val}) > max ({max_val})",
            field=field,
        )
        self.user_message = f"Invalid {field} range: minimum must be less than maximum"
        self.suggestion = f"Ensure: min_{field} < max_{field}"


# ============================================================================
# Resource Errors
# ============================================================================


class ResourceError(SampleMindError):
    """Base exception for resource-related errors."""
    pass


class DiskFullError(ResourceError):
    """Disk space is full."""

    def __init__(self, available_gb: float, required_gb: float) -> None:
        super().__init__(
            message=f"Disk full: {available_gb}GB available, {required_gb}GB required",
            user_message="Not enough disk space available",
            suggestion=f"Free up at least {required_gb}GB of disk space and try again.",
            error_code="DISK_FULL",
            available_gb=available_gb,
            required_gb=required_gb,
        )


class OutOfMemoryError(ResourceError):
    """Out of memory."""

    def __init__(self, operation: str) -> None:
        super().__init__(
            message=f"Out of memory during {operation}",
            user_message="Not enough memory available",
            suggestion="Close other applications or reduce the file size and try again.",
            error_code="OUT_OF_MEMORY",
            operation=operation,
        )


class ProcessTimeoutError(ResourceError):
    """Process timed out."""

    def __init__(self, operation: str, timeout_seconds: int) -> None:
        super().__init__(
            message=f"Operation timed out after {timeout_seconds}s: {operation}",
            user_message=f"Operation took too long and was cancelled",
            suggestion=f"Try again or use a shorter timeout: samplemind config:set timeout {timeout_seconds * 2}",
            error_code="PROCESS_TIMEOUT",
            operation=operation,
            timeout_seconds=timeout_seconds,
        )


# ============================================================================
# User Interruption Errors
# ============================================================================


class UserInterruptedError(SampleMindError):
    """User interrupted the operation (Ctrl+C)."""

    def __init__(self, operation: str) -> None:
        super().__init__(
            message=f"Operation interrupted by user: {operation}",
            user_message="Operation cancelled",
            suggestion="Run the command again to retry.",
            error_code="USER_INTERRUPTED",
            operation=operation,
        )


# ============================================================================
# Helper Functions
# ============================================================================


def is_samplemind_error(exception: Exception) -> bool:
    """Check if exception is a SampleMind error."""
    return isinstance(exception, SampleMindError)


def get_error_code(exception: Exception) -> str:
    """Get error code from exception."""
    if is_samplemind_error(exception):
        return exception.error_code  # type: ignore
    return "UNKNOWN_ERROR"


def get_user_message(exception: Exception) -> str:
    """Get user-friendly message from exception."""
    if is_samplemind_error(exception):
        return exception.user_message  # type: ignore
    return str(exception)
