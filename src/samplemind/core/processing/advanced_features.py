"""
Advanced Feature Extraction for detailed audio analysis.

Extracts:
- Temporal features (temporal centroid, variance)
- Spectral features (flux, stability)
- Harmonic features (constant-Q chromagram, tempogram)
- Timbral features (brightness, warmth, sharpness)
"""

import logging
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import librosa
from scipy import signal

logger = logging.getLogger(__name__)


@dataclass
class AdvancedAudioFeatures:
    """Extended audio features"""
    # Temporal features
    temporal_centroid: float  # Where is energy concentrated in time?
    temporal_variance: float  # How spread out is energy?

    # Spectral features
    spectral_flux: float  # How much does spectrum change?
    spectral_stability: np.ndarray  # Frame-by-frame stability

    # Harmonic features
    chromagram: np.ndarray  # (12 pitches, time_frames)
    tempogram: np.ndarray  # Tempo variance over time

    # Timbral features
    timbral_brightness: float  # 0-1
    timbral_warmth: float  # 0-1
    timbral_sharpness: float  # 0-1

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "temporal_centroid": float(self.temporal_centroid),
            "temporal_variance": float(self.temporal_variance),
            "spectral_flux": float(self.spectral_flux),
            "spectral_stability_mean": float(np.mean(self.spectral_stability)),
            "timbral_brightness": float(self.timbral_brightness),
            "timbral_warmth": float(self.timbral_warmth),
            "timbral_sharpness": float(self.timbral_sharpness),
        }


