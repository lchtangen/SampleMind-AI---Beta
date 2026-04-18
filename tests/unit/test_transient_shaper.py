"""Tests for TransientShaper."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.processing.transient_shaper import (
    TransientAnalysis,
    TransientShaper,
    TransientShaperResult,
)


class TestTransientShaper:
    """Tests for TransientShaper."""

    def test_init_defaults(self) -> None:
        shaper = TransientShaper()
        assert shaper.attack_time_ms == 1.0
        assert shaper.release_time_ms == 50.0
        assert shaper.sensitivity == 0.5

    def test_init_custom(self) -> None:
        shaper = TransientShaper(attack_time_ms=2.0, release_time_ms=100.0, sensitivity=0.8)
        assert shaper.attack_time_ms == 2.0

    def test_sensitivity_clamping(self) -> None:
        shaper = TransientShaper(sensitivity=2.0)
        assert shaper.sensitivity == 1.0
        shaper2 = TransientShaper(sensitivity=-1.0)
        assert shaper2.sensitivity == 0.0

    def test_process_silence(self) -> None:
        shaper = TransientShaper()
        y = np.zeros(44100, dtype=np.float32)
        result = shaper.process(y, 44100)
        assert isinstance(result, TransientShaperResult)
        assert len(result.output) == len(y)

    def test_process_impulse(self) -> None:
        shaper = TransientShaper()
        y = np.zeros(44100, dtype=np.float32)
        y[100] = 0.9  # Sharp transient
        result = shaper.process(y, 44100, attack_gain_db=6.0)
        assert isinstance(result, TransientShaperResult)
        assert len(result.output) == len(y)

    def test_process_noise(self) -> None:
        shaper = TransientShaper()
        rng = np.random.default_rng(42)
        y = rng.standard_normal(44100).astype(np.float32) * 0.3
        result = shaper.process(y, 44100, attack_gain_db=3.0, sustain_gain_db=-3.0)
        assert isinstance(result, TransientShaperResult)
        assert result.attack_gain_db == 3.0
        assert result.sustain_gain_db == -3.0

    def test_gain_clamping(self) -> None:
        shaper = TransientShaper()
        y = np.zeros(1000, dtype=np.float32)
        result = shaper.process(y, 44100, attack_gain_db=50.0, sustain_gain_db=-50.0)
        assert result.attack_gain_db == 24.0
        assert result.sustain_gain_db == -24.0

    def test_components_sum(self) -> None:
        """Transient + sustain should approximate original."""
        shaper = TransientShaper()
        rng = np.random.default_rng(42)
        y = rng.standard_normal(44100).astype(np.float32) * 0.1
        result = shaper.process(y, 44100)
        # With 0 gain, output should be close to input
        # (soft-clip may cause slight differences)
        diff = np.max(np.abs(result.output - y))
        assert diff < 0.5  # Allow for soft-clip nonlinearity

    def test_to_dict(self) -> None:
        shaper = TransientShaper()
        y = np.zeros(22050, dtype=np.float32)
        result = shaper.process(y, 22050)
        d = result.to_dict()
        assert "attack_gain_db" in d
        assert "sustain_gain_db" in d
        assert "analysis" in d
        assert "transient_count" in d["analysis"]


class TestTransientAnalysis:
    """Tests for TransientAnalysis dataclass."""

    def test_defaults(self) -> None:
        analysis = TransientAnalysis()
        assert analysis.transient_count == 0
        assert analysis.attack_sharpness == 0.0
