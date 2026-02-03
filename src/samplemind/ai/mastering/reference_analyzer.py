"""Reference track analysis for mastering parameter extraction."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MasteringProfile:
    """Reference track mastering profile."""

    target_lufs: float  # Loudness level (-23 to -5 LUFS typical)
    dynamic_range: float  # DR in dB
    spectral_balance: np.ndarray  # EQ curve (31-band ISO 1/3 octave)
    stereo_width: float  # Stereo imaging width (0.0-1.0)
    compression_ratio: float  # Estimated compression ratio
    peak_limit: float  # Peak ceiling (typically -0.3 to -0.1)
    low_end_boost: float  # Bass boost amount (dB)
    high_end_boost: float  # Treble boost amount (dB)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReferenceAnalyzer:
    """Analyze reference tracks to extract mastering parameters."""

    def __init__(self) -> None:
        """Initialize reference analyzer."""
        self.sample_rate = 44100

    def analyze_reference(
        self,
        reference_path: Path,
    ) -> MasteringProfile:
        """Analyze reference track and extract mastering profile.

        Args:
            reference_path: Path to reference audio file

        Returns:
            MasteringProfile with extracted parameters
        """
        try:
            import librosa
            import soundfile as sf
        except ImportError:
            logger.error("librosa or soundfile not available")
            raise

        # Load audio
        try:
            y, sr = librosa.load(reference_path, sr=self.sample_rate, mono=False)
        except Exception as e:
            logger.error(f"Failed to load reference track: {e}")
            raise

        # Analyze loudness (LUFS approximation)
        lufs = self._measure_lufs(y, sr)

        # Analyze dynamic range
        dynamic_range = self._measure_dynamic_range(y)

        # Analyze spectral balance (31-band EQ curve)
        spectral_balance = self._analyze_spectral_balance(y, sr)

        # Analyze stereo width
        stereo_width = self._measure_stereo_width(y)

        # Estimate compression ratio
        compression_ratio = self._estimate_compression(y)

        # Detect low/high end characteristics
        low_boost = spectral_balance[:8].mean()  # Low frequencies
        high_boost = spectral_balance[24:].mean()  # High frequencies

        return MasteringProfile(
            target_lufs=lufs,
            dynamic_range=dynamic_range,
            spectral_balance=spectral_balance,
            stereo_width=stereo_width,
            compression_ratio=compression_ratio,
            peak_limit=-0.1,  # Standard peak ceiling
            low_end_boost=low_boost,
            high_end_boost=high_boost,
            metadata={
                "reference_file": str(reference_path),
                "sample_rate": sr,
                "analysis_timestamp": int(__import__("time").time()),
            },
        )

    def _measure_lufs(self, y: np.ndarray, sr: int) -> float:
        """Measure integrated loudness (LUFS approximation).

        Uses simplified RMS-based estimation since full ITU-R BS.1770-4
        K-weighting requires more complex filter implementation.
        """
        if y.ndim > 1:
            y = np.mean(y, axis=0)  # Convert to mono

        # RMS-based LUFS approximation
        rms = np.sqrt(np.mean(y**2))

        # Reference is roughly -23 LUFS for 0dB RMS sine wave
        lufs_approx = 20 * np.log10(rms + 1e-10) - 23.0

        return float(np.clip(lufs_approx, -50, -0))

    def _measure_dynamic_range(self, y: np.ndarray) -> float:
        """Measure dynamic range (peak-to-RMS ratio)."""
        if y.ndim > 1:
            y = np.mean(y, axis=0)

        peak = np.max(np.abs(y))
        rms = np.sqrt(np.mean(y**2))

        if rms > 1e-10:
            dr = 20 * np.log10(peak / rms)
        else:
            dr = 0.0

        return float(max(0, min(30, dr)))

    def _analyze_spectral_balance(
        self,
        y: np.ndarray,
        sr: int,
    ) -> np.ndarray:
        """Analyze 31-band spectral balance (ISO 1/3 octave)."""
        try:
            import librosa
        except ImportError:
            # Return neutral profile if librosa not available
            return np.zeros(31)

        if y.ndim > 1:
            y = np.mean(y, axis=0)

        # Compute mel-spectrogram (approximation of frequency bands)
        S = np.abs(librosa.stft(y, n_fft=4096))
        mel_S = librosa.feature.melspectrogram(S=S, sr=sr, n_mels=31)

        # Convert to dB
        mel_S_db = librosa.power_to_db(mel_S, ref=np.max(mel_S))

        # Average across time
        band_energies = np.mean(mel_S_db, axis=1)

        # Normalize to mean
        mean_energy = np.mean(band_energies)
        spectral_balance = band_energies - mean_energy

        return spectral_balance

    def _measure_stereo_width(self, y: np.ndarray) -> float:
        """Measure stereo width (0.0 = mono, 1.0 = wide stereo)."""
        if y.ndim == 1:
            return 0.0  # Mono signal

        # Ensure 2D
        if y.shape[0] != 2:
            return 0.0

        left = y[0]
        right = y[1]

        # Calculate correlation between channels
        try:
            correlation = np.corrcoef(left, right)[0, 1]
        except (ValueError, RuntimeError):
            return 0.5

        # Handle NaN correlation
        if np.isnan(correlation):
            correlation = 1.0

        # Width: inverse of correlation
        # correlation = 1.0 → width = 0.0 (mono)
        # correlation = 0.0 → width = 1.0 (wide stereo)
        width = 1.0 - abs(correlation)

        return float(np.clip(width, 0.0, 1.0))

    def _estimate_compression(self, y: np.ndarray) -> float:
        """Estimate compression ratio from dynamic range."""
        dr = self._measure_dynamic_range(y)

        # Heuristic mapping of DR to compression ratio
        # DR < 8dB = heavy compression (ratio ~4:1)
        # DR > 15dB = light compression (ratio ~2:1)
        # DR > 20dB = minimal compression (ratio ~1.5:1)

        if dr < 8:
            return 4.0
        elif dr < 15:
            # Linear interpolation between 4:1 and 2:1
            return 4.0 - (dr - 8) / 7 * 2.0
        else:
            return 1.5
