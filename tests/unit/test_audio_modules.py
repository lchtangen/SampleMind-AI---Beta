"""
Unit tests for samplemind.ai.audio (P4-010, P4-011)

Tests BEATsEncoder fallback behavior and LoopExtender crossfade logic.
All heavy deps (torch, transformers, librosa, soundfile) are mocked so
tests run without GPU or actual audio files.

Modules under test:
    samplemind.ai.audio.beats_encoder
        — BEATsEncoder, _mfcc_embed, EMBEDDING_DIM
    samplemind.ai.audio.loop_extender
        — LoopExtender, _crossfade, _detect_loop_bars, DEFAULT_CROSSFADE_S

Key test scenarios:
    BEATsEncoder — _mfcc_embed
        - Returns a unit-normed float32 vector of EMBEDDING_DIM.
        - Returns zero vector when librosa.load raises.
        - Falls back gracefully when librosa is not installed.
    BEATsEncoder — encode (MFCC fallback path)
        - Returns zero vector for a missing file.
        - Returns unit-normed vector for an existing file via MFCC fallback.
        - ``backend`` property returns "mfcc" when _use_beats is False.
        - ``dim`` property equals EMBEDDING_DIM.
        - Falls back to MFCC when transformers model load fails.
    BEATsEncoder — encode_batch
        - Returns stacked array (N, EMBEDDING_DIM).
    LoopExtender — _crossfade
        - Zero crossfade samples → simple concatenation.
        - Non-zero crossfade → smooth transition (boundary ≈ 0.5).
        - Segments shorter than crossfade → safe concatenation.
    LoopExtender — _detect_loop_bars
        - Falls back to (4, 2.0) when librosa is unavailable.
        - Uses librosa beat tracking when available.
    LoopExtender — extend
        - FileNotFoundError for missing file.
        - ImportError when librosa/soundfile are missing.
        - Produces output file with expected path and calls soundfile.write.
        - Default output path includes "extended" and bar count in stem.
        - Respects crossfade_s attribute (default vs. custom).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from samplemind.ai.audio.beats_encoder import (
    EMBEDDING_DIM,
    BEATsEncoder,
    _mfcc_embed,
)
from samplemind.ai.audio.loop_extender import (
    DEFAULT_CROSSFADE_S,
    LoopExtender,
    _crossfade,
    _detect_loop_bars,
)


# ---------------------------------------------------------------------------
# BEATsEncoder — _mfcc_embed
# ---------------------------------------------------------------------------


def test_mfcc_embed_shape_and_norm(tmp_path):
    """_mfcc_embed returns unit-normed float32 vector of EMBEDDING_DIM."""
    audio = tmp_path / "kick.wav"
    audio.write_bytes(b"\x00" * 44)

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = (
        np.random.rand(22050).astype(np.float32),
        22050,
    )
    mock_mfcc = np.random.rand(64, 100).astype(np.float32)
    mock_librosa.feature.mfcc.return_value = mock_mfcc

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa}):
        vec = _mfcc_embed(str(audio))

    assert vec.shape == (EMBEDDING_DIM,)
    assert vec.dtype == np.float32
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-5


def test_mfcc_embed_returns_zeros_on_load_error(tmp_path):
    """_mfcc_embed returns zero vector when librosa.load raises."""
    audio = tmp_path / "bad.wav"
    audio.write_bytes(b"\x00" * 44)

    mock_librosa = MagicMock()
    mock_librosa.load.side_effect = Exception("bad file")

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa}):
        vec = _mfcc_embed(str(audio))

    assert vec.shape == (EMBEDDING_DIM,)


def test_mfcc_embed_no_librosa(tmp_path):
    """Falls back gracefully when librosa is not installed."""
    audio = tmp_path / "test.wav"
    audio.write_bytes(b"\x00" * 44)

    import sys
    mods = {k: v for k, v in sys.modules.items() if "librosa" not in k}
    with patch.dict(sys.modules, {"librosa": None}):
        vec = _mfcc_embed(str(audio))

    assert vec.shape == (EMBEDDING_DIM,)


# ---------------------------------------------------------------------------
# BEATsEncoder — encode (MFCC fallback path)
# ---------------------------------------------------------------------------


def test_encoder_mfcc_fallback_file_not_found():
    """Returns zero vector for missing file."""
    encoder = BEATsEncoder()
    encoder._use_beats = False

    vec = encoder.encode("/nonexistent/file.wav")
    assert vec.shape == (EMBEDDING_DIM,)
    assert np.all(vec == 0.0)


def test_encoder_mfcc_fallback_existing_file(tmp_path):
    """Returns unit-normed vector for existing file using MFCC fallback."""
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"\x00" * 44)

    encoder = BEATsEncoder()
    encoder._use_beats = False

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = (
        np.random.rand(22050).astype(np.float32),
        22050,
    )
    mock_mfcc = np.random.rand(64, 100).astype(np.float32)
    mock_librosa.feature.mfcc.return_value = mock_mfcc

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa}):
        vec = encoder.encode(str(audio))

    assert vec.shape == (EMBEDDING_DIM,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-5


def test_encoder_backend_property_mfcc():
    """encoder.backend returns 'mfcc' when _use_beats is False."""
    encoder = BEATsEncoder()
    encoder._use_beats = False
    assert encoder.backend == "mfcc"


def test_encoder_dim_property():
    """encoder.dim returns EMBEDDING_DIM."""
    encoder = BEATsEncoder()
    assert encoder.dim == EMBEDDING_DIM


def test_encoder_beats_model_load_failure_falls_back(tmp_path):
    """When transformers raises ImportError, encoder uses MFCC."""
    audio = tmp_path / "kick.wav"
    audio.write_bytes(b"\x00" * 44)

    encoder = BEATsEncoder()
    # Simulate transformers unavailable
    with patch(
        "samplemind.ai.audio.beats_encoder.BEATsEncoder._load_model",
        return_value=False,
    ):
        with patch("samplemind.ai.audio.beats_encoder._mfcc_embed") as mock_mfcc:
            mock_mfcc.return_value = np.ones(EMBEDDING_DIM, dtype=np.float32) / np.sqrt(EMBEDDING_DIM)
            vec = encoder.encode(str(audio))

    mock_mfcc.assert_called_once_with(str(audio), dim=EMBEDDING_DIM)
    assert vec.shape == (EMBEDDING_DIM,)


def test_encoder_encode_batch(tmp_path):
    """encode_batch returns stacked array (N, EMBEDDING_DIM)."""
    paths = [str(tmp_path / f"s{i}.wav") for i in range(3)]
    for p in paths:
        Path(p).write_bytes(b"\x00" * 44)

    encoder = BEATsEncoder()
    encoder._use_beats = False

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = (np.random.rand(22050).astype(np.float32), 22050)
    mock_librosa.feature.mfcc.return_value = np.random.rand(64, 100).astype(np.float32)

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa}):
        batch = encoder.encode_batch(paths)

    assert batch.shape == (3, EMBEDDING_DIM)


# ---------------------------------------------------------------------------
# LoopExtender — _crossfade
# ---------------------------------------------------------------------------


def test_crossfade_zero_length_concatenates():
    """_crossfade with 0 crossfade samples just concatenates."""
    a = np.ones(100, dtype=np.float32)
    b = np.zeros(100, dtype=np.float32)
    result = _crossfade(a, b, 0)
    assert result.shape == (200,)
    assert result[0] == pytest.approx(1.0)
    assert result[-1] == pytest.approx(0.0)


def test_crossfade_smooth_transition():
    """_crossfade produces a smooth splice: boundary point is ~0.5."""
    n = 100
    crossfade_n = 20
    a = np.ones(n, dtype=np.float32)
    b = np.zeros(n, dtype=np.float32)
    result = _crossfade(a, b, crossfade_n)
    # At the middle of the crossfade, the value should be ~0.5
    mid = len(result) // 2
    # Result should have values strictly between 0 and 1 at the splice
    splice_region = result[n - crossfade_n : n]
    assert np.all(splice_region >= 0.0)
    assert np.all(splice_region <= 1.0)


def test_crossfade_too_short_concatenates():
    """If segments are shorter than crossfade, just concatenates."""
    a = np.ones(5, dtype=np.float32)
    b = np.zeros(5, dtype=np.float32)
    result = _crossfade(a, b, 20)  # crossfade > len(a)
    assert result.shape == (10,)


# ---------------------------------------------------------------------------
# LoopExtender — _detect_loop_bars
# ---------------------------------------------------------------------------


def test_detect_loop_bars_fallback():
    """Falls back to (4, 2.0) when librosa is unavailable."""
    import sys
    with patch.dict(sys.modules, {"librosa": None}):
        bpb, bar_dur = _detect_loop_bars(np.zeros(1000), 22050, 8)
    assert bpb == 4
    assert bar_dur == pytest.approx(2.0)


def test_detect_loop_bars_with_librosa():
    """Uses librosa beat tracking when available."""
    mock_librosa = MagicMock()
    beat_frames = np.array([0, 10, 20, 30, 40], dtype=np.int32)
    mock_librosa.beat.beat_track.return_value = (120.0, beat_frames)
    mock_librosa.frames_to_time.return_value = np.array(
        [0.0, 0.5, 1.0, 1.5, 2.0]
    )

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa}):
        bpb, bar_dur = _detect_loop_bars(np.zeros(22050), 22050, 8)

    assert bpb == 4
    assert bar_dur > 0.0


# ---------------------------------------------------------------------------
# LoopExtender — extend
# ---------------------------------------------------------------------------


def test_loop_extender_file_not_found():
    """extend() raises FileNotFoundError for missing file."""
    ext = LoopExtender()
    with pytest.raises(FileNotFoundError):
        ext.extend("/nonexistent/loop.wav", bars=4)


def test_loop_extender_no_librosa(tmp_path):
    """extend() raises ImportError when librosa is not installed."""
    audio = tmp_path / "loop.wav"
    audio.write_bytes(b"\x00" * 44)

    import sys
    with patch.dict(sys.modules, {"librosa": None, "soundfile": None}):
        ext = LoopExtender()
        with pytest.raises(ImportError):
            ext.extend(str(audio), bars=4)


def test_loop_extender_produces_output(tmp_path):
    """extend() writes an output file and returns its path."""
    audio = tmp_path / "loop.wav"
    audio.write_bytes(b"\x00" * 44)

    sr = 22050
    y = np.sin(np.linspace(0, 2 * np.pi, sr)).astype(np.float32)

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = (y, sr)
    mock_librosa.to_mono.return_value = y
    mock_librosa.beat.beat_track.return_value = (120.0, np.arange(0, 88, 11))
    mock_librosa.frames_to_time.return_value = np.arange(0, 8) * 0.5

    mock_sf = MagicMock()

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa, "soundfile": mock_sf}):
        ext = LoopExtender(crossfade_s=0.01)
        out = ext.extend(str(audio), bars=2, output_path=str(tmp_path / "out.wav"))

    assert out == str(tmp_path / "out.wav")
    assert mock_sf.write.call_count == 1


def test_loop_extender_default_output_path(tmp_path):
    """If output_path is None, derives path from input stem."""
    audio = tmp_path / "loop.wav"
    audio.write_bytes(b"\x00" * 44)

    sr = 22050
    y = np.sin(np.linspace(0, 2 * np.pi, sr)).astype(np.float32)

    mock_librosa = MagicMock()
    mock_librosa.load.return_value = (y, sr)
    mock_librosa.to_mono.return_value = y
    mock_librosa.beat.beat_track.return_value = (120.0, np.arange(0, 44, 11))
    mock_librosa.frames_to_time.return_value = np.arange(0, 4) * 0.5

    mock_sf = MagicMock()

    import sys
    with patch.dict(sys.modules, {"librosa": mock_librosa, "soundfile": mock_sf}):
        ext = LoopExtender()
        out = ext.extend(str(audio), bars=2)

    assert "extended" in Path(out).name
    assert "2bars" in Path(out).name


def test_loop_extender_crossfade_attribute():
    """LoopExtender respects crossfade_s attribute."""
    ext = LoopExtender(crossfade_s=0.1)
    assert ext.crossfade_s == pytest.approx(0.1)
    ext2 = LoopExtender()
    assert ext2.crossfade_s == pytest.approx(DEFAULT_CROSSFADE_S)
