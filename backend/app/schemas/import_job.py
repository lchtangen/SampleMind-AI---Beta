"""Schemas for audio import jobs"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class ImportJobStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ImportJobBase(BaseModel):
    id: int
    user_id: int
    status: ImportJobStatusEnum
    source: Optional[str] = None
    manifest_path: Optional[str] = None

    total_files: int
    processed_files: int
    duplicate_files: int
    failed_files: int

    error_log: Optional[Dict[str, Any]] = None

    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ImportJobResponse(ImportJobBase):
    pass


class BulkImportInitRequest(BaseModel):
    total_files: int = Field(..., ge=0)
    source: Optional[str] = None
    manifest_path: Optional[str] = None


class ImportManifestEntry(BaseModel):
    path: str
    checksum: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BulkImportIngestRequest(BaseModel):
    job_id: int
    entries: List[ImportManifestEntry]


class ImportJobUpdate(BaseModel):
    status: Optional[ImportJobStatusEnum] = None
    processed_files: Optional[int] = None
    duplicate_files: Optional[int] = None
    failed_files: Optional[int] = None
    error_log: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