class AdvancedFeatureExtractor:
    """Extract advanced audio features for detailed analysis"""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    async def extract(self, audio: np.ndarray) -> AdvancedAudioFeatures:
        """
        Extract all advanced features.

        Args:
            audio: Audio time series

        Returns:
            AdvancedAudioFeatures dataclass
        """
        # Temporal features
        temporal_centroid, temporal_variance = self._extract_temporal_features(audio)

        # Spectral features
        spectral_flux, spectral_stability = self._extract_spectral_features(audio)

        # Harmonic features
        chromagram = self._extract_chromagram(audio)
        tempogram = self._extract_tempogram(audio)

        # Timbral features
        brightness, warmth, sharpness = self._extract_timbral_features(audio)

        return AdvancedAudioFeatures(
            temporal_centroid=temporal_centroid,
            temporal_variance=temporal_variance,
            spectral_flux=spectral_flux,
            spectral_stability=spectral_stability,
            chromagram=chromagram,
            tempogram=tempogram,
            timbral_brightness=brightness,
            timbral_warmth=warmth,
            timbral_sharpness=sharpness,
        )

    def _extract_temporal_features(self, audio: np.ndarray) -> Tuple[float, float]:
        """
        Extract temporal centroid and variance.

        Centroid: where is the energy concentrated in time?
        Variance: how spread out is the energy?
        """
        # Compute envelope (RMS energy over time)
        frame_length = 2048
        hop_length = 512
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        envelope = np.sqrt(np.mean(frames**2, axis=0))

        # Normalize
        if np.sum(envelope) > 0:
            envelope = envelope / np.sum(envelope)

        # Time axis
        times = librosa.frames_to_time(np.arange(len(envelope)), sr=self.sample_rate)

        # Centroid: weighted average time
        centroid = np.sum(times * envelope)

        # Variance: weighted standard deviation
        variance = np.sum(((times - centroid) ** 2) * envelope)

        return float(centroid), float(np.sqrt(variance))

    def _extract_spectral_features(self, audio: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Extract spectral flux and stability.

        Flux: how much does the spectrum change between frames?
        Stability: frame-by-frame spectral stability (0-1)
        """
        # Compute STFT
        D = librosa.stft(audio)
        mag = np.abs(D)

        # Spectral flux: difference between consecutive frames
        flux_frames = np.sqrt(np.sum(np.diff(mag, axis=1) ** 2, axis=0))
        flux = float(np.mean(flux_frames))

        # Spectral stability: correlation between consecutive frames
        stability = np.zeros(mag.shape[1] - 1)
        for i in range(mag.shape[1] - 1):
            frame_1 = mag[:, i]
            frame_2 = mag[:, i + 1]

            # Cosine similarity
            num = np.dot(frame_1, frame_2)
            denom = np.linalg.norm(frame_1) * np.linalg.norm(frame_2) + 1e-10
            stability[i] = num / denom

        return flux, stability

    def _extract_chromagram(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract constant-Q chromagram (pitch content over time).

        12 pitch classes (C, C#, D, etc.) tracked over time.
        """
        # Compute constant-Q transform (CQT) for better pitch resolution
        cqt = np.abs(librosa.cqt(audio, sr=self.sample_rate))

        # Convert to chromagram (aggregate to 12 pitch classes)
        chroma = librosa.feature.chroma_cqt(C=cqt, sr=self.sample_rate)

        return chroma

    def _extract_tempogram(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract tempogram (tempo variance over time).

        Shows how tempo changes throughout the track.
        """
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)

        # Compute tempogram
        tempogram = librosa.feature.tempogram(onset_env=onset_env, sr=self.sample_rate)

        return tempogram

    def _extract_timbral_features(self, audio: np.ndarray) -> Tuple[float, float, float]:
        """
        Extract timbral features: brightness, warmth, sharpness.

        Based on spectral characteristics:
        - Brightness: proportion of high-frequency energy
        - Warmth: proportion of low-frequency energy
        - Sharpness: spectral sparsity
        """
        # Compute mel-frequency spectrogram
        S = librosa.feature.melspectrogram(y=audio, sr=self.sample_rate)
        S_db = librosa.power_to_db(S, ref=np.max)

        # Frequency bands (mel scale)
        n_mels = S_db.shape[0]

        # Brightness: energy in high frequencies (75-100% of mel scale)
        high_freq_start = int(n_mels * 0.75)
        high_freq_energy = np.mean(S_db[high_freq_start:, :])

        # Warmth: energy in low frequencies (0-25% of mel scale)
        low_freq_end = int(n_mels * 0.25)
        low_freq_energy = np.mean(S_db[:low_freq_end, :])

        # Normalize to 0-1
        total_energy = np.mean(S_db)
        brightness = (high_freq_energy - np.min(S_db)) / (
            np.max(S_db) - np.min(S_db) + 1e-10
        )
        warmth = (low_freq_energy - np.min(S_db)) / (np.max(S_db) - np.min(S_db) + 1e-10)

        # Sharpness: spectral sparsity (concentration of energy)
        # High sharpness = energy concentrated in few bins
        # Low sharpness = energy spread across many bins
        spectral_mean = np.mean(S_db, axis=1)
        spectral_std = np.std(S_db, axis=1)
        sharpness = float(np.mean(spectral_std) / (np.mean(spectral_mean) + 1e-10))
        sharpness = min(1.0, sharpness)  # Normalize

        return float(brightness), float(warmth), float(sharpness)

    def get_timbral_profile(self, features: AdvancedAudioFeatures) -> Dict[str, str]:
        """
        Generate descriptive timbral profile.

        Returns:
            Dictionary describing the timbre
        """
        profile = {}

        # Brightness profile
        if features.timbral_brightness > 0.7:
            profile["brightness"] = "Bright, shimmering"
        elif features.timbral_brightness > 0.5:
            profile["brightness"] = "Moderate brightness"
        else:
            profile["brightness"] = "Dark, warm"

        # Warmth profile
        if features.timbral_warmth > 0.7:
            profile["warmth"] = "Warm, bassy"
        elif features.timbral_warmth > 0.4:
            profile["warmth"] = "Balanced"
        else:
            profile["warmth"] = "Thin, nasal"

        # Sharpness profile
        if features.timbral_sharpness > 0.7:
            profile["sharpness"] = "Sharp, percussive"
        elif features.timbral_sharpness > 0.4:
            profile["sharpness"] = "Smooth, blended"
        else:
            profile["sharpness"] = "Mellow, soft"

        return profile

    def get_harmonic_complexity(self, features: AdvancedAudioFeatures) -> float:
        """
        Get harmonic complexity score (0.0 = simple, 1.0 = complex).

        Based on chromagram entropy.
        """
        # Compute entropy of chromagram
        chroma_mean = np.mean(features.chromagram, axis=1)
        chroma_norm = chroma_mean / (np.sum(chroma_mean) + 1e-10)

        # Entropy (Shannon)
        entropy = -np.sum(chroma_norm * np.log2(chroma_norm + 1e-10))

        # Normalize (max entropy = log2(12) for 12 pitch classes)
        max_entropy = np.log2(12)
        complexity = entropy / max_entropy

        return float(complexity)

    def get_rhythmic_stability(self, features: AdvancedAudioFeatures) -> float:
        """
        Get rhythmic stability score (0.0 = unstable, 1.0 = very stable).

        Based on tempogram consistency.
        """
        # Stability = inverse of tempo variance
        tempo_variance = np.var(features.tempogram)

        # Normalize (higher variance = lower stability)
        stability = 1.0 / (1.0 + tempo_variance)

        return float(stability)


# Global instance
_extractor_instance: Optional[AdvancedFeatureExtractor] = None


def init_extractor(sample_rate: int = 44100) -> AdvancedFeatureExtractor:
    """Initialize global feature extractor"""
    global _extractor_instance
    _extractor_instance = AdvancedFeatureExtractor(sample_rate=sample_rate)
    return _extractor_instance


def get_extractor() -> AdvancedFeatureExtractor:
    """Get global feature extractor"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = AdvancedFeatureExtractor()
    return _extractor_instance
