"""Audio file upload and analysis endpoints"""

import uuid
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from samplemind.interfaces.api.schemas.audio import (
    AudioUploadResponse,
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    AudioFileMetadata
)
from samplemind.interfaces.api.config import get_settings
from samplemind.interfaces.api.exceptions import FileValidationError, ResourceNotFoundError
from samplemind.interfaces.api.dependencies import get_app_state

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=AudioUploadResponse)
async def upload_audio(file: UploadFile = File(...)):
    """Upload an audio file"""
    logger.info(f"Audio upload started: {file.filename} (type: {file.content_type})")
    settings = get_settings()
    
    # Validate file
    if not file.content_type in settings.ALLOWED_AUDIO_FORMATS:
        logger.warning(f"Upload rejected: Unsupported file type {file.content_type} for file {file.filename}")
        raise FileValidationError(
            f"Unsupported file type: {file.content_type}",
            details={"allowed_formats": settings.ALLOWED_AUDIO_FORMATS}
        )
    
    # Generate file ID and save
    file_id = str(uuid.uuid4())
    file_path = settings.UPLOAD_DIR / f"{file_id}_{file.filename}"
    
    # Save file
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        logger.warning(f"Upload rejected: File too large ({file_size / 1024 / 1024:.2f}MB) for file {file.filename}")
        raise FileValidationError(
            f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    logger.info(f"✅ Audio uploaded successfully: {file.filename} (ID: {file_id}, Size: {file_size / 1024 / 1024:.2f}MB)")
    
    return AudioUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_size=file_size
    )


@router.post("/analyze/{file_id}", response_model=AudioAnalysisResponse)
async def analyze_audio(
    file_id: str,
    request: AudioAnalysisRequest = Depends()
):
    """Analyze an uploaded audio file"""
    logger.info(f"Audio analysis started: file_id={file_id}, level={request.analysis_level}, ai={request.include_ai}")
    settings = get_settings()
    audio_engine = get_app_state("audio_engine")
    ai_manager = get_app_state("ai_manager")
    
    # Find file
    files = list(settings.UPLOAD_DIR.glob(f"{file_id}_*"))
    if not files:
        logger.error(f"Analysis failed: File not found - {file_id}")
        raise ResourceNotFoundError("audio_file", file_id)
    
    file_path = files[0]
    
    # Analyze audio
    from samplemind.core.engine.audio_engine import AnalysisLevel
    level = AnalysisLevel[request.analysis_level.upper()]
    
    import time
    start_time = time.time()
    
    try:
        features = audio_engine.analyze_audio(file_path, level=level)
    except Exception as e:
        logger.error(f"Audio analysis failed for {file_id}: {str(e)}")
        raise
    
    processing_time = time.time() - start_time
    analysis_id = str(uuid.uuid4())
    logger.info(f"Audio features extracted in {processing_time:.2f}s for file {file_id}")
    
    # Optional AI analysis
    ai_result = None
    if request.include_ai and ai_manager:
        from samplemind.integrations.ai_manager import AnalysisType, AIProvider
        
        provider = None
        if request.ai_provider:
            provider = AIProvider[request.ai_provider.upper()]
        
        logger.info(f"Starting AI analysis for {file_id} with provider: {provider or 'default'}")
        try:
            ai_result = await ai_manager.analyze_music(
                features.to_dict(),
                AnalysisType.COMPREHENSIVE_ANALYSIS,
                preferred_provider=provider
            )
            logger.info(f"AI analysis completed for {file_id}")
        except Exception as e:
            logger.error(f"AI analysis failed for {file_id}: {str(e)}")
            # Continue without AI results
    
    logger.info(f"✅ Analysis completed successfully for {file_id} (total time: {processing_time:.2f}s)")
    
    return AudioAnalysisResponse(
        analysis_id=analysis_id,
        file_id=file_id,
        duration=features.duration,
        tempo=features.tempo,
        key=features.key,
        mode=features.mode,
        time_signature=list(features.time_signature),
        spectral_features={
            "centroid": features.spectral_centroid,
            "bandwidth": features.spectral_bandwidth,
        } if level != AnalysisLevel.BASIC else None,
        ai_analysis=ai_result.to_dict() if ai_result else None,
        analysis_level=request.analysis_level,
        processing_time=processing_time,
        analyzed_at=datetime.now()
    )


@router.get("/files", response_model=List[AudioFileMetadata])
async def list_audio_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List uploaded audio files"""
    logger.info(f"Listing audio files: page={page}, page_size={page_size}")
    settings = get_settings()
    
    files = list(settings.UPLOAD_DIR.glob("*"))
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    page_files = files[start:end]
    
    result = []
    for file_path in page_files:
        file_id = file_path.stem.split("_")[0]
        filename = "_".join(file_path.stem.split("_")[1:]) + file_path.suffix
        
        # Try to get audio info
        try:
            import soundfile as sf
            info = sf.info(str(file_path))
            duration = info.duration
            sample_rate = info.samplerate
            channels = info.channels
        except:
            duration = 0.0
            sample_rate = 0
            channels = 0
        
        result.append(AudioFileMetadata(
            file_id=file_id,
            filename=filename,
            file_size=file_path.stat().st_size,
            duration=duration,
            sample_rate=sample_rate,
            channels=channels,
            format=file_path.suffix[1:],
            uploaded_at=datetime.fromtimestamp(file_path.stat().st_mtime)
        ))
    
    logger.info(f"Retrieved {len(result)} audio files for page {page}")
    return result
