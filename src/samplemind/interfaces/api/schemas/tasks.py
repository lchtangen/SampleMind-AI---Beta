"""
Task Schemas
Pydantic models for background task requests and responses
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class TaskSubmitRequest(BaseModel):
    """Submit a task for background processing"""
    file_id: str
    file_path: str
    user_id: Optional[str] = None
    analysis_options: Optional[Dict[str, Any]] = None


class BatchTaskSubmitRequest(BaseModel):
    """Submit multiple files for batch processing"""
    batch_id: str
    file_infos: List[Dict[str, Any]]
    user_id: Optional[str] = None
    analysis_options: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """Task status response"""
    task_id: str
    status: str  # PENDING, STARTED, PROGRESS, SUCCESS, FAILURE, RETRY
    result: Optional[Dict[str, Any]] = None
    progress: Optional[int] = None
    progress_message: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskSubmitResponse(BaseModel):
    """Task submission response"""
    task_id: str
    status: str
    message: str


class TaskListResponse(BaseModel):
    """List of tasks"""
    tasks: List[TaskStatusResponse]
    total: int
    
    
class WorkerInfo(BaseModel):
    """Celery worker information"""
    hostname: str
    status: str
    active_tasks: int
    processed_tasks: int
    

class WorkersStatusResponse(BaseModel):
    """Workers status response"""
    workers: List[WorkerInfo]
    total_workers: int


class QueueStats(BaseModel):
    """Queue statistics"""
    name: str
    messages: int
    consumers: int


class QueueStatsResponse(BaseModel):
    """Queue statistics response"""
    queues: List[QueueStats]
    total_queues: int
