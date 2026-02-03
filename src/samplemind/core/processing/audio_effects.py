"""
Advanced Audio Effects Processor (Phase 13.2)

Professional audio processing tools:
- 10-band parametric EQ
- Dynamic compression/limiting
- Distortion and saturation
- Reverb and delay effects
- Built-in presets for common use cases
"""

import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import librosa
import soundfile as sf
from scipy import signal

logger = logging.getLogger(__name__)


class EffectType(str, Enum):
    """Supported audio effects"""
    EQ = "eq"
    COMPRESSION = "compression"
    LIMITING = "limiting"
    DISTORTION = "distortion"
    SATURATION = "saturation"
    REVERB = "reverb"
    DELAY = "delay"
    CHORUS = "chorus"


@dataclass
class EQSettings:
    """10-band parametric EQ settings"""
    frequencies: List[float] = None  # Hz
    gains: List[float] = None        # dB
    q_factors: List[float] = None    # Resonance factor

    def __post_init__(self):
        if self.frequencies is None:
            # Standard 10-band EQ center frequencies (Hz)
            self.frequencies = [31, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
        if self.gains is None:
            self.gains = [0.0] * 10  # No gain by default
        if self.q_factors is None:
            self.q_factors = [0.707] * 10  # Standard Q factor


@dataclass
class CompressionSettings:
    """Dynamic compression settings"""
    ratio: float = 4.0              # Compression ratio (e.g., 4:1)
    threshold_db: float = -20.0     # Threshold in dB
    attack_ms: float = 10.0         # Attack time in ms
    release_ms: float = 100.0       # Release time in ms
    makeup_gain_db: float = 0.0     # Makeup gain in dB


@dataclass
class DistortionSettings:
    """Distortion/overdrive settings"""
    drive: float = 1.0              # Drive amount (1.0 = clean, >1.0 = distorted)
    tone: float = 0.5               # Tone shaping (0-1)
    output_gain_db: float = 0.0     # Output level


@dataclass
class ReverbSettings:
    """Reverb effect settings"""
    room_size: float = 0.5          # Room size (0-1)
    damping: float = 0.5            # Damping (0-1)
    width: float = 1.0              # Stereo width (0-1)
    dry_wet_mix: float = 0.3        # Dry/wet mix (0-1)


@dataclass
class EffectChain:
    """Container for multiple effects"""
    effects: List[Tuple[EffectType, Dict]] = None

    def __post_init__(self):
        if self.effects is None:
            self.effects = []

    def add_effect(self, effect_type: EffectType, settings: Dict):
        """Add an effect to the chain"""
        self.effects.append((effect_type, settings))

    def clear(self):
        """Clear all effects"""
        self.effects = []


class AudioEffectsProcessor:
    """
    Professional audio effects processor with multiple effect types.

    Example:
        processor = AudioEffectsProcessor(sample_rate=44100)
        audio = processor.load_audio("song.wav")
        processed = processor.apply_eq(audio, gains=[-5, 0, 3])
        processor.save_audio(processed, "output.wav")
    """

    def __init__(self, sample_rate: int = 44100):
        """
        Initialize effects processor.

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        logger.info(f"Audio Effects Processor initialized (SR: {sample_rate}Hz)")

    def load_audio(self, file_path: Path) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        audio, sr = librosa.load(str(file_path), sr=self.sample_rate, mono=False)
        logger.info(f"Loaded audio: {audio.shape}, SR: {sr}")
        return audio, sr

    def save_audio(self, audio: np.ndarray, file_path: Path, sr: int = None) -> None:
        """Save audio file"""
        if sr is None:
            sr = self.sample_rate
        sf.write(str(file_path), audio.T if audio.ndim > 1 else audio, sr)
        logger.info(f"Saved audio to {file_path}")

    # ========================================================================
    # EQ EFFECTS
    # ========================================================================

    def apply_eq(
        self,
        audio: np.ndarray,
        frequencies: Optional[List[float]] = None,
        gains: Optional[List[float]] = None,
        q_factors: Optional[List[float]] = None,
    ) -> np.ndarray:
        """
        Apply 10-band parametric EQ to audio.

        Args:
            audio: Input audio array
            frequencies: Center frequencies in Hz (default: 10-band standard)
            gains: Gain for each band in dB
            q_factors: Q factor for each band

        Returns:
            EQ-processed audio
        """
        settings = EQSettings(
            frequencies=frequencies,
            gains=gains,
            q_factors=q_factors
        )

        output = audio.copy()

        # Apply each band
        for freq, gain_db, q in zip(settings.frequencies, settings.gains, settings.q_factors):
            if abs(gain_db) > 0.01:  # Skip if no gain
                output = self._apply_peaking_filter(output, freq, gain_db, q)

        logger.info(f"Applied EQ: {len(settings.frequencies)} bands")
        return output

    def _apply_peaking_filter(
        self,
        audio: np.ndarray,
        frequency: float,
        gain_db: float,
        q: float,
    ) -> np.ndarray:
        """Apply a peaking filter to audio"""
        # Convert dB to linear
        gain_linear = 10 ** (gain_db / 20.0)

        # Design peaking filter
        w0 = 2 * np.pi * frequency / self.sample_rate
        sin_w0 = np.sin(w0)
        cos_w0 = np.cos(w0)
        alpha = sin_w0 / (2 * q)

        # Peaking filter coefficients
        b = np.array([
            1 + alpha * gain_linear,
            -2 * cos_w0,
            1 - alpha * gain_linear
        ])
        a = np.array([
            1 + alpha / gain_linear,
            -2 * cos_w0,
            1 - alpha / gain_linear
        ])

        # Normalize
        b = b / a[0]
        a = a / a[0]

        # Apply filter
        if audio.ndim == 1:  # Mono
            filtered = signal.lfilter(b, a, audio)
        else:  # Stereo
            filtered = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                filtered[ch] = signal.lfilter(b, a, audio[ch])

        return filtered

    # ========================================================================
    # COMPRESSION EFFECTS
    # ========================================================================

    def apply_compression(
        self,
        audio: np.ndarray,
        ratio: float = 4.0,
        threshold_db: float = -20.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
        makeup_gain_db: float = 0.0,
    ) -> np.ndarray:
        """
        Apply dynamic compression to audio.

        Args:
            audio: Input audio
            ratio: Compression ratio (e.g., 4.0 = 4:1)
            threshold_db: Threshold in dB
            attack_ms: Attack time in milliseconds
            release_ms: Release time in milliseconds
            makeup_gain_db: Makeup gain in dB

        Returns:
            Compressed audio
        """
        # Convert time constants to samples
        attack_samples = int(attack_ms * self.sample_rate / 1000)
        release_samples = int(release_ms * self.sample_rate / 1000)

        # Calculate gain reduction envelope
        threshold_linear = 10 ** (threshold_db / 20.0)
        makeup_gain_linear = 10 ** (makeup_gain_db / 20.0)

        if audio.ndim == 1:  # Mono
            output = self._compress_channel(
                audio,
                ratio,
                threshold_linear,
                attack_samples,
                release_samples,
                makeup_gain_linear
            )
        else:  # Stereo
            output = np.zeros_like(audio)
            for ch in range(audio.shape[0]):
                output[ch] = self._compress_channel(
                    audio[ch],
                    ratio,
                    threshold_linear,
                    attack_samples,
                    release_samples,
                    makeup_gain_linear
                )

        logger.info(f"Applied compression: {ratio}:1, threshold: {threshold_db}dB")
        return output

    def _compress_channel(
        self,
        channel: np.ndarray,
        ratio: float,
        threshold: float,
        attack_samples: int,
        release_samples: int,
        makeup_gain: float,
    ) -> np.ndarray:
        """Apply compression to a single channel"""
        # Calculate input level
        input_level = np.abs(channel)

        # Calculate gain reduction
        gain_reduction = np.ones_like(channel)
        above_threshold = input_level > threshold

        # Apply compression ratio where above threshold
        gain_reduction[above_threshold] = (threshold + (input_level[above_threshold] - threshold) / ratio) / input_level[above_threshold]

        # Apply attack/release envelope
        for i in range(1, len(gain_reduction)):
            if gain_reduction[i] < gain_reduction[i-1]:  # Attack
                alpha = 1.0 / max(1, attack_samples)
                gain_reduction[i] = gain_reduction[i-1] * (1 - alpha) + gain_reduction[i] * alpha
            else:  # Release
                alpha = 1.0 / max(1, release_samples)
                gain_reduction[i] = gain_reduction[i-1] * (1 - alpha) + gain_reduction[i] * alpha

        # Apply compression and makeup gain
        return channel * gain_reduction * makeup_gain

    def apply_limiting(
        self,
        audio: np.ndarray,
        threshold_db: float = -3.0,
        release_ms: float = 50.0,
    ) -> np.ndarray:
        """
        Apply hard limiter (infinite ratio compression).

        Args:
            audio: Input audio
            threshold_db: Limiting threshold in dB
            release_ms: Release time in milliseconds

        Returns:
            Limited audio
        """
        return self.apply_compression(
            audio,
            ratio=np.inf,
            threshold_db=threshold_db,
            attack_ms=1.0,
            release_ms=release_ms,
            makeup_gain_db=0.0
        )

    # ========================================================================
    # DISTORTION EFFECTS
    # ========================================================================

    def apply_distortion(
        self,
        audio: np.ndarray,
        drive: float = 1.0,
        tone: float = 0.5,
        output_gain_db: float = 0.0,
    ) -> np.ndarray:
        """
        Apply soft clipping distortion.

        Args:
            audio: Input audio
            drive: Drive amount (1.0 = clean, >1.0 = distorted)
            tone: Tone shaping (0-1, warmer to brighter)
            output_gain_db: Output level in dB

        Returns:
            Distorted audio
        """
        # Apply drive (preamp)
        driven = audio * drive

        # Soft clipping using tanh
        clipped = np.tanh(driven * 2) / 2

        # Tone shaping (simple high-pass blend)
        if tone < 1.0:
            # Mix with softer version
            blended = clipped * tone + audio * (1 - tone)
        else:
            blended = clipped

        # Output gain
        output_gain_linear = 10 ** (output_gain_db / 20.0)
        output = blended * output_gain_linear

        logger.info(f"Applied distortion: drive={drive}, tone={tone}")
        return output

    # ========================================================================
    # REVERB EFFECTS
    # ========================================================================

    def apply_reverb(
        self,
        audio: np.ndarray,
        room_size: float = 0.5,
        damping: float = 0.5,
        width: float = 1.0,
        dry_wet_mix: float = 0.3,
    ) -> np.ndarray:
        """
        Apply simple reverb effect using delays.

        Args:
            audio: Input audio
            room_size: Room size (0-1)
            damping: Damping (0-1)
            width: Stereo width (0-1)
            dry_wet_mix: Dry/wet mix (0-1, 1.0 = all wet)

        Returns:
            Reverb-processed audio
        """
        # Calculate delay times based on room size
        delay_times = [
            int(0.0297 * self.sample_rate * (0.5 + room_size * 0.5)),
            int(0.0371 * self.sample_rate * (0.5 + room_size * 0.5)),
            int(0.0411 * self.sample_rate * (0.5 + room_size * 0.5)),
            int(0.0437 * self.sample_rate * (0.5 + room_size * 0.5)),
        ]

        # Apply parallel delays with damping
        wet = audio.copy()
        for delay_samples in delay_times:
            delayed = np.pad(audio, (delay_samples, 0))[:-delay_samples]
            # Apply damping filter
            damping_factor = 1.0 - damping * 0.5
            wet = wet * damping_factor + delayed * damping_factor

        # Mix dry and wet
        output = audio * (1.0 - dry_wet_mix) + wet * dry_wet_mix

        logger.info(f"Applied reverb: room_size={room_size}, wet={dry_wet_mix}")
        return output

    # ========================================================================
    # PRESET EFFECTS
    # ========================================================================

    def apply_preset(
        self,
        audio: np.ndarray,
        preset_name: str,
    ) -> np.ndarray:
        """
        Apply a built-in effect preset.

        Available presets:
        - vocal: EQ (boost presence), compression, light reverb
        - drums: EQ (boost low), compression, saturation
        - bass: EQ (sub boost), compression, limiting
        - master: Parametric EQ, multiband compression, limiting
        - vintage: Saturation, colored compression, warmth

        Args:
            audio: Input audio
            preset_name: Name of preset

        Returns:
            Processed audio with preset effects
        """
        presets = {
            "vocal": self._preset_vocal,
            "drums": self._preset_drums,
            "bass": self._preset_bass,
            "master": self._preset_master,
            "vintage": self._preset_vintage,
        }

        if preset_name not in presets:
            logger.warning(f"Unknown preset: {preset_name}")
            return audio

        logger.info(f"Applying preset: {preset_name}")
        return presets[preset_name](audio)

    def _preset_vocal(self, audio: np.ndarray) -> np.ndarray:
        """Vocal enhancement preset"""
        # Boost presence (2-4kHz)
        gains = [0, 0, 0, 1, 2, 1, 3, 2, 0, 0]  # dB
        audio = self.apply_eq(audio, gains=gains)
        # Light compression
        audio = self.apply_compression(audio, ratio=4.0, threshold_db=-15)
        # Light reverb
        audio = self.apply_reverb(audio, room_size=0.3, dry_wet_mix=0.15)
        return audio

    def _preset_drums(self, audio: np.ndarray) -> np.ndarray:
        """Drum processing preset"""
        # Boost low end (60-250Hz)
        gains = [3, 2, 1, 0, 0, 0, 0, 0, 0, 0]  # dB
        audio = self.apply_eq(audio, gains=gains)
        # Medium compression
        audio = self.apply_compression(audio, ratio=3.0, threshold_db=-18)
        # Add saturation for punch
        audio = self.apply_distortion(audio, drive=1.5, tone=0.8, output_gain_db=-3)
        return audio

    def _preset_bass(self, audio: np.ndarray) -> np.ndarray:
        """Bass processing preset"""
        # Boost sub and mid-bass
        gains = [4, 3, 1, 0, 0, 0, 0, 0, 0, 0]  # dB
        audio = self.apply_eq(audio, gains=gains)
        # Strong compression for control
        audio = self.apply_compression(audio, ratio=6.0, threshold_db=-20)
        # Limiter to protect against peaks
        audio = self.apply_limiting(audio, threshold_db=-1.0)
        return audio

    def _preset_master(self, audio: np.ndarray) -> np.ndarray:
        """Master bus preset"""
        # Subtle master EQ
        gains = [1, 0, 0, 0, 0, 0, 0, -1, -2, -1]  # dB
        audio = self.apply_eq(audio, gains=gains)
        # Gentle compression for glue
        audio = self.apply_compression(audio, ratio=2.0, threshold_db=-12, makeup_gain_db=2)
        # Final limiter
        audio = self.apply_limiting(audio, threshold_db=-0.3)
        return audio

    def _preset_vintage(self, audio: np.ndarray) -> np.ndarray:
        """Vintage/warm sound preset"""
        # Warm up EQ (boost lows, reduce highs)
        gains = [2, 1, 0, 0, -1, -1, -2, -2, -1, 0]  # dB
        audio = self.apply_eq(audio, gains=gains)
        # Saturation for warmth
        audio = self.apply_distortion(audio, drive=1.2, tone=0.3, output_gain_db=-1)
        # Soft compression
        audio = self.apply_compression(audio, ratio=2.5, threshold_db=-15, makeup_gain_db=1)
        return audio


__all__ = [
    "AudioEffectsProcessor",
    "EffectType",
    "EQSettings",
    "CompressionSettings",
    "DistortionSettings",
    "ReverbSettings",
    "EffectChain",
]
