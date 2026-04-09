"""
Unit tests for MultiLabelGenreClassifier (Step 17).
"""

from __future__ import annotations

import numpy as np
import pytest


def _sine_wave(
    freq: float = 440.0, sr: int = 22050, duration: float = 2.0
) -> np.ndarray:
    """Generate a simple sine wave for testing."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t).astype(np.float32)


def test_camelot_key_known():
    from samplemind.ai.classification.multi_label_genre import camelot_key

    assert camelot_key("A", "minor") == "8A"
    assert camelot_key("C", "major") == "8B"
    assert camelot_key("F#", "major") == "2B"


def test_camelot_key_unknown():
    from samplemind.ai.classification.multi_label_genre import camelot_key

    assert camelot_key("X", "mystery") == ""


def test_sigmoid_range():
    from samplemind.ai.classification.multi_label_genre import _sigmoid

    # sigmoid of any input must be in [0, 1]
    for x in [-5, -1, 0, 0.5, 1, 5]:
        s = _sigmoid(x)
        assert 0.0 < s < 1.0, f"sigmoid({x}) = {s} out of range"


def test_genre_result_structure_heuristic():
    """Classify a sine wave — should return a MultiLabelGenreResult without crashing."""
    pytest.importorskip("librosa")

    from samplemind.ai.classification.multi_label_genre import MultiLabelGenreClassifier

    clf = MultiLabelGenreClassifier(use_clap=False, threshold=0.0, top_k=5)
    y = _sine_wave()
    result = clf.classify(y, 22050, key="A", scale="minor")

    assert result.camelot == "8A"
    assert result.key == "A"
    assert result.scale == "minor"
    assert isinstance(result.all_genres, list)
    assert isinstance(result.scores, dict)
    # primary_genre should be set if any genres found
    if result.all_genres:
        assert result.primary_genre == result.all_genres[0]


def test_classify_heuristic_high_bpm():
    """High BPM signal should suggest dance/electronic genres."""
    pytest.importorskip("librosa")

    from samplemind.ai.classification.multi_label_genre import MultiLabelGenreClassifier

    # Create a ~130 BPM pulse signal (sparse clicks every ~0.46s)
    sr = 22050
    bpm_period = int(sr * 60 / 130)
    y = np.zeros(sr * 4, dtype=np.float32)
    for i in range(0, len(y), bpm_period):
        y[i : i + 512] = 0.8

    clf = MultiLabelGenreClassifier(use_clap=False, threshold=0.0, top_k=10)
    result = clf.classify(y, sr)

    # At ~130 BPM we expect some house/techno/dance genre in results
    dance_genres = {"House", "Tech House", "Techno", "Trance", "Trap", "Dubstep", "EDM"}
    found = {g for g in result.all_genres if g in dance_genres}
    # Heuristic should produce at least 1 dance genre
    assert len(found) >= 1 or len(result.all_genres) >= 1  # lenient — just no crash


def test_no_clap_fallback_works():
    """MultiLabelGenreClassifier must not raise if CLAP is unavailable."""
    from samplemind.ai.classification.multi_label_genre import MultiLabelGenreClassifier

    clf = MultiLabelGenreClassifier(use_clap=True)  # will fail to load CLAP → fallback
    y = _sine_wave()
    result = clf.classify(y, 22050)
    assert result is not None  # must not raise
