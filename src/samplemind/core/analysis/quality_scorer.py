"""
Audio Quality Scorer — KP-30

Computes mastering-quality metrics:

- Integrated loudness (LUFS approx via RMS — lazy pyloudnorm for accuracy)
- True peak (dBFS)
- Dynamic range (LU)
- Signal-to-noise ratio estimate (dB)
- Clipping detection ratio
- Overall quality score (0–100) + label (excellent / good / fair / poor)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="quality")

# dB conversion helper
_EPSILON = 1e-12


def _db(linear: float) -> float:
    return 20.0 * float(np.log10(max(linear, _EPSILON)))


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class QualityMetrics:
    """Audio quality metrics."""

    # Loudness
    lufs_integrated: float = 0.0   # dBFS/LUFS (negative — louder is closer to 0)
    true_peak_dbfs: float = 0.0    # dBFS

    # Dynamics
    dynamic_range_lu: float = 0.0  # LU (LUFS units)
    snr_db: float = 0.0            # Estimated S/N ratio dB

    # Artifact indicators
    clipping_ratio: float = 0.0    # 0–1 fraction of clipped samples

    # Summary
    overall_score: float = 0.0     # 0–100
    quality_label: str = "unknown" # excellent | good | fair | poor

    # Metadata
    sample_rate: int = 44100
    duration: float = 0.0
    channels: int = 1


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class AudioQualityScorer:
    """
    Computes mastering-quality metrics for audio files.

    Uses *pyloudnorm* for accurate ITU-R BS.1770-4 measurements when it is
    installed; falls back to an RMS-based LUFS approximation otherwise.

    Recommended target for music production:
    - LUFS integrated: −14 to −9 LU (streaming / DJ)
    - True peak: ≤ −1 dBTP
    - Dynamic range: ≥ 6 LU
    - Clipping ratio: 0

    Usage::

        scorer = AudioQualityScorer()
        metrics = scorer.score(y, sr)
        metrics = await scorer.score_file(Path("master.wav"))
    """

    # --- Scoring thresholds ------------------------------------------------
    _EXCELLENT = 80.0
    _GOOD = 55.0
    _FAIR = 30.0

    def score(self, y: np.ndarray, sr: int) -> QualityMetrics:
        """
        Compute quality metrics from a loaded audio signal.

        Args:
            y: Audio time-series (mono, float32 or shape (channels, samples))
            sr: Sample rate

        Returns:
            QualityMetrics dataclass
        """
        # Ensure float64 for precision
        y = y.astype(np.float64)
        if y.ndim == 1:
            samples = y
            channels = 1
        else:
            samples = np.mean(y, axis=0)
            channels = y.shape[0]

        n_samples = len(samples)
        duration = float(n_samples) / max(sr, 1)
        metrics = QualityMetrics(sample_rate=sr, duration=duration, channels=channels)

        # --- LUFS (integrated loudness) -----------------------------------
        lufs = self._compute_lufs(samples, sr)
        metrics.lufs_integrated = round(lufs, 2)

        # --- True peak ----------------------------------------------------
        metrics.true_peak_dbfs = round(_db(float(np.max(np.abs(samples)))), 2)

        # --- Dynamic range ------------------------------------------------
        # LRA-inspired: difference between 95th and 10th percentile in LU
        nonzero = samples[np.abs(samples) > _EPSILON]
        if len(nonzero) > 0:
            p95 = _db(float(np.percentile(np.abs(nonzero), 95)))
            p10 = _db(float(np.percentile(np.abs(nonzero), 10)))
            metrics.dynamic_range_lu = round(max(0.0, p95 - p10), 2)
        else:
            metrics.dynamic_range_lu = 0.0

        # --- SNR estimate -------------------------------------------------
        # Signal: top 10% RMS frames; Noise: bottom 10% RMS frames
        frame_size = max(1, sr // 10)  # 100 ms frames
        rms_frames = [
            float(np.sqrt(np.mean(samples[i : i + frame_size] ** 2)))
            for i in range(0, n_samples - frame_size, frame_size)
        ]
        if len(rms_frames) >= 3:
            rms_arr = np.array(rms_frames)
            signal_level = float(np.percentile(rms_arr, 90))
            noise_level = float(np.percentile(rms_arr, 10))
            metrics.snr_db = round(_db(signal_level / max(noise_level, _EPSILON)), 2)

        # --- Clipping detection -------------------------------------------
        clip_threshold = 0.999  # digital clipping at ±1.0 (normalized)
        clipped = np.sum(np.abs(samples) >= clip_threshold)
        metrics.clipping_ratio = round(float(clipped) / max(n_samples, 1), 6)

        # --- Overall score ------------------------------------------------
        metrics.overall_score = self._compute_score(metrics)
        metrics.quality_label = self._assign_label(metrics.overall_score)

        return metrics

    async def score_file(
        self,
        path: Path,
        sample_rate: int = 44100,
    ) -> QualityMetrics:
        """
        Load and score an audio file asynchronously.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate (44100 for loudness accuracy)

        Returns:
            QualityMetrics for the file
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_score, path, sample_rate
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_score(self, path: Path, sample_rate: int) -> QualityMetrics:
        try:
            import librosa

            # Load at native SR first for true peak accuracy
            y, sr = librosa.load(path, sr=None, mono=False)
            # Resample for pyloudnorm if needed
            return self.score(y, sr)
        except Exception as exc:
            logger.error(f"AudioQualityScorer failed for {path}: {exc}")
            return QualityMetrics(sample_rate=sample_rate, duration=0.0)

    @staticmethod
    def _compute_lufs(samples: np.ndarray, sr: int) -> float:
        """
        Compute integrated loudness.

        Tries *pyloudnorm* (ITU-R BS.1770-4) first; falls back to an
        RMS-based approximation (offset of −0.691 dB applied).
        """
        try:
            import pyloudnorm as pyln

            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(samples)
            if np.isfinite(loudness):
                return float(loudness)
        except (ImportError, Exception):
            pass

        # RMS-based LUFS approximation (-0.691 dB offset per BS.1770)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        return _db(rms) - 0.691

    def _compute_score(self, m: QualityMetrics) -> float:
        """
        Weighted quality score (0–100).

        Criteria:
        - LUFS in target range (−14 to −9): +35 pts
        - True peak ≤ −1 dBFS: +20 pts
        - Dynamic range ≥ 6 LU: +25 pts
        - SNR ≥ 40 dB: +10 pts
        - No clipping: +10 pts
        """
        score = 0.0

        # LUFS score
        if -14.0 <= m.lufs_integrated <= -9.0:
            score += 35.0
        elif -18.0 <= m.lufs_integrated < -9.0 or -9.0 < m.lufs_integrated <= -6.0:
            score += 20.0
        elif m.lufs_integrated < -24.0:
            score += 5.0
        else:
            score += 12.0

        # True peak score
        if m.true_peak_dbfs <= -1.0:
            score += 20.0
        elif m.true_peak_dbfs <= 0.0:
            score += 10.0

        # Dynamic range score
        dr = m.dynamic_range_lu
        if dr >= 9.0:
            score += 25.0
        elif dr >= 6.0:
            score += 18.0
        elif dr >= 3.0:
            score += 10.0

        # SNR score
        if m.snr_db >= 50.0:
            score += 10.0
        elif m.snr_db >= 35.0:
            score += 6.0
        elif m.snr_db >= 20.0:
            score += 3.0

        # No-clipping bonus
        if m.clipping_ratio == 0.0:
            score += 10.0
        elif m.clipping_ratio < 0.0001:
            score += 5.0

        return round(min(100.0, score), 1)

    @staticmethod
    def _assign_label(score: float) -> str:
        if score >= 80.0:
            return "excellent"
        if score >= 55.0:
            return "good"
        if score >= 30.0:
            return "fair"
        return "poor"
