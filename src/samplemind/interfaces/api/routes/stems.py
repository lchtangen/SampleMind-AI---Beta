"""
Stem Separation API Routes

Endpoints for AI-powered audio stem separation.
"""

from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from samplemind.core.processing.stem_separation import (
    StemSeparationEngine,
    StemType,
    StemProvider
)

router = APIRouter(prefix="/stems", tags=["Stem Separation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class StemSeparationRequest(BaseModel):
    """Request model for stem separation"""
    stems: List[str] = ["vocals", "instrumental"]
    provider: str = "lalal_ai"
    quality: str = "high"
    api_key: Optional[str] = None


class StemSeparationResponse(BaseModel):
    """Response model for stem separation"""
    success: bool
    message: str
    stems: dict[str, str]  # {stem_type: file_path}
    processing_time: float


class StemBatchRequest(BaseModel):
    """Request model for batch stem separation"""
    file_urls: List[str]
    stems: List[str] = ["vocals", "instrumental"]
    provider: str = "lalal_ai"


class StemBatchResponse(BaseModel):
    """Response model for batch processing"""
    success: bool
    total_files: int
    processed: int
    failed: int
    results: List[dict]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/separate", response_model=StemSeparationResponse)
async def separate_stems(
    file: UploadFile = File(...),
    request: StemSeparationRequest = None
):
    """
    Separate audio file into stems (vocals, drums, bass, etc.)

    Supported stems:
    - vocals
    - drums
    - bass
    - piano
    - guitar
    - synth
    - other
    - instrumental

    Example:
        ```
        POST /api/v1/stems/separate
        {
            "stems": ["vocals", "drums"],
            "provider": "lalal_ai",
            "quality": "high"
        }
        ```
    """
    import time
    import tempfile

    start_time = time.time()

    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Parse request
        if request is None:
            request = StemSeparationRequest()

        # Convert stem strings to StemType
        stem_types = [StemType(s.lower()) for s in request.stems]

        # Initialize engine
        engine = StemSeparationEngine(
            provider=request.provider,
            api_key=request.api_key
        )

        # Separate stems
        result = await engine.separate_stems(
            tmp_path,
            stems=stem_types,
            quality=request.quality
        )

        # Convert result to paths
        stems_dict = {
            stem_type.value: str(path)
            for stem_type, path in result.items()
        }

        processing_time = time.time() - start_time

        return StemSeparationResponse(
            success=True,
            message=f"Successfully separated {len(result)} stems",
            stems=stems_dict,
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        tmp_path.unlink(missing_ok=True)


@router.post("/separate/batch", response_model=StemBatchResponse)
async def batch_separate_stems(
    request: StemBatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Batch process multiple audio files for stem separation

    Example:
        ```
        POST /api/v1/stems/separate/batch
        {
            "file_urls": [
                "https://example.com/song1.mp3",
                "https://example.com/song2.mp3"
            ],
            "stems": ["vocals", "drums"],
            "provider": "lalal_ai"
        }
        ```
    """
    # This would typically be processed as a background task
    # For now, return placeholder
    return StemBatchResponse(
        success=True,
        total_files=len(request.file_urls),
        processed=0,
        failed=0,
        results=[]
    )


@router.get("/download/{stem_type}/{file_id}")
async def download_stem(stem_type: str, file_id: str):
    """
    Download a separated stem

    Args:
        stem_type: Type of stem (vocals, drums, etc.)
        file_id: Unique file identifier

    Returns:
        Audio file
    """
    # Get file path from storage
    file_path = Path(f"./output/stems/{file_id}_{stem_type}.wav")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Stem file not found")

    return FileResponse(
        file_path,
        media_type="audio/wav",
        filename=file_path.name
    )


@router.get("/providers")
async def list_providers():
    """
    List available stem separation providers

    Returns:
        List of available providers with their capabilities
    """
    providers = [
        {
            "name": "lalal_ai",
            "display_name": "LALAL.AI",
            "description": "High-quality cloud-based stem separation",
            "requires_api_key": True,
            "supported_stems": [
                "vocals", "instrumental", "drums", "bass",
                "piano", "guitar", "synth", "other"
            ],
            "quality_levels": ["low", "medium", "high"]
        },
        {
            "name": "moises",
            "display_name": "Moises.ai",
            "description": "AI-powered music separation and practice tools",
            "requires_api_key": True,
            "supported_stems": [
                "vocals", "drums", "bass", "other"
            ],
            "quality_levels": ["standard", "high"]
        },
        {
            "name": "local",
            "display_name": "Local Processing",
            "description": "Process stems locally using Spleeter",
            "requires_api_key": False,
            "supported_stems": [
                "vocals", "drums", "bass", "other"
            ],
            "quality_levels": ["standard"]
        }
    ]

    return {
        "providers": providers,
        "total": len(providers)
    }


@router.get("/status/{job_id}")
async def get_separation_status(job_id: str):
    """
    Check status of stem separation job

    Args:
        job_id: Job identifier

    Returns:
        Job status and results
    """
    # This would check job status from database/queue
    # Placeholder response
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "stems_ready": ["vocals", "instrumental"],
        "estimated_time_remaining": 0
    }
