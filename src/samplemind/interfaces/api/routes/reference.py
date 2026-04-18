"""
Mix Reference Analyzer — Compare your mix against a reference track.

Endpoints:
  POST /api/v1/reference/compare — Upload two files, get comparative analysis
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reference", tags=["reference"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class CompareRequest(BaseModel):
    mix_path: str = Field(..., description="Path to your mix")
    reference_path: str = Field(..., description="Path to reference track")


class FrequencyBand(BaseModel):
    name: str
    range_hz: str
    mix_db: float
    reference_db: float
    difference_db: float


class CompareResponse(BaseModel):
    mix_lufs: float
    reference_lufs: float
    lufs_difference: float
    dynamic_range_mix: float
    dynamic_range_reference: float
    frequency_bands: list[FrequencyBand]
    ai_recommendations: list[str]
    overall_score: float = Field(..., ge=0.0, le=100.0)
    model_used: str = "rules+litellm"


# ── Audio analysis helpers ────────────────────────────────────────────────────


def _analyze_frequency_bands(y: Any, sr: int) -> dict[str, float]:
    """Compute average energy per frequency band."""
    import numpy as np

    try:
        import librosa

        S = np.abs(librosa.stft(y, n_fft=4096))
        freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)

        bands = {
            "sub": (20, 60),
            "bass": (60, 250),
            "low_mid": (250, 500),
            "mid": (500, 2000),
            "high_mid": (2000, 6000),
            "high": (6000, 12000),
            "air": (12000, 20000),
        }

        result: dict[str, float] = {}
        for band_name, (lo, hi) in bands.items():
            mask = (freqs >= lo) & (freqs < hi)
            if mask.any():
                band_energy = np.mean(S[mask, :])
                result[band_name] = float(20 * np.log10(max(band_energy, 1e-10)))
            else:
                result[band_name] = -60.0

        return result
    except ImportError:
        return {}


def _compute_lufs(y: Any, sr: int) -> float:
    """Compute integrated LUFS loudness."""
    import numpy as np

    try:
        import pyloudnorm as pyln

        meter = pyln.Meter(sr)
        if y.ndim == 1:
            y_stereo = np.stack([y, y], axis=-1)
        else:
            y_stereo = y.T if y.shape[0] < y.shape[1] else y
        return float(meter.integrated_loudness(y_stereo))
    except ImportError:
        # Fallback: approximate RMS-based loudness
        rms = float(np.sqrt(np.mean(y**2)))
        return float(20 * np.log10(max(rms, 1e-10)))


def _compute_dynamic_range(y: Any, sr: int) -> float:
    """Compute dynamic range in dB."""
    import numpy as np

    try:
        import librosa

        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
        rms_db = 20 * np.log10(np.maximum(rms, 1e-10))
        return float(np.percentile(rms_db, 95) - np.percentile(rms_db, 5))
    except ImportError:
        return 0.0


# ── Endpoint ──────────────────────────────────────────────────────────────────


@router.post("/compare")
@rate_limit("10/minute")
async def compare_mix(request: Request, body: CompareRequest) -> CompareResponse:
    """
    Compare your mix against a reference track.
    Returns frequency analysis, LUFS, dynamic range, and AI recommendations.
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path

    mix_path = Path(body.mix_path)
    ref_path = Path(body.reference_path)

    if not mix_path.exists():
        raise HTTPException(status_code=404, detail=f"Mix file not found: {body.mix_path}")
    if not ref_path.exists():
        raise HTTPException(status_code=404, detail=f"Reference file not found: {body.reference_path}")

    # Load audio in thread pool
    loop = asyncio.get_event_loop()

    def _load_and_analyze() -> dict[str, Any]:
        import librosa

        y_mix, sr_mix = librosa.load(str(mix_path), sr=44100, mono=True)
        y_ref, sr_ref = librosa.load(str(ref_path), sr=44100, mono=True)

        mix_bands = _analyze_frequency_bands(y_mix, sr_mix)
        ref_bands = _analyze_frequency_bands(y_ref, sr_ref)
        mix_lufs = _compute_lufs(y_mix, sr_mix)
        ref_lufs = _compute_lufs(y_ref, sr_ref)
        mix_dr = _compute_dynamic_range(y_mix, sr_mix)
        ref_dr = _compute_dynamic_range(y_ref, sr_ref)

        return {
            "mix_bands": mix_bands,
            "ref_bands": ref_bands,
            "mix_lufs": mix_lufs,
            "ref_lufs": ref_lufs,
            "mix_dr": mix_dr,
            "ref_dr": ref_dr,
        }

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            analysis = await loop.run_in_executor(pool, _load_and_analyze)
    except Exception as exc:
        logger.error("Audio loading failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {exc}")

    # Build frequency band comparison
    band_names = {
        "sub": "Sub (20-60Hz)",
        "bass": "Bass (60-250Hz)",
        "low_mid": "Low-Mid (250-500Hz)",
        "mid": "Mid (500-2kHz)",
        "high_mid": "High-Mid (2-6kHz)",
        "high": "High (6-12kHz)",
        "air": "Air (12-20kHz)",
    }

    frequency_bands = []
    for band_key, label in band_names.items():
        mix_db = analysis["mix_bands"].get(band_key, -60.0)
        ref_db = analysis["ref_bands"].get(band_key, -60.0)
        frequency_bands.append(
            FrequencyBand(
                name=label,
                range_hz=band_key,
                mix_db=round(mix_db, 1),
                reference_db=round(ref_db, 1),
                difference_db=round(mix_db - ref_db, 1),
            )
        )

    # Generate AI recommendations
    ai_recs = await _generate_ai_recommendations(
        analysis, frequency_bands
    )

    # Score: 100 = perfect match, penalize for LUFS diff + frequency deviations
    lufs_penalty = min(abs(analysis["mix_lufs"] - analysis["ref_lufs"]) * 5, 30)
    freq_penalty = min(
        sum(abs(b.difference_db) for b in frequency_bands) / len(frequency_bands) * 3,
        40,
    )
    dr_penalty = min(abs(analysis["mix_dr"] - analysis["ref_dr"]) * 2, 20)
    score = max(100 - lufs_penalty - freq_penalty - dr_penalty, 0)

    return CompareResponse(
        mix_lufs=round(analysis["mix_lufs"], 1),
        reference_lufs=round(analysis["ref_lufs"], 1),
        lufs_difference=round(analysis["mix_lufs"] - analysis["ref_lufs"], 1),
        dynamic_range_mix=round(analysis["mix_dr"], 1),
        dynamic_range_reference=round(analysis["ref_dr"], 1),
        frequency_bands=frequency_bands,
        ai_recommendations=ai_recs,
        overall_score=round(score, 1),
    )


