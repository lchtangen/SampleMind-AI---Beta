#!/usr/bin/env python3
"""
Professional Mastering Assistant

Comprehensive audio analysis for mastering decisions:
- Loudness (LUFS) analysis with platform targets
- Spectral balance (sub, bass, mids, highs)
- Stereo width and phase coherence
- Dynamic range and compression analysis
- Professional recommendations

Produces mastering-ready analysis reports.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np

from samplemind.core.processing.loudness_analyzer import (
    LoudnessAnalyzer,
    LoudnessAnalysis,
    PLATFORM_TARGETS,
)

logger = logging.getLogger(__name__)

# ============================================================================
# MASTERING ANALYSIS RESULTS
# ============================================================================

@dataclass
class MasteringAnalysis:
    """Comprehensive mastering analysis"""
    # Loudness metrics
    loudness: LoudnessAnalysis
    target_platform: str
    platform_target: float

    # Spectral analysis
    spectral_balance: Dict[str, float]  # sub, bass, mids, highs
    estimated_brightness: float  # 0-1

    # Stereo analysis
    stereo_width: float  # 0-100 %
    phase_correlation: float  # -1 to 1
    center_energy: float  # 0-100 %

    # Additional metrics
    has_clipping: bool
    loudness_headroom: float  # dB to target
    requires_gain_adjustment: bool

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "loudness": self.loudness.to_dict(),
            "target_platform": self.target_platform,
            "platform_target": self.platform_target,
            "spectral_balance": {
                k: round(v, 2) for k, v in self.spectral_balance.items()
            },
            "estimated_brightness": round(self.estimated_brightness, 2),
            "stereo_width": round(self.stereo_width, 2),
            "phase_correlation": round(self.phase_correlation, 2),
            "center_energy": round(self.center_energy, 2),
            "has_clipping": self.has_clipping,
            "loudness_headroom": round(self.loudness_headroom, 2),
            "requires_gain_adjustment": self.requires_gain_adjustment,
        }


# ============================================================================
# MASTERING ANALYZER ENGINE
# ============================================================================

class MasteringAnalyzer:
    """Comprehensive mastering analysis engine"""

    def __init__(self) -> None:
        self.loudness_analyzer = LoudnessAnalyzer()

    def analyze(
        self,
        audio: np.ndarray,
        sample_rate: int = 44100,
        target_platform: str = "spotify",
    ) -> MasteringAnalysis:
        """
        Perform comprehensive mastering analysis

        Args:
            audio: Audio samples (mono or stereo)
            sample_rate: Sample rate in Hz
            target_platform: Target platform for loudness target

        Returns:
            MasteringAnalysis object
        """
        # Ensure stereo
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        # 1. Loudness analysis
        loudness = self.loudness_analyzer.analyze_loudness(audio, sample_rate)

        # 2. Spectral balance
        spectral_balance = self._analyze_spectral_balance(audio, sample_rate)

        # 3. Stereo analysis
        stereo_width, phase_correlation, center_energy = self._analyze_stereo(audio)

        # 4. Additional metrics
        if target_platform not in PLATFORM_TARGETS:
            target_platform = "spotify"

        platform_target = PLATFORM_TARGETS[target_platform]["integrated_loudness"]

        loudness_headroom = platform_target - loudness.integrated_loudness

        return MasteringAnalysis(
            loudness=loudness,
            target_platform=target_platform,
            platform_target=platform_target,
            spectral_balance=spectral_balance,
            estimated_brightness=self._estimate_brightness(spectral_balance),
            stereo_width=stereo_width,
            phase_correlation=phase_correlation,
            center_energy=center_energy,
            has_clipping=loudness.is_clipping,
            loudness_headroom=loudness_headroom,
            requires_gain_adjustment=loudness.needs_gain_adjustment(platform_target),
        )

    # ========================================================================
    # SPECTRAL ANALYSIS
    # ========================================================================

    def _analyze_spectral_balance(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> Dict[str, float]:
        """Analyze spectral balance across frequency ranges"""
        # Use FFT to analyze frequency content
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio

        # Normalize
        if np.max(np.abs(audio_mono)) > 0:
            audio_mono = audio_mono / np.max(np.abs(audio_mono))

        # FFT
        fft = np.abs(np.fft.rfft(audio_mono))
        freqs = np.fft.rfftfreq(len(audio_mono), 1 / sample_rate)

        # Frequency bands (in dB relative to total)
        total_power = np.sum(fft ** 2)

        # Sub-bass (20-60 Hz)
        sub_mask = (freqs >= 20) & (freqs < 60)
        sub_power = np.sum(fft[sub_mask] ** 2)
        sub_db = 20 * np.log10((sub_power / total_power) + 1e-10)

        # Bass (60-250 Hz)
        bass_mask = (freqs >= 60) & (freqs < 250)
        bass_power = np.sum(fft[bass_mask] ** 2)
        bass_db = 20 * np.log10((bass_power / total_power) + 1e-10)

        # Mids (250-2000 Hz)
        mids_mask = (freqs >= 250) & (freqs < 2000)
        mids_power = np.sum(fft[mids_mask] ** 2)
        mids_db = 20 * np.log10((mids_power / total_power) + 1e-10)

        # Highs (2000+ Hz)
        highs_mask = freqs >= 2000
        highs_power = np.sum(fft[highs_mask] ** 2)
        highs_db = 20 * np.log10((highs_power / total_power) + 1e-10)

        # Normalize to reference (0 = balanced)
        reference = mids_db
        return {
            "sub": sub_db - reference,
            "bass": bass_db - reference,
            "mids": 0.0,  # Reference
            "highs": highs_db - reference,
        }

    def _estimate_brightness(self, spectral_balance: Dict[str, float]) -> float:
        """Estimate brightness from spectral balance (0-1)"""
        highs = spectral_balance.get("highs", 0)
        # Normalize: -12dB = 0.0 (dark), +12dB = 1.0 (bright)
        brightness = (highs + 12) / 24
        return float(np.clip(brightness, 0.0, 1.0))

    # ========================================================================
    # STEREO ANALYSIS
    # ========================================================================

    def _analyze_stereo(self, audio: np.ndarray) -> tuple:
        """Analyze stereo width and phase coherence"""
        if audio.ndim == 1 or audio.shape[1] == 1:
            # Mono
            return 0.0, 1.0, 100.0

        left = audio[:, 0]
        right = audio[:, 1]

        # 1. Stereo width (using MS encoding)
        mid = (left + right) / 2
        side = (left - right) / 2

        mid_power = np.mean(mid ** 2)
        side_power = np.mean(side ** 2)
        total_power = mid_power + side_power

        if total_power == 0:
            stereo_width = 0.0
        else:
            stereo_width = 100 * side_power / total_power

        # 2. Phase correlation
        cross_product = np.mean(left * right)
        left_power = np.sqrt(np.mean(left ** 2))
        right_power = np.sqrt(np.mean(right ** 2))

        if left_power == 0 or right_power == 0:
            phase_correlation = 1.0
        else:
            phase_correlation = float(
                cross_product / (left_power * right_power + 1e-10)
            )

        # 3. Center energy (mid channel energy percentage)
        mid_power = np.mean(mid ** 2)
        total_power = np.mean(left ** 2) + np.mean(right ** 2)

        if total_power == 0:
            center_energy = 50.0
        else:
            center_energy = 100 * mid_power / total_power

        return float(stereo_width), float(phase_correlation), float(center_energy)

    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================

    def get_recommendations(self, analysis: MasteringAnalysis) -> List[str]:
        """
        Generate actionable mastering recommendations

        Args:
            analysis: MasteringAnalysis object

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Loudness recommendations
        if analysis.loudness_headroom > 0.5:
            gain_db = analysis.loudness_headroom
            recommendations.append(
                f"📈 Increase overall gain by {gain_db:.1f} dB to reach target {analysis.platform_target} LUFS"
            )

        # Clipping warnings
        if analysis.has_clipping:
            recommendations.append(
                "⚠️  Audio is clipping! Add limiter at -1.0 dBTP to prevent distortion"
            )

        # Spectral recommendations
        sub_balance = analysis.spectral_balance.get("sub", 0)
        bass_balance = analysis.spectral_balance.get("bass", 0)
        highs_balance = analysis.spectral_balance.get("highs", 0)

        if sub_balance < -6:
            recommendations.append(
                f"🎛️  Sub-bass is low ({sub_balance:.1f} dB). Consider shelf boost at 40 Hz (+2-3 dB)"
            )
        elif sub_balance > 6:
            recommendations.append(
                f"🎛️  Sub-bass is excessive ({sub_balance:.1f} dB). Consider cut at 40 Hz (-2-3 dB)"
            )

        if bass_balance < -4:
            recommendations.append(
                f"🎛️  Bass is thin ({bass_balance:.1f} dB). Boost around 100-200 Hz (+1-2 dB)"
            )

        if highs_balance < -3:
            recommendations.append(
                f"🎛️  Highs are dull ({highs_balance:.1f} dB). Boost 3kHz-8kHz region (+1-2 dB)"
            )
        elif highs_balance > 6:
            recommendations.append(
                f"🎛️  Highs are harsh ({highs_balance:.1f} dB). Gentle cut 5kHz-10kHz (-1-2 dB)"
            )

        # Stereo recommendations
        if analysis.stereo_width < 10:
            recommendations.append(
                "🔀 Mono or nearly mono. Consider stereo widening if appropriate for style"
            )
        elif analysis.stereo_width > 80:
            recommendations.append(
                "🔀 Very wide stereo image. Check mono compatibility - may phase cancel"
            )

        if analysis.phase_correlation < 0.7:
            recommendations.append(
                f"⚠️  Low phase correlation ({analysis.phase_correlation:.2f}). May have mono compatibility issues"
            )

        # Dynamic range
        if analysis.loudness.dynamic_range < 6:
            recommendations.append(
                f"📊 Very compressed ({analysis.loudness.dynamic_range:.1f} dB DR). May lack dynamics/punch"
            )
        elif analysis.loudness.dynamic_range > 16:
            recommendations.append(
                f"📊 Very dynamic ({analysis.loudness.dynamic_range:.1f} dB DR). Could use slight compression"
            )

        # Final limiting
        recommendations.append(
            f"🔒 Use final limiter: Threshold {analysis.loudness_headroom - 4:.1f} dBFS, Release 50ms"
        )

        if not recommendations:
            recommendations.append("✅ Audio looks mastering-ready!")

        return recommendations

    # ========================================================================
    # COMPARISON & METRICS
    # ========================================================================

    def compare_to_reference(
        self,
        analysis: MasteringAnalysis,
        reference_loudness: float = -14.0,
    ) -> Dict[str, float]:
        """Compare to reference metrics"""
        return {
            "loudness_difference": analysis.loudness.integrated_loudness - reference_loudness,
            "loudness_ratio": 10 ** ((analysis.loudness.integrated_loudness - reference_loudness) / 20),
        }

    def get_mastering_grade(self, analysis: MasteringAnalysis) -> str:
        """
        Assign a mastering readiness grade

        Returns: A-F grade
        """
        issues = 0

        # Clipping is critical
        if analysis.has_clipping:
            issues += 3

        # Loudness deviation
        loudness_diff = abs(analysis.loudness_headroom)
        if loudness_diff > 2:
            issues += 2
        elif loudness_diff > 1:
            issues += 1

        # Phase issues
        if analysis.phase_correlation < 0.7:
            issues += 1

        # Spectral imbalance
        spectral_issues = sum(
            1 for v in analysis.spectral_balance.values() if abs(v) > 6
        )
        issues += spectral_issues

        # Grade mapping
        if issues == 0:
            return "A"  # Perfect
        elif issues <= 1:
            return "B"  # Good
        elif issues <= 2:
            return "C"  # Fair
        elif issues <= 4:
            return "D"  # Needs work
        else:
            return "F"  # Major issues


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "MasteringAnalysis",
    "MasteringAnalyzer",
]


