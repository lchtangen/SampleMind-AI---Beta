"""
Style Transfer — SampleMind Phase 16

Applies the sonic "style" of a reference track to a target sample by:
  1. Separating the reference with demucs (drums / bass / melody / other)
  2. Time-stretching each stem to match target BPM (librosa PSOLA)
  3. Pitch-shifting each stem to match target key (librosa phase vocoder)
  4. Recombining stems with optional mix controls

Degrade gracefully:
  - demucs unavailable → skip separation, work on full reference mix
  - librosa unavailable → output unmodified target
  - numpy unavailable → output unmodified target

Configuration (env vars):
    STYLE_TRANSFER_OUTPUT_DIR — Where outputs are saved
                                (default: ~/.samplemind/generated/style_transfer)
    DEMUCS_MODEL              — demucs model name (default: htdemucs)

Usage::

    from samplemind.ai.generation.style_transfer import StyleTransferService

    svc = StyleTransferService()
    result = await svc.transfer(
        reference_path="/path/to/ref.wav",
        target_path="/path/to/sample.wav",
        target_bpm=140,
        target_key="Am",
    )
    print(result.output_path)

CLI::
    samplemind generate style-transfer --source ref.wav --target sample.wav --bpm 140
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

STYLE_TRANSFER_OUTPUT_DIR = Path(
    os.getenv(
        "STYLE_TRANSFER_OUTPUT_DIR",
        str(Path.home() / ".samplemind" / "generated" / "style_transfer"),
    )
)
DEMUCS_MODEL = os.getenv("DEMUCS_MODEL", "htdemucs")

# Camelot Wheel semitone offsets from C for key transposition
_KEY_SEMITONES: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    # Minor variants (same root note for transposition)
    "Cm": 0, "C#m": 1, "Dm": 2, "D#m": 3, "Ebm": 3,
    "Em": 4, "Fm": 5, "F#m": 6, "Gm": 7, "G#m": 8,
    "Am": 9, "A#m": 10, "Bbm": 10, "Bm": 11,
}


@dataclass
class StyleTransferResult:
    """Result from a style transfer operation."""
    output_path: str
    reference_path: str
    target_path: str
    target_bpm: Optional[int]
    target_key: Optional[str]
    stems_used: list[str]
    processing_time_s: float
    warnings: list[str] = field(default_factory=list)


class StyleTransferService:
    """
    Applies BPM/key style from a reference track to a target sample.

    Uses demucs for stem separation and librosa for time-stretch/pitch-shift.
    Falls back gracefully when dependencies are unavailable.
    """

    def __init__(self) -> None:
        STYLE_TRANSFER_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    async def transfer(
        self,
        reference_path: str,
        target_path: str,
        target_bpm: Optional[int] = None,
        target_key: Optional[str] = None,
        stems: list[str] = ("drums", "bass", "other"),
        stem_gains: Optional[dict[str, float]] = None,
        output_filename: Optional[str] = None,
    ) -> StyleTransferResult:
        """
        Apply style transfer from reference to target.

        Args:
            reference_path: Path to reference audio (the style source).
            target_path: Path to the sample being transformed.
            target_bpm: Target BPM; if None, no time-stretch applied.
            target_key: Target key (e.g. "Am"); if None, no pitch-shift applied.
            stems: Which demucs stems to include in the output mix.
            stem_gains: Per-stem volume multipliers (e.g. {"drums": 1.2, "bass": 0.8}).
            output_filename: Override output file name (without extension).

        Returns:
            StyleTransferResult with output_path and processing metadata.
        """
        start = time.perf_counter()
        warnings: list[str] = []
        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            self._process,
            reference_path,
            target_path,
            target_bpm,
            target_key,
            list(stems),
            stem_gains or {},
            output_filename,
            warnings,
        )

        elapsed = time.perf_counter() - start
        logger.info("Style transfer complete in %.2fs: %s", elapsed, result)

        return StyleTransferResult(
            output_path=result,
            reference_path=reference_path,
            target_path=target_path,
            target_bpm=target_bpm,
            target_key=target_key,
            stems_used=list(stems),
            processing_time_s=round(elapsed, 3),
            warnings=warnings,
        )

    # ── Blocking processing (runs in thread executor) ─────────────────────────

    def _process(
        self,
        reference_path: str,
        target_path: str,
        target_bpm: Optional[int],
        target_key: Optional[str],
        stems: list[str],
        stem_gains: dict[str, float],
        output_filename: Optional[str],
        warnings: list[str],
    ) -> str:
        try:
            import numpy as np
        except ImportError:
            warnings.append("numpy not available — returning original target")
            return target_path

        try:
            import librosa
            import soundfile as sf
        except ImportError:
            warnings.append("librosa/soundfile not available — returning original target")
            return target_path

        # ── Load reference ────────────────────────────────────────────────────
        ref_audio, ref_sr = librosa.load(reference_path, sr=None, mono=False)
        if ref_audio.ndim == 1:
            ref_audio = ref_audio[np.newaxis, :]  # (1, samples)

        # ── Separate reference into stems ─────────────────────────────────────
        separated = self._separate_stems(ref_audio, ref_sr, stems, warnings)

        # ── Detect reference BPM for time-stretch ratio ───────────────────────
        ref_mono = np.mean(ref_audio, axis=0)
        ref_bpm, _ = librosa.beat.beat_track(y=ref_mono, sr=ref_sr)
        ref_bpm = float(ref_bpm) if ref_bpm else None

        # ── Time-stretch separated stems ──────────────────────────────────────
        if target_bpm and ref_bpm and abs(ref_bpm - target_bpm) > 1.0:
            rate = target_bpm / ref_bpm
            stretched = {}
            for stem_name, stem_audio in separated.items():
                mono = np.mean(stem_audio, axis=0)
                stretched[stem_name] = librosa.effects.time_stretch(mono, rate=rate)
        else:
            stretched = {k: np.mean(v, axis=0) for k, v in separated.items()}

        # ── Pitch-shift to target key ─────────────────────────────────────────
        if target_key:
            ref_key = _detect_key(ref_mono, ref_sr)
            n_steps = _semitone_shift(ref_key, target_key)
            if n_steps != 0:
                shifted = {}
                for stem_name, stem_audio in stretched.items():
                    shifted[stem_name] = librosa.effects.pitch_shift(
                        stem_audio, sr=ref_sr, n_steps=n_steps
                    )
                stretched = shifted

        # ── Mix stems ─────────────────────────────────────────────────────────
        if not stretched:
            warnings.append("No stems to mix — returning original target")
            return target_path

        # Align lengths to shortest stem
        min_len = min(a.shape[-1] for a in stretched.values())
        mixed = np.zeros(min_len)
        for stem_name, stem_audio in stretched.items():
            gain = stem_gains.get(stem_name, 1.0)
            mixed += stem_audio[:min_len] * gain

        # Normalize to prevent clipping
        peak = np.max(np.abs(mixed))
        if peak > 0.98:
            mixed = mixed * (0.98 / peak)

        # ── Write output ──────────────────────────────────────────────────────
        ref_stem = Path(reference_path).stem
        tgt_stem = Path(target_path).stem
        fname = output_filename or f"st_{tgt_stem}_from_{ref_stem}_{int(time.time())}"
        out_path = STYLE_TRANSFER_OUTPUT_DIR / f"{fname}.wav"

        sf.write(str(out_path), mixed, ref_sr)
        return str(out_path)

    def _separate_stems(
        self,
        audio: "np.ndarray",
        sr: int,
        stems: list[str],
        warnings: list[str],
    ) -> dict[str, "np.ndarray"]:
        """
        Separate audio into stems using demucs.

        Falls back to returning the full mix as 'other' if demucs unavailable.
        """
        try:
            import torch
            from demucs.pretrained import get_model  # type: ignore
            from demucs.apply import apply_model  # type: ignore

            model = get_model(DEMUCS_MODEL)
            model.eval()

            import numpy as np
            # demucs expects (batch, channels, samples) float32 tensor
            tensor = torch.from_numpy(audio.astype("float32")).unsqueeze(0)
            with torch.no_grad():
                sources = apply_model(model, tensor, device="cpu", progress=False)
            # sources: (batch, n_sources, channels, samples)
            source_names = model.sources  # e.g. ["drums", "bass", "other", "vocals"]
            result = {}
            for i, name in enumerate(source_names):
                if name in stems:
                    result[name] = sources[0, i].numpy()  # (channels, samples)
            if result:
                return result
        except ImportError:
            warnings.append(f"demucs not available — using full reference mix (install: pip install demucs)")
        except Exception as exc:
            warnings.append(f"demucs separation failed: {exc} — using full reference mix")

        # Fallback: return full mix as 'other'
        return {"other": audio}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _detect_key(mono: "np.ndarray", sr: int) -> Optional[str]:
    """Estimate key using librosa chroma features + major/minor template matching."""
    try:
        import numpy as np
        import librosa

        chroma = librosa.feature.chroma_cqt(y=mono, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        # Major/minor correlation templates
        major_template = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52,
                                    5.19, 2.39, 3.66, 2.29, 2.88])
        minor_template = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54,
                                    4.75, 3.98, 2.69, 3.34, 3.17])

        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        best_score = -1.0
        best_key = None

        for i, note in enumerate(notes):
            rotated = np.roll(chroma_mean, -i)
            maj_score = float(np.corrcoef(rotated, major_template)[0, 1])
            min_score = float(np.corrcoef(rotated, minor_template)[0, 1])
            if maj_score > best_score:
                best_score, best_key = maj_score, note
            if min_score > best_score:
                best_score, best_key = min_score, f"{note}m"

        return best_key
    except Exception:
        return None


def _semitone_shift(source_key: Optional[str], target_key: Optional[str]) -> int:
    """Calculate the semitone shift needed to transpose from source_key to target_key."""
    if not source_key or not target_key:
        return 0
    src = _KEY_SEMITONES.get(source_key, 0)
    tgt = _KEY_SEMITONES.get(target_key, 0)
    diff = (tgt - src) % 12
    # Use shortest path (max ±6 semitones)
    return diff if diff <= 6 else diff - 12


# ── Singleton ─────────────────────────────────────────────────────────────────

_service: StyleTransferService | None = None


def get_style_transfer() -> StyleTransferService:
    """Return the StyleTransferService singleton."""
    global _service
    if _service is None:
        _service = StyleTransferService()
    return _service
