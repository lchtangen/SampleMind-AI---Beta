"""
Unit tests for MoodDetector — Russell circumplex model (Step 18).
"""

from __future__ import annotations

import numpy as np
import pytest


def _sine(freq=440.0, sr=22050, duration=2.0, amplitude=0.5) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return (amplitude * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_quadrant_mapping():
    from samplemind.ai.classification.mood_detector import _quadrant

    assert _quadrant(0.5, 0.5) == "high_valence_high_arousal"
    assert _quadrant(0.5, -0.5) == "high_valence_low_arousal"
    assert _quadrant(-0.5, 0.5) == "low_valence_high_arousal"
    assert _quadrant(-0.5, -0.5) == "low_valence_low_arousal"
    assert _quadrant(0.0, 0.0) == "high_valence_high_arousal"  # origin → high/high by convention


def test_detect_returns_result():
    pytest.importorskip("librosa")

    from samplemind.ai.classification.mood_detector import MoodDetector

    det = MoodDetector(use_clap=False)
    y = _sine()
    result = det.detect(y, 22050)

    assert -1.0 <= result.valence <= 1.0
    assert -1.0 <= result.arousal <= 1.0
    assert isinstance(result.moods, list)
    assert len(result.moods) >= 1
    assert result.primary_mood != ""
    assert 0.0 <= result.confidence <= 1.0


def test_quiet_signal_low_arousal():
    """Very low RMS → should yield low arousal."""
    pytest.importorskip("librosa")

    from samplemind.ai.classification.mood_detector import MoodDetector

    det = MoodDetector(use_clap=False)
    y = _sine(amplitude=0.001)  # near-silent
    result = det.detect(y, 22050)
    # Low RMS → lower arousal end
    assert result.arousal < 0.5  # should not be max arousal


def test_high_rms_high_arousal():
    """High RMS + fast BPM → high arousal."""
    pytest.importorskip("librosa")

    from samplemind.ai.classification.mood_detector import MoodDetector

    det = MoodDetector(use_clap=False)
    # Create noisy high-energy signal
    rng = np.random.default_rng(42)
    y = rng.uniform(-0.9, 0.9, 22050 * 2).astype(np.float32)
    result = det.detect(y, 22050)
    assert result.arousal > 0.0  # should lean positive arousal


def test_production_hints_present():
    from samplemind.ai.classification.mood_detector import MOOD_PRODUCTION_HINTS, _MOOD_LABELS

    # Every mood in _MOOD_LABELS should have a production hint
    for quadrant, labels in _MOOD_LABELS.items():
        for mood in labels:
            assert mood in MOOD_PRODUCTION_HINTS, f"No hint for mood={mood}"


def test_clap_fallback_no_crash():
    """detect() must not raise when CLAP is unavailable."""
    from samplemind.ai.classification.mood_detector import MoodDetector

    det = MoodDetector(use_clap=True)
    y = _sine()
    result = det.detect(y, 22050)
    assert result is not None
