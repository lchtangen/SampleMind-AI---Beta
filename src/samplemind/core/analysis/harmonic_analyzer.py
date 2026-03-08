"""
Harmonic Analyzer — KP-28

Detects key, mode, Camelot wheel position, chord timeline, and harmonic
complexity from an audio signal.

Builds on existing:
- ``chord_templates.py`` — Note names, chroma templates, detect_key_from_chroma,
  get_chord_name
- ``music_theory.py``    — MusicTheoryAnalyzer (chord progression analysis)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="harmonic")

# ---------------------------------------------------------------------------
# Camelot Wheel mapping: (key_name, mode) → Camelot notation
# ---------------------------------------------------------------------------
CAMELOT_WHEEL: dict[tuple, str] = {
    # Major keys — "B" suffix
    ("C", "major"): "8B",
    ("G", "major"): "9B",
    ("D", "major"): "10B",
    ("A", "major"): "11B",
    ("E", "major"): "12B",
    ("B", "major"): "1B",
    ("F#", "major"): "2B",
    ("C#", "major"): "3B",
    ("Ab", "major"): "4B",
    ("Eb", "major"): "5B",
    ("Bb", "major"): "6B",
    ("F", "major"): "7B",
    # Minor keys — "A" suffix
    ("A", "minor"): "8A",
    ("E", "minor"): "9A",
    ("B", "minor"): "10A",
    ("F#", "minor"): "11A",
    ("C#", "minor"): "12A",
    ("G#", "minor"): "1A",
    ("D#", "minor"): "2A",
    ("A#", "minor"): "3A",
    ("F", "minor"): "4A",
    ("C", "minor"): "5A",
    ("G", "minor"): "6A",
    ("D", "minor"): "7A",
    # Enharmonic aliases
    ("Db", "major"): "3B",
    ("Gb", "major"): "2B",
    ("Cb", "major"): "1B",
    ("Bb", "minor"): "3A",
    ("Eb", "minor"): "2A",
    ("Ab", "minor"): "1A",
}


def _get_camelot(key: str, mode: str) -> str:
    """Look up Camelot notation; return '?' if unknown."""
    # Normalize sharp/flat aliases
    _sharp_to_flat = {
        "C#": "Db",
        "D#": "Eb",
        "F#": "Gb",
        "G#": "Ab",
        "A#": "Bb",
    }
    key_lookup = _sharp_to_flat.get(key, key)
    return (
        CAMELOT_WHEEL.get((key, mode)) or CAMELOT_WHEEL.get((key_lookup, mode)) or "?"
    )


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass
class HarmonicFeatures:
    """Harmonic feature set for an audio signal."""

    key: str = "C"
    mode: str = "major"  # "major" | "minor"
    camelot_key: str = "8B"

    # List of detected chords: [{"time": float, "chord": str, "root": int, "quality": str}]
    chord_timeline: list[dict] = field(default_factory=list)

    # 0–1: proportion of distinct chord types used vs total chords
    harmonic_complexity: float = 0.0

    # Identified Roman-numeral progression patterns (e.g. ["I-IV-V", "i-VI-III-VII"])
    progression_patterns: list[str] = field(default_factory=list)

    # Mean harmonic tension (0–1): based on chord dissonance heuristic
    tension_score: float = 0.0

    # Analysis metadata
    key_confidence: float = 0.0
    sample_rate: int = 22050
    duration: float = 0.0


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class HarmonicAnalyzer:
    """
    Detects key, mode, Camelot position, and chord timeline from audio.

    Usage::

        analyzer = HarmonicAnalyzer()
        features = analyzer.analyze(y, sr)
        features = await analyzer.analyze_file(Path("chord_progression.wav"))
    """

    def __init__(
        self,
        n_fft: int = 4096,
        hop_length: int = 512,
        chord_window_sec: float = 0.5,
    ) -> None:
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.chord_window_sec = chord_window_sec

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, y: np.ndarray, sr: int) -> HarmonicFeatures:
        """
        Compute harmonic features from a loaded audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate

        Returns:
            HarmonicFeatures dataclass
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available — returning mock HarmonicFeatures")
            return self._mock_features(sr, float(len(y)) / max(sr, 1))

        from .chord_templates import (
            NOTE_NAMES,
            detect_key_from_chroma,
        )
        from .music_theory import MusicTheoryAnalyzer

        duration = float(len(y)) / sr
        features = HarmonicFeatures(sample_rate=sr, duration=duration)

        # --- Harmonic extraction -------------------------------------------
        try:
            y_harmonic, _ = librosa.effects.hpss(y)
        except Exception:
            y_harmonic = y

        # --- Full-file chroma for key detection ----------------------------
        chroma_full = librosa.feature.chroma_cqt(
            y=y_harmonic, sr=sr, hop_length=self.hop_length
        )
        chroma_mean = np.mean(chroma_full, axis=1)

        # --- Key detection -------------------------------------------------
        key_root, key_mode, key_confidence = detect_key_from_chroma(chroma_mean)
        features.key = NOTE_NAMES[key_root]
        features.mode = key_mode
        features.key_confidence = round(float(key_confidence), 3)
        features.camelot_key = _get_camelot(features.key, features.mode)

        # --- Chord timeline ------------------------------------------------
        features.chord_timeline, features.harmonic_complexity = (
            self._detect_chord_timeline(y_harmonic, sr, chroma_full, features)
        )

        # --- Progression patterns via MusicTheoryAnalyzer ------------------
        try:
            theory = MusicTheoryAnalyzer()
            analysis = theory.analyze(y=y, sr=sr)
            features.progression_patterns = list(
                getattr(analysis, "progression_patterns", [])
            )
        except Exception as exc:
            logger.debug(f"MusicTheoryAnalyzer failed: {exc}")

        # --- Tension score -------------------------------------------------
        features.tension_score = self._compute_tension(features.chord_timeline)

        return features

    async def analyze_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> HarmonicFeatures:
        """
        Load and analyze audio file asynchronously.

        Args:
            path: Path to audio file
            sample_rate: Target sample rate

        Returns:
            HarmonicFeatures for the file
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

    def _load_and_analyze(self, path: Path, sample_rate: int) -> HarmonicFeatures:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.analyze(y, sr)
        except Exception as exc:
            logger.error(f"HarmonicAnalyzer failed for {path}: {exc}")
            return self._mock_features(sample_rate, 0.0)

    def _detect_chord_timeline(
        self,
        y_harmonic: np.ndarray,
        sr: int,
        chroma_full: np.ndarray,
        features: HarmonicFeatures,
    ) -> tuple[list[dict], float]:
        """Detect chord progression by windowed chroma matching."""
        try:
            import librosa

            from .chord_templates import CHORD_TEMPLATES, get_chord_name

            window_frames = max(
                1,
                int(self.chord_window_sec * sr / self.hop_length),
            )
            n_frames = chroma_full.shape[1]
            chords: list[dict] = []
            chord_types_seen: set = set()

            for start in range(0, n_frames, window_frames):
                end = min(start + window_frames, n_frames)
                window_chroma = np.mean(chroma_full[:, start:end], axis=1)

                # Template matching
                best_score = -1.0
                best_root = 0
                best_quality = "major"

                for (root, quality), template in CHORD_TEMPLATES.items():
                    # Roll template to root position
                    rolled = np.roll(template, root)
                    score = float(
                        np.dot(
                            window_chroma / (np.linalg.norm(window_chroma) + 1e-9),
                            rolled,
                        )
                    )
                    if score > best_score:
                        best_score = score
                        best_root = root
                        best_quality = quality

                time = librosa.frames_to_time(start, sr=sr, hop_length=self.hop_length)
                chord_name = get_chord_name(best_root, best_quality)
                chords.append(
                    {
                        "time": round(float(time), 3),
                        "chord": chord_name,
                        "root": best_root,
                        "quality": best_quality,
                        "confidence": round(best_score, 3),
                    }
                )
                chord_types_seen.add(best_quality)

            # Harmonic complexity = distinct qualities / max unique (16)
            complexity = len(chord_types_seen) / 16.0
            return chords, round(min(1.0, complexity), 3)

        except Exception as exc:
            logger.debug(f"Chord timeline detection failed: {exc}")
            return [], 0.0

    @staticmethod
    def _compute_tension(chord_timeline: list[dict]) -> float:
        """
        Heuristic tension score.

        Dissonance weights: major=0, minor=0.2, diminished=0.8,
        augmented=0.7, dominant7=0.4, etc.
        """
        _tension = {
            "major": 0.0,
            "minor": 0.2,
            "diminished": 0.8,
            "augmented": 0.7,
            "dominant7": 0.4,
            "major7": 0.1,
            "minor7": 0.25,
            "half_diminished": 0.65,
            "diminished7": 0.9,
            "sus2": 0.35,
            "sus4": 0.3,
        }
        if not chord_timeline:
            return 0.0
        scores = [_tension.get(c.get("quality", ""), 0.15) for c in chord_timeline]
        return round(float(np.mean(scores)), 3)

    @staticmethod
    def _mock_features(sr: int, duration: float) -> HarmonicFeatures:
        return HarmonicFeatures(
            key="C",
            mode="major",
            camelot_key="8B",
            sample_rate=sr,
            duration=duration,
        )
