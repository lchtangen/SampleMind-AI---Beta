"""
Real-time Effects Chain — SampleMind Phase 17 (P1-014)

Provides a pedalboard-based real-time audio effects processing pipeline.
Effects can be chained, reordered, and parameterised at runtime.

Architecture:
  - ``RealtimeEffectsChain`` wraps a ``pedalboard.Pedalboard`` instance.
  - Effects are added/removed/reordered by name; each effect exposes
    its parameters as a flat dict for easy serialisation (REST/WebSocket).
  - ``process_file()`` applies the chain to a file and writes output.
  - ``process_buffer()`` applies the chain to a numpy buffer (for streaming).

Fallback:
  - If ``pedalboard`` is not installed, the chain operates as a pass-through
    and logs a warning.

Supported effects (via Spotify pedalboard):
  - ``eq`` — 3-band parametric EQ (low/mid/high gain)
  - ``compressor`` — Dynamic range compression
  - ``reverb`` — Algorithmic reverb (room size, damping, wet/dry)
  - ``delay`` — Feedback delay with sync-friendly time
  - ``chorus`` — Modulated chorus
  - ``distortion`` — Soft-clip distortion / saturation
  - ``limiter`` — Brickwall limiter for output protection
  - ``gain`` — Volume adjustment in dB
  - ``highpass`` — High-pass filter
  - ``lowpass`` — Low-pass filter

Usage::

    from samplemind.core.processing.realtime_effects import RealtimeEffectsChain

    chain = RealtimeEffectsChain()
    chain.add_effect("compressor", threshold_db=-20, ratio=4)
    chain.add_effect("reverb", room_size=0.5, wet_level=0.3)
    chain.add_effect("limiter", threshold_db=-1)

    output_path = await chain.process_file(
        input_path="/path/to/sample.wav",
        output_path="/path/to/output.wav",
    )
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)


# ── Effect registry ───────────────────────────────────────────────────────────

EFFECT_DEFAULTS: dict[str, dict[str, Any]] = {
    "eq": {"low_gain_db": 0.0, "mid_gain_db": 0.0, "high_gain_db": 0.0},
    "compressor": {
        "threshold_db": -20.0,
        "ratio": 4.0,
        "attack_ms": 10.0,
        "release_ms": 100.0,
    },
    "reverb": {
        "room_size": 0.5,
        "damping": 0.5,
        "wet_level": 0.3,
        "dry_level": 0.7,
    },
    "delay": {"delay_seconds": 0.25, "feedback": 0.3, "mix": 0.3},
    "chorus": {"rate_hz": 1.0, "depth": 0.25, "mix": 0.5},
    "distortion": {"drive_db": 20.0},
    "limiter": {"threshold_db": -1.0, "release_ms": 100.0},
    "gain": {"gain_db": 0.0},
    "highpass": {"cutoff_frequency_hz": 80.0},
    "lowpass": {"cutoff_frequency_hz": 18000.0},
}


# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class EffectSlot:
    """An effect in the chain with its parameters."""

    name: str
    enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "params": self.params,
        }


@dataclass
class ProcessingResult:
    """Result of processing an audio file through the effects chain."""

    input_path: str
    output_path: str
    effects_applied: list[str]
    processing_time_seconds: float = 0.0
    sample_rate: int = 44100
    duration_seconds: float = 0.0


# ── Pedalboard builder ────────────────────────────────────────────────────────


def _build_pedalboard_effect(slot: EffectSlot) -> Any:
    """Create a pedalboard effect instance from an EffectSlot."""
    try:
        import pedalboard as pb
    except ImportError:
        return None

    name = slot.name.lower()
    p = slot.params

    if name == "compressor":
        return pb.Compressor(
            threshold_db=p.get("threshold_db", -20.0),
            ratio=p.get("ratio", 4.0),
            attack_ms=p.get("attack_ms", 10.0),
            release_ms=p.get("release_ms", 100.0),
        )
    elif name == "reverb":
        return pb.Reverb(
            room_size=p.get("room_size", 0.5),
            damping=p.get("damping", 0.5),
            wet_level=p.get("wet_level", 0.3),
            dry_level=p.get("dry_level", 0.7),
        )
    elif name == "chorus":
        return pb.Chorus(
            rate_hz=p.get("rate_hz", 1.0),
            depth=p.get("depth", 0.25),
            mix=p.get("mix", 0.5),
        )
    elif name == "distortion":
        return pb.Distortion(drive_db=p.get("drive_db", 20.0))
    elif name == "limiter":
        return pb.Limiter(
            threshold_db=p.get("threshold_db", -1.0),
            release_ms=p.get("release_ms", 100.0),
        )
    elif name == "gain":
        return pb.Gain(gain_db=p.get("gain_db", 0.0))
    elif name == "highpass":
        return pb.HighpassFilter(
            cutoff_frequency_hz=p.get("cutoff_frequency_hz", 80.0)
        )
    elif name == "lowpass":
        return pb.LowpassFilter(
            cutoff_frequency_hz=p.get("cutoff_frequency_hz", 18000.0)
        )
    elif name == "delay":
        return pb.Delay(
            delay_seconds=p.get("delay_seconds", 0.25),
            feedback=p.get("feedback", 0.3),
            mix=p.get("mix", 0.3),
        )
    elif name == "eq":
        effects = []
        low = p.get("low_gain_db", 0.0)
        mid = p.get("mid_gain_db", 0.0)
        high = p.get("high_gain_db", 0.0)
        if abs(low) > 0.1:
            effects.append(
                pb.PeakFilter(
                    cutoff_frequency_hz=200.0, gain_db=low, q=0.7
                )
            )
        if abs(mid) > 0.1:
            effects.append(
                pb.PeakFilter(
                    cutoff_frequency_hz=1000.0, gain_db=mid, q=0.7
                )
            )
        if abs(high) > 0.1:
            effects.append(
                pb.PeakFilter(
                    cutoff_frequency_hz=5000.0, gain_db=high, q=0.7
                )
            )
        return effects if effects else None
    else:
        logger.warning("Unknown effect: %s", name)
        return None


# ── Main class ────────────────────────────────────────────────────────────────


class RealtimeEffectsChain:
    """
    Configurable audio effects chain powered by Spotify's pedalboard.

    Effects are stacked in order and applied to audio buffers or files.
    The chain can be serialised to/from dicts for REST API transport.
    """

    def __init__(self) -> None:
        self._slots: list[EffectSlot] = []
        self._pedalboard_available = self._check_pedalboard()

    @staticmethod
    def _check_pedalboard() -> bool:
        try:
            import pedalboard  # noqa: F401

            return True
        except ImportError:
            logger.warning(
                "pedalboard not installed — effects chain will pass through "
                "audio unmodified. Install with: pip install pedalboard"
            )
            return False

    # ── Chain manipulation ─────────────────────────────────────────────────

    def add_effect(self, name: str, **params: Any) -> EffectSlot:
        """Add an effect to the end of the chain."""
        defaults = EFFECT_DEFAULTS.get(name.lower(), {})
        merged = {**defaults, **params}
        slot = EffectSlot(name=name.lower(), params=merged)
        self._slots.append(slot)
        logger.debug("Added effect: %s with params %s", name, merged)
        return slot

    def remove_effect(self, index: int) -> EffectSlot | None:
        """Remove an effect by index. Returns the removed slot or None."""
        if 0 <= index < len(self._slots):
            removed = self._slots.pop(index)
            logger.debug(
                "Removed effect at index %d: %s", index, removed.name
            )
            return removed
        return None

    def move_effect(self, from_index: int, to_index: int) -> bool:
        """Move an effect from one position to another."""
        if 0 <= from_index < len(self._slots) and 0 <= to_index < len(
            self._slots
        ):
            slot = self._slots.pop(from_index)
            self._slots.insert(to_index, slot)
            return True
        return False

    def toggle_effect(self, index: int) -> bool:
        """Toggle an effect on/off. Returns new enabled state."""
        if 0 <= index < len(self._slots):
            self._slots[index].enabled = not self._slots[index].enabled
            return self._slots[index].enabled
        return False

    def update_params(self, index: int, **params: Any) -> bool:
        """Update parameters for an effect at the given index."""
        if 0 <= index < len(self._slots):
            self._slots[index].params.update(params)
            return True
        return False

    def clear(self) -> None:
        """Remove all effects from the chain."""
        self._slots.clear()

    @property
    def effects(self) -> list[EffectSlot]:
        """Current list of effect slots."""
        return list(self._slots)

    # ── Serialisation ──────────────────────────────────────────────────────

    def to_dict(self) -> list[dict[str, Any]]:
        """Serialise the chain to a list of dicts."""
        return [s.to_dict() for s in self._slots]

    @classmethod
    def from_dict(cls, chain_data: list[dict[str, Any]]) -> RealtimeEffectsChain:
        """Reconstruct a chain from serialised data."""
        instance = cls()
        for item in chain_data:
            slot = EffectSlot(
                name=item["name"],
                enabled=item.get("enabled", True),
                params=item.get("params", {}),
            )
            instance._slots.append(slot)
        return instance

    # ── Processing ─────────────────────────────────────────────────────────

    def _build_board(self) -> Any:
        """Build a pedalboard.Pedalboard from the current chain."""
        if not self._pedalboard_available:
            return None

        try:
            import pedalboard as pb

            effects = []
            for slot in self._slots:
                if not slot.enabled:
                    continue
                effect = _build_pedalboard_effect(slot)
                if effect is None:
                    continue
                if isinstance(effect, list):
                    effects.extend(effect)
                else:
                    effects.append(effect)

            return pb.Pedalboard(effects) if effects else None
        except Exception as exc:
            logger.error("Failed to build pedalboard: %s", exc)
            return None

    def process_buffer(self, audio: Any, sample_rate: int) -> Any:
        """
        Apply the effects chain to a numpy audio buffer.

        Args:
            audio: numpy array of shape (samples,) or (channels, samples).
            sample_rate: Audio sample rate in Hz.

        Returns:
            Processed numpy array (same shape as input).
        """
        import numpy as np

        board = self._build_board()
        if board is None:
            return audio

        if audio.ndim == 1:
            audio_2d = audio.reshape(1, -1).astype(np.float32)
        else:
            audio_2d = audio.astype(np.float32)

        processed = board(audio_2d, sample_rate)

        if audio.ndim == 1:
            return processed.flatten()
        return processed

    async def process_file(
        self,
        input_path: str,
        output_path: str | None = None,
    ) -> ProcessingResult:
        """
        Apply the effects chain to an audio file and write the output.

        Args:
            input_path: Path to input audio file.
            output_path: Path for output. Defaults to {input}_fx.wav.

        Returns:
            ProcessingResult with paths and metadata.
        """
        import time

        t0 = time.time()

        if output_path is None:
            stem = Path(input_path).stem
            output_path = str(Path(input_path).parent / f"{stem}_fx.wav")

        def _process() -> tuple[int, float]:
            import numpy as np

            try:
                import soundfile as sf

                audio, sr = sf.read(input_path, dtype="float32")
            except ImportError:
                import librosa

                audio, sr = librosa.load(input_path, sr=None, mono=False)
                audio = audio.T if audio.ndim > 1 else audio

            if audio.ndim == 1:
                audio = audio.reshape(1, -1).astype(np.float32)
            elif audio.ndim == 2:
                audio = audio.T.astype(np.float32)

            board = self._build_board()
            if board is not None:
                processed = board(audio, sr)
            else:
                processed = audio

            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            try:
                import soundfile as sf

                if processed.ndim == 2:
                    sf.write(output_path, processed.T, sr, subtype="PCM_16")
                else:
                    sf.write(output_path, processed, sr, subtype="PCM_16")
            except ImportError:
                import scipy.io.wavfile

                if processed.ndim == 2:
                    scipy.io.wavfile.write(
                        output_path,
                        sr,
                        (processed.T * 32767).astype(np.int16),
                    )
                else:
                    scipy.io.wavfile.write(
                        output_path,
                        sr,
                        (processed * 32767).astype(np.int16),
                    )

            duration = (
                processed.shape[-1] / sr
                if processed.ndim == 2
                else len(processed) / sr
            )
            return sr, duration

        loop = asyncio.get_event_loop()
        sr, duration = await loop.run_in_executor(_executor, _process)

        applied = [s.name for s in self._slots if s.enabled]
        elapsed = time.time() - t0

        logger.info(
            "Processed %s → %s (%d effects, %.1fs)",
            input_path,
            output_path,
            len(applied),
            elapsed,
        )

        return ProcessingResult(
            input_path=input_path,
            output_path=output_path,
            effects_applied=applied,
            processing_time_seconds=elapsed,
            sample_rate=sr,
            duration_seconds=duration,
        )

    @staticmethod
    def available_effects() -> dict[str, dict[str, Any]]:
        """Return the list of available effects and their default parameters."""
        return dict(EFFECT_DEFAULTS)
