"""
Audio Processing API Endpoints

This module provides RESTful API endpoints for audio file processing, analysis,
and feature extraction in the SampleMind AI platform.
"""

import asyncio
import logging
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from samplemind.core.engine.audio_engine import AdvancedFeatureExtractor, AudioProcessor
from samplemind.core.processing.audio_pipeline import AudioFormat, AudioPipeline
from samplemind.interfaces.api.config import get_settings
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.interfaces.api.exceptions import (
    FileValidationError,
    ResourceNotFoundError,
)
from samplemind.interfaces.api.schemas.audio import (
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    AudioFeatureExtractionResponse,
    AudioFileMetadata,
    AudioProcessRequest,
    AudioProcessResponse,
    AudioUploadResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=AudioUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an audio file",
    description="""
           Upload an audio file for processing and analysis.

           Supported formats: WAV, MP3, FLAC, AIFF, OGG, M4A
           Max file size: 100MB
           """,
)
async def upload_audio(
    file: UploadFile = File(..., description="Audio file to upload"),
    background_tasks: BackgroundTasks = None,
) -> None:
    """
    Upload an audio file to the server for processing.

    The file will be stored in the server's upload directory and assigned a unique ID.
    This ID can be used for subsequent operations on the file.
    """
    logger.info(f"Audio upload started: {file.filename} (type: {file.content_type})")
    settings = get_settings()

    # Validate file type
    if not file.content_type.lower() in [f"audio/{fmt.value}" for fmt in AudioFormat]:
        logger.warning(
            f"Upload rejected: Unsupported file type {file.content_type} for file {file.filename}"
        )
        raise FileValidationError(
            f"Unsupported file type: {file.content_type}",
            details={"allowed_formats": [f"audio/{fmt.value}" for fmt in AudioFormat]},
        )

    # Generate file ID and save path
    file_id = str(uuid.uuid4())
    file_path = settings.UPLOAD_DIR / f"{file_id}_{file.filename}"

    # Read and validate file size
    contents = await file.read()
    file_size = len(contents)
    max_size_mb = getattr(settings, "MAX_UPLOAD_SIZE_MB", 100)

    if file_size > max_size_mb * 1024 * 1024:
        logger.warning(
            f"Upload rejected: File too large ({file_size / 1024 / 1024:.2f}MB) for file {file.filename}"
        )
        raise FileValidationError(f"File too large. Max size: {max_size_mb}MB")

    # Save file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Process file in background if needed
    if background_tasks:
        background_tasks.add_task(
            process_uploaded_file, file_path=file_path, file_id=file_id
        )

    logger.info(
        f"✅ Audio uploaded successfully: {file.filename} (ID: {file_id}, Size: {file_size / 1024 / 1024:.2f}MB)"
    )

    return AudioUploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_size=file_size,
        message="File uploaded successfully",
    )


@router.post(
    "/process/{file_id}",
    response_model=AudioProcessResponse,
    summary="Process an audio file",
    description="""
           Process an uploaded audio file with various audio effects and filters.

           Options include:
           - Sample rate conversion
           - Channel conversion (stereo/mono)
           - Normalization and gain control
           - Noise reduction and filtering
           - Silence trimming
           """,
)
async def process_audio(
    file_id: str, request: AudioProcessRequest, background_tasks: BackgroundTasks = None
) -> None:
    """
    Process an audio file with the specified processing pipeline.

    This endpoint applies a series of audio processing steps to the uploaded file
    and returns the processed audio file or saves it to the specified location.
    """
    logger.info(f"Audio processing started: file_id={file_id}, steps={request.steps}")
    settings = get_settings()

    # Find file
    files = list(settings.UPLOAD_DIR.glob(f"{file_id}_*"))
    if not files:
        logger.error(f"Processing failed: File not found - {file_id}")
        raise ResourceNotFoundError("audio_file", file_id)

    file_path = files[0]
    output_path = settings.PROCESSED_DIR / f"{file_id}_processed{file_path.suffix}"

    # Process file (synchronously or in background)
    if background_tasks and request.background:
        background_tasks.add_task(
            process_audio_file,
            input_path=file_path,
            output_path=output_path,
            steps=request.steps,
        )

        return AudioProcessResponse(
            file_id=file_id,
            status="processing",
            message="Audio processing started in background",
            output_path=str(output_path) if request.return_path else None,
        )
    else:
        try:
            result = process_audio_file(
                input_path=file_path, output_path=output_path, steps=request.steps
            )

            return AudioProcessResponse(
                file_id=file_id,
                status="completed",
                message="Audio processing completed successfully",
                output_path=str(output_path) if request.return_path else None,
                processing_time=result.get("processing_time", 0),
                processing_steps=result.get("steps", []),
            )
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Audio processing failed: {str(e)}",
            )


