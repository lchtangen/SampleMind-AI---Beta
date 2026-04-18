"""
Spectral Morphing Engine — Creative Audio Generation

Blends spectral characteristics between two audio files to create hybrid
timbres. Uses STFT-domain interpolation with optional harmonic alignment.

Use cases:
  - Morph a synth pad into a vocal texture
  - Blend kick drum body with snare transient
  - Create evolving timbral transitions for sound design
  - Generate hybrid instruments (e.g., piano-guitar blend)
  - Time-varying morph with automation curve

Algorithm:
  1. Compute STFT of both source and target audio
  2. Optionally align harmonics via pitch tracking
  3. Interpolate magnitude spectra using morph factor (0–1)
  4. Preserve phase from source (or blend phases for experimental results)
  5. Reconstruct via inverse STFT with overlap-add

Usage::

    from samplemind.ai.generation.spectral_morph import SpectralMorphEngine

    engine = SpectralMorphEngine()
    result = engine.morph(source_audio, target_audio, sr, morph_factor=0.5)
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="specmorph")


@dataclass
class MorphAnalysis:
    """Analysis of the morph operation."""

    spectral_distance: float = 0.0  # How different the two sources are (0–1)
    harmonic_overlap: float = 0.0  # Harmonic content overlap ratio
    timbral_shift: float = 0.0  # How much the timbre changed
    source_centroid_hz: float = 0.0
    target_centroid_hz: float = 0.0
    output_centroid_hz: float = 0.0


@dataclass
class MorphResult:
    """Result from spectral morphing."""

    output: np.ndarray  # Morphed audio
    morph_factor: float = 0.0
    phase_mode: str = "source"
    analysis: MorphAnalysis = field(default_factory=MorphAnalysis)

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata (not audio data)."""
        return {
            "morph_factor": self.morph_factor,
            "phase_mode": self.phase_mode,
            "output_duration": round(float(len(self.output)) / 44100, 3),
            "output_peak": round(float(np.max(np.abs(self.output))), 4),
            "analysis": {
                "spectral_distance": round(
                    self.analysis.spectral_distance, 4
                ),
                "harmonic_overlap": round(
                    self.analysis.harmonic_overlap, 4
                ),
                "timbral_shift": round(self.analysis.timbral_shift, 4),
                "source_centroid_hz": round(
                    self.analysis.source_centroid_hz, 2
                ),
                "target_centroid_hz": round(
                    self.analysis.target_centroid_hz, 2
                ),
                "output_centroid_hz": round(
                    self.analysis.output_centroid_hz, 2
                ),
            },
        }