async def _generate_ai_recommendations(
    analysis: dict[str, Any], bands: list[FrequencyBand]
) -> list[str]:
    """Generate AI mixing recommendations based on comparison data."""
    try:
        from samplemind.integrations.litellm_router import chat_completion

        band_summary = "\n".join(
            f"  {b.name}: mix={b.mix_db}dB, ref={b.reference_db}dB, diff={b.difference_db}dB"
            for b in bands
        )

        prompt = f"""As a mastering engineer, analyze this mix vs reference comparison:

LUFS: mix={analysis['mix_lufs']:.1f}, ref={analysis['ref_lufs']:.1f}
Dynamic Range: mix={analysis['mix_dr']:.1f}dB, ref={analysis['ref_dr']:.1f}dB

Frequency Band Comparison:
{band_summary}

Give exactly 5 specific, actionable mixing recommendations. Be concise (1 sentence each).
Format as a JSON array of strings."""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            prefer_fast=True,
            max_tokens=512,
        )

        import json

        content = response.choices[0].message.content
        try:
            recs = json.loads(content)
            if isinstance(recs, list):
                return recs[:5]
        except json.JSONDecodeError:
            pass

        return [line.strip("- ") for line in content.strip().split("\n") if line.strip()][:5]

    except Exception as exc:
        logger.warning("AI recommendations failed: %s", exc)
        # Rule-based fallback
        recs = []
        lufs_diff = analysis["mix_lufs"] - analysis["ref_lufs"]
        if lufs_diff > 2:
            recs.append(f"Your mix is {lufs_diff:.1f} LUFS louder than reference. Consider reducing the limiter ceiling.")
        elif lufs_diff < -2:
            recs.append(f"Your mix is {abs(lufs_diff):.1f} LUFS quieter than reference. Increase overall gain or limiter threshold.")

        for b in bands:
            if b.difference_db > 3:
                recs.append(f"Your {b.name} is {b.difference_db:.1f}dB louder than reference. Cut to match.")
            elif b.difference_db < -3:
                recs.append(f"Your {b.name} is {abs(b.difference_db):.1f}dB quieter than reference. Boost to match.")

        return recs[:5] if recs else ["Mix closely matches reference profile."]
