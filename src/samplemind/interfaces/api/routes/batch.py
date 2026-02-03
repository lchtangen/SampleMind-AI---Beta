"""
Batch Audio Analysis API
Analyze multiple audio files in parallel with progress tracking
"""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel

from samplemind.core.engine.audio_engine import AudioEngine
from samplemind.integrations.ai_manager import SampleMindAIManager, AnalysisType


router = APIRouter(prefix="/batch", tags=["Batch Processing"])


# Models
class BatchAnalysisRequest(BaseModel):
    """Request for batch audio analysis"""
    analysis_type: str = "comprehensive"
    max_workers: int = 4
    use_cache: bool = True


class BatchJobStatus(BaseModel):
    """Status of a batch analysis job"""
    job_id: str
    status: str  # pending, processing, completed, failed
    total_files: int
    processed_files: int
    progress_percent: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []


# In-memory job storage (use Redis in production)
active_jobs: Dict[str, BatchJobStatus] = {}


@dataclass
class BatchProcessor:
    """Process multiple audio files in parallel"""
    audio_engine: AudioEngine = field(default_factory=AudioEngine)
    ai_manager: SampleMindAIManager = field(default_factory=SampleMindAIManager)
    max_workers: int = 4
    
    async def process_batch(
        self,
        job_id: str,
        file_paths: List[Path],
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE_ANALYSIS
    ) -> None:
        """Process batch of audio files"""
        job = active_jobs[job_id]
        job.status = "processing"
        
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._process_single, path): path
                    for path in file_paths
                }
                
                for future in as_completed(futures):
                    path = futures[future]
                    try:
                        result = future.result()
                        job.results.append(result)
                        job.processed_files += 1
                        job.progress_percent = (job.processed_files / job.total_files) * 100
                    except Exception as e:
                        job.errors.append({
                            "file": str(path),
                            "error": str(e)
                        })
            
            job.status = "completed"
            job.completed_at = datetime.now()
            
        except Exception as e:
            job.status = "failed"
            job.errors.append({"error": str(e)})
    
    def _process_single(self, file_path: Path) -> Dict[str, Any]:
        """Process single audio file"""
        features = self.audio_engine.analyze_audio(file_path)
        return {
            "file": str(file_path),
            "features": features.to_dict(),
            "analyzed_at": datetime.now().isoformat()
        }


# Global processor instance
processor = BatchProcessor()


@router.post("/analyze", response_model=Dict[str, str])
async def create_batch_analysis(
    files: List[UploadFile] = File(...),
    request: BatchAnalysisRequest = BatchAnalysisRequest(),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """
    Create batch analysis job for multiple audio files
    
    Returns job_id for tracking progress
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded files temporarily
    temp_dir = Path("/tmp/samplemind_batch") / job_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    file_paths = []
    for file in files:
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        file_paths.append(file_path)
    
    # Create job status
    job = BatchJobStatus(
        job_id=job_id,
        status="pending",
        total_files=len(files),
        processed_files=0,
        progress_percent=0.0,
        started_at=datetime.now()
    )
    active_jobs[job_id] = job
    
    # Start processing in background
    background_tasks.add_task(
        processor.process_batch,
        job_id,
        file_paths,
        AnalysisType[request.analysis_type.upper()]
    )
    
    return {"job_id": job_id, "status": "pending"}


@router.get("/status/{job_id}", response_model=BatchJobStatus)
async def get_batch_status(job_id: str) -> BatchJobStatus:
    """Get status of batch analysis job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return active_jobs[job_id]


@router.get("/results/{job_id}")
async def get_batch_results(job_id: str) -> Dict[str, Any]:
    """Get results of completed batch analysis"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job.status}"
        )
    
    return {
        "job_id": job_id,
        "total_files": job.total_files,
        "successful": len(job.results),
        "failed": len(job.errors),
        "results": job.results,
        "errors": job.errors
    }


@router.delete("/jobs/{job_id}")
async def cancel_batch_job(job_id: str) -> Dict[str, str]:
    """Cancel and delete batch analysis job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up temp files
    temp_dir = Path("/tmp/samplemind_batch") / job_id
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    # Remove job
    del active_jobs[job_id]
    
    return {"status": "deleted", "job_id": job_id}
