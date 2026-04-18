"""
Transient Shaper — Audio Processing Tool

Professional transient shaping for percussive enhancement or smoothing.
Separates audio into transient (attack) and sustain (body) components,
then allows independent gain control of each.

Use cases:
  - Punch up drums by boosting transients
  - Smooth out harsh attacks on synths
  - Add snap to dull percussion samples
  - Reduce room ambience by cutting sustain
  - Creative sound design via extreme settings

Algorithm:
  1. Compute onset envelope and envelope follower
  2. Detect transient regions via adaptive thresholding
  3. Create transient/sustain masks using smooth crossfade
  4. Apply independent gain to transient and sustain portions
  5. Recombine with phase-coherent overlap-add

Usage::

    from samplemind.core.processing.transient_shaper import TransientShaper

    shaper = TransientShaper()
    result = shaper.process(y, sr, attack_gain_db=6.0, sustain_gain_db=-3.0)
    shaped_audio = result.output
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="transient")


@dataclass
class TransientAnalysis:
    """Analysis of transient characteristics."""

    transient_count: int = 0
    avg_attack_time_ms: float = 0.0
    avg_sustain_time_ms: float = 0.0
    transient_ratio: float = 0.0  # Fraction of signal that is transient
    peak_transient_db: float = -96.0
    attack_sharpness: float = 0.0  # 0 = soft, 1 = very sharp attacks


@dataclass
class TransientShaperResult:
    """Result from transient shaping."""

    output: np.ndarray  # Shaped audio output
    transient_component: np.ndarray  # Isolated transient signal
    sustain_component: np.ndarray  # Isolated sustain signal
    analysis: TransientAnalysis = field(default_factory=TransientAnalysis)
    attack_gain_db: float = 0.0
    sustain_gain_db: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata (not audio data)."""
        return {
            "attack_gain_db": self.attack_gain_db,
            "sustain_gain_db": self.sustain_gain_db,
            "output_peak": round(float(np.max(np.abs(self.output))), 4),
            "output_rms": round(
                float(np.sqrt(np.mean(self.output**2))), 6
            ),
            "analysis": {
                "transient_count": self.analysis.transient_count,
                "avg_attack_time_ms": round(
                    self.analysis.avg_attack_time_ms, 2
                ),
                "avg_sustain_time_ms": round(
                    self.analysis.avg_sustain_time_ms, 2
                ),
                "transient_ratio": round(self.analysis.transient_ratio, 4),
                "peak_transient_db": round(
                    self.analysis.peak_transient_db, 2
                ),
                "attack_sharpness": round(
                    self.analysis.attack_sharpness, 3
                ),
            },
        }


