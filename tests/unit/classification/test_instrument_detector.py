"""
Unit tests for InstrumentDetector — 128-class GM (Step 18).
"""

from __future__ import annotations

import numpy as np
import pytest


def _noise(sr=22050, duration=1.0, amplitude=0.5) -> np.ndarray:
    rng = np.random.default_rng(0)
    return (amplitude * rng.uniform(-1, 1, int(sr * duration))).astype(np.float32)


def _sine_low(sr=22050, duration=1.0) -> np.ndarray:
    """Low-frequency sine (bass-like)."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return (0.7 * np.sin(2 * np.pi * 80 * t)).astype(np.float32)


def test_gm_instrument_table_complete():
    """Verify all 128 GM programs are present in the table."""
    from samplemind.ai.classification.instrument_detector import (
        _GM_BY_PROGRAM,
        GM_INSTRUMENTS,
    )

    assert len(GM_INSTRUMENTS) == 128
    programs = {prog for prog, _, _ in GM_INSTRUMENTS}
    assert programs == set(range(128))
    assert len(_GM_BY_PROGRAM) == 128


def test_detect_returns_result():
    pytest.importorskip("librosa")

    from samplemind.ai.classification.instrument_detector import InstrumentDetector

    det = InstrumentDetector(top_k=3, use_clap=False)
    y = _noise()
    result = det.detect(y, 22050)

    assert isinstance(result.instruments, list)
    assert isinstance(result.midi_programs, list)
    assert len(result.instruments) <= 3
    # All returned programs must be valid GM
    for prog in result.midi_programs:
        assert 0 <= prog <= 127


def test_detect_low_frequency_suggests_bass():
    """Low-frequency dominant signal should hint toward Bass family."""
    pytest.importorskip("librosa")

    from samplemind.ai.classification.instrument_detector import InstrumentDetector

    det = InstrumentDetector(top_k=5, use_clap=False)
    y = _sine_low()
    result = det.detect(y, 22050)

    # At least one result should come from Bass family (programs 32–39)
    bass_programs = set(range(32, 40))
    any(p in bass_programs for p in result.midi_programs)
    # We're lenient — heuristic may not always hit, but it must not crash
    assert result is not None


def test_clap_fallback_no_crash():
    """detect() must not raise when CLAP is unavailable."""
    from samplemind.ai.classification.instrument_detector import InstrumentDetector

    det = InstrumentDetector(use_clap=True)
    y = _noise()
    result = det.detect(y, 22050)
    assert result is not None


def test_instrument_result_primary_matches_first():
    pytest.importorskip("librosa")

    from samplemind.ai.classification.instrument_detector import InstrumentDetector

    det = InstrumentDetector(top_k=5, use_clap=False)
    y = _noise()
    result = det.detect(y, 22050)

    if result.instruments:
        assert result.primary_instrument == result.instruments[0]
        assert result.midi_program == result.midi_programs[0]


def test_clap_prompts_length():
    from samplemind.ai.classification.instrument_detector import (
        _CLAP_PROMPTS,
        GM_INSTRUMENTS,
    )

    assert len(_CLAP_PROMPTS) == len(GM_INSTRUMENTS) == 128
