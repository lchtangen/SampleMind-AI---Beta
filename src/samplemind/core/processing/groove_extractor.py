#!/usr/bin/env python3
"""
Groove Template Extraction

Extracts timing and velocity patterns from drum loops and samples.
Quantifies "groove feel" including swing, humanization, and timing deviations.

Can save/load groove templates and apply to MIDI or audio.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# GROOVE TEMPLATE DATA
# ============================================================================

@dataclass
class GrooveTemplate:
    """Extracted groove template"""
    name: str
    tempo_bpm: float
    time_signature: str
    swing_amount: float  # 0-100% (50% = straight, >50% = swung)
    groove_type: str  # "straight", "swing", "shuffle", "jdilla", etc.
    timing_deviation_ms: float  # RMS timing deviation
    velocity_pattern: List[float]  # Velocity percentages for beats
    note_timings: List[float]  # Timing of each note relative to grid (ms)
    description: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "tempo_bpm": float(self.tempo_bpm),
            "time_signature": self.time_signature,
            "swing_amount": float(self.swing_amount),
            "groove_type": self.groove_type,
            "timing_deviation_ms": float(self.timing_deviation_ms),
            "velocity_pattern": [float(v) for v in self.velocity_pattern],
            "note_timings": [float(t) for t in self.note_timings],
            "description": self.description,
        }

    def save(self, path: Path):
        """Save groove to JSON file"""
        path.write_text(json.dumps(self.to_dict(), indent=2))
        logger.info(f"Groove saved to {path}")

    @classmethod
    def load(cls, path: Path) -> "GrooveTemplate":
        """Load groove from JSON file"""
        data = json.loads(path.read_text())
        return cls(**data)


# ============================================================================
# GROOVE EXTRACTOR ENGINE
# ============================================================================

class GrooveExtractor:
    """Extracts groove templates from audio"""

    def __init__(self):
        self.window_size = 2048
        self.hop_length = 512

    def extract(
        self,
        audio: np.ndarray,
        sample_rate: int = 44100,
        name: str = "extracted_groove",
        tempo_bpm: Optional[float] = None,
    ) -> GrooveTemplate:
        """
        Extract groove template from audio

        Args:
            audio: Audio samples (mono or stereo)
            sample_rate: Sample rate in Hz
            name: Name for the groove template
            tempo_bpm: Optional tempo (auto-detect if not provided)

        Returns:
            GrooveTemplate object
        """
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-10)

        # 1. Detect onsets (for timing analysis)
        onsets = self._detect_onsets(audio, sample_rate)

        # 2. Calculate timing deviations
        note_timings, timing_deviation = self._analyze_timing_deviation(onsets, sample_rate)

        # 3. Analyze velocity/amplitude patterns
        velocity_pattern = self._analyze_velocity_pattern(audio, onsets, sample_rate)

        # 4. Detect swing
        swing_amount = self._detect_swing(note_timings)

        # 5. Classify groove type
        groove_type = self._classify_groove_type(swing_amount, timing_deviation)

        # 6. Estimate tempo if not provided
        if tempo_bpm is None:
            tempo_bpm = self._estimate_tempo(onsets, sample_rate)

        return GrooveTemplate(
            name=name,
            tempo_bpm=tempo_bpm,
            time_signature="4/4",  # Assume common time
            swing_amount=swing_amount,
            groove_type=groove_type,
            timing_deviation_ms=timing_deviation,
            velocity_pattern=velocity_pattern,
            note_timings=note_timings,
            description=f"Extracted from {name}",
        )

    # ========================================================================
    # ANALYSIS METHODS
    # ========================================================================

    def _detect_onsets(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Detect onset times in audio"""
        # Energy-based onset detection
        window_size = int(0.01 * sample_rate)  # 10ms windows

        energy = np.array([
            np.sum(audio[i:i+window_size]**2)
            for i in range(0, len(audio)-window_size, window_size)
        ])

        # Smooth energy
        energy_smooth = np.convolve(energy, np.hanning(5)/5, mode='same')

        # Find peaks
        diff = np.diff(energy_smooth)
        threshold = np.mean(diff) + np.std(diff)

        onsets_idx = np.where(diff > threshold)[0]

        # Convert back to sample indices
        onsets = onsets_idx * window_size

        return onsets

    def _analyze_timing_deviation(self, onsets: np.ndarray, sample_rate: int) -> tuple:
        """Analyze timing deviations from grid"""
        if len(onsets) < 2:
            return [0.0], 0.0

        # Calculate inter-onset intervals
        iois = np.diff(onsets)

        # Assume steady tempo
        median_ioi = np.median(iois)

        # Calculate deviations
        deviations = iois - median_ioi

        # Convert to milliseconds and percentage
        deviations_ms = deviations / sample_rate * 1000

        timing_deviation = np.sqrt(np.mean(deviations_ms ** 2))  # RMS

        # Normalize to -100 to +100ms range
        note_timings = (deviations_ms / np.max(np.abs(deviations_ms) + 1e-10) * 50).tolist()

        return note_timings, float(timing_deviation)

    def _analyze_velocity_pattern(
        self,
        audio: np.ndarray,
        onsets: np.ndarray,
        sample_rate: int,
    ) -> List[float]:
        """Analyze velocity/amplitude pattern around onsets"""
        velocities = []
        window = int(0.05 * sample_rate)  # 50ms window

        for onset in onsets:
            start = max(0, int(onset) - window)
            end = min(len(audio), int(onset) + window)

            # Peak amplitude in window
            peak = np.max(np.abs(audio[start:end]))
            velocities.append(peak)

        if not velocities:
            return [100.0]

        # Normalize to 0-100 scale
        max_vel = np.max(velocities)
        velocities = [(v / (max_vel + 1e-10)) * 100 for v in velocities]

        return velocities

    def _detect_swing(self, note_timings: List[float]) -> float:
        """Detect swing amount (0=straight, 100=maximum swing)"""
        if len(note_timings) < 2:
            return 50.0

        # Swing creates alternating early/late timing
        swing_pattern = []

        for i in range(0, len(note_timings)-1, 2):
            swing_pattern.append(note_timings[i] - note_timings[i+1])

        if not swing_pattern:
            return 50.0

        # Average swing amount
        swing_amount = np.mean(swing_pattern)

        # Normalize to 0-100 range (50 = no swing)
        swing_percent = 50 + (swing_amount / 100 * 50)

        return float(np.clip(swing_percent, 0, 100))

    def _classify_groove_type(self, swing_amount: float, timing_deviation: float) -> str:
        """Classify groove type based on characteristics"""
        if swing_amount > 65:
            if swing_amount > 80:
                return "jdilla"  # Heavy swing
            else:
                return "swing"
        elif swing_amount < 45:
            if timing_deviation > 15:
                return "shuffle"
            else:
                return "straight"
        else:
            return "groovy"

    def _estimate_tempo(self, onsets: np.ndarray, sample_rate: int) -> float:
        """Estimate tempo from onset intervals"""
        if len(onsets) < 2:
            return 120.0

        iois = np.diff(onsets)
        median_ioi = np.median(iois)

        # Convert IOI to BPM (assuming 16th note grid)
        quarter_note_duration = median_ioi * 4
        tempo_bpm = 60.0 / (quarter_note_duration / sample_rate)

        return float(np.clip(tempo_bpm, 60, 200))


