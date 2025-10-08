"""
Audio-to-MIDI Conversion API Routes

Endpoints for converting audio files to MIDI format.
"""

from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from samplemind.core.processing.audio_to_midi import (
    AudioToMIDIConverter,
    MIDIConversionMode
)

router = APIRouter(prefix="/midi", tags=["MIDI Conversion"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MIDIConversionRequest(BaseModel):
    """Request model for MIDI conversion"""
    mode: str = "auto"  # monophonic, polyphonic, percussion, auto
    tempo: Optional[float] = None
    min_note_duration: float = 0.1


class MIDIConversionResponse(BaseModel):
    """Response model for MIDI conversion"""
    success: bool
    message: str
    midi_file: str
    mode_used: str
    detected_tempo: Optional[float]
    note_count: int
    processing_time: float


class MIDIBatchRequest(BaseModel):
    """Request model for batch MIDI conversion"""
    file_urls: List[str]
    mode: str = "auto"


class MIDIBatchResponse(BaseModel):
    """Response model for batch MIDI conversion"""
    success: bool
    total_files: int
    processed: int
    failed: int
    results: List[dict]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/convert", response_model=MIDIConversionResponse)
async def convert_to_midi(
    file: UploadFile = File(...),
    request: MIDIConversionRequest = None
):
    """
    Convert audio file to MIDI

    Supports three conversion modes:
    - **monophonic**: Single note melody lines (best for vocals, leads)
    - **polyphonic**: Multiple simultaneous notes/chords (pianos, guitars)
    - **percussion**: Drums and percussion (rhythm patterns)
    - **auto**: Automatically detect best mode

    Example:
        ```
        POST /api/v1/midi/convert
        {
            "mode": "monophonic",
            "tempo": 120.0,
            "min_note_duration": 0.1
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
            request = MIDIConversionRequest()

        # Initialize converter
        converter = AudioToMIDIConverter()

        # Convert to MIDI
        midi_path = await converter.convert_to_midi(
            tmp_path,
            mode=MIDIConversionMode(request.mode.lower()),
            tempo=request.tempo,
            min_note_duration=request.min_note_duration
        )

        processing_time = time.time() - start_time

        # Count notes in MIDI file
        import mido
        mid = mido.MidiFile(midi_path)
        note_count = sum(
            1 for track in mid.tracks
            for msg in track
            if msg.type == 'note_on'
        )

        # Detect tempo if not provided
        detected_tempo = request.tempo
        if detected_tempo is None:
            # Extract from MIDI file
            for track in mid.tracks:
                for msg in track:
                    if msg.type == 'set_tempo':
                        detected_tempo = mido.tempo2bpm(msg.tempo)
                        break

        return MIDIConversionResponse(
            success=True,
            message=f"Successfully converted to MIDI ({note_count} notes)",
            midi_file=str(midi_path),
            mode_used=request.mode,
            detected_tempo=detected_tempo,
            note_count=note_count,
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        tmp_path.unlink(missing_ok=True)


@router.post("/convert/batch", response_model=MIDIBatchResponse)
async def batch_convert_to_midi(request: MIDIBatchRequest):
    """
    Batch convert multiple audio files to MIDI

    Example:
        ```
        POST /api/v1/midi/convert/batch
        {
            "file_urls": [
                "https://example.com/melody1.mp3",
                "https://example.com/melody2.mp3"
            ],
            "mode": "monophonic"
        }
        ```
    """
    # Placeholder for batch processing
    return MIDIBatchResponse(
        success=True,
        total_files=len(request.file_urls),
        processed=0,
        failed=0,
        results=[]
    )


@router.get("/download/{file_id}")
async def download_midi(file_id: str):
    """
    Download converted MIDI file

    Args:
        file_id: Unique file identifier

    Returns:
        MIDI file
    """
    file_path = Path(f"./output/midi/{file_id}.mid")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="MIDI file not found")

    return FileResponse(
        file_path,
        media_type="audio/midi",
        filename=file_path.name
    )


@router.get("/modes")
async def list_conversion_modes():
    """
    List available MIDI conversion modes

    Returns:
        List of conversion modes with descriptions
    """
    modes = [
        {
            "name": "auto",
            "display_name": "Automatic",
            "description": "Automatically detect best conversion mode",
            "best_for": ["Unknown content", "Mixed audio"],
            "accuracy": "Good"
        },
        {
            "name": "monophonic",
            "display_name": "Monophonic",
            "description": "Single note melody line conversion",
            "best_for": ["Vocals", "Lead synths", "Flutes", "Solo instruments"],
            "accuracy": "High"
        },
        {
            "name": "polyphonic",
            "display_name": "Polyphonic",
            "description": "Multiple simultaneous notes and chords",
            "best_for": ["Piano", "Guitar chords", "String sections"],
            "accuracy": "Medium"
        },
        {
            "name": "percussion",
            "display_name": "Percussion",
            "description": "Rhythm and drum pattern extraction",
            "best_for": ["Drums", "Percussion", "Rhythmic elements"],
            "accuracy": "Medium"
        }
    ]

    return {
        "modes": modes,
        "total": len(modes)
    }


@router.post("/analyze")
async def analyze_audio_for_midi(file: UploadFile = File(...)):
    """
    Analyze audio to suggest best MIDI conversion mode

    Returns recommended mode, detected features, and conversion parameters.

    Example response:
        ```json
        {
            "recommended_mode": "monophonic",
            "confidence": 0.85,
            "detected_features": {
                "is_harmonic": true,
                "is_percussive": false,
                "polyphony_estimate": 1.2,
                "tempo": 120.0
            },
            "suggested_params": {
                "mode": "monophonic",
                "min_note_duration": 0.1
            }
        }
        ```
    """
    import tempfile
    import numpy as np
    import librosa

    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Load audio
        y, sr = librosa.load(tmp_path, sr=22050)

        # Analyze characteristics
        # Harmonic/percussive separation
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        harmonic_energy = float(np.sum(y_harmonic ** 2))
        percussive_energy = float(np.sum(y_percussive ** 2))

        # Estimate polyphony
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        active_notes = np.sum(chroma > 0.5, axis=0)
        polyphony_estimate = float(np.mean(active_notes))

        # Detect tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        detected_tempo = float(tempo.item() if hasattr(tempo, 'item') else tempo)

        # Determine recommended mode
        if percussive_energy > harmonic_energy * 2:
            recommended_mode = "percussion"
            confidence = 0.8
        elif polyphony_estimate < 1.5:
            recommended_mode = "monophonic"
            confidence = 0.85
        elif polyphony_estimate > 2.5:
            recommended_mode = "polyphonic"
            confidence = 0.75
        else:
            recommended_mode = "auto"
            confidence = 0.7

        return {
            "recommended_mode": recommended_mode,
            "confidence": confidence,
            "detected_features": {
                "is_harmonic": harmonic_energy > percussive_energy,
                "is_percussive": percussive_energy > harmonic_energy,
                "polyphony_estimate": polyphony_estimate,
                "tempo": detected_tempo
            },
            "suggested_params": {
                "mode": recommended_mode,
                "tempo": detected_tempo,
                "min_note_duration": 0.1 if recommended_mode != "percussion" else 0.05
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        tmp_path.unlink(missing_ok=True)
