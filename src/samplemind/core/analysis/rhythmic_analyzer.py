"""
Rhythmic Analyzer — KP-27

Beat tracking with librosa primary + optional madmom (if installed) for
improved accuracy via weighted confidence voting.

Computes:
- BPM with confidence score
- Beat and onset times
- Tempo stability, time signature estimate
- 16-step grid pattern (onset quantization)
- Syncopation score
- Duration class: one_shot | loop | pad | texture
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="rhythmic")

# Weights for BPM confidence voting when both librosa and madmom produce results
_MADMOM_WEIGHT = 0.6
_LIBROSA_WEIGHT = 0.4


@dataclass
class RhythmicFeatures:
    """Rhythmic feature set extracted from an audio signal."""

    bpm: float = 0.0
    bpm_confidence: float = 0.0  # 0–1

    beat_times: list[float] = field(default_factory=list)  # seconds
    onset_times: list[float] = field(default_factory=list)  # seconds

    # Coefficient of variation of inter-beat intervals (lower = more stable)
    tempo_stability: float = 0.0  # 0–1 (1 = perfectly stable)

    time_signature: str = "4/4"

    # 16-step onset grid (1 = onset present, 0 = silent)
    grid_pattern: list[int] = field(default_factory=lambda: [0] * 16)

    # Fraction of onsets that land off the main beat grid
    syncopation_score: float = 0.0  # 0–1

    # Heuristic duration type
    duration_class: str = "unknown"  # one_shot | loop | pad | texture | unknown

    # Analysis metadata
    sample_rate: int = 22050
    duration: float = 0.0
    used_madmom: bool = False


class RhythmicAnalyzer:
    """
    Extracts rhythmic features from audio signals.

    When *madmom* is installed, beat tracking results from both librosa
    and madmom are combined via weighted voting for higher accuracy.

    Usage::

        analyzer = RhythmicAnalyzer()
        features = analyzer.analyze(y, sr)
        features = await analyzer.analyze_file(Path("loop.wav"))
    """

    def __init__(self, hop_length: int = 512) -> None:
        self.hop_length = hop_length

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, y: np.ndarray, sr: int) -> RhythmicFeatures:
        """
        Compute rhythmic features from a loaded audio signal.

        Args:
            y: Audio time-series (mono, float32)
            sr: Sample rate in Hz

        Returns:
            RhythmicFeatures dataclass
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available — returning mock RhythmicFeatures")
            return RhythmicFeatures(sample_rate=sr, duration=float(len(y)) / max(sr, 1))

        duration = float(len(y)) / sr
        features = RhythmicFeatures(sample_rate=sr, duration=duration)

        # --- Onset envelope -------------------------------------------------
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)

        # --- librosa beat tracking ------------------------------------------
        tempo_lib, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
        )
        bpm_librosa = (
            float(tempo_lib) if np.isscalar(tempo_lib) else float(tempo_lib[0])
        )
        beat_times_lib = librosa.frames_to_time(
            beat_frames, sr=sr, hop_length=self.hop_length
        )

        # Pulse LP (probabilistic) for confidence estimate
        try:
            plp = librosa.beat.plp(
                onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
            )
            bpm_confidence_lib = float(np.mean(plp))
        except Exception:
            bpm_confidence_lib = 0.5

        # --- Optional madmom beat tracking ----------------------------------
        bpm_madmom: float | None = None
        beat_times_madmom: np.ndarray | None = None
        features.used_madmom = False

        try:
            from madmom.features.beats import BeatTrackingProcessor, RNNBeatProcessor

            rnn_proc = RNNBeatProcessor()
            beat_proc = BeatTrackingProcessor(fps=100)

            # madmom operates on files; work from the signal via temp array
            import os
            import tempfile

            import soundfile as sf

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            sf.write(tmp_path, y, sr)
            try:
                rnn_act = rnn_proc(tmp_path)
                beat_times_madmom = beat_proc(rnn_act)
                if len(beat_times_madmom) > 1:
                    ibi = np.diff(beat_times_madmom)
                    bpm_madmom = 60.0 / float(np.median(ibi))
                    features.used_madmom = True
            finally:
                os.unlink(tmp_path)

        except (ImportError, Exception) as exc:
            if "madmom" not in str(type(exc).__module__):
                logger.debug(f"madmom beat tracking failed: {exc}")

        # --- Weighted BPM vote ----------------------------------------------
        if bpm_madmom is not None and features.used_madmom:
            weighted_bpm = _MADMOM_WEIGHT * bpm_madmom + _LIBROSA_WEIGHT * bpm_librosa
            features.bpm = round(weighted_bpm, 2)
            features.bpm_confidence = min(1.0, bpm_confidence_lib + 0.2)
            # Use madmom beat times (typically more accurate at boundaries)
            beat_times = beat_times_madmom
        else:
            features.bpm = round(bpm_librosa, 2)
            features.bpm_confidence = round(
                float(np.clip(bpm_confidence_lib, 0.0, 1.0)), 3
            )
            beat_times = beat_times_lib

        features.beat_times = (
            beat_times.tolist()
            if isinstance(beat_times, np.ndarray)
            else list(beat_times)
        )

        # --- Onset detection ------------------------------------------------
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop_length,
            backtrack=True,
        )
        features.onset_times = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=self.hop_length
        ).tolist()

        # --- Tempo stability ------------------------------------------------
        if len(features.beat_times) > 2:
            ibis = np.diff(features.beat_times)
            cv = float(np.std(ibis) / (np.mean(ibis) + 1e-9))
            features.tempo_stability = round(float(np.clip(1.0 - cv, 0.0, 1.0)), 3)
        else:
            features.tempo_stability = 0.0

        # --- Time signature estimate ----------------------------------------
        features.time_signature = self._estimate_time_signature(
            features.beat_times, features.onset_times
        )

        # --- 16-step grid ---------------------------------------------------
        features.grid_pattern = self._build_grid_pattern(
            features.onset_times, duration, features.bpm
        )

        # --- Syncopation score ----------------------------------------------
        features.syncopation_score = self._compute_syncopation(features.grid_pattern)

        # --- Duration class -------------------------------------------------
        features.duration_class = self._classify_duration(features.onset_times, y, sr)

        return features

    async def analyze_file(
        self,
        path: Path,
        sample_rate: int = 22050,
    ) -> RhythmicFeatures:
        """
        Load and analyze an audio file asynchronously.

        Args:
            path: Path to the audio file
            sample_rate: Target sample rate

        Returns:
            RhythmicFeatures for the file
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

    def _load_and_analyze(self, path: Path, sample_rate: int) -> RhythmicFeatures:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.analyze(y, sr)
        except Exception as exc:
            logger.error(f"RhythmicAnalyzer failed for {path}: {exc}")
            return RhythmicFeatures(sample_rate=sample_rate, duration=0.0)

    @staticmethod
    def _estimate_time_signature(
        beat_times: list[float],
        onset_times: list[float],
    ) -> str:
        """Heuristic: count onsets per beat and infer numerator."""
        if len(beat_times) < 2:
            return "4/4"
        try:
            avg_ibi = float(np.mean(np.diff(beat_times)))
            if avg_ibi <= 0:
                return "4/4"
            # Group onsets into beats
            counts = []
            for i in range(len(beat_times) - 1):
                start, end = beat_times[i], beat_times[i + 1]
                n = sum(1 for t in onset_times if start <= t < end)
                counts.append(n)
            median_count = int(np.median(counts)) if counts else 4
            if median_count <= 2:
                return "2/4"
            elif median_count >= 6:
                return "6/8"
            elif median_count == 3:
                return "3/4"
            return "4/4"
        except Exception:
            return "4/4"

    @staticmethod
    def _build_grid_pattern(
        onset_times: list[float],
        duration: float,
        bpm: float,
    ) -> list[int]:
        """Quantize onsets onto a 16-step grid."""
        grid = [0] * 16
        if bpm <= 0 or duration <= 0 or not onset_times:
            return grid

        # Determine grid step duration based on 4/4 assumption (16th notes)
        beat_duration = 60.0 / bpm
        bar_duration = beat_duration * 4
        # Use first bar length
        bar_dur = min(bar_duration, duration)
        if bar_dur <= 0:
            return grid

        step_dur = bar_dur / 16.0
        for t in onset_times:
            if t >= bar_dur:
                continue
            step = int(t / step_dur)
            if 0 <= step < 16:
                grid[step] = 1

        return grid

    @staticmethod
    def _compute_syncopation(grid: list[int]) -> float:
        """
        Compute syncopation score as the fraction of off-beat onsets.

        Positions 0, 4, 8, 12 are main beats in 4/4.
        """
        if not any(grid):
            return 0.0
        strong_beats = {0, 4, 8, 12}
        on_beat = sum(grid[i] for i in strong_beats)
        total = sum(grid)
        if total == 0:
            return 0.0
        off_beat = total - on_beat
        return round(float(off_beat) / total, 3)

    @staticmethod
    def _classify_duration(
        onset_times: list[float],
        y: np.ndarray,
        sr: int,
    ) -> str:
        """
        Heuristic duration-class classifier.

        one_shot  — single transient, short (<3 s), onset at start
        loop      — multiple onsets, duration near a bar length
        pad       — few onsets, long, sustained
        texture   — many onsets spread throughout
        """
        duration = len(y) / max(sr, 1)
        n_onsets = len(onset_times)

        if duration < 3.0 and n_onsets <= 2:
            return "one_shot"

        if n_onsets > 8 and duration < 10.0:
            return "loop"

        if duration >= 3.0 and n_onsets <= 4:
            return "pad"

        if n_onsets > 16:
            return "texture"

        return "loop" if duration <= 8.0 else "pad"
