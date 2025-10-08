"""
Analysis API Routes

FastAPI endpoints for BPM/Key detection, loop segmentation,
and audio fingerprinting with async support and progress tracking.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from pathlib import Path
import tempfile
import shutil
from loguru import logger

from samplemind.core.analysis import BPMKeyDetector, LoopSegmenter
from samplemind.integrations import AcoustIDClient

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# Request/Response Models
class BPMKeyResponse(BaseModel):
    bpm: float
    confidence: float
    key: str
    file: str
    librosa_bpm: Optional[float] = None
    madmom_bpm: Optional[float] = None


class LoopSegment(BaseModel):
    start_bar: int
    end_bar: int
    start_sample: int
    end_sample: int
    duration: float
    bpm: float
    segment_index: int
    quality_score: Optional[float] = None


class LoopsResponse(BaseModel):
    segments: List[LoopSegment]
    total_segments: int
    file: str


class IdentifyMatch(BaseModel):
    score: float
    recording_id: str
    title: str
    artist: str
    metadata: Optional[Dict] = None


class IdentifyResponse(BaseModel):
    matches: List[IdentifyMatch]
    total_matches: int
    file: str


class DuplicatePair(BaseModel):
    file1: str
    file2: str


class DedupeResponse(BaseModel):
    duplicates: List[DuplicatePair]
    total_duplicates: int
    directory: str


# ============================================================================
# BPM/Key Detection Endpoints
# ============================================================================

@router.post("/bpm-key", response_model=BPMKeyResponse)
async def detect_bpm_key(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Detect BPM and musical key from uploaded audio file.
    
    Returns:
        BPM, key, and confidence scores
    """
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        detector = BPMKeyDetector()
        
        # Run detection
        bpm_data = detector.detect_bpm(tmp_path)
        key = detector.detect_key(tmp_path)
        
        return BPMKeyResponse(
            bpm=bpm_data['bpm'],
            confidence=bpm_data['confidence'],
            key=key,
            file=file.filename,
            librosa_bpm=bpm_data.get('librosa_bpm'),
            madmom_bpm=bpm_data.get('madmom_bpm')
        )
    
    except Exception as e:
        logger.error(f"Error detecting BPM/key: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if background_tasks:
            background_tasks.add_task(tmp_path.unlink, missing_ok=True)
        else:
            tmp_path.unlink(missing_ok=True)


@router.post("/bpm-key/batch")
async def batch_detect_bpm_key(
    files: List[UploadFile] = File(...),
):
    """
    Batch detect BPM and key for multiple files.
    
    Returns:
        List of BPM/key results
    """
    results = []
    
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = Path(tmp.name)
        
        try:
            detector = BPMKeyDetector()
            bpm_data = detector.detect_bpm(tmp_path)
            key = detector.detect_key(tmp_path)
            
            results.append(BPMKeyResponse(
                bpm=bpm_data['bpm'],
                confidence=bpm_data['confidence'],
                key=key,
                file=file.filename
            ))
        
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            results.append({
                "file": file.filename,
                "error": str(e)
            })
        
        finally:
            tmp_path.unlink(missing_ok=True)
    
    return {"results": results, "total": len(results)}


# ============================================================================
# Loop Segmentation Endpoints
# ============================================================================

@router.post("/loops", response_model=LoopsResponse)
async def extract_loops(
    file: UploadFile = File(...),
    bars: int = 8,
    background_tasks: BackgroundTasks = None
):
    """
    Extract 8-bar loops from uploaded audio file.
    
    Args:
        file: Audio file
        bars: Bars per segment (default 8)
    
    Returns:
        List of extracted loop segments
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        segmenter = LoopSegmenter()
        segments = segmenter.segment_8bars(tmp_path, bars)
        
        # Convert segments to response format
        loop_segments = []
        for seg in segments:
            loop_segments.append(LoopSegment(
                start_bar=seg['start_bar'],
                end_bar=seg['end_bar'],
                start_sample=seg['start_sample'],
                end_sample=seg['end_sample'],
                duration=seg['duration'],
                bpm=seg['bpm'],
                segment_index=seg['segment_index'],
                quality_score=segmenter._score_segment(seg['audio'], seg['sample_rate'])
            ))
        
        return LoopsResponse(
            segments=loop_segments,
            total_segments=len(loop_segments),
            file=file.filename
        )
    
    except Exception as e:
        logger.error(f"Error extracting loops: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if background_tasks:
            background_tasks.add_task(tmp_path.unlink, missing_ok=True)
        else:
            tmp_path.unlink(missing_ok=True)


@router.post("/loops/best")
async def extract_best_loop(
    file: UploadFile = File(...),
    bars: int = 8,
    background_tasks: BackgroundTasks = None
):
    """
    Extract the best quality loop from audio file.
    
    Returns:
        Single best loop segment
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        segmenter = LoopSegmenter()
        best_loop = segmenter.extract_best_loop(tmp_path, bars)
        
        if not best_loop:
            raise HTTPException(status_code=404, detail="No suitable loops found")
        
        return {
            "segment": LoopSegment(
                start_bar=best_loop['start_bar'],
                end_bar=best_loop['end_bar'],
                start_sample=best_loop['start_sample'],
                end_sample=best_loop['end_sample'],
                duration=best_loop['duration'],
                bpm=best_loop['bpm'],
                segment_index=best_loop['segment_index'],
                quality_score=segmenter._score_segment(best_loop['audio'], best_loop['sample_rate'])
            ),
            "file": file.filename
        }
    
    except Exception as e:
        logger.error(f"Error extracting best loop: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if background_tasks:
            background_tasks.add_task(tmp_path.unlink, missing_ok=True)
        else:
            tmp_path.unlink(missing_ok=True)


# ============================================================================
# Audio Identification Endpoints
# ============================================================================

@router.post("/identify", response_model=IdentifyResponse)
async def identify_audio(
    file: UploadFile = File(...),
    threshold: float = 0.8,
    background_tasks: BackgroundTasks = None
):
    """
    Identify audio file using AcoustID fingerprinting.
    
    Args:
        file: Audio file
        threshold: Minimum confidence threshold (0-1)
    
    Returns:
        List of matches with metadata
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        client = AcoustIDClient()
        matches = client.identify(tmp_path, threshold)
        
        # Convert matches to response format
        match_list = []
        for match in matches:
            match_list.append(IdentifyMatch(
                score=match['score'],
                recording_id=match['recording_id'],
                title=match['title'],
                artist=match['artist'],
                metadata=match.get('metadata')
            ))
        
        return IdentifyResponse(
            matches=match_list,
            total_matches=len(match_list),
            file=file.filename
        )
    
    except Exception as e:
        logger.error(f"Error identifying audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if background_tasks:
            background_tasks.add_task(tmp_path.unlink, missing_ok=True)
        else:
            tmp_path.unlink(missing_ok=True)


# ============================================================================
# Duplicate Detection Endpoints
# ============================================================================

@router.post("/dedupe", response_model=DedupeResponse)
async def detect_duplicates(
    files: List[UploadFile] = File(...),
    threshold: float = 0.95
):
    """
    Find duplicate audio files using fingerprinting.
    
    Args:
        files: List of audio files
        threshold: Similarity threshold (0-1)
    
    Returns:
        List of duplicate pairs
    """
    # Save all files temporarily
    temp_dir = Path(tempfile.mkdtemp())
    temp_files = []
    
    for file in files:
        temp_path = temp_dir / file.filename
        with open(temp_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        temp_files.append(temp_path)
    
    try:
        client = AcoustIDClient()
        duplicates = client.find_duplicates(temp_dir, threshold)
        
        # Convert to response format
        duplicate_list = []
        for file1, file2 in duplicates:
            duplicate_list.append(DuplicatePair(
                file1=file1.name,
                file2=file2.name
            ))
        
        return DedupeResponse(
            duplicates=duplicate_list,
            total_duplicates=len(duplicate_list),
            directory="uploaded_files"
        )
    
    except Exception as e:
        logger.error(f"Error detecting duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "analysis",
        "features": [
            "bpm-key-detection",
            "loop-segmentation",
            "audio-identification",
            "duplicate-detection"
        ]
    }