@router.post(
    "/analyze/{file_id}",
    response_model=AudioAnalysisResponse,
    summary="Analyze audio features",
    description="""
           Extract and analyze audio features from an uploaded file.

           Features include:
           - Tonal analysis (key, mode, pitch)
           - Rhythmic analysis (tempo, beats, onsets)
           - Spectral analysis (centroid, bandwidth, rolloff)
           - MFCCs and other advanced features
           """,
)
async def analyze_audio(
    file_id: str,
    request: AudioAnalysisRequest = Depends(),
    background_tasks: BackgroundTasks = None,
) -> None:
    """
    Analyze an audio file and extract various audio features.

    This endpoint performs comprehensive audio analysis including:
    - Tonal analysis (key, mode, pitch)
    - Rhythmic analysis (tempo, beats, onsets)
    - Spectral analysis (centroid, bandwidth, rolloff)
    - MFCCs and other advanced features
    """
    logger.info(
        f"Audio analysis started: file_id={file_id}, level={request.analysis_level}"
    )
    settings = get_settings()

    # Find file
    files = list(settings.UPLOAD_DIR.glob(f"{file_id}_*"))
    if not files:
        logger.error(f"Analysis failed: File not found - {file_id}")
        raise ResourceNotFoundError("audio_file", file_id)

    file_path = files[0]

    # Get services from app state
    try:
        audio_engine = get_app_state("audio_engine")
    except Exception:
        # Fallback if app state not initialized (e.g. testing)
        from samplemind.core.engine.audio_engine import AudioEngine

        audio_engine = AudioEngine()

    from samplemind.core.engine.audio_engine import AnalysisLevel

    try:
        level_enum = AnalysisLevel[request.analysis_level.upper()]
    except KeyError:
        level_enum = AnalysisLevel.STANDARD

    import time

    start_time = time.time()

    try:
        # 1. Audio Engine Analysis
        # Run in thread pool to avoid blocking async event loop
        features = await asyncio.to_thread(
            audio_engine.analyze_audio, file_path, analysis_level=level_enum
        )

        # 2. Save Semantic Embedding (Phase 4.5)
        analysis_id = str(uuid.uuid4())
        try:
            if features.neural_embedding:
                from samplemind.core.database.chroma import add_embedding

                # Basic metadata for filtering
                meta = {
                    "filename": file_path.name,
                    "analysis_id": analysis_id,
                    "tempo": float(features.tempo) if features.tempo else 0.0,
                    "key": str(features.key),
                    "mode": str(features.mode),
                    "duration": float(features.duration),
                }

                await add_embedding(
                    file_id=file_id, embedding=features.neural_embedding, metadata=meta
                )
                logger.info(f"✅ Saved embedding for {file_id} to ChromaDB")

                # ALSO, save sidecar JSON for SyncManager to pick up
                await asyncio.to_thread(features.save, file_path)
                logger.info(f"✅ Saved analysis sidecar for {file_path}")

        except Exception as e:
            logger.error(f"Failed to save embedding to ChromaDB: {e}")

        # 3. AI Analysis (Optional)
        ai_analysis_result = None
        if request.include_ai:
            try:
                ai_manager = get_app_state("ai_manager")
                if ai_manager:
                    # AI Manager might need the file path or the extracted features
                    # Assuming an interface that accepts file_path + prompt/context
                    # For now, let's assume a method classify_genre_style or similar
                    # Or generic analyze method

                    # If ai_manager isn't ready, we skip or use mock
                    if hasattr(ai_manager, "analyze_content"):
                        ai_analysis_result = await ai_manager.analyze_content(
                            content_type="audio_features",
                            content=asdict(features),
                            prompt="Analyze genre, mood, and style based on these audio features.",
                        )
            except Exception as e:
                logger.warning(f"AI analysis failed or skipped: {e}")

        # 3. Construct Response
        processing_time = time.time() - start_time
        # analysis_id defined above

        return AudioAnalysisResponse(
            analysis_id=analysis_id,
            file_id=file_id,
            duration=features.duration,
            tempo=features.tempo,
            key=features.key,
            mode=features.mode,
            time_signature=list(features.time_signature),
            spectral_features={
                "centroid_mean": (
                    sum(features.spectral_centroid) / len(features.spectral_centroid)
                    if features.spectral_centroid
                    else 0
                ),
                "rolloff_mean": (
                    sum(features.spectral_rolloff) / len(features.spectral_rolloff)
                    if features.spectral_rolloff
                    else 0
                ),
            },
            ai_analysis=ai_analysis_result,
            analysis_level=request.analysis_level,
            processing_time=processing_time,
            analyzed_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"Audio analysis failed for {file_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio analysis failed: {str(e)}",
        )


