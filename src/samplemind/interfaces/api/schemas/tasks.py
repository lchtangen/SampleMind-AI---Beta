"""
Task Schemas
Pydantic models for background task requests and responses
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskSubmitRequest(BaseModel):
    """Submit a task for background processing"""

    file_id: str
    file_path: str
    user_id: str | None = None
    analysis_options: dict[str, Any] | None = None


class BatchTaskSubmitRequest(BaseModel):
    """Submit multiple files for batch processing"""

    batch_id: str
    file_infos: list[dict[str, Any]]
    user_id: str | None = None
    analysis_options: dict[str, Any] | None = None


class TaskStatusResponse(BaseModel):
    """Task status response"""

    task_id: str
    status: str  # PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, RETRY
    result: dict[str, Any] | None = None
    progress: int | None = None
    progress_message: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TaskSubmitResponse(BaseModel):
    """Task submission response"""

    task_id: str
    status: str
    message: str


class TaskListResponse(BaseModel):
    """List of tasks"""

    tasks: list[TaskStatusResponse]
    total: int


class WorkerInfo(BaseModel):
    """Celery worker information"""

    hostname: str
    status: str
    active_tasks: int
    processed_tasks: int


class WorkersStatusResponse(BaseModel):
    """Workers status response"""

    workers: list[WorkerInfo]
    total_workers: int


class QueueStats(BaseModel):
    """Queue statistics"""

    name: str
    messages: int
    consumers: int


class QueueStatsResponse(BaseModel):
    """Queue statistics response"""

    queues: list[QueueStats]
    total_queues: int
