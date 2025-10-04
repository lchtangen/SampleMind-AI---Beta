"""
Pydantic schemas for request/response validation
"""

from .common import ErrorResponse, HealthCheckResponse, PaginationParams
from .audio import (
    AudioUploadResponse,
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    AudioFileMetadata
)
from .ai import AIProviderInfo, AIAnalysisRequest, AIAnalysisResponse
from .batch import BatchUploadRequest, BatchStatusResponse

__all__ = [
    "ErrorResponse",
    "HealthCheckResponse",
    "PaginationParams",
    "AudioUploadResponse",
    "AudioAnalysisRequest",
    "AudioAnalysisResponse",
    "AudioFileMetadata",
    "AIProviderInfo",
    "AIAnalysisRequest",
    "AIAnalysisResponse",
    "BatchUploadRequest",
    "BatchStatusResponse",
]
