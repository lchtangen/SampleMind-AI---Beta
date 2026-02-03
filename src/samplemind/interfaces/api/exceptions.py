"""
Custom exceptions for SampleMind AI Backend
"""

from typing import Optional, Dict, Any


class SampleMindException(Exception):
    """Base exception for SampleMind API"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "api_error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


class FileValidationError(SampleMindException):
    """File validation failed"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_type="file_validation_error",
            details=details
        )


class AudioProcessingError(SampleMindException):
    """Audio processing failed"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_type="audio_processing_error",
            details=details
        )


class AIProviderError(SampleMindException):
    """AI provider request failed"""
    
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None) -> None:
        details = details or {}
        details["provider"] = provider
        super().__init__(
            message=message,
            status_code=503,
            error_type="ai_provider_error",
            details=details
        )


class ResourceNotFoundError(SampleMindException):
    """Requested resource not found"""
    
    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource_type} not found",
            status_code=404,
            error_type="resource_not_found",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class RateLimitError(SampleMindException):
    """Rate limit exceeded"""
    
    def __init__(self, retry_after: Optional[int] = None) -> None:
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            error_type="rate_limit_exceeded",
            details=details
        )


class StorageError(SampleMindException):
    """File storage operation failed"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            status_code=500,
            error_type="storage_error",
            details=details
        )
