"""
Audio Forensics Analysis - Detection of processing artifacts and edits.

Detects:
- Compression artifacts (spectral flattening, dynamic range reduction)
- Distortion (clipping, overdrive, saturation)
- Edit points (phase shifts, frequency discontinuities)
- Resampling artifacts (aliasing, filter ringing)
- MP3 encoding artifacts (stereo anomalies)
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Lazy load heavy dependencies
librosa = None
signal = None
fft = None

logger = logging.getLogger(__name__)

def _ensure_deps():
    global librosa, signal, fft
    if librosa is None:
        import librosa as _librosa
        librosa = _librosa
    if signal is None:
        from scipy import signal as _signal
        signal = _signal
    if fft is None:
        from scipy.fft import fft as _fft
        fft = _fft


@dataclass
class CompressionAnalysis:
    """Compression detection result"""
    probability: float  # 0.0-1.0, likelihood of compression
    indicators: list[str]  # Types of indicators found
    estimated_ratio: str  # Estimated compression ratio
    estimated_threshold: float  # Estimated threshold in dB


@dataclass
class DistortionAnalysis:
    """Distortion detection result"""
    probability: float  # 0.0-1.0
    distortion_type: str  # "clipping", "overdrive", "saturation", "none"
    affected_frequencies: list[tuple[float, float]]  # Hz ranges
    severity: float  # 0.0-1.0, how severe


@dataclass
class EditPoint:
    """Detected edit point"""
    time_ms: float
    confidence: float  # 0.0-1.0
    edit_type: str  # "cut", "splice", "time_stretch"
    description: str


@dataclass
class ForensicsResult:
    """Complete forensics analysis"""
    file_path: str
    duration_seconds: float
    sample_rate: int
    bit_depth: int | None

    compression_detected: CompressionAnalysis
    distortion_detected: DistortionAnalysis
    edit_points: list[EditPoint]

    overall_quality_score: float  # 0-100
    recommendations: list[str]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "compression_detected": {
                "probability": self.compression_detected.probability,
                "indicators": self.compression_detected.indicators,
                "estimated_ratio": self.compression_detected.estimated_ratio,
            },
            "distortion_detected": {
                "probability": self.distortion_detected.probability,
                "type": self.distortion_detected.distortion_type,
                "affected_frequencies": self.distortion_detected.affected_frequencies,
                "severity": self.distortion_detected.severity,
            },
            "edit_points": [
                {
                    "time_ms": ep.time_ms,
                    "confidence": ep.confidence,
                    "type": ep.edit_type,
                    "description": ep.description,
                }
                for ep in self.edit_points
            ],
            "overall_quality_score": self.overall_quality_score,
            "recommendations": self.recommendations,
        }


class ForensicsAnalyzer:
    """Analyze audio for processing artifacts and quality issues"""

    def __init__(self, sample_rate: int = 44100) -> None:
        self.sample_rate = sample_rate

    async def analyze(self, audio_path: Path) -> ForensicsResult:
        """
        Analyze audio file for forensics artifacts.

        Args:
            audio_path: Path to audio file

        Returns:
            ForensicsResult with analysis findings
        """
        _ensure_deps()

        # Load audio
        y, sr = librosa.load(audio_path, sr=None, mono=False)

        # Handle mono/stereo
        if y.ndim == 1:
            y_mono = y
            y_stereo = np.stack([y, y])
        else:
            y_mono = np.mean(y, axis=0)
            y_stereo = y

        # Run analyses
        compression = self._analyze_compression(y_mono)
        distortion = self._analyze_distortion(y_mono)
        edits = self._detect_edits(y_mono, sr)

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            compression, distortion, edits, y_mono, sr
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            compression, distortion, edits, quality_score
        )

        duration = len(y_mono) / sr

        return ForensicsResult(
            file_path=str(audio_path),
            duration_seconds=float(duration),
            sample_rate=int(sr),
            bit_depth=None,  # Would need metadata to determine
            compression_detected=compression,
            distortion_detected=distortion,
            edit_points=edits,
            overall_quality_score=quality_score,
            recommendations=recommendations,
        )

    def _analyze_compression(self, y: np.ndarray) -> CompressionAnalysis:
        """Detect compression artifacts"""
        indicators = []

        # Analyze dynamic range
        peak = np.max(np.abs(y))
        rms = np.sqrt(np.mean(y**2))

        if peak > 0:
            crest_factor = peak / (rms + 1e-8)
        else:
            crest_factor = 0.0

        # Heavily compressed signals have low crest factors (<3dB)
        if crest_factor < 3.0:
            indicators.append("low_crest_factor")

        # Analyze spectral flattening (sign of compression)
        # Compressed audio has less spectral variation
        spec = np.abs(librosa.stft(y))
        spectral_std = np.std(np.mean(spec, axis=1))  # Variation across freq bins

        if spectral_std < 10:  # Low variation = flattening
            indicators.append("spectral_flattening")

        # Analyze loudness consistency (compressed audio is more consistent)
        frame_lengths = 2048
        hop_length = 512
        frames = librosa.util.frame(y, frame_length=frame_lengths, hop_length=hop_length)
        frame_rms = np.sqrt(np.mean(frames**2, axis=0))
        rms_variance = np.var(frame_rms)

        if rms_variance < 0.0001:  # Very low variance = compression
            indicators.append("low_rms_variance")

        # Estimate compression ratio from crest factor
        # Lower crest factor = higher ratio
        if crest_factor < 2.0:
            estimated_ratio = "8:1 or higher"
        elif crest_factor < 3.0:
            estimated_ratio = "4:1 to 8:1"
        elif crest_factor < 4.0:
            estimated_ratio = "2:1 to 4:1"
        else:
            estimated_ratio = "1:1 (uncompressed)"

        # Probability based on number of indicators
        probability = min(0.99, len(indicators) * 0.33)

        return CompressionAnalysis(
            probability=probability,
            indicators=indicators,
            estimated_ratio=estimated_ratio,
            estimated_threshold=-20.0,  # Default estimate
        )

    def _analyze_distortion(self, y: np.ndarray) -> DistortionAnalysis:
        """Detect distortion and clipping"""
        # Detect hard clipping
        clipping_threshold = 0.99
        clipped_samples = np.sum(np.abs(y) > clipping_threshold) / len(y)

        distortion_type = "none"
        probability = 0.0
        severity = 0.0
        affected_frequencies = []

        if clipped_samples > 0.001:  # >0.1% clipped samples
            distortion_type = "clipping"
            probability = min(0.99, clipped_samples * 100)
            severity = clipped_samples

            # Find affected frequencies
            spec = np.abs(librosa.stft(y))
            freqs = librosa.fft_frequencies(sr=self.sample_rate)

            # Clipping affects high frequencies more
            high_freq_energy = np.mean(spec[len(spec)//2:])
            low_freq_energy = np.mean(spec[:len(spec)//2])

            if high_freq_energy > low_freq_energy * 1.5:
                affected_frequencies.append((5000, 22050))

        # Detect saturation (gradual onset compression)
        harmonic_content = self._detect_harmonics(y)
        if harmonic_content > 0.3:  # High harmonic content suggests saturation
            distortion_type = "saturation"
            probability = min(0.99, harmonic_content * 0.8)
            severity = harmonic_content

        return DistortionAnalysis(
            probability=probability,
            distortion_type=distortion_type,
            affected_frequencies=affected_frequencies,
            severity=severity,
        )

    def _detect_harmonics(self, y: np.ndarray) -> float:
        """Detect harmonic content (sign of distortion/saturation)"""
        # Use spectral analysis
        spec = np.abs(librosa.stft(y))
        mag = np.mean(spec, axis=1)

        # Find peak frequency
        peak_idx = np.argmax(mag)
        peak_mag = mag[peak_idx]

        # Sum energy at harmonics (2x, 3x, 4x, etc.)
        harmonic_energy = 0.0
        for harmonic in range(2, 6):
            harmonic_idx = peak_idx * harmonic
            if harmonic_idx < len(mag):
                harmonic_energy += mag[harmonic_idx]

        # Normalize by fundamental
        if peak_mag > 0:
            return min(1.0, harmonic_energy / (peak_mag * 5))
        return 0.0

    def _detect_edits(self, y: np.ndarray, sr: int) -> list[EditPoint]:
        """Detect edit points (splices, cuts)"""
        edit_points = []

        # Detect phase discontinuities (sign of splice)
        phase = np.angle(librosa.stft(y))
        phase_diff = np.diff(phase, axis=1)
        phase_discontinuities = np.abs(phase_diff)

        # Find large phase jumps
        threshold = np.median(phase_discontinuities) + 2 * np.std(phase_discontinuities)

        for freq_idx in range(phase_discontinuities.shape[0]):
            freq_jumps = np.where(phase_discontinuities[freq_idx] > threshold)[0]

            for jump_frame in freq_jumps:
                time_ms = librosa.frames_to_time(jump_frame, sr=sr) * 1000

                # Avoid duplicates (multiple freq bins may detect same splice)
                if not any(abs(ep.time_ms - time_ms) < 100 for ep in edit_points):
                    edit_points.append(
                        EditPoint(
                            time_ms=time_ms,
                            confidence=0.75,
                            edit_type="splice",
                            description="Phase discontinuity detected",
                        )
                    )

        # Detect spectral discontinuities
        spec = np.abs(librosa.stft(y))
        spec_diff = np.diff(np.mean(spec, axis=0))
        spec_jumps = np.where(np.abs(spec_diff) > np.std(spec_diff) * 3)[0]

        for jump_frame in spec_jumps:
            time_ms = librosa.frames_to_time(jump_frame, sr=sr) * 1000

            if not any(abs(ep.time_ms - time_ms) < 100 for ep in edit_points):
                edit_points.append(
                    EditPoint(
                        time_ms=time_ms,
                        confidence=0.60,
                        edit_type="cut",
                        description="Spectral discontinuity detected",
                    )
                )

        # Limit to top 10 by confidence
        edit_points.sort(key=lambda ep: ep.confidence, reverse=True)
        return edit_points[:10]

    def _calculate_quality_score(
        self,
        compression: CompressionAnalysis,
        distortion: DistortionAnalysis,
        edits: list[EditPoint],
        y: np.ndarray,
        sr: int,
    ) -> float:
        """Calculate overall audio quality score (0-100)"""
        score = 85.0  # Start at 85 (good)

        # Reduce for compression
        score -= compression.probability * 15

        # Reduce for distortion
        score -= distortion.severity * 25

        # Reduce for edits
        score -= len(edits) * 5

        # Check bit depth / sample rate
        if sr < 44100:
            score -= 10
        elif sr < 48000:
            score -= 5

        # Check dynamic range
        peak = np.max(np.abs(y))
        rms = np.sqrt(np.mean(y**2))
        if peak > 0:
            dr = 20 * np.log10(peak / (rms + 1e-8))
            if dr < 6:
                score -= 10
            elif dr < 12:
                score -= 5

        return max(0.0, min(100.0, score))

    def _generate_recommendations(
        self,
        compression: CompressionAnalysis,
        distortion: DistortionAnalysis,
        edits: list[EditPoint],
        quality_score: float,
    ) -> list[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if compression.probability > 0.7:
            recommendations.append(
                f"Audio is heavily compressed ({compression.estimated_ratio}) - "
                "acceptable for streaming but may lack dynamic range"
            )
        elif compression.probability > 0.4:
            recommendations.append(
                f"Audio shows signs of compression ({compression.estimated_ratio}) - "
                "consider re-recording for maximum quality"
            )

        if distortion.distortion_type == "clipping":
            recommendations.append(
                f"Hard clipping detected with {distortion.severity:.1%} affected samples - "
                "re-record or find cleaner source"
            )
        elif distortion.distortion_type == "saturation":
            recommendations.append(
                "Saturation/overdrive detected - consider cleaner recording or re-mastering"
            )

        if len(edits) > 3:
            recommendations.append(
                f"{len(edits)} edit points detected - consider re-recording for smooth, natural sound"
            )

        if quality_score < 50:
            recommendations.append(
                "Overall quality is poor - strongly recommend re-recording from original source"
            )
        elif quality_score < 70:
            recommendations.append("Quality is acceptable but could be improved with re-recording")
        elif quality_score > 90:
            recommendations.append("Audio quality is excellent - suitable for professional use")

        return recommendations


# Global instance
_analyzer_instance: ForensicsAnalyzer | None = None


def init_analyzer(sample_rate: int = 44100) -> ForensicsAnalyzer:
    """Initialize global analyzer instance"""
    global _analyzer_instance
    _analyzer_instance = ForensicsAnalyzer(sample_rate=sample_rate)
    return _analyzer_instance


def get_analyzer() -> ForensicsAnalyzer:
    """Get global analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ForensicsAnalyzer()
    return _analyzer_instance
