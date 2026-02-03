"""
Music Theory Analyzer

Provides comprehensive harmonic analysis of audio files including:
- Chord progression detection using chroma features
- Key detection with the Krumhansl-Kessler algorithm
- Modulation detection
- Roman numeral functional analysis
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

from .chord_templates import (
    NOTE_NAMES,
    CHORD_TEMPLATES,
    CHORD_SYMBOLS,
    KEY_PROFILES,
    get_chord_template,
    get_chord_name,
    get_roman_numeral,
    detect_key_from_chroma,
)

logger = logging.getLogger(__name__)


@dataclass
class ChordEvent:
    """A detected chord at a specific time"""
    start_time: float       # Start time in seconds
    end_time: float         # End time in seconds
    chord: str              # Full chord name (e.g., "Am7")
    root: int               # Root pitch class (0-11)
    root_name: str          # Root note name (e.g., "A")
    quality: str            # Chord quality (e.g., "minor7")
    confidence: float       # Detection confidence (0-1)
    roman_numeral: str = "" # Roman numeral in context of key

    @property
    def duration(self) -> float:
        """Duration in seconds"""
        return self.end_time - self.start_time


@dataclass
class Modulation:
    """A detected key change"""
    time: float            # Time of modulation in seconds
    from_key: str          # Previous key (e.g., "C major")
    to_key: str            # New key (e.g., "G major")
    pivot_chord: Optional[str] = None  # Pivot chord if detected


@dataclass
class HarmonicAnalysis:
    """Complete harmonic analysis of an audio file"""
    key: str                           # Detected key (e.g., "C major")
    key_root: int                      # Key root pitch class
    key_mode: str                      # "major" or "minor"
    key_confidence: float              # Key detection confidence
    chord_progression: List[ChordEvent] = field(default_factory=list)
    modulations: List[Modulation] = field(default_factory=list)
    harmonic_rhythm: float = 0.0       # Average chord changes per bar
    duration: float = 0.0              # Total duration analyzed

    @property
    def chord_sequence(self) -> List[str]:
        """Simple list of chord names"""
        return [c.chord for c in self.chord_progression]

    @property
    def roman_sequence(self) -> List[str]:
        """Simple list of Roman numerals"""
        return [c.roman_numeral for c in self.chord_progression]


class MusicTheoryAnalyzer:
    """
    Analyzes audio files for harmonic content.

    Uses chroma features and music theory templates to detect:
    - Overall key
    - Chord progressions
    - Key modulations
    """

    def __init__(
        self,
        hop_length: int = 512,
        min_chord_duration: float = 0.25,
        chord_change_threshold: float = 0.3,
    ):
        """
        Initialize the analyzer.

        Args:
            hop_length: Hop length for feature extraction
            min_chord_duration: Minimum chord duration in seconds
            chord_change_threshold: Threshold for detecting chord changes
        """
        self.hop_length = hop_length
        self.min_chord_duration = min_chord_duration
        self.chord_change_threshold = chord_change_threshold

    def analyze(self, file_path: Path) -> HarmonicAnalysis:
        """
        Perform complete harmonic analysis on an audio file.

        Args:
            file_path: Path to audio file

        Returns:
            HarmonicAnalysis with key, chords, and modulations
        """
        import librosa

        file_path = Path(file_path).expanduser().resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        logger.info(f"Analyzing harmony: {file_path.name}")

        # Load audio
        y, sr = librosa.load(file_path, sr=22050, mono=True)
        duration = len(y) / sr

        # Extract chroma features
        chroma = librosa.feature.chroma_cqt(
            y=y, sr=sr, hop_length=self.hop_length
        )

        # Detect overall key
        chroma_mean = np.mean(chroma, axis=1)
        key_root, key_mode, key_confidence = detect_key_from_chroma(chroma_mean)
        key_name = f"{NOTE_NAMES[key_root]} {key_mode}"

        # Detect chord progression
        chords = self._detect_chords(chroma, sr, key_root, key_mode)

        # Detect modulations
        modulations = self._detect_modulations(chroma, sr, key_root, key_mode)

        # Calculate harmonic rhythm (changes per beat)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if duration > 0 and tempo > 0:
            beats_total = (duration / 60) * tempo
            harmonic_rhythm = len(chords) / max(beats_total / 4, 1)  # Changes per bar
        else:
            harmonic_rhythm = 0.0

        return HarmonicAnalysis(
            key=key_name,
            key_root=key_root,
            key_mode=key_mode,
            key_confidence=key_confidence,
            chord_progression=chords,
            modulations=modulations,
            harmonic_rhythm=harmonic_rhythm,
            duration=duration,
        )

    def detect_key(self, file_path: Path) -> Tuple[str, float]:
        """
        Detect only the key of an audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (key_name, confidence)
        """
        import librosa

        file_path = Path(file_path).expanduser().resolve()
        y, sr = librosa.load(file_path, sr=22050, mono=True)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        key_root, key_mode, confidence = detect_key_from_chroma(chroma_mean)
        key_name = f"{NOTE_NAMES[key_root]} {key_mode}"

        return key_name, confidence

    def detect_chords(self, file_path: Path) -> List[ChordEvent]:
        """
        Detect only the chord progression.

        Args:
            file_path: Path to audio file

        Returns:
            List of ChordEvent objects
        """
        import librosa

        file_path = Path(file_path).expanduser().resolve()
        y, sr = librosa.load(file_path, sr=22050, mono=True)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
        chroma_mean = np.mean(chroma, axis=1)
        key_root, key_mode, _ = detect_key_from_chroma(chroma_mean)

        return self._detect_chords(chroma, sr, key_root, key_mode)

    def _detect_chords(
        self,
        chroma: np.ndarray,
        sr: int,
        key_root: int,
        key_mode: str,
    ) -> List[ChordEvent]:
        """
        Internal chord detection from chroma features.

        Args:
            chroma: Chroma feature matrix (12 x frames)
            sr: Sample rate
            key_root: Key root pitch class
            key_mode: Key mode ('major' or 'minor')

        Returns:
            List of ChordEvent objects
        """
        n_frames = chroma.shape[1]
        frame_duration = self.hop_length / sr
        min_frames = int(self.min_chord_duration / frame_duration)

        chords = []
        current_chord = None
        chord_start = 0

        # Chord qualities to try (in order of likelihood)
        qualities = ['major', 'minor', 'dominant7', 'minor7', 'major7', 'diminished', 'sus4']

        for frame in range(n_frames):
            # Get chroma vector for this frame
            frame_chroma = chroma[:, frame]

            # Find best matching chord
            best_chord = None
            best_correlation = -1

            for root in range(12):
                for quality in qualities:
                    template = get_chord_template(root, quality)
                    correlation = np.dot(frame_chroma, template)

                    if correlation > best_correlation:
                        best_correlation = correlation
                        best_chord = (root, quality, correlation)

            if best_chord:
                root, quality, correlation = best_chord
                chord_name = get_chord_name(root, quality)

                # Check if chord changed
                if current_chord is None or current_chord != chord_name:
                    # Save previous chord if it meets minimum duration
                    if current_chord is not None:
                        frames_duration = frame - chord_start
                        if frames_duration >= min_frames:
                            roman = get_roman_numeral(
                                prev_root, key_root, key_mode, prev_quality
                            )
                            chords.append(ChordEvent(
                                start_time=chord_start * frame_duration,
                                end_time=frame * frame_duration,
                                chord=current_chord,
                                root=prev_root,
                                root_name=NOTE_NAMES[prev_root],
                                quality=prev_quality,
                                confidence=prev_confidence,
                                roman_numeral=roman,
                            ))

                    # Start new chord
                    current_chord = chord_name
                    chord_start = frame
                    prev_root = root
                    prev_quality = quality
                    prev_confidence = correlation

        # Don't forget last chord
        if current_chord is not None:
            frames_duration = n_frames - chord_start
            if frames_duration >= min_frames:
                roman = get_roman_numeral(prev_root, key_root, key_mode, prev_quality)
                chords.append(ChordEvent(
                    start_time=chord_start * frame_duration,
                    end_time=n_frames * frame_duration,
                    chord=current_chord,
                    root=prev_root,
                    root_name=NOTE_NAMES[prev_root],
                    quality=prev_quality,
                    confidence=prev_confidence,
                    roman_numeral=roman,
                ))

        return chords

    def _detect_modulations(
        self,
        chroma: np.ndarray,
        sr: int,
        initial_key_root: int,
        initial_key_mode: str,
    ) -> List[Modulation]:
        """
        Detect key modulations within the piece.

        Uses a sliding window approach to find key changes.

        Args:
            chroma: Chroma feature matrix
            sr: Sample rate
            initial_key_root: Initial key root
            initial_key_mode: Initial key mode

        Returns:
            List of Modulation objects
        """
        modulations = []
        n_frames = chroma.shape[1]
        frame_duration = self.hop_length / sr

        # Window size for key detection (about 4 seconds)
        window_size = int(4.0 / frame_duration)
        hop = window_size // 2

        current_key_root = initial_key_root
        current_key_mode = initial_key_mode

        for start in range(0, n_frames - window_size, hop):
            end = start + window_size
            window_chroma = np.mean(chroma[:, start:end], axis=1)

            key_root, key_mode, confidence = detect_key_from_chroma(window_chroma)

            # Check for modulation (key change with high confidence)
            if confidence > 0.6 and (key_root != current_key_root or key_mode != current_key_mode):
                time = (start + window_size // 2) * frame_duration
                from_key = f"{NOTE_NAMES[current_key_root]} {current_key_mode}"
                to_key = f"{NOTE_NAMES[key_root]} {key_mode}"

                modulations.append(Modulation(
                    time=time,
                    from_key=from_key,
                    to_key=to_key,
                ))

                current_key_root = key_root
                current_key_mode = key_mode

        return modulations

    def get_scale_notes(self, key_root: int, key_mode: str) -> List[str]:
        """
        Get the notes in a scale.

        Args:
            key_root: Root pitch class (0-11)
            key_mode: 'major' or 'minor'

        Returns:
            List of note names in the scale
        """
        if key_mode == 'major':
            intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale intervals
        else:
            intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale intervals

        return [NOTE_NAMES[(key_root + i) % 12] for i in intervals]
