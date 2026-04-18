"""
Advanced Audio Processing API Endpoints

Provides REST API endpoints for the new SampleMind audio processing tools:
  - Transient shaping
  - Spectral morphing
  - Audio DNA comparison
  - Micro-timing analysis
  - Smart auto-categorization
  - Parallel batch processing
  - Streaming chunk analysis
"""

from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/processing", tags=["Advanced Processing"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────


class MicroTimingResponse(BaseModel):
    """Response from micro-timing analysis."""

    swing: dict[str, Any] = Field(default_factory=dict)
    ghost_notes: dict[str, Any] = Field(default_factory=dict)
    pocket: dict[str, Any] = Field(default_factory=dict)
    human_feel_score: float = 0.0
    groove_dna: str = ""
    timing_rms_ms: float = 0.0
    bpm: float = 0.0
    onset_count: int = 0
    processing_time_ms: float = 0.0


class TransientShapeRequest(BaseModel):
    """Request for transient shaping."""

    attack_gain_db: float = Field(0.0, ge=-24.0, le=24.0)
    sustain_gain_db: float = Field(0.0, ge=-24.0, le=24.0)
    sensitivity: float = Field(0.5, ge=0.0, le=1.0)


class TransientShapeResponse(BaseModel):
    """Response from transient shaping."""

    analysis: dict[str, Any] = Field(default_factory=dict)
    attack_gain_db: float = 0.0
    sustain_gain_db: float = 0.0
    output_file: str = ""
    processing_time_ms: float = 0.0


class AudioDNAResponse(BaseModel):
    """Response from audio DNA extraction."""

    dimension: int = 128
    strands: dict[str, list[float]] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0.0


class DNAComparisonResponse(BaseModel):
    """Response from DNA comparison."""

    overall_similarity: float = 0.0
    most_similar_strand: str = ""
    least_similar_strand: str = ""
    similarity_profile: dict[str, float] = Field(default_factory=dict)
    description: str = ""
    processing_time_ms: float = 0.0


class CategoryResponse(BaseModel):
    """Response from auto-categorization."""

    category: str = "unknown"
    subcategory: str = "unknown"
    character: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    energy_level: str = "mid"
    duration_class: str = "unknown"
    bpm: float | None = None
    estimated_key: str | None = None
    suggested_path: str = ""
    processing_time_ms: float = 0.0


class SpectralMorphResponse(BaseModel):
    """Response from spectral morphing."""

    morph_factor: float = 0.0
    phase_mode: str = "source"
    analysis: dict[str, Any] = Field(default_factory=dict)
    output_file: str = ""
    processing_time_ms: float = 0.0


# ── Helper: save upload to temp ──────────────────────────────────────────────


async def _save_upload(file: UploadFile) -> Path:
    """Save uploaded file to a temporary location and return the path."""
    suffix = Path(file.filename or "upload.wav").suffix or ".wav"
    temp_path = Path(f"/tmp/samplemind_{uuid.uuid4().hex}{suffix}")
    content = await file.read()
    temp_path.write_bytes(content)
    return temp_path


