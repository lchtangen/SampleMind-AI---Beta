"""
Audio Format Converter — KP-36

Converts audio files between formats with optional quality settings.

Primary backend: ``pedalboard.io.AudioFile`` (Spotify pedalboard)
Fallback backend: ``pydub`` (for AIFF, M4A, OPUS, OGG and other formats
                  that require ffmpeg)

Supported output formats: wav, flac, mp3, ogg, aiff, m4a, opus
"""

from __future__ import annotations

import logging
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="convert")

# Quality presets for lossy formats
QUALITY_PRESETS: dict[str, dict[str, int]] = {
    "low": {"mp3": 128, "ogg": 96, "opus": 64, "m4a": 128},
    "medium": {"mp3": 192, "ogg": 160, "opus": 128, "m4a": 192},
    "high": {"mp3": 320, "ogg": 256, "opus": 256, "m4a": 256},
    "lossless": {"flac": 0, "wav": 0, "aiff": 0},
}

# Formats natively supported by pedalboard.io
_PEDALBOARD_FORMATS = {"wav", "flac", "mp3", "ogg"}

# Formats that require pydub + ffmpeg
_PYDUB_FORMATS = {"aiff", "m4a", "opus", "aac"}


@dataclass
class ConversionResult:
    """Result of an audio format conversion."""

    source_path: str
    destination_path: str
    success: bool
    backend_used: str = "unknown"  # pedalboard | pydub | copy
    error: str | None = None
    source_format: str = ""
    target_format: str = ""
    file_size_bytes: int = 0


