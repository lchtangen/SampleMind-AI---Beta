"""Batch processing endpoints"""

import uuid
from datetime import datetime
from typing import Dict, List
from fastapi import APIRouter, UploadFile, File
from samplemind.interfaces.api.schemas.batch import BatchUploadRequest, BatchStatusResponse, BatchFileStatus

router = APIRouter()

# In-memory batch storage (for MVP - will move to database)
batch_store: Dict[str, Dict] = {}


@router.post("/upload", response_model=BatchStatusResponse)
async def upload_batch(files: List[UploadFile] = File(...)):
    """Upload multiple audio files for batch processing"""
    batch_id = str(uuid.uuid4())
    
    file_statuses = []
    for file in files:
        file_id = str(uuid.uuid4())
        file_statuses.append(BatchFileStatus(
            file_id=file_id,
            filename=file.filename,
            status="pending",
            progress=0.0
        ))
    
    batch_data = {
        "batch_id": batch_id,
        "status": "pending",
        "files": file_statuses,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    batch_store[batch_id] = batch_data
    
    return BatchStatusResponse(
        batch_id=batch_id,
        status="pending",
        total_files=len(files),
        completed=0,
        failed=0,
        progress=0.0,
        files=file_statuses,
        created_at=batch_data["created_at"],
        updated_at=batch_data["updated_at"]
    )


@router.get("/status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str):
    """Get batch processing status"""
    batch_data = batch_store.get(batch_id)
    
    if not batch_data:
        from samplemind.interfaces.api.exceptions import ResourceNotFoundError
        raise ResourceNotFoundError("batch", batch_id)
    
    files = batch_data["files"]
    completed = sum(1 for f in files if f.status == "completed")
    failed = sum(1 for f in files if f.status == "failed")
    
    return BatchStatusResponse(
        batch_id=batch_id,
        status=batch_data["status"],
        total_files=len(files),
        completed=completed,
        failed=failed,
        progress=(completed + failed) / len(files) * 100 if files else 0,
        files=files,
        created_at=batch_data["created_at"],
        updated_at=batch_data["updated_at"]
    )
