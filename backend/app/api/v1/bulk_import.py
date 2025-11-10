"""Bulk import API endpoints"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token, verify_token_type
from app.models import AudioImportJob, ImportJobStatus
from app.schemas import (
    BulkImportInitRequest,
    BulkImportIngestRequest,
    ImportJobResponse,
)

router = APIRouter(prefix="/bulk-import", tags=["bulk-import"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract the user id from a JWT access token"""
    token = credentials.credentials

    if not verify_token_type(token, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    return int(user_id)


@router.post("/init", response_model=ImportJobResponse, status_code=status.HTTP_201_CREATED)
def init_bulk_import(
    request: BulkImportInitRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Any:
    """Register a new bulk import job"""
    job = AudioImportJob(
        user_id=user_id,
        total_files=request.total_files,
        source=request.source,
        manifest_path=request.manifest_path,
        status=ImportJobStatus.PENDING,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/ingest", response_model=ImportJobResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_manifest(
    payload: BulkImportIngestRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Any:
    """Accept a manifest containing files to import and mark the job as running"""
    job = db.query(AudioImportJob).filter(AudioImportJob.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")
    if job.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this job")

    if job.status in {ImportJobStatus.COMPLETED, ImportJobStatus.CANCELLED}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job is not accepting new entries")

    if job.status == ImportJobStatus.PENDING:
        job.status = ImportJobStatus.RUNNING
        job.started_at = datetime.utcnow()

    # Update job metrics
    if payload.entries:
        job.total_files = max(job.total_files, len(payload.entries))

    # Placeholder for actual processing – to be implemented in Step 3
    # Future work: enqueue entries into Celery task queue for fingerprinting & analysis

    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}/status", response_model=ImportJobResponse)
def get_import_status(
    job_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> Any:
    """Return the latest status of a bulk import job"""
    job = db.query(AudioImportJob).filter(AudioImportJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import job not found")
    if job.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this job")
    return job