class TransientShaper:
    """
    Professional transient shaper for audio processing.

    Separates audio into transient and sustain components using envelope
    analysis and adaptive thresholding, then applies independent gain.
    """

    def __init__(
        self,
        attack_time_ms: float = 1.0,
        release_time_ms: float = 50.0,
        sensitivity: float = 0.5,
    ) -> None:
        """
        Args:
            attack_time_ms: Envelope follower attack time (ms).
                Lower = faster.
            release_time_ms: Envelope follower release time (ms).
            sensitivity: Transient detection sensitivity (0–1).
                Higher = more transients.
        """
        self.attack_time_ms = max(0.1, attack_time_ms)
        self.release_time_ms = max(1.0, release_time_ms)
        self.sensitivity = np.clip(sensitivity, 0.0, 1.0)

    def process(
        self,
        y: np.ndarray,
        sr: int,
        attack_gain_db: float = 0.0,
        sustain_gain_db: float = 0.0,
    ) -> TransientShaperResult:
        """
        Apply transient shaping to an audio signal.

        Args:
            y: Audio time-series (mono, float32).
            sr: Sample rate.
            attack_gain_db: Gain for transient portions (-24 to +24 dB).
            sustain_gain_db: Gain for sustain portions (-24 to +24 dB).

        Returns:
            TransientShaperResult with shaped audio and analysis.
        """
        # Clamp gain ranges
        attack_gain_db = float(np.clip(attack_gain_db, -24.0, 24.0))
        sustain_gain_db = float(np.clip(sustain_gain_db, -24.0, 24.0))

        # Convert gains to linear
        attack_gain = 10.0 ** (attack_gain_db / 20.0)
        sustain_gain = 10.0 ** (sustain_gain_db / 20.0)

        # Step 1: Compute envelope followers
        fast_env = self._envelope_follower(
            y, sr, attack_ms=self.attack_time_ms, release_ms=5.0
        )
        slow_env = self._envelope_follower(
            y, sr, attack_ms=10.0, release_ms=self.release_time_ms
        )

        # Step 2: Compute transient mask
        # Transient = where fast envelope exceeds slow envelope
        diff = fast_env - slow_env
        threshold = float(
            np.percentile(
                np.abs(diff), (1.0 - self.sensitivity) * 100
            )
        )
        transient_mask = np.clip(
            diff / max(threshold, 1e-9), 0.0, 1.0
        )

        # Smooth the mask to avoid clicks
        smooth_samples = max(1, int(0.002 * sr))  # 2ms smoothing
        kernel = np.hanning(smooth_samples * 2 + 1)
        kernel = kernel / kernel.sum()
        transient_mask = np.convolve(transient_mask, kernel, mode="same")
        transient_mask = np.clip(transient_mask, 0.0, 1.0)

        # Sustain mask is complement
        sustain_mask = 1.0 - transient_mask

        # Step 3: Separate components
        transient_component = y * transient_mask
        sustain_component = y * sustain_mask

        # Step 4: Apply gains and recombine
        output = (
            transient_component * attack_gain
            + sustain_component * sustain_gain
        )

        # Soft-clip to prevent harsh digital overs
        output = np.tanh(output * 0.95) / 0.95

        # Step 5: Analyze transient characteristics
        analysis = self._analyze_transients(
            y, sr, transient_mask, fast_env
        )

        return TransientShaperResult(
            output=output.astype(np.float32),
            transient_component=transient_component.astype(np.float32),
            sustain_component=sustain_component.astype(np.float32),
            analysis=analysis,
            attack_gain_db=attack_gain_db,
            sustain_gain_db=sustain_gain_db,
        )

    async def process_file(
        self,
        path: Path,
        attack_gain_db: float = 0.0,
        sustain_gain_db: float = 0.0,
        target_sr: int = 44100,
    ) -> TransientShaperResult:
        """
        Load and process an audio file asynchronously.

        Args:
            path: Path to audio file.
            attack_gain_db: Transient gain adjustment.
            sustain_gain_db: Sustain gain adjustment.
            target_sr: Target sample rate.

        Returns:
            TransientShaperResult for the file.
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR,
            self._load_and_process,
            path,
            attack_gain_db,
            sustain_gain_db,
            target_sr,
        )

    # ── Private helpers ──────────────────────────────────────────────

    def _load_and_process(
        self,
        path: Path,
        attack_gain_db: float,
        sustain_gain_db: float,
        target_sr: int,
    ) -> TransientShaperResult:
        try:
            import librosa

            y, sr = librosa.load(str(path), sr=target_sr, mono=True)
            return self.process(y, sr, attack_gain_db, sustain_gain_db)
        except Exception as exc:
            logger.error(
                "TransientShaper failed for %s: %s", path, exc
            )
            empty = np.array([], dtype=np.float32)
            return TransientShaperResult(
                output=empty,
                transient_component=empty,
                sustain_component=empty,
            )

    @staticmethod
    def _envelope_follower(
        y: np.ndarray,
        sr: int,
        attack_ms: float = 1.0,
        release_ms: float = 50.0,
    ) -> np.ndarray:
        """
        Compute an envelope follower (peak detector).

        Args:
            y: Audio signal.
            sr: Sample rate.
            attack_ms: Attack time constant (ms).
            release_ms: Release time constant (ms).

        Returns:
            Envelope signal (same length as y).
        """
        attack_coeff = 1.0 - np.exp(
            -1.0 / (attack_ms * sr / 1000.0)
        )
        release_coeff = 1.0 - np.exp(
            -1.0 / (release_ms * sr / 1000.0)
        )

        envelope = np.zeros_like(y)
        abs_y = np.abs(y)

        current = 0.0
        for i in range(len(y)):
            sample = abs_y[i]
            if sample > current:
                current += attack_coeff * (sample - current)
            else:
                current += release_coeff * (sample - current)
            envelope[i] = current

        return envelope

    @staticmethod
    def _analyze_transients(
        y: np.ndarray,
        sr: int,
        transient_mask: np.ndarray,
        fast_env: np.ndarray,
    ) -> TransientAnalysis:
        """Analyze transient characteristics from the mask."""
        # Find transient regions (contiguous mask > 0.5)
        is_transient = transient_mask > 0.5
        transitions = np.diff(is_transient.astype(int))

        # Transient starts and ends
        starts = np.where(transitions == 1)[0]
        ends = np.where(transitions == -1)[0]

        # Align starts and ends
        if len(ends) > 0 and len(starts) > 0:
            if ends[0] < starts[0]:
                ends = ends[1:]
            min_len = min(len(starts), len(ends))
            starts = starts[:min_len]
            ends = ends[:min_len]
        else:
            starts = np.array([])
            ends = np.array([])

        transient_count = len(starts)

        # Attack times
        attack_times_ms: list[float] = []
        sustain_times_ms: list[float] = []

        for s_idx, e_idx in zip(starts, ends, strict=False):
            attack_dur = (e_idx - s_idx) / sr * 1000
            attack_times_ms.append(attack_dur)

        # Sustain = gap between transient end and next start
        for i in range(len(ends) - 1):
            gap = (starts[i + 1] - ends[i]) / sr * 1000
            sustain_times_ms.append(gap)

        # Transient ratio
        transient_samples = int(np.sum(is_transient))
        transient_ratio = transient_samples / max(len(y), 1)

        # Peak transient level
        transient_signal = y * transient_mask
        peak_transient = float(np.max(np.abs(transient_signal)))
        peak_db = (
            20.0 * np.log10(peak_transient + 1e-9)
            if peak_transient > 0
            else -96.0
        )

        # Attack sharpness: how fast the envelope rises
        if len(fast_env) > 1:
            env_diff = np.diff(fast_env)
            positive = env_diff[env_diff > 0]
            sharpness = (
                float(np.percentile(positive, 95))
                if len(positive) > 0
                else 0.0
            )
            sharpness = min(1.0, sharpness * 10)  # Normalize to 0–1
        else:
            sharpness = 0.0

        return TransientAnalysis(
            transient_count=transient_count,
            avg_attack_time_ms=(
                float(np.mean(attack_times_ms))
                if attack_times_ms
                else 0.0
            ),
            avg_sustain_time_ms=(
                float(np.mean(sustain_times_ms))
                if sustain_times_ms
                else 0.0
            ),
            transient_ratio=float(transient_ratio),
            peak_transient_db=float(peak_db),
            attack_sharpness=float(sharpness),
        )


# ── Module exports ────────────────────────────────────────────────────

__all__ = [
    "TransientShaper",
    "TransientShaperResult",
    "TransientAnalysis",
]