class AudioFormatConverter:
    """
    Converts audio files between formats.

    Tries ``pedalboard.io`` first (higher quality, no ffmpeg dependency),
    falls back to ``pydub`` for AIFF, M4A, and OPUS which pedalboard does
    not support.

    Usage::

        converter = AudioFormatConverter()
        result = converter.convert(Path("track.wav"), Path("track.flac"))
        result = await converter.convert_async(Path("track.wav"), Path("track.mp3"))
    """

    def __init__(self, default_sample_rate: int = 44100) -> None:
        self.default_sample_rate = default_sample_rate

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def convert(
        self,
        source: Path,
        destination: Path,
        quality: str = "high",
        sample_rate: int | None = None,
        normalize_loudness: bool = False,
    ) -> ConversionResult:
        """
        Convert an audio file to a different format.

        Args:
            source: Input file path
            destination: Output file path (extension determines format)
            quality: \"low\" | \"medium\" | \"high\" | \"lossless\"
            sample_rate: Override output sample rate (None = preserve source SR)
            normalize_loudness: Apply −14 LUFS normalization before writing

        Returns:
            ConversionResult describing the outcome
        """
        source = Path(source).expanduser().resolve()
        destination = Path(destination).expanduser().resolve()

        src_fmt = source.suffix.lstrip(".").lower()
        dst_fmt = destination.suffix.lstrip(".").lower()

        result = ConversionResult(
            source_path=str(source),
            destination_path=str(destination),
            success=False,
            source_format=src_fmt,
            target_format=dst_fmt,
        )

        if not source.exists():
            result.error = f"Source file not found: {source}"
            return result

        # Same format — just copy
        if src_fmt == dst_fmt and not normalize_loudness:
            try:
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                result.success = True
                result.backend_used = "copy"
                result.file_size_bytes = destination.stat().st_size
                return result
            except Exception as exc:
                result.error = str(exc)
                return result

        # Determine target SR
        target_sr = sample_rate or self.default_sample_rate

        # Choose backend
        if dst_fmt in _PYDUB_FORMATS or src_fmt in _PYDUB_FORMATS:
            return self._convert_pydub(source, destination, result, quality, target_sr, normalize_loudness)

        # Primary: pedalboard
        pedalboard_result = self._convert_pedalboard(
            source, destination, result, quality, target_sr, normalize_loudness
        )
        if pedalboard_result.success:
            return pedalboard_result

        # Fallback: pydub
        logger.info(f"pedalboard failed, trying pydub for {source.name}")
        return self._convert_pydub(source, destination, result, quality, target_sr, normalize_loudness)

    async def convert_async(
        self,
        source: Path,
        destination: Path,
        quality: str = "high",
        sample_rate: int | None = None,
        normalize_loudness: bool = False,
    ) -> ConversionResult:
        """
        Async wrapper around convert(). Offloads to thread pool.

        Args:
            source: Input file path
            destination: Output file path
            quality: Quality preset
            sample_rate: Override output sample rate
            normalize_loudness: Apply loudness normalization

        Returns:
            ConversionResult
        """
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR,
            lambda: self.convert(source, destination, quality, sample_rate, normalize_loudness),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _convert_pedalboard(
        source: Path,
        destination: Path,
        result: ConversionResult,
        quality: str,
        target_sr: int,
        normalize_loudness: bool,
    ) -> ConversionResult:
        """Convert using pedalboard.io."""
        try:
            from pedalboard.io import AudioFile

            destination.parent.mkdir(parents=True, exist_ok=True)

            with AudioFile(str(source)) as reader:
                sr = reader.samplerate
                audio = reader.read(reader.frames)  # shape: (channels, frames)

            if normalize_loudness:
                audio = _normalize_to_lufs(audio, sr, target_lufs=-14.0)

            dst_fmt = result.target_format
            quality_kbps = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["high"]).get(
                dst_fmt, 320
            )

            write_kwargs: dict = {"samplerate": target_sr}
            if dst_fmt == "mp3":
                write_kwargs["quality"] = quality_kbps / 320.0  # pedalboard uses 0–1
            elif dst_fmt == "ogg":
                write_kwargs["quality"] = quality_kbps / 320.0

            with AudioFile(str(destination), "w", **write_kwargs) as writer:
                writer.write(audio)

            result.success = True
            result.backend_used = "pedalboard"
            result.file_size_bytes = destination.stat().st_size
            return result

        except Exception as exc:
            logger.debug(f"pedalboard conversion failed: {exc}")
            result.error = str(exc)
            return result

    @staticmethod
    def _convert_pydub(
        source: Path,
        destination: Path,
        result: ConversionResult,
        quality: str,
        target_sr: int,
        normalize_loudness: bool,
    ) -> ConversionResult:
        """Convert using pydub (requires ffmpeg on PATH)."""
        try:
            from pydub import AudioSegment

            destination.parent.mkdir(parents=True, exist_ok=True)

            seg = AudioSegment.from_file(str(source))
            seg = seg.set_frame_rate(target_sr)

            if normalize_loudness:
                # pydub dBFS normalization (approximate)
                target_dBFS = -14.0
                change_dBFS = target_dBFS - seg.dBFS
                seg = seg.apply_gain(change_dBFS)

            dst_fmt = result.target_format
            export_kwargs: dict = {"format": dst_fmt}

            bitrate_map = QUALITY_PRESETS.get(quality, QUALITY_PRESETS["high"])
            if dst_fmt in bitrate_map and bitrate_map[dst_fmt] > 0:
                export_kwargs["bitrate"] = f"{bitrate_map[dst_fmt]}k"

            seg.export(str(destination), **export_kwargs)

            result.success = True
            result.backend_used = "pydub"
            result.error = None
            result.file_size_bytes = destination.stat().st_size
            return result

        except Exception as exc:
            logger.error(f"pydub conversion failed for {source}: {exc}")
            result.error = str(exc)
            return result


# ---------------------------------------------------------------------------
# Loudness normalization helper
# ---------------------------------------------------------------------------


def _normalize_to_lufs(
    audio: np.ndarray,
    sr: int,
    target_lufs: float = -14.0,
) -> np.ndarray:
    """
    Normalize audio to target LUFS using pyloudnorm if available,
    otherwise applies simple RMS gain.

    Args:
        audio: (channels, frames) float array
        sr: Sample rate
        target_lufs: Target integrated loudness

    Returns:
        Gain-adjusted audio array (same shape)
    """
    import numpy as np

    try:
        import pyloudnorm as pyln

        meter = pyln.Meter(sr)
        mono = audio[0] if audio.ndim > 1 else audio
        current = meter.integrated_loudness(mono)
        if np.isfinite(current):
            gain_db = target_lufs - current
            gain_linear = 10.0 ** (gain_db / 20.0)
            return (audio * gain_linear).clip(-1.0, 1.0).astype(audio.dtype)
    except (ImportError, Exception):
        pass

    # RMS fallback
    rms = float(np.sqrt(np.mean(audio ** 2)))
    if rms > 1e-9:
        target_rms = 10.0 ** (target_lufs / 20.0)
        gain = target_rms / rms
        return (audio * gain).clip(-1.0, 1.0).astype(audio.dtype)

    return audio
