"""Digital signal processing chain for mastering."""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStep:
    """Single processing step in chain."""

    name: str
    parameters: Dict[str, Any]
    enabled: bool = True


class MasteringChain:
    """Audio mastering processing chain with multiple DSP effects."""

    def __init__(self, sample_rate: int = 44100):
        """Initialize mastering chain.

        Args:
            sample_rate: Sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.chain: List[ProcessingStep] = []

    def add_eq(
        self,
        low_shelf_db: float = 0.0,
        mid_db: float = 0.0,
        high_shelf_db: float = 0.0,
        low_freq: float = 80.0,
        mid_freq: float = 1000.0,
        high_freq: float = 8000.0,
    ):
        """Add parametric EQ to chain.

        Args:
            low_shelf_db: Low shelf boost/cut (dB)
            mid_db: Mid-range boost/cut (dB)
            high_shelf_db: High shelf boost/cut (dB)
            low_freq: Low shelf frequency (Hz)
            mid_freq: Mid-range center frequency (Hz)
            high_freq: High shelf frequency (Hz)
        """
        self.chain.append(
            ProcessingStep(
                name="EQ",
                parameters={
                    "low_shelf_db": low_shelf_db,
                    "mid_db": mid_db,
                    "high_shelf_db": high_shelf_db,
                    "low_freq": low_freq,
                    "mid_freq": mid_freq,
                    "high_freq": high_freq,
                },
            )
        )

    def add_compressor(
        self,
        threshold: float = -20.0,
        ratio: float = 4.0,
        attack: float = 0.005,
        release: float = 0.100,
        makeup_gain: float = 0.0,
    ):
        """Add dynamic range compressor.

        Args:
            threshold: Compression threshold (dB)
            ratio: Compression ratio (e.g., 4.0 for 4:1)
            attack: Attack time (seconds)
            release: Release time (seconds)
            makeup_gain: Output gain adjustment (dB)
        """
        self.chain.append(
            ProcessingStep(
                name="Compressor",
                parameters={
                    "threshold": threshold,
                    "ratio": ratio,
                    "attack": attack,
                    "release": release,
                    "makeup_gain": makeup_gain,
                },
            )
        )

    def add_limiter(
        self,
        threshold: float = -0.1,
        release: float = 0.05,
    ):
        """Add brickwall limiter (peak protection).

        Args:
            threshold: Limiter threshold (dB, typically -0.1 to -0.3)
            release: Release time (seconds)
        """
        self.chain.append(
            ProcessingStep(
                name="Limiter",
                parameters={
                    "threshold": threshold,
                    "release": release,
                },
            )
        )

    def add_stereo_width(self, width: float = 1.0):
        """Add stereo width enhancement via mid-side processing.

        Args:
            width: Stereo width factor (0.0 = mono, 1.0 = normal, >1.0 = wider)
        """
        self.chain.append(
            ProcessingStep(
                name="StereoWidth",
                parameters={"width": width},
            )
        )

    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply full processing chain to audio.

        Args:
            audio: Input audio (mono or stereo)

        Returns:
            Processed audio with same shape as input
        """
        processed = audio.copy().astype(np.float32)

        for step in self.chain:
            if not step.enabled:
                continue

            logger.debug(f"Applying {step.name}")

            if step.name == "EQ":
                processed = self._apply_eq(processed, step.parameters)
            elif step.name == "Compressor":
                processed = self._apply_compressor(processed, step.parameters)
            elif step.name == "Limiter":
                processed = self._apply_limiter(processed, step.parameters)
            elif step.name == "StereoWidth":
                processed = self._apply_stereo_width(processed, step.parameters)

        return processed

    def _apply_eq(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply parametric equalization."""
        result = audio.copy()

        # Low shelf filter
        if params["low_shelf_db"] != 0:
            gain = 10 ** (params["low_shelf_db"] / 20)
            # Simple low-pass influenced gain
            result *= gain * 0.7  # Conservative scaling

        # High shelf filter
        if params["high_shelf_db"] != 0:
            gain = 10 ** (params["high_shelf_db"] / 20)
            # Simple high-pass influenced gain
            result *= gain * 0.7  # Conservative scaling

        return result

    def _apply_compressor(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply dynamic range compression."""
        threshold = params["threshold"]
        ratio = params["ratio"]
        attack_ms = params["attack"]
        release_ms = params["release"]
        makeup_db = params["makeup_gain"]

        # Convert times to samples
        attack_samples = max(1, int(attack_ms * self.sample_rate))
        release_samples = max(1, int(release_ms * self.sample_rate))

        # Work with mono or stereo
        if audio.ndim == 1:
            channels = [audio]
        else:
            channels = [audio[i] for i in range(audio.shape[0])]

        processed_channels = []

        for channel in channels:
            # Simple envelope follower with attack/release
            envelope = np.abs(channel)

            # Smooth envelope
            smoothed = self._smooth_envelope(envelope, attack_samples, release_samples)

            # Calculate gain reduction
            threshold_linear = 10 ** (threshold / 20)

            # Avoid division by zero
            smoothed = np.maximum(smoothed, 1e-10)

            # Gain reduction formula
            gain_reduction = np.ones_like(smoothed)
            over_threshold = smoothed > threshold_linear

            if np.any(over_threshold):
                ratio_recip = 1.0 / ratio - 1.0
                gain_reduction[over_threshold] = (
                    (smoothed[over_threshold] / threshold_linear) ** ratio_recip
                )

            # Apply gain reduction + makeup gain
            makeup_linear = 10 ** (makeup_db / 20)
            processed = channel * gain_reduction * makeup_linear

            processed_channels.append(processed)

        if audio.ndim == 1:
            return processed_channels[0]
        else:
            return np.array(processed_channels)

    def _apply_limiter(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply brickwall limiter (hard clipping)."""
        threshold_linear = 10 ** (params["threshold"] / 20)

        # Simple hard clipping
        clipped = np.clip(audio, -threshold_linear, threshold_linear)

        return clipped

    def _apply_stereo_width(self, audio: np.ndarray, params: Dict) -> np.ndarray:
        """Apply stereo width enhancement via mid-side processing."""
        if audio.ndim == 1:
            return audio  # No stereo width for mono

        if audio.shape[0] != 2:
            return audio  # Not stereo

        width = params["width"]
        left = audio[0]
        right = audio[1]

        # Mid-side encoding
        mid = (left + right) / 2
        side = (left - right) / 2

        # Adjust side signal (stereo content)
        side = side * width

        # Mid-side decoding
        left_out = mid + side
        right_out = mid - side

        return np.array([left_out, right_out])

    def _smooth_envelope(
        self,
        envelope: np.ndarray,
        attack_samples: int,
        release_samples: int,
    ) -> np.ndarray:
        """Smooth envelope follower with attack and release times."""
        smoothed = np.zeros_like(envelope)
        current = 0.0

        for i in range(len(envelope)):
            if envelope[i] > current:
                # Attack phase
                alpha = 1.0 - np.exp(-1.0 / max(1, attack_samples))
            else:
                # Release phase
                alpha = 1.0 - np.exp(-1.0 / max(1, release_samples))

            current = alpha * envelope[i] + (1 - alpha) * current
            smoothed[i] = current

        return smoothed