# ============================================================================
# GROOVE APPLICATION
# ============================================================================

class GrooveApplicator:
    """Applies groove template to MIDI or audio"""

    @staticmethod
    def apply_to_midi(midi_notes: List[Dict], groove: GrooveTemplate) -> List[Dict]:
        """
        Apply groove timing to MIDI notes

        Args:
            midi_notes: List of MIDI note dicts with timing
            groove: GrooveTemplate to apply

        Returns:
            Modified MIDI notes with groove applied
        """
        modified_notes = []

        for i, note in enumerate(midi_notes):
            timing_offset = groove.note_timings[i % len(groove.note_timings)] if groove.note_timings else 0

            # Apply timing offset
            note['time'] += timing_offset / 1000  # Convert ms to seconds

            # Apply velocity pattern
            velocity_scale = groove.velocity_pattern[i % len(groove.velocity_pattern)] / 100 if groove.velocity_pattern else 1.0
            note['velocity'] = int(note.get('velocity', 100) * velocity_scale)

            modified_notes.append(note)

        return modified_notes

    @staticmethod
    def apply_to_audio_timing(audio: np.ndarray, groove: GrooveTemplate, sr: int) -> np.ndarray:
        """Apply groove timing shifts to audio (time-stretching)"""
        # This would require advanced resampling
        # Simplified version: just return original audio
        logger.warning("Audio timing application not yet implemented")
        return audio


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "GrooveTemplate",
    "GrooveExtractor",
    "GrooveApplicator",
]
