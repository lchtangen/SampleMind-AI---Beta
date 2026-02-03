"""Audio-related schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AudioFileMetadata(BaseModel):
    """Audio file metadata"""
    file_id: str
    filename: str
    file_size: int
    duration: float
    sample_rate: int
    channels: int
    format: str
    uploaded_at: datetime


class AudioUploadResponse(BaseModel):
    """Response after audio upload"""
    file_id: str
    filename: str
    file_size: int
    message: str = "File uploaded successfully"


class AudioAnalysisRequest(BaseModel):
    """Request for audio analysis"""
    analysis_level: str = Field("standard", description="Analysis level: basic, standard, detailed, professional")
    include_ai: bool = Field(True, description="Include AI analysis")
    ai_provider: Optional[str] = Field(None, description="Preferred AI provider: google_ai or openai")


class AudioAnalysisResponse(BaseModel):
    """Audio analysis results"""
    analysis_id: str
    file_id: str

    # Basic audio features
    duration: float
    tempo: float
    key: str
    mode: str
    time_signature: List[int]

    # Spectral features
    spectral_features: Optional[Dict[str, Any]] = None

    # AI analysis
    ai_analysis: Optional[Dict[str, Any]] = None

    # Metadata
    analysis_level: str
    processing_time: float
    analyzed_at: datetime

class AudioProcessRequest(BaseModel):
    """Request for audio processing"""
    operation: str
    params: Dict[str, Any] = {}

class AudioFeatureExtractionResponse(BaseModel):
    """Response for feature extraction"""
    features: Dict[str, Any]

class AudioProcessResponse(BaseModel):
    """Response for audio processing"""
    success: bool
    result: Dict[str, Any]
