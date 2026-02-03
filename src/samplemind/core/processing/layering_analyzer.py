#!/usr/bin/env python3
"""
Intelligent Sample Layering Analyzer

Analyzes phase relationships and frequency masking when layering samples.
Provides recommendations for clean, non-destructive sample stacking.

Features:
- Phase correlation analysis (detect phase cancellation)
- Frequency masking detection (find overlapping frequencies)
- Transient conflict analysis (check for timing clashes)
- EQ recommendations (suggest cuts to avoid masking)
- Loudness balance analysis
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

# ============================================================================
# LAYERING ANALYSIS RESULTS
# ============================================================================

@dataclass
class FrequencyMask:
    """Represents a frequency masking issue"""
    frequency_hz: float
    min_freq: float
    max_freq: float
    sample1_power: float
    sample2_power: float
    power_difference_db: float
    severity: str  # low, medium, high

    @property
    def is_severe(self) -> bool:
        """Check if conflict is severe"""
        return self.severity == "high"


@dataclass
class LayeringAnalysis:
    """Results from sample layering analysis"""
    # Compatibility metrics
    compatibility_score: float  # 0-10
    can_layer: bool

    # Phase analysis
    phase_correlation: float  # -1 to 1
    phase_status: str  # "in-phase", "phase-cancellation", "orthogonal"

    # Frequency analysis
    frequency_masks: List[FrequencyMask]
    has_masking: bool

    # Transient analysis
    transient_offset_ms: float  # Positive if sample2 is delayed
    transient_conflict: bool
    transient_status: str

    # Loudness balance
    loudness_difference_db: float
    loudness_ratio: float

    # Recommendations
    recommended_actions: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "compatibility_score": round(self.compatibility_score, 2),
            "can_layer": self.can_layer,
            "phase_correlation": round(self.phase_correlation, 2),
            "phase_status": self.phase_status,
            "frequency_masks": len(self.frequency_masks),
            "has_masking": self.has_masking,
            "transient_offset_ms": round(self.transient_offset_ms, 1),
            "transient_conflict": self.transient_conflict,
            "loudness_difference_db": round(self.loudness_difference_db, 2),
            "recommended_actions": self.recommended_actions,
        }


# ============================================================================
# LAYERING ANALYZER ENGINE
# ============================================================================

class LayeringAnalyzer:
    """Analyzes compatibility of samples for layering"""

    def __init__(self):
        self.fft_size = 2048
        self.hop_length = 512

    def analyze(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int = 44100,
    ) -> LayeringAnalysis:
        """
        Analyze compatibility of two samples for layering

        Args:
            audio1: First audio sample
            audio2: Second audio sample
            sample_rate: Sample rate in Hz

        Returns:
            LayeringAnalysis object
        """
        # Ensure mono
        if audio1.ndim > 1:
            audio1 = np.mean(audio1, axis=1)
        if audio2.ndim > 1:
            audio2 = np.mean(audio2, axis=1)

        # 1. Phase analysis
        phase_corr = self._calculate_phase_correlation(audio1, audio2)
        phase_status = self._get_phase_status(phase_corr)

        # 2. Frequency masking analysis
        frequency_masks = self._analyze_frequency_masking(audio1, audio2, sample_rate)
        has_masking = len(frequency_masks) > 0

        # 3. Transient analysis
        transient_offset, transient_conflict = self._analyze_transients(audio1, audio2, sample_rate)
        transient_status = "conflict" if transient_conflict else "aligned"

        # 4. Loudness analysis
        loudness_diff, loudness_ratio = self._analyze_loudness_balance(audio1, audio2)

        # 5. Generate compatibility score
        compatibility_score = self._calculate_compatibility_score(
            phase_corr,
            has_masking,
            transient_conflict,
            loudness_diff,
        )

        # 6. Generate recommendations
        recommendations = self._generate_recommendations(
            phase_corr,
            frequency_masks,
            transient_offset,
            loudness_diff,
        )

        return LayeringAnalysis(
            compatibility_score=compatibility_score,
            can_layer=compatibility_score >= 6.0,
            phase_correlation=phase_corr,
            phase_status=phase_status,
            frequency_masks=frequency_masks,
            has_masking=has_masking,
            transient_offset_ms=transient_offset * 1000 / sample_rate,
            transient_conflict=transient_conflict,
            transient_status=transient_status,
            loudness_difference_db=loudness_diff,
            loudness_ratio=loudness_ratio,
            recommended_actions=recommendations,
        )

    # ========================================================================
    # ANALYSIS METHODS
    # ========================================================================

    def _calculate_phase_correlation(self, audio1: np.ndarray, audio2: np.ndarray) -> float:
        """Calculate phase correlation between two signals"""
        # Normalize
        audio1 = audio1 / (np.max(np.abs(audio1)) + 1e-10)
        audio2 = audio2 / (np.max(np.abs(audio2)) + 1e-10)

        # Align to same length
        min_len = min(len(audio1), len(audio2))
        audio1 = audio1[:min_len]
        audio2 = audio2[:min_len]

        # Cross-correlation
        cross_product = np.mean(audio1 * audio2)
        auto1 = np.sqrt(np.mean(audio1 ** 2))
        auto2 = np.sqrt(np.mean(audio2 ** 2))

        correlation = cross_product / (auto1 * auto2 + 1e-10)

        return float(correlation)

    def _get_phase_status(self, correlation: float) -> str:
        """Describe phase relationship"""
        if correlation > 0.8:
            return "in-phase"
        elif correlation < -0.8:
            return "phase-cancellation"
        else:
            return "orthogonal"

    def _analyze_frequency_masking(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int,
    ) -> List[FrequencyMask]:
        """Detect frequency masking issues"""
        masks = []

        # FFT analysis
        fft1 = np.abs(np.fft.rfft(audio1, n=self.fft_size))
        fft2 = np.abs(np.fft.rfft(audio2, n=self.fft_size))
        freqs = np.fft.rfftfreq(self.fft_size, 1 / sample_rate)

        # Find peaks in both signals
        threshold1 = np.max(fft1) * 0.1
        threshold2 = np.max(fft2) * 0.1

        peaks1 = np.where(fft1 > threshold1)[0]
        peaks2 = np.where(fft2 > threshold2)[0]

        # Check for overlapping frequency content
        overlap = np.intersect1d(peaks1, peaks2)

        for idx in overlap:
            freq = freqs[idx]

            # Only care about significant overlaps
            power1 = fft1[idx]
            power2 = fft2[idx]
            power_diff_db = 20 * np.log10((power1 / power2) + 1e-10)

            if abs(power_diff_db) > 3:  # >3dB difference indicates masking
                # Determine severity
                if abs(power_diff_db) > 10:
                    severity = "high"
                elif abs(power_diff_db) > 6:
                    severity = "medium"
                else:
                    severity = "low"

                # Create mask entry
                mask = FrequencyMask(
                    frequency_hz=float(freq),
                    min_freq=float(freq * 0.9),
                    max_freq=float(freq * 1.1),
                    sample1_power=float(power1),
                    sample2_power=float(power2),
                    power_difference_db=float(power_diff_db),
                    severity=severity,
                )

                masks.append(mask)

        return masks

    def _analyze_transients(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
        sample_rate: int,
    ) -> Tuple[float, bool]:
        """Analyze transient timing and conflicts"""
        # Simple onset detection using energy envelope
        window_size = int(0.01 * sample_rate)  # 10ms windows

        def get_onsets(audio):
            """Detect onsets in audio signal"""
            energy = np.array([
                np.sum(audio[i:i+window_size]**2)
                for i in range(0, len(audio)-window_size, window_size)
            ])

            # Find significant energy jumps
            diff = np.diff(energy)
            threshold = np.mean(diff) + 2 * np.std(diff)
            onsets = np.where(diff > threshold)[0]

            return onsets[0] * window_size if len(onsets) > 0 else 0

        onset1 = get_onsets(audio1)
        onset2 = get_onsets(audio2)

        offset = onset1 - onset2

        # Transient conflict if onsets are within 30ms
        conflict = abs(offset) < int(0.03 * sample_rate)

        return float(offset), conflict

    def _analyze_loudness_balance(
        self,
        audio1: np.ndarray,
        audio2: np.ndarray,
    ) -> Tuple[float, float]:
        """Analyze loudness relationship"""
        rms1 = np.sqrt(np.mean(audio1 ** 2))
        rms2 = np.sqrt(np.mean(audio2 ** 2))

        # Difference in dB
        loudness_diff = 20 * np.log10((rms1 / rms2) + 1e-10)

        # Ratio (linear)
        loudness_ratio = rms1 / (rms2 + 1e-10)

        return float(loudness_diff), float(loudness_ratio)

    # ========================================================================
    # SCORING & RECOMMENDATIONS
    # ========================================================================

    def _calculate_compatibility_score(
        self,
        phase_corr: float,
        has_masking: bool,
        transient_conflict: bool,
        loudness_diff: float,
    ) -> float:
        """Calculate overall compatibility score (0-10)"""
        score = 10.0

        # Phase penalty
        if phase_corr < -0.5:
            score -= 3  # Phase cancellation is bad
        elif phase_corr < 0:
            score -= 1

        # Masking penalty
        if has_masking:
            score -= 2

        # Transient conflict penalty
        if transient_conflict:
            score -= 1

        # Loudness balance penalty
        if abs(loudness_diff) > 10:
            score -= 2
        elif abs(loudness_diff) > 6:
            score -= 1

        return max(0.0, min(10.0, score))

    def _generate_recommendations(
        self,
        phase_corr: float,
        frequency_masks: List[FrequencyMask],
        transient_offset: float,
        loudness_diff: float,
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Phase recommendations
        if phase_corr < -0.5:
            recommendations.append(
                "⚠️  Phase cancellation detected! Try flipping polarity on one sample."
            )

        # Frequency masking recommendations
        if frequency_masks:
            # Group by severity
            high_severity = [m for m in frequency_masks if m.is_severe]

            if high_severity:
                freqs = [m.frequency_hz for m in high_severity[:3]]
                freq_str = ", ".join([f"{f:.0f}Hz" for f in freqs])
                recommendations.append(
                    f"🎛️  Frequency masking at {freq_str}. Try EQ cut on the masked sample."
                )

        # Transient recommendations
        if abs(transient_offset) > 10:
            recommendations.append(
                f"📍 Transient offset: {abs(transient_offset):.0f} samples. "
                "Consider aligning onsets for tighter layering."
            )

        # Loudness recommendations
        if loudness_diff > 6:
            recommendations.append(
                f"🔊 Sample 1 is {loudness_diff:.1f}dB louder. Reduce level or boost sample 2."
            )
        elif loudness_diff < -6:
            recommendations.append(
                f"🔊 Sample 2 is {abs(loudness_diff):.1f}dB louder. Reduce level or boost sample 1."
            )

        # Positive feedback
        if not recommendations:
            recommendations.append("✅ Great compatibility! These samples layer well together.")

        return recommendations


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "FrequencyMask",
    "LayeringAnalysis",
    "LayeringAnalyzer",
]
