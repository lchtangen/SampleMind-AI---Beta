"""
Loop Detector — KP-32

Detects whether an audio file is a seamless loop and, if so, measures:

- Loop probability (0–1)
- Optimal loop length in beats and seconds
- Phase alignment quality at loop boundaries
- Suggested start/end sample positions for perfect splice
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="loop")


@dataclass
class LoopResult:
    """Loop detection result."""

    is_loop: bool = False
    loop_probability: float = 0.0  # 0–1

    # Best loop region
    loop_start_sec: float = 0.0
    loop_end_sec: float = 0.0
    loop_length_sec: float = 0.0
    loop_length_beats: float = 0.0

    # Boundary quality
    phase_alignment: float = 0.0  # 0–1 (1 = perfectly phase-aligned)
    spectral_continuity: float = 0.0  # 0–1 (1 = no audible seam)

    # BPM (required for beat-based loop length)
    bpm: float = 0.0

    # Metadata
    sample_rate: int = 22050
    duration: float = 0.0


class LoopDetector:
    """
    Detects seamless loops using onset autocorrelation.

    Algorithm::

        1. Compute onset envelope via librosa
        2. Autocorrelate the onset envelope to find repeating period
        3. Validate at the raw waveform level:
           - Phase alignment of the loop boundaries (cross-correlation)
           - Spectral continuity at the cross-fade point
        4. Assign a probability score and classify as loop / not-loop

    Usage::

        detector = LoopDetector()
        result = detector.detect(y, sr)
        result = await detector.detect_file(Path("loop.wav"))
    """

    def __init__(
        self,
        hop_length: int = 512,
        loop_prob_threshold: float = 0.65,
        boundary_window_sec: float = 0.05,
    ) -> None:
        self.hop_length = hop_length
        self.loop_prob_threshold = loop_prob_threshold
        self.boundary_window_sec = boundary_window_sec

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(self, y: np.ndarray, sr: int) -> LoopResult:
        """
        Detect loop properties in an audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate

        Returns:
            LoopResult dataclass
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available — returning mock LoopResult")
            return LoopResult(sample_rate=sr, duration=float(len(y)) / max(sr, 1))

        duration = float(len(y)) / sr
        result = LoopResult(sample_rate=sr, duration=duration)

        if duration < 0.1:
            return result

        # --- Onset envelope -----------------------------------------------
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)

        # --- BPM estimate (for beat-length validation) --------------------
        tempo_arr, _ = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
        )
        bpm = float(tempo_arr) if np.isscalar(tempo_arr) else float(tempo_arr[0])
        result.bpm = round(bpm, 2)

        # --- Autocorrelation on onset envelope ----------------------------
        ac = _autocorrelate(onset_env)

        # Find peak lags (excluding lag=0)
        min_lag = max(1, int(0.25 * sr / self.hop_length))  # ≥ 250 ms
        max_lag = len(ac) - 1

        if max_lag <= min_lag:
            return result

        ac_search = ac[min_lag:max_lag]
        if len(ac_search) == 0:
            return result

        peak_lag_offset = int(np.argmax(ac_search))
        peak_lag = peak_lag_offset + min_lag
        peak_val = float(ac[peak_lag]) / max(float(ac[0]), 1e-9)

        # --- Loop length --------------------------------------------------
        loop_frames = peak_lag
        loop_sec = loop_frames * self.hop_length / sr
        result.loop_length_sec = round(loop_sec, 4)
        result.loop_start_sec = 0.0
        result.loop_end_sec = round(loop_sec, 4)

        if bpm > 0:
            beat_sec = 60.0 / bpm
            result.loop_length_beats = round(loop_sec / beat_sec, 2)

        # --- Boundary quality: phase alignment ----------------------------
        boundary_samples = max(1, int(self.boundary_window_sec * sr))
        loop_sample = int(loop_sec * sr)

        result.phase_alignment = _compute_phase_alignment(
            y, loop_sample, boundary_samples
        )
        result.spectral_continuity = _compute_spectral_continuity(
            y, loop_sample, boundary_samples, sr
        )

        # --- Loop probability score ---------------------------------------
        result.loop_probability = round(
            float(
                np.clip(
                    0.4 * peak_val
                    + 0.3 * result.phase_alignment
                    + 0.3 * result.spectral_continuity,
                    0.0,
                    1.0,
                )
            ),
            3,
        )
        result.is_loop = result.loop_probability >= self.loop_prob_threshold

        return result

    async def detect_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> LoopResult:
        """
        Load and detect loop properties asynchronously.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate

        Returns:
            LoopResult for the file
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_detect, path, sample_rate
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_detect(self, path: Path, sample_rate: int) -> LoopResult:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.detect(y, sr)
        except Exception as exc:
            logger.error(f"LoopDetector failed for {path}: {exc}")
            return LoopResult(sample_rate=sample_rate, duration=0.0)


# ---------------------------------------------------------------------------
# Module-level helpers (stateless)
# ---------------------------------------------------------------------------


def _autocorrelate(x: np.ndarray) -> np.ndarray:
    """Normalized full autocorrelation via FFT."""
    n = len(x)
    x_centered = x - float(np.mean(x))
    # FFT-based correlation (zero-padded to avoid circular wrap)
    fft = np.fft.rfft(x_centered, n=2 * n)
    ac_full = np.fft.irfft(fft * np.conj(fft))[:n]
    # Normalize by zero-lag
    if ac_full[0] > 0:
        ac_full = ac_full / ac_full[0]
    return ac_full


def _compute_phase_alignment(
    y: np.ndarray,
    loop_sample: int,
    window: int,
) -> float:
    """
    Cross-correlation of end-of-loop and start-of-loop boundaries.

    Returns 0–1: 1 means the two boundaries are identical (perfect loop).
    """
    if loop_sample <= window or loop_sample + window > len(y):
        return 0.0

    # Tail of loop (just before wrap point)
    tail = y[loop_sample - window : loop_sample]
    # Head of loop (beginning)
    head = y[:window]

    if len(tail) != len(head) or len(head) == 0:
        return 0.0

    # Pearson correlation coefficient
    try:
        corr = float(np.corrcoef(tail, head)[0, 1])
        return float(np.clip((corr + 1.0) / 2.0, 0.0, 1.0))
    except Exception:
        return 0.0


def _compute_spectral_continuity(
    y: np.ndarray,
    loop_sample: int,
    window: int,
    sr: int,
) -> float:
    """
    Compare spectral centroids at the loop boundary vs the middle of the clip.

    Returns 0–1: higher = more spectrally consistent.
    """
    import librosa

    if loop_sample <= window or loop_sample + window > len(y):
        return 0.0

    try:
        # Boundary region
        boundary = np.concatenate(
            [
                y[loop_sample - window : loop_sample],
                y[:window],
            ]
        )
        # Mid-segment region (reference)
        mid_start = max(0, loop_sample // 2 - window)
        mid_region = y[mid_start : mid_start + 2 * window]

        c_boundary = float(
            np.mean(librosa.feature.spectral_centroid(y=boundary, sr=sr))
        )
        c_mid = float(np.mean(librosa.feature.spectral_centroid(y=mid_region, sr=sr)))

        diff_ratio = abs(c_boundary - c_mid) / max(c_mid, 1.0)
        return round(float(np.clip(1.0 - diff_ratio, 0.0, 1.0)), 3)
    except Exception:
        return 0.0