class SpectralMorphEngine:
    """
    Spectral morphing engine for blending audio timbres.

    Operates in the STFT domain to interpolate between the spectral
    characteristics of two audio signals.
    """

    def __init__(
        self,
        n_fft: int = 2048,
        hop_length: int = 512,
        window: str = "hann",
    ) -> None:
        """
        Args:
            n_fft: FFT size.
            hop_length: STFT hop length.
            window: Window function name.
        """
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.window = window

    def morph(
        self,
        source: np.ndarray,
        target: np.ndarray,
        sr: int,
        morph_factor: float = 0.5,
        phase_mode: str = "source",
        time_varying: np.ndarray | None = None,
    ) -> MorphResult:
        """
        Morph between source and target audio spectra.

        Args:
            source: Source audio (mono, float32).
            target: Target audio (mono, float32).
            sr: Sample rate (both signals must share the same rate).
            morph_factor: Blend factor
                (0 = pure source, 1 = pure target).
            phase_mode: Phase handling strategy:
                - "source": Use source phase (preserves timing feel).
                - "target": Use target phase.
                - "blend": Linear phase interpolation (experimental).
                - "random": Random phase (textural result).
            time_varying: Optional per-frame morph curve
                (overrides morph_factor).

        Returns:
            MorphResult with blended audio.
        """
        try:
            from scipy.signal import get_window
        except ImportError:
            logger.warning(
                "scipy not available — returning source audio"
            )
            return MorphResult(
                output=source.copy(), morph_factor=morph_factor
            )

        morph_factor = float(np.clip(morph_factor, 0.0, 1.0))

        # Length-match: pad shorter signal
        max_len = max(len(source), len(target))
        source_padded = np.pad(source, (0, max_len - len(source)))
        target_padded = np.pad(target, (0, max_len - len(target)))

        # Compute STFTs
        win = get_window(self.window, self.n_fft)
        source_stft = self._stft(source_padded, win)
        target_stft = self._stft(target_padded, win)

        # Match STFT shapes (pad shorter in time axis)
        n_frames = max(source_stft.shape[1], target_stft.shape[1])
        if source_stft.shape[1] < n_frames:
            pad_width = n_frames - source_stft.shape[1]
            source_stft = np.pad(
                source_stft, ((0, 0), (0, pad_width))
            )
        if target_stft.shape[1] < n_frames:
            pad_width = n_frames - target_stft.shape[1]
            target_stft = np.pad(
                target_stft, ((0, 0), (0, pad_width))
            )

        # Extract magnitude and phase
        source_mag = np.abs(source_stft)
        source_phase = np.angle(source_stft)
        target_mag = np.abs(target_stft)
        target_phase = np.angle(target_stft)

        # Morph magnitudes
        if time_varying is not None:
            # Time-varying morph: one factor per frame
            factors = np.interp(
                np.linspace(0, 1, n_frames),
                np.linspace(0, 1, len(time_varying)),
                time_varying,
            )
            factors = np.clip(factors, 0.0, 1.0)
            # Broadcast across frequency bins
            morph_factors: np.ndarray | float = factors[np.newaxis, :]
        else:
            morph_factors = morph_factor

        morphed_mag = (
            source_mag * (1.0 - morph_factors)
            + target_mag * morph_factors
        )

        # Phase handling
        if phase_mode == "target":
            morphed_phase = target_phase
        elif phase_mode == "blend":
            morphed_phase = self._blend_phase(
                source_phase, target_phase, morph_factor
            )
        elif phase_mode == "random":
            morphed_phase = np.random.uniform(
                -np.pi, np.pi, size=source_phase.shape
            )
        else:
            # Default: source phase
            morphed_phase = source_phase

        # Reconstruct complex STFT
        morphed_stft = morphed_mag * np.exp(1j * morphed_phase)

        # Inverse STFT
        output = self._istft(morphed_stft, win, max_len)

        # Normalize to prevent clipping
        peak = np.max(np.abs(output))
        if peak > 1.0:
            output = output / peak * 0.95

        # Analyze the morph
        analysis = self._analyze_morph(
            source_mag, target_mag, morphed_mag, sr
        )

        return MorphResult(
            output=output.astype(np.float32),
            morph_factor=morph_factor,
            phase_mode=phase_mode,
            analysis=analysis,
        )

    async def morph_files(
        self,
        source_path: Path,
        target_path: Path,
        morph_factor: float = 0.5,
        phase_mode: str = "source",
        target_sr: int = 44100,
    ) -> MorphResult:
        """
        Load two audio files and morph between them.

        Args:
            source_path: Path to source audio.
            target_path: Path to target audio.
            morph_factor: Blend factor (0–1).
            phase_mode: Phase handling strategy.
            target_sr: Target sample rate.

        Returns:
            MorphResult with blended audio.
        """
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _EXECUTOR,
            self._load_and_morph,
            Path(source_path),
            Path(target_path),
            morph_factor,
            phase_mode,
            target_sr,
        )

    def create_morph_sequence(
        self,
        source: np.ndarray,
        target: np.ndarray,
        sr: int,
        n_steps: int = 5,
        phase_mode: str = "source",
    ) -> list[MorphResult]:
        """
        Create a sequence of morphs from source to target.

        Args:
            source: Source audio.
            target: Target audio.
            sr: Sample rate.
            n_steps: Number of intermediate steps (including endpoints).
            phase_mode: Phase handling strategy.

        Returns:
            List of MorphResult objects from 0.0 to 1.0 morph factor.
        """
        factors = np.linspace(0.0, 1.0, max(2, n_steps))
        return [
            self.morph(source, target, sr, float(f), phase_mode)
            for f in factors
        ]

    # ── Private helpers ──────────────────────────────────────────────

    def _stft(
        self, y: np.ndarray, window: np.ndarray
    ) -> np.ndarray:
        """Compute Short-Time Fourier Transform."""
        n_fft = self.n_fft
        hop = self.hop_length
        n_frames = 1 + (len(y) - n_fft) // hop

        stft_matrix = np.zeros(
            (n_fft // 2 + 1, max(1, n_frames)), dtype=np.complex128
        )

        for i in range(max(0, n_frames)):
            frame = y[i * hop : i * hop + n_fft]
            if len(frame) < n_fft:
                frame = np.pad(frame, (0, n_fft - len(frame)))
            windowed = frame * window
            spectrum = np.fft.rfft(windowed)
            stft_matrix[:, i] = spectrum

        return stft_matrix

    def _istft(
        self,
        stft_matrix: np.ndarray,
        window: np.ndarray,
        expected_length: int,
    ) -> np.ndarray:
        """Compute inverse STFT with overlap-add."""
        n_fft = self.n_fft
        hop = self.hop_length
        n_frames = stft_matrix.shape[1]
        output_length = n_fft + (n_frames - 1) * hop

        output = np.zeros(output_length)
        window_sum = np.zeros(output_length)

        for i in range(n_frames):
            frame = np.fft.irfft(stft_matrix[:, i], n=n_fft)
            start = i * hop
            end = start + n_fft
            output[start:end] += frame * window
            window_sum[start:end] += window**2

        # Normalize by window sum (avoid division by zero)
        nonzero = window_sum > 1e-8
        output[nonzero] /= window_sum[nonzero]

        return output[:expected_length]

    @staticmethod
    def _blend_phase(
        phase_a: np.ndarray,
        phase_b: np.ndarray,
        factor: float,
    ) -> np.ndarray:
        """Blend two phase arrays using circular interpolation."""
        a_complex = np.exp(1j * phase_a)
        b_complex = np.exp(1j * phase_b)
        blended = a_complex * (1.0 - factor) + b_complex * factor
        return np.angle(blended)

    def _load_and_morph(
        self,
        source_path: Path,
        target_path: Path,
        morph_factor: float,
        phase_mode: str,
        target_sr: int,
    ) -> MorphResult:
        try:
            import librosa

            source, _ = librosa.load(
                str(source_path), sr=target_sr, mono=True
            )
            target, _ = librosa.load(
                str(target_path), sr=target_sr, mono=True
            )
            return self.morph(
                source, target, target_sr, morph_factor, phase_mode
            )
        except Exception as exc:
            logger.error("SpectralMorphEngine failed: %s", exc)
            return MorphResult(output=np.array([], dtype=np.float32))

    @staticmethod
    def _analyze_morph(
        source_mag: np.ndarray,
        target_mag: np.ndarray,
        morphed_mag: np.ndarray,
        sr: int,
    ) -> MorphAnalysis:
        """Analyze the spectral characteristics of the morph."""
        # Spectral distance between source and target
        s_norm = source_mag / (np.max(source_mag) + 1e-9)
        t_norm = target_mag / (np.max(target_mag) + 1e-9)
        distance = float(np.mean(np.abs(s_norm - t_norm)))

        # Spectral centroids
        freqs = np.linspace(0, sr / 2, source_mag.shape[0])
        freq_col = (
            freqs[:, np.newaxis] if source_mag.ndim > 1 else freqs
        )

        def centroid(mag: np.ndarray) -> float:
            mag_sum = np.sum(mag, axis=0)
            weighted = np.sum(freq_col * mag, axis=0)
            valid = mag_sum > 1e-9
            if np.any(valid):
                return float(
                    np.mean(weighted[valid] / mag_sum[valid])
                )
            return 0.0

        source_centroid = centroid(source_mag)
        target_centroid = centroid(target_mag)
        output_centroid = centroid(morphed_mag)

        # Harmonic overlap: correlation of magnitude spectra
        s_flat = source_mag.flatten()
        t_flat = target_mag.flatten()
        if len(s_flat) > 0 and len(t_flat) > 0:
            min_len = min(len(s_flat), len(t_flat))
            corr = float(
                np.corrcoef(
                    s_flat[:min_len], t_flat[:min_len]
                )[0, 1]
            )
            harmonic_overlap = max(0.0, corr)
        else:
            harmonic_overlap = 0.0

        # Timbral shift: how much the centroid moved
        if source_centroid > 0:
            timbral_shift = (
                abs(output_centroid - source_centroid) / source_centroid
            )
        else:
            timbral_shift = 0.0

        return MorphAnalysis(
            spectral_distance=min(1.0, distance),
            harmonic_overlap=harmonic_overlap,
            timbral_shift=min(1.0, timbral_shift),
            source_centroid_hz=source_centroid,
            target_centroid_hz=target_centroid,
            output_centroid_hz=output_centroid,
        )


# ── Module exports ─────────────────────────────────────────────────────

__all__ = [
    "SpectralMorphEngine",
    "MorphResult",
    "MorphAnalysis",
]
