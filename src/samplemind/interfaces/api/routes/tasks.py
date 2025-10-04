"""
Task Management Routes
Submit, query, and monitor background tasks via Celery
"""

import os
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from samplemind.interfaces.api.schemas.tasks import (
    TaskSubmitRequest,
    BatchTaskSubmitRequest,
    TaskSubmitResponse,
    TaskStatusResponse,
    TaskListResponse,
    WorkersStatusResponse,
    WorkerInfo,
    QueueStatsResponse,
    QueueStats,
)
from samplemind.core.auth import get_current_active_user

# Celery app imports
from samplemind.core.tasks import celery_app
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Tasks"]) 


@router.post("/analyze", response_model=TaskSubmitResponse)
async def submit_audio_analysis(
    request: TaskSubmitRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Submit a single audio file for background analysis
    """
    # Submit task to celery
    result = celery_app.send_task(
        "samplemind.core.tasks.audio_tasks.process_audio_analysis",
        kwargs={
            "file_id": request.file_id,
            "file_path": request.file_path,
            "user_id": request.user_id or current_user.user_id,
            "analysis_options": request.analysis_options or {},
        },
        queue="audio_processing",
        routing_key="audio.process"
    )
    
    logger.info(f"Submitted analysis task {result.id} for file {request.file_id}")
    
    return TaskSubmitResponse(
        task_id=result.id,
        status="submitted",
        message="Audio analysis task submitted"
    )


@router.post("/analyze/batch", response_model=TaskSubmitResponse)
async def submit_batch_audio_analysis(
    request: BatchTaskSubmitRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Submit multiple audio files for background batch processing
    """
    result = celery_app.send_task(
        "samplemind.core.tasks.audio_tasks.batch_process_audio_files",
        kwargs={
            "batch_id": request.batch_id,
            "file_infos": request.file_infos,
            "user_id": request.user_id or current_user.user_id,
            "analysis_options": request.analysis_options or {},
        },
        queue="audio_processing",
        routing_key="audio.process"
    )
    
    logger.info(f"Submitted batch task {result.id} with {len(request.file_infos)} files")
    
    return TaskSubmitResponse(
        task_id=result.id,
        status="submitted",
        message="Batch audio analysis task submitted"
    )


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get task status and result
    """
    async_result = AsyncResult(task_id, app=celery_app)
    status_str = async_result.status
    
    progress = None
    progress_message = None
    result = None
    error = None
    started_at = None
    completed_at = None
    
    try:
        if async_result.info and isinstance(async_result.info, dict):
            info = async_result.info
            progress = info.get("progress")
            progress_message = info.get("status")
    except Exception:
        pass
    
    if async_result.successful():
        try:
            result = async_result.get(disable_sync_subtasks=False)
            completed_at = result.get("completed_at")
        except Exception as e:
            error = str(e)
    elif async_result.failed():
        try:
            result = async_result.get(propagate=False)
        except Exception as e:
            error = str(e)
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status_str,
        result=result,
        progress=progress,
        progress_message=progress_message,
        error=error,
        started_at=started_at,
        completed_at=completed_at
    )


@router.get("/workers/status", response_model=WorkersStatusResponse)
async def get_workers_status(current_user = Depends(get_current_active_user)):
    """
    Get Celery workers status
    """
    try:
        insp = celery_app.control.inspect(timeout=1.0)
        active = insp.active() or {}
        stats = insp.stats() or {}
        
        workers: list[WorkerInfo] = []
        for hostname, tasks in active.items():
            st = stats.get(hostname, {})
            workers.append(
                WorkerInfo(
                    hostname=hostname,
                    status="online",
                    active_tasks=len(tasks or []),
                    processed_tasks=st.get("total", {}).get("task-received", 0)
                )
            )
        
        return WorkersStatusResponse(workers=workers, total_workers=len(workers))
    except Exception as e:
        logger.warning(f"Could not fetch workers status: {e}")
        return WorkersStatusResponse(workers=[], total_workers=0)


@router.get("/queues/stats", response_model=QueueStatsResponse)
async def get_queue_stats(current_user = Depends(get_current_active_user)):
    """
    Get queue statistics
    """
    try:
        # Kombu connection via celery_app
        with celery_app.pool.acquire(block=True) as conn:
            channel = conn.channel()
            queues = []
            for q in celery_app.conf.task_queues:
                try:
                    bound = q.bind(conn)
                    # inspect queue for messages and consumers
                    _, message_count, consumer_count = bound.queue_declare(passive=True)
                    queues.append(QueueStats(name=q.name, messages=message_count, consumers=consumer_count))
                except Exception:
                    queues.append(QueueStats(name=q.name, messages=0, consumers=0))
            return QueueStatsResponse(queues=queues, total_queues=len(queues))
    except Exception as e:
        logger.warning(f"Could not fetch queue stats: {e}")
        return QueueStatsResponse(queues=[], total_queues=0)