if __name__ == "__main__":
    # Demo
    import numpy as np

    # Generate test signal
    duration = 5
    sample_rate = 44100
    t = np.arange(duration * sample_rate) / sample_rate

    # Create stereo signal with different frequencies
    left = 0.4 * np.sin(2 * np.pi * 440 * t)  # A4
    right = 0.35 * np.sin(2 * np.pi * 480 * t)  # Different pitch for stereo

    audio = np.column_stack([left, right])

    # Analyze
    analyzer = MasteringAnalyzer()
    analysis = analyzer.analyze(audio, sample_rate, "spotify")

    print("\n🎚️  Mastering Analysis")
    print("=" * 60)
    print(f"Integrated Loudness: {analysis.loudness.integrated_loudness:.2f} LUFS")
    print(f"Target: {analysis.platform_target} LUFS ({analysis.target_platform})")
    print(f"Headroom: {analysis.loudness_headroom:.2f} dB")
    print()
    print("Spectral Balance (relative to mids):")
    for band, balance in analysis.spectral_balance.items():
        print(f"  {band.upper():<10} {balance:+.2f} dB")
    print()
    print(f"Stereo Width: {analysis.stereo_width:.1f}%")
    print(f"Phase Correlation: {analysis.phase_correlation:.2f}")
    print()
    print("Recommendations:")
    for rec in analyzer.get_recommendations(analysis):
        print(f"  • {rec}")
    print()
    print(f"Grade: {analyzer.get_mastering_grade(analysis)}")
