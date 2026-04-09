"""Custom exception hierarchy for SampleMind AI.

All domain-specific exceptions inherit from SampleMindError for unified
error handling across CLI, TUI, and API interfaces.

Usage:
    >>> from samplemind.core.exceptions import AudioAnalysisError
    >>> try:
    ...     analyze_audio(file)
    ... except AudioAnalysisError as e:
    ...     logger.error(f"Analysis failed: {e}")
"""

__all__ = [
    "SampleMindError",
    "AudioAnalysisError",
    "SearchIndexError",
    "AgentPipelineError",
    "RateLimitError",
    "ConfigurationError",
    "ValidationError",
]


class SampleMindError(Exception):
    """Base exception for all SampleMind AI errors.

    All domain-specific exceptions inherit from this for unified error
    handling across the entire system.
    """
    pass


class AudioAnalysisError(SampleMindError):
    """Raised when audio analysis fails.

    Examples:
        - BPM detection failure
        - Key detection failure
        - Insufficient audio data for analysis
    """
    pass


class SearchIndexError(SampleMindError):
    """Raised when FAISS index operations fail.

    Examples:
        - Index build failure
        - Search query parsing error
        - Embedding generation failure
    """
    pass


class AgentPipelineError(SampleMindError):
    """Raised when LangGraph agent pipeline fails.

    Examples:
        - Agent graph execution error
        - Task state corruption
        - LLM API call failure
    """
    pass


class RateLimitError(SampleMindError):
    """Raised when rate limit is exceeded.

    HTTP: 429 Too Many Requests
    """
    pass


class ConfigurationError(SampleMindError):
    """Raised when configuration is invalid or missing.

    Examples:
        - Missing required environment variables
        - Invalid API key format
        - Invalid model name
    """
    pass


class ValidationError(SampleMindError):
    """Raised when input validation fails.

    Examples:
        - Invalid file format
        - Unsupported audio codec
        - Invalid query parameters
    """
    pass