# Helper functions for background processing
async def process_uploaded_file(file_path: Path, file_id: str):
    """Background task to process an uploaded file"""
    try:
        # Here you could add automatic processing of uploaded files
        # For example, generate waveform images, extract metadata, etc.
        logger.info(f"Processing uploaded file in background: {file_path}")

        # Example: Generate a waveform preview
        # generate_waveform_preview(file_path, file_id)

    except Exception as e:
        logger.error(
            f"Background processing failed for {file_id}: {str(e)}", exc_info=True
        )


def process_audio_file(
    input_path: Path, output_path: Path, steps: Dict[str, Any]
) -> Dict[str, Any]:
    """Process an audio file with the given processing steps"""
    start_time = time.time()

    try:
        # Initialize audio pipeline
        pipeline = AudioPipeline()

        # Process audio
        pipeline.process(input_path, **steps)

        # Save processed audio
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pipeline.save(output_path)

        return {
            "processing_time": time.time() - start_time,
            "output_path": str(output_path),
            "steps": pipeline.get_processing_history(),
        }

    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}", exc_info=True)
        raise


async def analyze_audio_file(
    file_path: Path,
    file_id: str,
    analysis_level: str = "standard",
    include_ai: bool = False,
    save_results: bool = True,
) -> Dict[str, Any]:
    """Analyze an audio file and return features"""
    start_time = time.time()
    settings = get_settings()

    try:
        # Initialize audio engine
        audio_engine = get_app_state("audio_engine")
        ai_manager = get_app_state("ai_manager") if include_ai else None

        # Load and preprocess audio
        pipeline = AudioPipeline()
        y, sr = pipeline.load(file_path).to_mono().get_audio_data()

        # Extract features
        extractor = AdvancedFeatureExtractor(sample_rate=sr)

        # Extract features based on analysis level
        features = {}

        if analysis_level in ["basic", "standard", "detailed"]:
            features["tonal"] = extractor.extract_tonal_features(y)
            features["rhythmic"] = extractor.extract_rhythmic_features(y)

        if analysis_level in ["standard", "detailed"]:
            features["spectral"] = extractor.extract_spectral_features(y)
            features["mfcc"] = extractor.extract_mfcc_features(y)

        if analysis_level == "detailed":
            # Add any additional detailed analysis here
            pass

        # Add metadata
        features["metadata"] = {
            "filename": file_path.name,
            "duration": len(y) / sr,
            "sample_rate": sr,
            "channels": 1,  # Always mono after processing
            "analysis_level": analysis_level,
            "processing_time": time.time() - start_time,
        }

        # AI analysis if requested
        ai_analysis = {}
        if include_ai and ai_manager:
            try:
                ai_analysis = await ai_manager.analyze_audio(file_path, features)
            except Exception as e:
                logger.warning(f"AI analysis failed: {str(e)}")
                ai_analysis = {"error": str(e)}

        # Save results if requested
        if save_results:
            analysis_id = str(uuid.uuid4())
            analysis_dir = settings.ANALYSIS_DIR / file_id
            analysis_dir.mkdir(parents=True, exist_ok=True)

            analysis_file = analysis_dir / f"analysis_{analysis_id}.json"
            with open(analysis_file, "w") as f:
                import json

                json.dump(
                    {
                        "analysis_id": analysis_id,
                        "file_id": file_id,
                        "filename": file_path.name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "processing_time_seconds": time.time() - start_time,
                        "analysis_level": analysis_level,
                        "features": features,
                        "ai_analysis": ai_analysis,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Analysis results saved to {analysis_file}")

        return {
            "processing_time": time.time() - start_time,
            "features": features,
            "ai_analysis": ai_analysis,
            "analysis_id": analysis_id if save_results else None,
        }

    except Exception as e:
        logger.error(f"Audio analysis failed: {str(e)}", exc_info=True)
        raise


@router.get(
    "/list",
    response_model=List[AudioFileMetadata],
    summary="List uploaded audio files",
    description="""
           Get a paginated list of uploaded audio files with metadata.

           Returns basic information about each file including:
           - File ID and original filename
           - File size and MIME type
           - Upload timestamp
           """,
)
async def list_audio_files(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    file_type: Optional[str] = Query(
        None, description="Filter by file type (e.g., 'wav', 'mp3')"
    ),
) -> None:
    """
    List all uploaded audio files with pagination and filtering.

    This endpoint provides a paginated list of audio files that have been
    uploaded to the server, along with their metadata.
    """
    settings = get_settings()

    # Get all audio files
    audio_files = []
    for ext in [".wav", ".mp3", ".flac", ".aiff", ".ogg", ".m4a"]:
        if file_type and f".{file_type.lower()}" != ext:
            continue
        audio_files.extend(settings.UPLOAD_DIR.glob(f"*{ext}"))

    # Sort by modification time (newest first)
    audio_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    # Apply pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_files = audio_files[start_idx:end_idx]

    # Prepare response
    result = []
    for file_path in paginated_files:
        try:
            # Extract file ID and original filename
            parts = file_path.name.split("_", 1)
            if len(parts) == 2:
                file_id, original_filename = parts
            else:
                file_id = str(uuid.uuid4())
                original_filename = file_path.name

            # Get file stats
            stat = file_path.stat()

            result.append(
                AudioFileMetadata(
                    file_id=file_id,
                    filename=original_filename,
                    file_size=stat.st_size,
                    upload_time=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    mime_type=f"audio/{file_path.suffix[1:].lower()}",
                    duration=get_audio_duration(file_path),
                )
            )
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {str(e)}")
            continue

    logger.info(f"Retrieved {len(result)} audio files for page {page}")
    return result


# ---------------------------------------------------------------------------
# Stem Separation (P1-013) — demucs htdemucs_6s
# ---------------------------------------------------------------------------


class StemSeparationResponse(BaseModel):
    """Response for stem separation endpoint."""

    source_file: str
    model: str
    stems: List[str]
    output_dir: Optional[str] = None
    processing_time_s: float
    mock: bool = False


@router.post(
    "/separate",
    response_model=StemSeparationResponse,
    summary="Separate audio into stems",
    description="""
    Separate a full audio track into up to 6 stems using Demucs htdemucs_6s.

    Stems: drums, bass, vocals, piano, guitar, other.
    Output WAV files are written to a temp directory when save_stems=true.
    """,
    tags=["Audio Processing"],
)
async def separate_audio_stems(
    file: UploadFile = File(...),
    model: str = Query("htdemucs_6s", description="Demucs model name"),
    save_stems: bool = Query(False, description="Write stem WAV files to disk"),
) -> StemSeparationResponse:
    """Run Demucs 6-stem source separation on the uploaded file."""
    import tempfile

    from samplemind.core.engine.audio_engine import AudioEngine

    temp_path = Path(f"/tmp/{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    engine = AudioEngine()
    output_dir = Path(tempfile.mkdtemp(prefix="sm_stems_")) if save_stems else None

    try:
        result = await engine.separate_stems(temp_path, model=model, output_dir=output_dir)
        return StemSeparationResponse(
            source_file=file.filename or "",
            model=result.model_name,
            stems=result.stem_names,
            output_dir=str(result.output_dir) if result.output_dir else None,
            processing_time_s=result.processing_time,
            mock=result.mock,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()


# ---------------------------------------------------------------------------
# Effects Chain (P1-012) — pedalboard
# ---------------------------------------------------------------------------


class EffectsConfig(BaseModel):
    """Pedalboard effects chain configuration."""

    reverb_room_size: float = Field(0.3, ge=0.0, le=1.0)
    reverb_wet_level: float = Field(0.2, ge=0.0, le=1.0)
    compressor_threshold_db: float = Field(-20.0, le=0.0)
    compressor_ratio: float = Field(2.0, ge=1.0, le=20.0)
    eq_low_gain_db: float = Field(0.0, ge=-24.0, le=24.0)
    eq_mid_gain_db: float = Field(0.0, ge=-24.0, le=24.0)
    eq_high_gain_db: float = Field(0.0, ge=-24.0, le=24.0)
    gain_db: float = Field(0.0, ge=-60.0, le=24.0)


class EffectsResponse(BaseModel):
    """Response for effects processing endpoint."""

    source_file: str
    output_file: str
    effects_applied: List[str]
    processing_time_s: float


@router.post(
    "/effects",
    response_model=EffectsResponse,
    summary="Apply pedalboard effects chain",
    description="Apply reverb, compression, EQ, and gain to an uploaded audio file.",
    tags=["Audio Processing"],
)
async def apply_audio_effects(
    file: UploadFile = File(...),
    config: EffectsConfig = Depends(),
) -> EffectsResponse:
    """Apply a configurable pedalboard effects chain to the uploaded audio."""
    import time

    try:
        import pedalboard
        import soundfile as sf
        import numpy as np
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"pedalboard not installed: {exc}",
        )

    temp_in = Path(f"/tmp/sm_fx_in_{file.filename}")
    temp_out = Path(f"/tmp/sm_fx_out_{file.filename}")

    with open(temp_in, "wb") as f:
        f.write(await file.read())

    start = time.time()
    effects_applied: List[str] = []

    try:
        audio, sr = sf.read(str(temp_in))
        if audio.ndim == 1:
            audio = audio[:, np.newaxis]

        board = pedalboard.Pedalboard()

        if config.compressor_ratio > 1.0 or config.compressor_threshold_db < 0:
            board.append(
                pedalboard.Compressor(
                    threshold_db=config.compressor_threshold_db,
                    ratio=config.compressor_ratio,
                )
            )
            effects_applied.append("Compressor")

        # Simple EQ via HighShelfFilter + LowShelfFilter
        if config.eq_low_gain_db != 0.0:
            board.append(pedalboard.LowShelfFilter(gain_db=config.eq_low_gain_db, cutoff_frequency_hz=200))
            effects_applied.append("EQ Low Shelf")
        if config.eq_high_gain_db != 0.0:
            board.append(pedalboard.HighShelfFilter(gain_db=config.eq_high_gain_db, cutoff_frequency_hz=8000))
            effects_applied.append("EQ High Shelf")

        if config.reverb_wet_level > 0.0:
            board.append(
                pedalboard.Reverb(
                    room_size=config.reverb_room_size,
                    wet_level=config.reverb_wet_level,
                )
            )
            effects_applied.append("Reverb")

        if config.gain_db != 0.0:
            board.append(pedalboard.Gain(gain_db=config.gain_db))
            effects_applied.append("Gain")

        processed = board(audio.T, sr).T
        sf.write(str(temp_out), processed, sr)

        return EffectsResponse(
            source_file=file.filename or "",
            output_file=temp_out.name,
            effects_applied=effects_applied,
            processing_time_s=time.time() - start,
        )
    finally:
        if temp_in.exists():
            temp_in.unlink()


# ---------------------------------------------------------------------------
# MIDI Transcription (P1-015) — basic-pitch
# ---------------------------------------------------------------------------


class MidiTranscribeResponse(BaseModel):
    """Response for MIDI transcription endpoint."""

    source_file: str
    note_count: int
    pitch_range: List[int]
    midi_path: Optional[str] = None
    processing_time_s: float
    summary: str
    mock: bool = False


@router.post(
    "/transcribe-midi",
    response_model=MidiTranscribeResponse,
    summary="Transcribe audio to MIDI",
    description="Detect pitched notes in audio and return MIDI note events using basic-pitch.",
    tags=["Audio Processing"],
)
async def transcribe_audio_to_midi(
    file: UploadFile = File(...),
    onset_threshold: float = Query(0.5, ge=0.0, le=1.0),
    frame_threshold: float = Query(0.3, ge=0.0, le=1.0),
    save_midi: bool = Query(False, description="Write .mid file to disk"),
) -> MidiTranscribeResponse:
    """Transcribe pitched audio into MIDI note events via basic-pitch."""
    import tempfile

    from samplemind.core.engine.audio_engine import AudioEngine

    temp_path = Path(f"/tmp/sm_midi_{file.filename}")
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    engine = AudioEngine()
    output_dir = Path(tempfile.mkdtemp(prefix="sm_midi_")) if save_midi else None

    try:
        result = await engine.transcribe_midi(
            temp_path,
            output_dir=output_dir,
            onset_threshold=onset_threshold,
            frame_threshold=frame_threshold,
        )
        return MidiTranscribeResponse(
            source_file=file.filename or "",
            note_count=result.note_count,
            pitch_range=list(result.pitch_range),
            midi_path=str(result.midi_path) if result.midi_path else None,
            processing_time_s=result.processing_time,
            summary=result.to_summary(),
            mock=result.mock,
        )
    finally:
        if temp_path.exists():
            temp_path.unlink()
