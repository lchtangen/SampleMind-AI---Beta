"""
Micro-Timing Analyzer — P4-006

Analyzes micro-timing deviations, groove feel, humanization, and rhythmic
nuance in audio samples. Goes beyond BPM detection to capture the *feel*
of a performance.

Capabilities:
  - Swing ratio detection (straight/shuffle/bounce/J Dilla)
  - Pocket quality scoring (how well the performance sits in the groove)
  - Ghost note detection (low-velocity hits between main beats)
  - Human feel scoring (machine-quantized vs human-played spectrum)
  - Groove DNA fingerprint (compact rhythmic signature for similarity)
  - Micro-timing deviation histogram per beat subdivision

Usage::

    from samplemind.core.analysis.micro_timing_analyzer import MicroTimingAnalyzer

    analyzer = MicroTimingAnalyzer()
    result = analyzer.analyze(y, sr)
    # or async:
    result = await analyzer.analyze_file(Path("loop.wav"))
"""

from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="microtiming")


# ── Result dataclasses ───────────────────────────────────────────────────────


@dataclass
class SwingProfile:
    """Swing characteristics of a rhythmic pattern."""

    ratio: float = 0.5  # 0.5 = straight, 0.67 = triplet swing, >0.7 = heavy swing
    style: str = "straight"  # straight | light_swing | shuffle | bounce | heavy_swing
    consistency: float = 0.0  # How consistent the swing is (0–1)
    description: str = ""


@dataclass
class GhostNoteProfile:
    """Ghost note (low-velocity inter-beat hit) characteristics."""

    count: int = 0
    density: float = 0.0  # Ghost notes per beat
    avg_velocity_ratio: float = 0.0  # Avg ghost velocity / avg main velocity
    positions: list[float] = field(default_factory=list)  # Time positions in seconds


@dataclass
class PocketProfile:
    """How well the performance sits in the rhythmic 'pocket'."""

    score: float = 0.0  # 0–1, 1 = perfectly in the pocket
    tightness: float = 0.0  # How close to the grid (0–1)
    consistency: float = 0.0  # How consistent the timing deviations are (0–1)
    feel: str = "neutral"  # ahead | on_top | behind | neutral
    description: str = ""


@dataclass
class MicroTimingResult:
    """Complete micro-timing analysis result."""

    # Swing
    swing: SwingProfile = field(default_factory=SwingProfile)

    # Ghost notes
    ghost_notes: GhostNoteProfile = field(default_factory=GhostNoteProfile)

    # Pocket feel
    pocket: PocketProfile = field(default_factory=PocketProfile)

    # Human feel score: 0 = perfectly quantized machine, 1 = human performance
    human_feel_score: float = 0.0

    # Groove DNA: compact 32-char hex fingerprint of rhythmic signature
    groove_dna: str = ""

    # Per-subdivision timing deviations (16th note grid, in milliseconds)
    subdivision_deviations_ms: list[float] = field(default_factory=list)

    # Overall timing deviation RMS (ms)
    timing_rms_ms: float = 0.0

    # Velocity contour: relative velocity per 16th-note step (0–1 scale)
    velocity_contour: list[float] = field(default_factory=list)

    # Analysis metadata
    bpm: float = 0.0
    duration: float = 0.0
    sample_rate: int = 22050
    onset_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "swing": {
                "ratio": self.swing.ratio,
                "style": self.swing.style,
                "consistency": self.swing.consistency,
                "description": self.swing.description,
            },
            "ghost_notes": {
                "count": self.ghost_notes.count,
                "density": self.ghost_notes.density,
                "avg_velocity_ratio": self.ghost_notes.avg_velocity_ratio,
            },
            "pocket": {
                "score": self.pocket.score,
                "tightness": self.pocket.tightness,
                "consistency": self.pocket.consistency,
                "feel": self.pocket.feel,
                "description": self.pocket.description,
            },
            "human_feel_score": self.human_feel_score,
            "groove_dna": self.groove_dna,
            "subdivision_deviations_ms": self.subdivision_deviations_ms,
            "timing_rms_ms": self.timing_rms_ms,
            "velocity_contour": self.velocity_contour,
            "bpm": self.bpm,
            "duration": self.duration,
            "onset_count": self.onset_count,
        }


