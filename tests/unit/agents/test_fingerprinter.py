"""
Unit tests for AudioFingerprinter (Step 19).
"""

from __future__ import annotations

import hashlib

import numpy as np
import pytest


def _white_noise(sr=22050, duration=2.0, seed=0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(-0.5, 0.5, int(sr * duration)).astype(np.float32)


def test_fingerprint_returns_hex_string():
    pytest.importorskip("librosa")

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter

    fp = AudioFingerprinter()
    y = _white_noise()
    result = fp.fingerprint(y, 22050)

    assert isinstance(result.fingerprint, str)
    assert len(result.fingerprint) == 64  # SHA-256 hex
    assert result.duration > 0.0
    assert result.sample_rate == 22050


def test_fingerprint_identical_signal():
    """Same signal → same fingerprint."""
    pytest.importorskip("librosa")

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter

    fp = AudioFingerprinter()
    y = _white_noise(seed=42)
    r1 = fp.fingerprint(y, 22050)
    r2 = fp.fingerprint(y, 22050)
    assert r1.fingerprint == r2.fingerprint


def test_fingerprint_different_signals():
    """Different signals → different fingerprints (with high probability)."""
    pytest.importorskip("librosa")

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter

    fp = AudioFingerprinter()
    y1 = _white_noise(seed=1)
    y2 = _white_noise(seed=2)
    assert fp.fingerprint(y1, 22050).fingerprint != fp.fingerprint(y2, 22050).fingerprint


def test_fingerprint_no_near_duplicates_initial():
    """Without a similarity DB, near_duplicates should be empty."""
    pytest.importorskip("librosa")

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter

    fp = AudioFingerprinter()
    y = _white_noise()
    result = fp.fingerprint(y, 22050)
    assert result.near_duplicates == []
    assert result.is_exact_duplicate is False


def test_fingerprint_and_search_without_db(tmp_path):
    """fingerprint_and_search with similarity_db=None should not crash."""
    pytest.importorskip("librosa")
    import asyncio

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter
    import librosa
    import soundfile as sf

    # Create a real WAV file
    y = _white_noise()
    wav = tmp_path / "test.wav"
    sf.write(str(wav), y, 22050)

    fp = AudioFingerprinter()
    result = asyncio.run(fp.fingerprint_and_search(wav, similarity_db=None))

    assert result.file_path == str(wav)
    assert isinstance(result.fingerprint, str)


def test_fingerprint_near_duplicate_detection():
    """Simulate a near-duplicate DB returning one hit."""
    pytest.importorskip("librosa")
    import asyncio
    from unittest.mock import MagicMock

    from samplemind.core.analysis.fingerprinter import AudioFingerprinter, NearDuplicate
    import soundfile as sf
    import tempfile
    from pathlib import Path

    y = _white_noise(seed=99)

    # Mock similarity DB
    mock_similar = MagicMock()
    mock_similar.file_id = "abc123"
    mock_similar.file_path = "/other/sample.wav"
    mock_similar.similarity = 0.97
    mock_similar.metadata = {}

    mock_db = MagicMock()
    mock_db.find_similar.return_value = [mock_similar]

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, y, 22050)
        wav_path = Path(tmp.name)

    try:
        fp = AudioFingerprinter()
        result = asyncio.run(fp.fingerprint_and_search(wav_path, similarity_db=mock_db))
        assert result.duplicate_count == 1
        assert result.near_duplicates[0].similarity == 0.97
    finally:
        wav_path.unlink(missing_ok=True)