def _cleanup(path: Path) -> None:
    """Remove temporary file if it exists."""
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/micro-timing", response_model=MicroTimingResponse)
async def analyze_micro_timing(
    file: UploadFile = File(...),
    bpm: float | None = Query(None, description="Known BPM (auto-detect if omitted)"),
) -> MicroTimingResponse:
    """
    Analyze micro-timing characteristics of an audio file.

    Returns swing profile, pocket quality, ghost notes, human feel score,
    and groove DNA fingerprint.
    """
    temp_path = await _save_upload(file)
    try:
        start = time.monotonic()

        from samplemind.core.analysis.micro_timing_analyzer import (
            MicroTimingAnalyzer,
        )

        analyzer = MicroTimingAnalyzer()
        result = await analyzer.analyze_file(temp_path, bpm=bpm)
        elapsed = (time.monotonic() - start) * 1000

        data = result.to_dict()
        return MicroTimingResponse(
            swing=data.get("swing", {}),
            ghost_notes=data.get("ghost_notes", {}),
            pocket=data.get("pocket", {}),
            human_feel_score=result.human_feel_score,
            groove_dna=result.groove_dna,
            timing_rms_ms=result.timing_rms_ms,
            bpm=result.bpm,
            onset_count=result.onset_count,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Micro-timing analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(temp_path)


@router.post("/transient-shape", response_model=TransientShapeResponse)
async def shape_transients(
    file: UploadFile = File(...),
    attack_gain_db: float = Query(0.0, ge=-24.0, le=24.0),
    sustain_gain_db: float = Query(0.0, ge=-24.0, le=24.0),
    sensitivity: float = Query(0.5, ge=0.0, le=1.0),
) -> TransientShapeResponse:
    """
    Apply transient shaping to an audio file.

    Boosts or reduces attack transients and sustain portions independently.
    Returns the shaped audio and transient analysis.
    """
    temp_path = await _save_upload(file)
    try:
        start = time.monotonic()

        from samplemind.core.processing.transient_shaper import TransientShaper

        shaper = TransientShaper(sensitivity=sensitivity)
        result = await shaper.process_file(
            temp_path,
            attack_gain_db=attack_gain_db,
            sustain_gain_db=sustain_gain_db,
        )
        elapsed = (time.monotonic() - start) * 1000

        # Save output to temp file
        output_path = temp_path.with_suffix(".shaped.wav")
        try:
            import soundfile as sf

            sf.write(str(output_path), result.output, 44100)
            output_file = str(output_path)
        except ImportError:
            output_file = ""

        data = result.to_dict()
        return TransientShapeResponse(
            analysis=data.get("analysis", {}),
            attack_gain_db=attack_gain_db,
            sustain_gain_db=sustain_gain_db,
            output_file=output_file,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Transient shaping failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(temp_path)


@router.post("/audio-dna", response_model=AudioDNAResponse)
async def extract_audio_dna(
    file: UploadFile = File(...),
) -> AudioDNAResponse:
    """
    Extract a 128-dimensional Audio DNA fingerprint from an audio file.

    The DNA captures 8 structural aspects: spectral shape, temporal envelope,
    harmonic profile, rhythmic signature, stereo image, frequency balance,
    dynamic range, and texture density.
    """
    temp_path = await _save_upload(file)
    try:
        start = time.monotonic()

        from samplemind.core.similarity.audio_dna import AudioDNAComparator

        comparator = AudioDNAComparator()
        dna = await comparator.extract_dna_file(temp_path)
        elapsed = (time.monotonic() - start) * 1000

        return AudioDNAResponse(
            dimension=len(dna.vector),
            strands={
                k: [round(float(x), 6) for x in v]
                for k, v in dna.strands.items()
            },
            metadata=dna.metadata,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Audio DNA extraction failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(temp_path)


@router.post("/audio-dna/compare", response_model=DNAComparisonResponse)
async def compare_audio_dna(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
) -> DNAComparisonResponse:
    """
    Compare two audio files using deep structural Audio DNA analysis.

    Returns overall similarity and per-strand breakdown showing exactly
    which aspects are similar or different.
    """
    temp_a = await _save_upload(file_a)
    temp_b = await _save_upload(file_b)
    try:
        start = time.monotonic()

        from samplemind.core.similarity.audio_dna import AudioDNAComparator

        comparator = AudioDNAComparator()
        comparison = await comparator.compare_files(temp_a, temp_b)
        elapsed = (time.monotonic() - start) * 1000

        return DNAComparisonResponse(
            overall_similarity=comparison.overall_similarity,
            most_similar_strand=comparison.most_similar_strand,
            least_similar_strand=comparison.least_similar_strand,
            similarity_profile=comparison.similarity_profile,
            description=comparison.description,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Audio DNA comparison failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(temp_a)
        _cleanup(temp_b)


@router.post("/categorize", response_model=CategoryResponse)
async def auto_categorize(
    file: UploadFile = File(...),
) -> CategoryResponse:
    """
    Automatically categorize an audio sample using hybrid rule + ML analysis.

    Returns category, subcategory, character tags, confidence score,
    and a suggested library organization path.
    """
    temp_path = await _save_upload(file)
    try:
        start = time.monotonic()

        from samplemind.core.library.auto_categorizer import SmartAutoCategorizer

        categorizer = SmartAutoCategorizer()
        result = await categorizer.categorize_file(temp_path)
        elapsed = (time.monotonic() - start) * 1000

        return CategoryResponse(
            category=result.category,
            subcategory=result.subcategory,
            character=result.character,
            tags=result.tags,
            confidence=result.confidence,
            energy_level=result.energy_level,
            duration_class=result.duration_class,
            bpm=result.bpm,
            estimated_key=result.estimated_key,
            suggested_path=result.suggested_path,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Auto-categorization failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(temp_path)


@router.post("/spectral-morph", response_model=SpectralMorphResponse)
async def spectral_morph(
    source: UploadFile = File(...),
    target: UploadFile = File(...),
    morph_factor: float = Query(0.5, ge=0.0, le=1.0),
    phase_mode: str = Query("source", regex="^(source|target|blend|random)$"),
) -> SpectralMorphResponse:
    """
    Blend spectral characteristics between two audio files.

    Creates a hybrid timbre by interpolating magnitude spectra in the
    STFT domain with configurable phase handling.
    """
    source_path = await _save_upload(source)
    target_path = await _save_upload(target)
    try:
        start = time.monotonic()

        from samplemind.ai.generation.spectral_morph import SpectralMorphEngine

        engine = SpectralMorphEngine()
        result = await engine.morph_files(
            source_path, target_path, morph_factor=morph_factor, phase_mode=phase_mode
        )
        elapsed = (time.monotonic() - start) * 1000

        # Save output
        output_path = source_path.with_suffix(".morphed.wav")
        try:
            import soundfile as sf

            sf.write(str(output_path), result.output, 44100)
            output_file = str(output_path)
        except ImportError:
            output_file = ""

        data = result.to_dict()
        return SpectralMorphResponse(
            morph_factor=morph_factor,
            phase_mode=phase_mode,
            analysis=data.get("analysis", {}),
            output_file=output_file,
            processing_time_ms=round(elapsed, 1),
        )
    except Exception as exc:
        logger.error("Spectral morph failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        _cleanup(source_path)
        _cleanup(target_path)
