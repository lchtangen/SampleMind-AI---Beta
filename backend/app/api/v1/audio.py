"""
Audio endpoints for SampleMind AI
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import time
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.audio import (
    AudioUploadResponse,
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    AudioListResponse,
    AudioListItem,
    AudioDetailResponse,
    AudioSearchRequest,
    AudioFeatures,
    AIAnalysisResult
)
from app.core.security import decode_token, verify_token_type
from app.core.config import settings
from app.core.database import get_db
from app.models.audio import Audio, AudioAnalysis
from app.services import EmbeddingService

router = APIRouter(prefix="/audio", tags=["audio"])
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from JWT token"""
    token = credentials.credentials
    
    if not verify_token_type(token, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    return int(payload.get("sub"))


@router.post("/upload", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for processing
    
    - **file**: Audio file (WAV, MP3, FLAC, AIFF, OGG)
    - Returns: Upload confirmation with file metadata
    """
    # Validate file format
    file_extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_extension not in settings.ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    # TODO: Save file to disk/cloud storage
    # TODO: Extract basic metadata using librosa
    
    # Create audio record
    audio_record = Audio(
        user_id=user_id,
        filename=file.filename,
        original_filename=file.filename,
        file_path=f"/uploads/{file.filename}",  # TODO: Save to actual storage
        file_format=file_extension,
        file_size=file_size,
        status="uploaded"
    )
    
    db.add(audio_record)
    db.commit()
    db.refresh(audio_record)
    
    return AudioUploadResponse(
        id=audio_record.id,
        filename=audio_record.filename,
        file_size=audio_record.file_size,
        format=audio_record.file_format,
        duration=audio_record.duration,
        sample_rate=audio_record.sample_rate,
        channels=audio_record.channels,
        uploaded_at=audio_record.uploaded_at.isoformat(),
        status=audio_record.status
    )


@router.post("/analyze", response_model=AudioAnalysisResponse)
async def analyze_audio(
    request: AudioAnalysisRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Analyze an uploaded audio file
    
    - **audio_id**: ID of the uploaded audio file
    - **analysis_type**: Type of analysis (full, quick, custom)
    - **extract_features**: Extract audio features (tempo, key, etc.)
    - **ai_analysis**: Perform AI-powered analysis
    """
    # Verify audio file exists and belongs to user
    audio = db.query(Audio).filter(Audio.id == request.audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    if audio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to analyze this audio"
        )
    
    start_time = time.time()
    
    # TODO: Integrate with actual audio engine from /src/samplemind/core/audio/
    # TODO: Run analysis in Celery task for async processing
    
    # Simulated feature extraction
    features = None
    features_dict = None
    if request.extract_features:
        features = AudioFeatures(
            tempo=128.5,
            key="C major",
            time_signature="4/4",
            duration=180.0,
            loudness=-12.5,
            energy=0.75,
            danceability=0.68,
            valence=0.72,
            spectral_centroid=1500.5,
            zero_crossing_rate=0.08
        )
        features_dict = features.model_dump()
    
    # Simulated AI analysis
    ai_analysis = None
    ai_analysis_dict = None
    if request.ai_analysis:
        ai_analysis = AIAnalysisResult(
            genre=["Electronic", "House"],
            mood=["Energetic", "Uplifting"],
            instruments=["Synthesizer", "Drums", "Bass"],
            tags=["Dance", "Club", "EDM"],
            similarity_score=0.85,
            description="An energetic electronic track with a driving beat and uplifting melodies."
        )
        ai_analysis_dict = ai_analysis.model_dump()
    
    processing_time = time.time() - start_time
    
    # Store or update analysis results
    analysis = db.query(AudioAnalysis).filter(AudioAnalysis.audio_id == request.audio_id).first()
    if analysis:
        if features:
            analysis.tempo = features.tempo
            analysis.key = features.key
            analysis.time_signature = features.time_signature
            analysis.loudness = features.loudness
            analysis.energy = features.energy
            analysis.danceability = features.danceability
            analysis.valence = features.valence
            analysis.spectral_centroid = features.spectral_centroid
            analysis.zero_crossing_rate = features.zero_crossing_rate
        if ai_analysis:
            analysis.genres = ai_analysis.genre
            analysis.moods = ai_analysis.mood
            analysis.instruments = ai_analysis.instruments
            analysis.tags = ai_analysis.tags
            analysis.description = ai_analysis.description
            analysis.similarity_score = ai_analysis.similarity_score
    else:
        analysis = AudioAnalysis(
            audio_id=request.audio_id,
            tempo=features.tempo if features else None,
            key=features.key if features else None,
            time_signature=features.time_signature if features else None,
            loudness=features.loudness if features else None,
            energy=features.energy if features else None,
            danceability=features.danceability if features else None,
            valence=features.valence if features else None,
            spectral_centroid=features.spectral_centroid if features else None,
            zero_crossing_rate=features.zero_crossing_rate if features else None,
            genres=ai_analysis.genre if ai_analysis else None,
            moods=ai_analysis.mood if ai_analysis else None,
            instruments=ai_analysis.instruments if ai_analysis else None,
            tags=ai_analysis.tags if ai_analysis else None,
            description=ai_analysis.description if ai_analysis else None,
            similarity_score=ai_analysis.similarity_score if ai_analysis else None
        )
        db.add(analysis)
    
    db.commit()
    db.refresh(analysis)
    db.refresh(audio)

    EmbeddingService(db).ensure_embedding(audio)
    
    return AudioAnalysisResponse(
        audio_id=request.audio_id,
        status="completed",
        features=features,
        ai_analysis=ai_analysis,
        processing_time=processing_time,
        analyzed_at=analysis.analyzed_at.isoformat()
    )


@router.get("", response_model=AudioListResponse)
async def list_audio(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    List all audio files for the current user
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    # Query user's audio files
    query = db.query(Audio).filter(Audio.user_id == user_id)
    total = query.count()
    
    # Pagination and sorting
    audio_files = query.order_by(Audio.uploaded_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = [
        AudioListItem(
            id=audio.id,
            filename=audio.filename,
            duration=audio.duration,
            format=audio.file_format,
            uploaded_at=audio.uploaded_at.isoformat(),
            has_analysis=db.query(AudioAnalysis).filter(AudioAnalysis.audio_id == audio.id).first() is not None
        )
        for audio in audio_files
    ]
    
    return AudioListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{audio_id}", response_model=AudioDetailResponse)
async def get_audio_detail(
    audio_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about an audio file
    
    - **audio_id**: ID of the audio file
    """
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    if audio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audio"
        )
    
    # Get analysis if available
    analysis = db.query(AudioAnalysis).filter(AudioAnalysis.audio_id == audio_id).first()
    features = None
    ai_analysis = None
    
    if analysis:
        if analysis.tempo is not None:  # Check if features exist
            features = AudioFeatures(
                tempo=analysis.tempo,
                key=analysis.key,
                time_signature=analysis.time_signature,
                duration=audio.duration,
                loudness=analysis.loudness,
                energy=analysis.energy,
                danceability=analysis.danceability,
                valence=analysis.valence,
                spectral_centroid=analysis.spectral_centroid,
                zero_crossing_rate=analysis.zero_crossing_rate
            )
        if analysis.genres:  # Check if AI analysis exists
            ai_analysis = AIAnalysisResult(
                genre=analysis.genres,
                mood=analysis.moods,
                instruments=analysis.instruments,
                tags=analysis.tags,
                similarity_score=analysis.similarity_score,
                description=analysis.description
            )
    
    return AudioDetailResponse(
        id=audio.id,
        filename=audio.filename,
        file_size=audio.file_size,
        format=audio.file_format,
        duration=audio.duration,
        sample_rate=audio.sample_rate,
        channels=audio.channels,
        uploaded_at=audio.uploaded_at.isoformat(),
        status=audio.status,
        features=features,
        ai_analysis=ai_analysis,
        metadata=None
    )


@router.delete("/{audio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audio(
    audio_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete an audio file
    
    - **audio_id**: ID of the audio file to delete
    """
    audio = db.query(Audio).filter(Audio.id == audio_id).first()
    if not audio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    if audio.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this audio"
        )
    
    # TODO: Delete file from storage
    db.delete(audio)
    db.commit()
    
    return None
