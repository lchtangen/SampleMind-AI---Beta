"""
LoopExtender — AI-powered audio loop extension (P4-010).

Extends a short audio loop to a target length using:
  1. Beat-aligned tiling (librosa beat tracking)
  2. Crossfade stitching at splice points to avoid clicks
  3. Optional pitch / tempo shift before tiling

The result is written to a new file alongside the original
(or to a caller-specified output path).

Usage::

    ext = LoopExtender()
    out_path = ext.extend("/path/to/4bar.wav", bars=16)
    # Returns "/path/to/4bar_extended_16bars.wav"
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# Default crossfade duration (seconds) applied at each splice point
DEFAULT_CROSSFADE_S = 0.05

# Supported output formats
_SUPPORTED_FORMATS = {".wav", ".flac", ".mp3", ".ogg"}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _detect_loop_bars(
    y: np.ndarray,
    sr: int,
    target_bars: int,
) -> tuple[int, float]:
    """
    Use librosa beat tracking to estimate beats per bar and return
    (beats_per_bar, estimated_bar_duration_s).

    Falls back to 4/4 at 120 BPM if librosa is unavailable or tracking fails.
    """
    try:
        import librosa  # type: ignore

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        if len(beat_times) >= 4:
            # Estimate bar duration from median inter-beat interval * 4
            ibi = float(np.median(np.diff(beat_times)))
            bar_duration_s = ibi * 4.0
        else:
            bar_duration_s = 60.0 / float(tempo) * 4.0

        return 4, bar_duration_s  # assume 4/4

    except Exception as exc:
        logger.debug("Beat tracking failed: %s — using 120 BPM default", exc)
        return 4, 2.0  # 120 BPM, 4/4 → 2s per bar


def _crossfade(
    seg_a: np.ndarray,
    seg_b: np.ndarray,
    crossfade_samples: int,
) -> np.ndarray:
    """
    Crossfade the tail of *seg_a* with the head of *seg_b*.

    Returns the concatenated result with a smooth splice.
    """
    if (
        crossfade_samples <= 0
        or len(seg_a) < crossfade_samples
        or len(seg_b) < crossfade_samples
    ):
        return np.concatenate([seg_a, seg_b])

    fade_out = np.linspace(1.0, 0.0, crossfade_samples, dtype=np.float32)
    fade_in = np.linspace(0.0, 1.0, crossfade_samples, dtype=np.float32)

    # Handle stereo arrays
    if seg_a.ndim == 2:
        fade_out = fade_out[:, None]
        fade_in = fade_in[:, None]

    overlap = (
        seg_a[-crossfade_samples:] * fade_out + seg_b[:crossfade_samples] * fade_in
    )
    return np.concatenate(
        [seg_a[:-crossfade_samples], overlap, seg_b[crossfade_samples:]]
    )


# ---------------------------------------------------------------------------
# LoopExtender
# ---------------------------------------------------------------------------


class LoopExtender:
    """
    Tile-and-crossfade loop extender.

    Attributes:
        crossfade_s: Crossfade duration in seconds at each splice point.
    """

    def __init__(self, crossfade_s: float = DEFAULT_CROSSFADE_S) -> None:
        self.crossfade_s = crossfade_s

    def extend(
        self,
        path: str,
        bars: int = 8,
        output_path: str | None = None,
        semitone_shift: float = 0.0,
        tempo_ratio: float = 1.0,
    ) -> str:
        """
        Extend an audio loop to *bars* bars.

        Args:
            path: Input audio file path (WAV, FLAC, MP3, OGG).
            bars: Target length in bars (default 8).
            output_path: Override output file path. If None, a path is
                derived automatically.
            semitone_shift: Pitch shift in semitones before tiling.
            tempo_ratio: Tempo stretch factor (1.0 = unchanged).

        Returns:
            Path to the output file.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ImportError: If librosa / soundfile are not installed.
        """
        in_path = Path(path)
        if not in_path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        try:
            import librosa  # type: ignore
            import soundfile as sf  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "loop_extender requires librosa and soundfile. "
                "Install with: pip install librosa soundfile"
            ) from exc

        # Load audio
        y, sr = librosa.load(str(in_path), sr=None, mono=False)
        mono = y.ndim == 1

        # Optional pitch shift
        if abs(semitone_shift) > 0.01:
            y_proc = librosa.effects.pitch_shift(
                y if mono else librosa.to_mono(y),
                sr=sr,
                n_steps=semitone_shift,
            )
            if not mono:
                # Re-apply shift per channel
                chans = [
                    librosa.effects.pitch_shift(y[c], sr=sr, n_steps=semitone_shift)
                    for c in range(y.shape[0])
                ]
                y = np.stack(chans)
            else:
                y = y_proc

        # Optional tempo stretch
        if abs(tempo_ratio - 1.0) > 0.01:
            if mono:
                y = librosa.effects.time_stretch(y, rate=tempo_ratio)
            else:
                y = np.stack(
                    [
                        librosa.effects.time_stretch(y[c], rate=tempo_ratio)
                        for c in range(y.shape[0])
                    ]
                )

        # Detect bar length
        y_mono = y if mono else librosa.to_mono(y)
        _bpb, bar_dur_s = _detect_loop_bars(y_mono, sr, bars)

        # How many times to tile the source
        source_dur_s = len(y_mono) / sr
        if source_dur_s < 0.1:
            raise ValueError("Input audio is too short to extend.")

        target_dur_s = bar_dur_s * bars
        n_tiles = max(1, int(np.ceil(target_dur_s / source_dur_s)))
        target_samples = int(target_dur_s * sr)
        crossfade_samples = int(self.crossfade_s * sr)

        # Tile with crossfade
        if mono:
            tiled = y.copy()
            for _ in range(n_tiles - 1):
                tiled = _crossfade(tiled, y, crossfade_samples)
            result = tiled[:target_samples]
        else:
            # Process each channel
            channels = []
            for c in range(y.shape[0]):
                ch = y[c].copy()
                for _ in range(n_tiles - 1):
                    ch = _crossfade(ch, y[c], crossfade_samples)
                channels.append(ch[:target_samples])
            result = np.stack(channels)

        # Normalise to -1 dBFS
        peak = np.max(np.abs(result))
        if peak > 1e-6:
            result = result * (10 ** (-1 / 20)) / peak

        # Determine output path
        if output_path is None:
            stem = in_path.stem
            suffix = in_path.suffix if in_path.suffix in _SUPPORTED_FORMATS else ".wav"
            output_path = str(in_path.parent / f"{stem}_extended_{bars}bars{suffix}")

        # Write output
        result_write = (
            result.T if not mono else result
        )  # soundfile: (samples, channels)
        sf.write(output_path, result_write, sr, subtype="PCM_24")
        logger.info(
            "LoopExtender: %s → %s (%.1fs, %d bars)",
            in_path.name,
            Path(output_path).name,
            target_dur_s,
            bars,
        )
        return output_path

    def extend_to_seconds(
        self,
        path: str,
        target_seconds: float,
        output_path: str | None = None,
    ) -> str:
        """
        Convenience method: extend loop to a target duration in seconds.

        Args:
            path: Input audio path.
            target_seconds: Desired output length.
            output_path: Optional output path override.

        Returns:
            Path to the output file.
        """
        try:
            import librosa  # type: ignore

            y, sr = librosa.load(path, sr=None, mono=True, duration=30.0)
            _bpb, bar_dur_s = _detect_loop_bars(y, sr, 8)
            target_bars = max(1, int(np.ceil(target_seconds / bar_dur_s)))
        except Exception:
            target_bars = max(1, int(np.ceil(target_seconds / 2.0)))  # 120 BPM default

        return self.extend(path, bars=target_bars, output_path=output_path)
