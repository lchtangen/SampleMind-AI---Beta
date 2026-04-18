"""Tests for SpectralMorphEngine."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.ai.generation.spectral_morph import (
    MorphAnalysis,
    MorphResult,
    SpectralMorphEngine,
)


class TestSpectralMorphEngine:
    """Tests for SpectralMorphEngine."""

    def test_init_defaults(self) -> None:
        engine = SpectralMorphEngine()
        assert engine.n_fft == 2048
        assert engine.hop_length == 512

    def test_morph_identical_signals(self) -> None:
        engine = SpectralMorphEngine()
        sr = 22050
        t = np.linspace(0, 1.0, sr, dtype=np.float64)
        source = np.sin(2 * np.pi * 440 * t).astype(np.float64)
        target = source.copy()
        result = engine.morph(source, target, sr, morph_factor=0.5)
        assert isinstance(result, MorphResult)
        assert len(result.output) > 0
        assert result.morph_factor == 0.5

    def test_morph_factor_zero(self) -> None:
        """morph_factor=0 should produce something close to source."""
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.sin(2 * np.pi * 220 * np.linspace(0, 1, sr))
        target = np.sin(2 * np.pi * 880 * np.linspace(0, 1, sr))
        result = engine.morph(source, target, sr, morph_factor=0.0)
        assert result.morph_factor == 0.0
        # STFT framing may trim a few samples; allow small difference
        assert abs(len(result.output) - len(source)) < engine.n_fft

    def test_morph_factor_one(self) -> None:
        """morph_factor=1 should produce something close to target."""
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.sin(2 * np.pi * 220 * np.linspace(0, 1, sr))
        target = np.sin(2 * np.pi * 880 * np.linspace(0, 1, sr))
        result = engine.morph(source, target, sr, morph_factor=1.0)
        assert result.morph_factor == 1.0

    def test_morph_different_lengths(self) -> None:
        """Should handle signals of different lengths."""
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sr))
        target = np.sin(2 * np.pi * 440 * np.linspace(0, 2, sr * 2))
        result = engine.morph(source, target, sr, morph_factor=0.5)
        assert len(result.output) > 0

    def test_morph_factor_clamped(self) -> None:
        """Out-of-range morph factors should be clamped."""
        engine = SpectralMorphEngine()
        sr = 22050
        y = np.zeros(sr)
        result = engine.morph(y, y, sr, morph_factor=1.5)
        assert result.morph_factor == 1.0

    def test_phase_modes(self) -> None:
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.random.randn(sr) * 0.1
        target = np.random.randn(sr) * 0.1
        for mode in ["source", "target", "blend", "random"]:
            result = engine.morph(source, target, sr, phase_mode=mode)
            assert result.phase_mode == mode
            assert len(result.output) > 0

    def test_time_varying_morph(self) -> None:
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.sin(2 * np.pi * 220 * np.linspace(0, 1, sr))
        target = np.sin(2 * np.pi * 880 * np.linspace(0, 1, sr))
        curve = np.linspace(0, 1, 10)
        result = engine.morph(source, target, sr, time_varying=curve)
        assert len(result.output) > 0

    def test_morph_sequence(self) -> None:
        engine = SpectralMorphEngine()
        sr = 22050
        source = np.random.randn(sr) * 0.1
        target = np.random.randn(sr) * 0.1
        sequence = engine.create_morph_sequence(source, target, sr, n_steps=3)
        assert len(sequence) == 3
        assert sequence[0].morph_factor == pytest.approx(0.0)
        assert sequence[-1].morph_factor == pytest.approx(1.0)

    def test_to_dict(self) -> None:
        result = MorphResult(output=np.zeros(100, dtype=np.float32), morph_factor=0.5)
        d = result.to_dict()
        assert "morph_factor" in d
        assert "analysis" in d


class TestMorphAnalysis:
    """Tests for MorphAnalysis."""

    def test_defaults(self) -> None:
        analysis = MorphAnalysis()
        assert analysis.spectral_distance == 0.0
        assert analysis.harmonic_overlap == 0.0
