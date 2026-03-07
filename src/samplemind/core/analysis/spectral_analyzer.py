"""
Spectral Analyzer — KP-26

Standalone spectral feature extraction with async support.
Computes MFCCs, spectral centroid/bandwidth/rolloff, spectral contrast,
zero-crossing rate, RMS energy, spectral flatness, and spectral flux.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="spectral")


@dataclass
class SpectralFeatures:
    """Full spectral feature set extracted from an audio signal."""

    # Spectral centroid (Hz)
    centroid_mean: float = 0.0
    centroid_std: float = 0.0

    # Spectral bandwidth (Hz)
    bandwidth_mean: float = 0.0
    bandwidth_std: float = 0.0

    # Spectral rolloff (Hz - frequency below which 85% of energy is concentrated)
    rolloff_mean: float = 0.0
    rolloff_std: float = 0.0

    # Zero-crossing rate
    zcr_mean: float = 0.0
    zcr_std: float = 0.0

    # RMS energy
    rms_mean: float = 0.0
    rms_std: float = 0.0

    # Spectral flatness (0=tonal, 1=noise-like)
    flatness_mean: float = 0.0

    # Spectral contrast per sub-band (6 bands + 1 valley)
    contrast_mean: list[float] = field(default_factory=lambda: [0.0] * 7)

    # MFCCs — 20 coefficients, mean and std
    mfcc_mean: list[float] = field(default_factory=lambda: [0.0] * 20)
    mfcc_std: list[float] = field(default_factory=lambda: [0.0] * 20)

    # Spectral flux (frame-to-frame spectral change)
    spectral_flux: float = 0.0

    # Analysis metadata
    sample_rate: int = 22050
    duration: float = 0.0
    n_fft: int = 2048
    hop_length: int = 512


class SpectralAnalyzer:
    """
    Extracts spectral features from audio signals using librosa.

    Usage::

        analyzer = SpectralAnalyzer()
        features = analyzer.analyze(y, sr)
        # or async:
        features = await analyzer.analyze_file(Path("sample.wav"))
    """

    def __init__(
        self,
        n_fft: int = 2048,
        hop_length: int = 512,
        n_mfcc: int = 20,
    ) -> None:
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mfcc = n_mfcc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, y: np.ndarray, sr: int) -> SpectralFeatures:
        """
        Compute spectral features from a loaded audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate in Hz

        Returns:
            SpectralFeatures dataclass populated with computed values
        """
        try:
            import librosa  # lazy import — heavy dependency
        except ImportError:
            logger.warning("librosa not available — returning mock SpectralFeatures")
            return self._mock_features(sr, len(y) / max(sr, 1))

        features = SpectralFeatures(
            sample_rate=sr,
            duration=float(len(y)) / sr,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
        )

        # --- Short-time Fourier Transform -----------------------------------
        D = np.abs(librosa.stft(y, n_fft=self.n_fft, hop_length=self.hop_length))

        # --- Spectral centroid ----------------------------------------------
        centroid = librosa.feature.spectral_centroid(S=D, sr=sr)[0]
        features.centroid_mean = float(np.mean(centroid))
        features.centroid_std = float(np.std(centroid))

        # --- Spectral bandwidth ---------------------------------------------
        bandwidth = librosa.feature.spectral_bandwidth(S=D, sr=sr)[0]
        features.bandwidth_mean = float(np.mean(bandwidth))
        features.bandwidth_std = float(np.std(bandwidth))

        # --- Spectral rolloff -----------------------------------------------
        rolloff = librosa.feature.spectral_rolloff(S=D, sr=sr)[0]
        features.rolloff_mean = float(np.mean(rolloff))
        features.rolloff_std = float(np.std(rolloff))

        # --- Spectral flatness ----------------------------------------------
        flatness = librosa.feature.spectral_flatness(S=D)[0]
        features.flatness_mean = float(np.mean(flatness))

        # --- Spectral contrast (6 sub-bands) --------------------------------
        contrast = librosa.feature.spectral_contrast(S=D, sr=sr)
        features.contrast_mean = [float(np.mean(contrast[b])) for b in range(contrast.shape[0])]

        # --- Zero-crossing rate ---------------------------------------------
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
        features.zcr_mean = float(np.mean(zcr))
        features.zcr_std = float(np.std(zcr))

        # --- RMS energy -----------------------------------------------------
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        features.rms_mean = float(np.mean(rms))
        features.rms_std = float(np.std(rms))

        # --- MFCCs ----------------------------------------------------------
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length)
        features.mfcc_mean = [float(v) for v in np.mean(mfccs, axis=1)]
        features.mfcc_std = [float(v) for v in np.std(mfccs, axis=1)]

        # --- Spectral flux (L1 difference of consecutive magnitude frames) --
        if D.shape[1] > 1:
            flux = np.sum(np.diff(D, axis=1) ** 2, axis=0)
            features.spectral_flux = float(np.mean(flux))

        return features

    async def analyze_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> SpectralFeatures:
        """
        Load and analyze an audio file asynchronously (offloads to thread pool).

        Args:
            path: Path to the audio file
            sample_rate: Target sample rate for loading

        Returns:
            SpectralFeatures for the file
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_analyze, path, sample_rate
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_and_analyze(self, path: Path, sample_rate: int) -> SpectralFeatures:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.analyze(y, sr)
        except Exception as exc:
            logger.error(f"SpectralAnalyzer failed for {path}: {exc}")
            return self._mock_features(sample_rate, 0.0)

    @staticmethod
    def _mock_features(sr: int, duration: float) -> SpectralFeatures:
        """Return a zero-filled fallback when analysis is unavailable."""
        return SpectralFeatures(sample_rate=sr, duration=duration)