# ── Analyzer ─────────────────────────────────────────────────────────────────


class MicroTimingAnalyzer:
    """
    Analyzes micro-timing characteristics of audio performances.

    Goes beyond standard BPM/beat detection to quantify the *feel* of a
    rhythm — swing, pocket, ghost notes, and humanization.
    """

    def __init__(self, hop_length: int = 512) -> None:
        self.hop_length = hop_length

    # ── Public API ────────────────────────────────────────────────────────

    def analyze(
        self, y: np.ndarray, sr: int, bpm: float | None = None
    ) -> MicroTimingResult:
        """
        Analyze micro-timing from a loaded audio signal.

        Args:
            y: Audio time-series (mono, float32).
            sr: Sample rate in Hz.
            bpm: Optional BPM (auto-detected if None).

        Returns:
            MicroTimingResult with full analysis.
        """
        try:
            import librosa
        except ImportError:
            logger.warning(
                "librosa not available — returning empty MicroTimingResult"
            )
            return MicroTimingResult(
                sample_rate=sr, duration=float(len(y)) / max(sr, 1)
            )

        duration = float(len(y)) / sr
        result = MicroTimingResult(sample_rate=sr, duration=duration)

        # --- Beat tracking ----------------------------------------------------
        onset_env = librosa.onset.onset_strength(
            y=y, sr=sr, hop_length=self.hop_length
        )
        if bpm is None:
            tempo, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env, sr=sr, hop_length=self.hop_length
            )
            bpm = (
                float(tempo) if np.isscalar(tempo) else float(tempo[0])
            )
        else:
            _, beat_frames = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=self.hop_length,
                bpm=bpm,
            )

        result.bpm = round(bpm, 2)
        beat_times = librosa.frames_to_time(
            beat_frames, sr=sr, hop_length=self.hop_length
        )

        # --- Onset detection with strength ------------------------------------
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop_length,
            backtrack=False,
        )
        onset_times = librosa.frames_to_time(
            onset_frames, sr=sr, hop_length=self.hop_length
        )
        onset_strengths = (
            onset_env[onset_frames]
            if len(onset_frames) > 0
            else np.array([])
        )
        result.onset_count = len(onset_times)

        if len(onset_times) < 2 or len(beat_times) < 2:
            return result

        # --- Subdivision grid (16th notes) ------------------------------------
        beat_duration = 60.0 / bpm
        sixteenth = beat_duration / 4.0

        # Build ideal grid spanning the audio
        grid_start = beat_times[0] if len(beat_times) > 0 else 0.0
        grid_end = min(duration, grid_start + beat_duration * len(beat_times))
        ideal_grid = np.arange(grid_start, grid_end, sixteenth)

        # --- Map onsets to nearest grid point ---------------------------------
        deviations_ms: list[float] = []
        for onset_t in onset_times:
            if len(ideal_grid) == 0:
                break
            nearest_idx = int(np.argmin(np.abs(ideal_grid - onset_t)))
            dev_ms = (onset_t - ideal_grid[nearest_idx]) * 1000.0
            deviations_ms.append(round(dev_ms, 2))

        result.subdivision_deviations_ms = deviations_ms
        if deviations_ms:
            result.timing_rms_ms = round(
                float(np.sqrt(np.mean(np.array(deviations_ms) ** 2))), 2
            )

        # --- Swing analysis ---------------------------------------------------
        result.swing = self._analyze_swing(onset_times, beat_times, bpm)

        # --- Ghost note detection ---------------------------------------------
        result.ghost_notes = self._detect_ghost_notes(
            onset_times, onset_strengths, beat_times, bpm
        )

        # --- Pocket analysis --------------------------------------------------
        result.pocket = self._analyze_pocket(
            deviations_ms, beat_times, onset_times
        )

        # --- Human feel score -------------------------------------------------
        result.human_feel_score = self._compute_human_feel(
            deviations_ms, result.swing, result.ghost_notes, result.pocket
        )

        # --- Velocity contour (16 steps) --------------------------------------
        result.velocity_contour = self._build_velocity_contour(
            onset_times, onset_strengths, beat_times, bpm
        )

        # --- Groove DNA fingerprint -------------------------------------------
        result.groove_dna = self._compute_groove_dna(
            deviations_ms, result.velocity_contour, result.swing.ratio
        )

        return result

    async def analyze_file(
        self,
        path: Path,
        sample_rate: int = 22050,
        bpm: float | None = None,
    ) -> MicroTimingResult:
        """
        Load and analyze an audio file asynchronously.

        Args:
            path: Path to the audio file.
            sample_rate: Target sample rate.
            bpm: Optional known BPM.

        Returns:
            MicroTimingResult for the file.
        """
        import asyncio

        path = Path(path).expanduser().resolve()
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR, self._load_and_analyze, path, sample_rate, bpm
        )

    # ── Private helpers ───────────────────────────────────────────────────

    def _load_and_analyze(
        self, path: Path, sample_rate: int, bpm: float | None
    ) -> MicroTimingResult:
        try:
            import librosa

            y, sr = librosa.load(path, sr=sample_rate, mono=True)
            return self.analyze(y, sr, bpm=bpm)
        except Exception as exc:
            logger.error(
                "MicroTimingAnalyzer failed for %s: %s", path, exc
            )
            return MicroTimingResult(
                sample_rate=sample_rate, duration=0.0
            )

    # ── Swing ─────────────────────────────────────────────────────────────

    def _analyze_swing(
        self,
        onset_times: np.ndarray,
        beat_times: np.ndarray,
        bpm: float,
    ) -> SwingProfile:
        """Measure swing ratio from alternating 8th-note positions."""
        beat_dur = 60.0 / bpm
        eighth = beat_dur / 2.0

        ratios: list[float] = []
        for bt in beat_times:
            # Find onsets near the downbeat and upbeat positions
            down_window = onset_times[
                (onset_times >= bt - 0.03) & (onset_times <= bt + 0.03)
            ]
            up_expected = bt + eighth
            up_window = onset_times[
                (onset_times >= up_expected - eighth * 0.4)
                & (onset_times <= up_expected + eighth * 0.4)
            ]
            if len(down_window) > 0 and len(up_window) > 0:
                actual_up = float(up_window[0])
                actual_down = float(down_window[0])
                interval = actual_up - actual_down
                if interval > 0 and beat_dur > 0:
                    ratio = interval / beat_dur
                    if 0.2 < ratio < 0.8:
                        ratios.append(ratio)

        if not ratios:
            return SwingProfile(
                ratio=0.5,
                style="straight",
                consistency=0.0,
                description="Insufficient data for swing analysis",
            )

        avg_ratio = float(np.mean(ratios))
        # Higher std = less consistent
        consistency = float(1.0 - np.std(ratios) * 4)
        consistency = max(0.0, min(1.0, consistency))

        # Classify swing style
        if avg_ratio < 0.52:
            style = "straight"
            desc = "Straight 8th-note feel"
        elif avg_ratio < 0.58:
            style = "light_swing"
            desc = "Light swing feel — subtle groove"
        elif avg_ratio < 0.65:
            style = "shuffle"
            desc = "Shuffle groove — moderate swing"
        elif avg_ratio < 0.72:
            style = "bounce"
            desc = "Bouncy groove — heavy swing approaching triplet feel"
        else:
            style = "heavy_swing"
            desc = "Heavy swing — J Dilla / broken beat territory"

        return SwingProfile(
            ratio=round(avg_ratio, 3),
            style=style,
            consistency=round(consistency, 3),
            description=desc,
        )

    # ── Ghost notes ───────────────────────────────────────────────────────

    def _detect_ghost_notes(
        self,
        onset_times: np.ndarray,
        onset_strengths: np.ndarray,
        beat_times: np.ndarray,
        bpm: float,
    ) -> GhostNoteProfile:
        """Detect low-velocity hits between main beats (ghost notes)."""
        if len(onset_strengths) == 0 or len(beat_times) < 2:
            return GhostNoteProfile()

        # Normalize strengths
        max_str = float(np.max(onset_strengths))
        if max_str <= 0:
            return GhostNoteProfile()

        norm_strengths = onset_strengths / max_str

        # Ghost note = onset with strength < 0.35 of max AND not on a beat
        beat_dur = 60.0 / bpm
        ghost_threshold = 0.35
        beat_tolerance = beat_dur * 0.12  # 12% of beat duration

        ghost_positions: list[float] = []
        ghost_velocities: list[float] = []
        main_velocities: list[float] = []

        for t, s in zip(onset_times, norm_strengths, strict=False):
            on_beat = any(
                abs(t - bt) < beat_tolerance for bt in beat_times
            )
            if s < ghost_threshold and not on_beat:
                ghost_positions.append(float(t))
                ghost_velocities.append(float(s))
            else:
                main_velocities.append(float(s))

        n_beats = max(1, len(beat_times))
        avg_main = (
            float(np.mean(main_velocities)) if main_velocities else 1.0
        )
        avg_ghost = (
            float(np.mean(ghost_velocities)) if ghost_velocities else 0.0
        )

        return GhostNoteProfile(
            count=len(ghost_positions),
            density=round(len(ghost_positions) / n_beats, 2),
            avg_velocity_ratio=round(
                avg_ghost / max(avg_main, 1e-9), 3
            ),
            positions=ghost_positions[:50],  # Cap at 50 positions
        )

    # ── Pocket ────────────────────────────────────────────────────────────

    def _analyze_pocket(
        self,
        deviations_ms: list[float],
        beat_times: np.ndarray,
        onset_times: np.ndarray,
    ) -> PocketProfile:
        """Analyze how well the performance sits in the 'pocket'."""
        if not deviations_ms:
            return PocketProfile()

        devs = np.array(deviations_ms)
        abs_devs = np.abs(devs)

        # Tightness: inverse of mean absolute deviation
        mean_abs_dev = float(np.mean(abs_devs))
        tightness = max(0.0, 1.0 - mean_abs_dev / 30.0)  # 30ms = loose

        # Consistency: inverse of standard deviation of deviations
        dev_std = float(np.std(devs))
        consistency = max(
            0.0, 1.0 - dev_std / 20.0
        )  # 20ms std = inconsistent

        # Feel: average signed deviation
        mean_dev = float(np.mean(devs))
        if mean_dev < -3.0:
            feel = "ahead"
            feel_desc = "Playing ahead of the beat — pushing feel"
        elif mean_dev > 3.0:
            feel = "behind"
            feel_desc = "Playing behind the beat — laid-back feel"
        elif abs(mean_dev) < 1.0:
            feel = "on_top"
            feel_desc = "Right on top of the beat — tight and precise"
        else:
            feel = "neutral"
            feel_desc = "Neutral pocket — balanced feel"

        # Overall pocket score
        pocket_score = tightness * 0.4 + consistency * 0.6

        return PocketProfile(
            score=round(pocket_score, 3),
            tightness=round(tightness, 3),
            consistency=round(consistency, 3),
            feel=feel,
            description=feel_desc,
        )

    # ── Human feel ────────────────────────────────────────────────────────

    @staticmethod
    def _compute_human_feel(
        deviations_ms: list[float],
        swing: SwingProfile,
        ghost_notes: GhostNoteProfile,
        pocket: PocketProfile,
    ) -> float:
        """
        Compute human feel score (0 = machine, 1 = human).

        Combines: timing variance, swing presence, ghost notes, and
        consistent-but-imperfect deviations.
        """
        if not deviations_ms:
            return 0.0

        devs = np.array(deviations_ms)

        # Factor 1: Non-zero timing variation (machines = 0)
        timing_var = float(np.std(devs))
        timing_factor = min(1.0, timing_var / 15.0)  # 15ms std = very human

        # Factor 2: Swing presence
        swing_factor = 0.0
        if swing.style != "straight":
            swing_factor = min(1.0, abs(swing.ratio - 0.5) * 4.0)

        # Factor 3: Ghost note presence
        ghost_factor = min(1.0, ghost_notes.density * 0.5)

        # Factor 4: Consistent deviations (humans are consistently imperfect)
        if timing_var > 0:
            # Coefficient of variation of absolute deviations
            cv = float(
                np.std(np.abs(devs)) / (np.mean(np.abs(devs)) + 1e-9)
            )
            # Low CV = consistent deviations = human
            consistency_factor = max(0.0, 1.0 - cv)
        else:
            consistency_factor = 0.0

        # Weighted combination
        score = (
            timing_factor * 0.35
            + swing_factor * 0.25
            + ghost_factor * 0.15
            + consistency_factor * 0.25
        )

        return round(min(1.0, max(0.0, score)), 3)

    # ── Velocity contour ──────────────────────────────────────────────────

    @staticmethod
    def _build_velocity_contour(
        onset_times: np.ndarray,
        onset_strengths: np.ndarray,
        beat_times: np.ndarray,
        bpm: float,
    ) -> list[float]:
        """Build a 16-step velocity contour (normalized 0–1)."""
        contour = [0.0] * 16
        if len(onset_times) == 0 or len(beat_times) < 2 or bpm <= 0:
            return contour

        beat_dur = 60.0 / bpm
        bar_dur = beat_dur * 4
        bar_start = float(beat_times[0])

        max_str = (
            float(np.max(onset_strengths))
            if len(onset_strengths) > 0
            else 1.0
        )
        if max_str <= 0:
            max_str = 1.0

        step_dur = bar_dur / 16.0
        for t, s in zip(onset_times, onset_strengths, strict=False):
            rel_t = t - bar_start
            if rel_t < 0 or rel_t >= bar_dur:
                continue
            step = int(rel_t / step_dur)
            if 0 <= step < 16:
                norm_vel = float(s / max_str)
                contour[step] = max(contour[step], round(norm_vel, 3))

        return contour

    # ── Groove DNA ────────────────────────────────────────────────────────

    @staticmethod
    def _compute_groove_dna(
        deviations_ms: list[float],
        velocity_contour: list[float],
        swing_ratio: float,
    ) -> str:
        """
        Compute a compact groove DNA fingerprint.

        Encodes timing deviations, velocity contour, and swing into a
        32-character hex string for fast groove similarity comparison.
        """
        # Quantize deviations to 8 bins (-20ms to +20ms)
        bins = 8
        dev_quantized = []
        for d in deviations_ms[:16]:
            b = int(np.clip((d + 20) / 40.0 * bins, 0, bins - 1))
            dev_quantized.append(b)

        # Pad to 16
        while len(dev_quantized) < 16:
            dev_quantized.append(bins // 2)

        # Quantize velocity contour to 4 bits each
        vel_quantized = [
            int(np.clip(v * 15, 0, 15)) for v in velocity_contour[:16]
        ]
        while len(vel_quantized) < 16:
            vel_quantized.append(0)

        # Combine into bytes
        data = bytes(dev_quantized + vel_quantized)
        data += int(swing_ratio * 1000).to_bytes(2, "big")

        # SHA-256 and take first 32 hex chars
        return hashlib.sha256(data).hexdigest()[:32]


# ── Module exports ────────────────────────────────────────────────────────────

__all__ = [
    "MicroTimingAnalyzer",
    "MicroTimingResult",
    "SwingProfile",
    "GhostNoteProfile",
    "PocketProfile",
]
