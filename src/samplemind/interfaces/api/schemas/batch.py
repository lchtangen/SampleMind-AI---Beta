"""Batch processing schemas"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BatchUploadRequest(BaseModel):
    """Batch upload configuration"""
    analysis_level: str = Field("standard", description="Analysis level for all files")
    include_ai: bool = Field(True, description="Include AI analysis")


class BatchFileStatus(BaseModel):
    """Status of a single file in batch"""
    file_id: str
    filename: str
    status: str = Field(description="Status: pending, processing, completed, failed")
    progress: float = Field(0.0, ge=0.0, le=100.0)
    analysis_id: Optional[str] = None
    error: Optional[str] = None


class BatchStatusResponse(BaseModel):
    """Batch processing status"""
    batch_id: str
    status: str = Field(description="Overall status: pending, processing, completed, failed")
    total_files: int
    completed: int
    failed: int
    progress: float = Field(0.0, ge=0.0, le=100.0)
    files: List[BatchFileStatus]
    created_at: datetime
    updated_at: datetime