"""
Pydantic schemas for audio endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AudioUploadResponse(BaseModel):
    """Response schema for audio upload"""
    id: int
    filename: str
    file_size: int
    format: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    uploaded_at: str
    status: str = "uploaded"
    
    class Config:
        from_attributes = True


class AudioAnalysisRequest(BaseModel):
    """Request schema for audio analysis"""
    audio_id: int = Field(..., description="ID of uploaded audio file")
    analysis_type: str = Field(
        default="full",
        description="Analysis type: full, quick, or custom"
    )
    extract_features: bool = Field(
        default=True,
        description="Extract audio features (tempo, key, etc.)"
    )
    ai_analysis: bool = Field(
        default=True,
        description="Perform AI-powered analysis"
    )


class AudioFeatures(BaseModel):
    """Audio feature extraction results"""
    tempo: Optional[float] = Field(None, description="BPM (beats per minute)")
    key: Optional[str] = Field(None, description="Musical key")
    time_signature: Optional[str] = Field(None, description="Time signature")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    loudness: Optional[float] = Field(None, description="Loudness in dB")
    energy: Optional[float] = Field(None, description="Energy level (0-1)")
    danceability: Optional[float] = Field(None, description="Danceability score (0-1)")
    valence: Optional[float] = Field(None, description="Musical positiveness (0-1)")
    spectral_centroid: Optional[float] = Field(None, description="Spectral centroid")
    zero_crossing_rate: Optional[float] = Field(None, description="Zero crossing rate")


class AIAnalysisResult(BaseModel):
    """AI-powered analysis results"""
    genre: Optional[List[str]] = Field(None, description="Detected genres")
    mood: Optional[List[str]] = Field(None, description="Detected moods")
    instruments: Optional[List[str]] = Field(None, description="Detected instruments")
    tags: Optional[List[str]] = Field(None, description="Descriptive tags")
    similarity_score: Optional[float] = Field(None, description="Quality score (0-1)")
    description: Optional[str] = Field(None, description="AI-generated description")


class AudioAnalysisResponse(BaseModel):
    """Complete analysis response"""
    audio_id: int
    status: str = "completed"
    features: Optional[AudioFeatures] = None
    ai_analysis: Optional[AIAnalysisResult] = None
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    analyzed_at: str


class AudioListItem(BaseModel):
    """Audio item in list"""
    id: int
    filename: str
    duration: Optional[float] = None
    format: str
    uploaded_at: str
    has_analysis: bool = False


class AudioListResponse(BaseModel):
    """List of audio files"""
    items: List[AudioListItem]
    total: int
    page: int = 1
    page_size: int = 20
    pages: int


class AudioDetailResponse(BaseModel):
    """Detailed audio information"""
    id: int
    filename: str
    file_size: int
    format: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    uploaded_at: str
    status: str
    features: Optional[AudioFeatures] = None
    ai_analysis: Optional[AIAnalysisResult] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AudioSearchRequest(BaseModel):
    """Search/filter request"""
    query: Optional[str] = Field(None, description="Text search query")
    min_tempo: Optional[float] = Field(None, description="Minimum BPM")
    max_tempo: Optional[float] = Field(None, description="Maximum BPM")
    key: Optional[str] = Field(None, description="Musical key filter")
    genre: Optional[List[str]] = Field(None, description="Genre filters")
    mood: Optional[List[str]] = Field(None, description="Mood filters")
    sort_by: str = Field(default="uploaded_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
