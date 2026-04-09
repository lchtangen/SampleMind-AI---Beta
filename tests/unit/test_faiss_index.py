"""
Unit tests for samplemind.core.search.faiss_index

All heavy deps (faiss, transformers, librosa) are mocked so the tests run
in any CI environment without GPU or audio-file fixtures.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from samplemind.core.search.faiss_index import (
    EMBEDDING_DIM,
    CLAPEmbedder,
    FAISSIndex,
    IndexEntry,
    SearchResult,
    _normalize,
    get_index,
)

# ── helpers ───────────────────────────────────────────────────────────────────


def _random_unit_vec() -> np.ndarray:
    """Return a random unit-normalised float32 vector of EMBEDDING_DIM."""
    v = np.random.rand(EMBEDDING_DIM).astype(np.float32)
    return v / np.linalg.norm(v)


def _mock_embedder() -> CLAPEmbedder:
    """Return a CLAPEmbedder whose embed_* methods return deterministic vectors."""
    emb = MagicMock(spec=CLAPEmbedder)
    emb.embed_audio.return_value = _random_unit_vec()
    emb.embed_text.return_value = _random_unit_vec()
    return emb


def _fake_faiss_index(n_entries: int = 0):
    """Minimal faiss.IndexIDMap stub that records add_with_ids calls."""
    idx = MagicMock()
    idx.ntotal = n_entries
    # search returns (scores, ids) as 2-D arrays
    scores = np.array([[0.9, 0.7]], dtype=np.float32)
    ids = np.array([[0, 1]], dtype=np.int64)
    idx.search.return_value = (scores, ids)
    return idx


# ── _normalize ────────────────────────────────────────────────────────────────


def test_normalize_unit_vector():
    v = np.array([3.0, 4.0], dtype=np.float32)
    n = _normalize(v)
    assert abs(np.linalg.norm(n) - 1.0) < 1e-6


def test_normalize_zero_vector():
    v = np.zeros(4, dtype=np.float32)
    n = _normalize(v)
    # Should return unchanged (no division by zero)
    assert np.all(n == 0.0)


# ── CLAPEmbedder fallback ─────────────────────────────────────────────────────


def test_clap_embedder_text_hash_fallback():
    """_text_hash_embed should return unit vector of EMBEDDING_DIM."""
    embedder = CLAPEmbedder.__new__(CLAPEmbedder)
    embedder._use_clap = False
    vec = embedder._text_hash_embed("dark trap kick")
    assert vec.shape == (EMBEDDING_DIM,)
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-6


def test_clap_embedder_mfcc_fallback_no_file(tmp_path):
    """_mfcc_embed should return zero-padded vector when file is missing."""
    embedder = CLAPEmbedder.__new__(CLAPEmbedder)
    embedder._use_clap = False
    # librosa.load will fail for missing file — fallback to zeros
    vec = embedder._mfcc_embed(str(tmp_path / "missing.wav"))
    assert vec.shape == (EMBEDDING_DIM,)


# ── FAISSIndex.add ─────────────────────────────────────────────────────────────


def test_faiss_add_increments_size():
    fake_idx = _fake_faiss_index()
    embedder = _mock_embedder()

    with patch("samplemind.core.search.faiss_index.FAISSIndex._get_or_create_index", return_value=fake_idx):
        index = FAISSIndex.__new__(FAISSIndex)
        index._dir = Path(tempfile.mkdtemp())
        index._index_path = index._dir / "index.bin"
        index._meta_path = index._dir / "metadata.json"
        index._embedder = embedder
        index._index = fake_idx
        index._entries = []

        idx_id = index.add("/fake/kick.wav", metadata={"bpm": 140.0, "key": "Am"})

    assert idx_id == 0
    assert index.size == 1
    assert index._entries[0].filename == "kick.wav"
    assert index._entries[0].bpm == 140.0


def test_faiss_add_multiple():
    fake_idx = _fake_faiss_index()
    embedder = _mock_embedder()

    with patch("samplemind.core.search.faiss_index.FAISSIndex._get_or_create_index", return_value=fake_idx):
        index = FAISSIndex.__new__(FAISSIndex)
        index._dir = Path(tempfile.mkdtemp())
        index._index_path = index._dir / "index.bin"
        index._meta_path = index._dir / "metadata.json"
        index._embedder = embedder
        index._index = fake_idx
        index._entries = []

        for i in range(3):
            index.add(f"/fake/sample_{i}.wav")

    assert index.size == 3


# ── FAISSIndex.search_text ─────────────────────────────────────────────────────


def test_search_text_returns_results():
    fake_idx = _fake_faiss_index(n_entries=2)
    embedder = _mock_embedder()

    index = FAISSIndex.__new__(FAISSIndex)
    index._dir = Path(tempfile.mkdtemp())
    index._index_path = index._dir / "index.bin"
    index._meta_path = index._dir / "metadata.json"
    index._embedder = embedder
    index._index = fake_idx
    index._entries = [
        IndexEntry(index_id=0, path="/a.wav", filename="a.wav"),
        IndexEntry(index_id=1, path="/b.wav", filename="b.wav"),
    ]

    results = index.search_text("dark trap kick", top_k=2)

    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert isinstance(r, SearchResult)
        assert 0.0 <= r.score <= 1.0


def test_search_text_empty_index():
    embedder = _mock_embedder()
    index = FAISSIndex.__new__(FAISSIndex)
    index._embedder = embedder
    index._index = None
    index._entries = []

    results = index.search_text("anything")
    assert results == []


# ── FAISSIndex.save / load ────────────────────────────────────────────────────


def test_save_writes_metadata_json(tmp_path):
    fake_faiss = MagicMock()

    index = FAISSIndex.__new__(FAISSIndex)
    index._dir = tmp_path
    index._index_path = tmp_path / "index.bin"
    index._meta_path = tmp_path / "metadata.json"
    index._index = fake_faiss
    index._entries = [
        IndexEntry(index_id=0, path="/kick.wav", filename="kick.wav", bpm=140.0),
    ]

    import sys
    from unittest.mock import MagicMock as MM

    fake_faiss_mod = sys.modules.get("faiss", MM())
    fake_faiss_mod.write_index = MM()  # type: ignore[attr-defined]
    with patch.dict(sys.modules, {"faiss": fake_faiss_mod}):
        index.save()

    meta = json.loads((tmp_path / "metadata.json").read_text())
    assert len(meta) == 1
    assert meta[0]["filename"] == "kick.wav"
    assert meta[0]["bpm"] == 140.0


def test_load_returns_false_when_no_file(tmp_path):
    index = FAISSIndex.__new__(FAISSIndex)
    index._dir = tmp_path
    index._index_path = tmp_path / "nonexistent.bin"
    index._meta_path = tmp_path / "nonexistent.json"
    index._index = None
    index._entries = []

    result = index.load()
    assert result is False


# ── get_index singleton ───────────────────────────────────────────────────────


def test_get_index_returns_faiss_index():
    import samplemind.core.search.faiss_index as mod

    # Reset singleton
    mod._global_index = None

    with patch.object(FAISSIndex, "load", return_value=False):
        with patch.object(FAISSIndex, "__init__", lambda self, *a, **kw: None):
            idx = FAISSIndex.__new__(FAISSIndex)
            idx._dir = Path(tempfile.mkdtemp())
            idx._index_path = idx._dir / "i.bin"
            idx._meta_path = idx._dir / "m.json"
            idx._index = None
            idx._entries = []
            idx._embedder = _mock_embedder()
            mod._global_index = idx
            result = get_index(auto_load=False)

    assert result is idx
    mod._global_index = None  # cleanup
