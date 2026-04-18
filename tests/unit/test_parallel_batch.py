"""Tests for ParallelBatchProcessor (P1-018)."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.processing.parallel_batch import (
    BatchFileResult,
    BatchResult,
    ParallelBatchProcessor,
    _default_batch_analysis,
)


class TestBatchFileResult:
    """Tests for BatchFileResult."""

    def test_defaults(self) -> None:
        r = BatchFileResult(file_path="/test.wav")
        assert r.file_path == "/test.wav"
        assert r.success is False
        assert r.error is None
        assert r.features == {}


class TestBatchResult:
    """Tests for BatchResult."""

    def test_to_dict(self) -> None:
        r = BatchResult(total_files=5, successful=4, failed=1)
        d = r.to_dict()
        assert d["total_files"] == 5
        assert d["successful"] == 4
        assert d["failed"] == 1
        assert "results" in d
        assert "errors" in d


class TestDefaultBatchAnalysis:
    """Tests for default analysis function."""

    def test_basic_features(self) -> None:
        y = np.random.randn(22050).astype(np.float32)
        features = _default_batch_analysis(y, 22050)
        assert "duration" in features
        assert "rms" in features
        assert "peak" in features
        assert "crest_factor" in features
        assert features["duration"] == pytest.approx(1.0, abs=0.01)

    def test_silence(self) -> None:
        y = np.zeros(22050, dtype=np.float32)
        features = _default_batch_analysis(y, 22050)
        assert features["rms"] == 0.0
        assert features["peak"] == 0.0


class TestParallelBatchProcessor:
    """Tests for ParallelBatchProcessor."""

    def test_init_defaults(self) -> None:
        p = ParallelBatchProcessor()
        assert p.n_jobs >= 1
        assert p.batch_size == 50

    def test_init_custom(self) -> None:
        p = ParallelBatchProcessor(n_jobs=2, batch_size=10, target_sr=44100)
        assert p.n_jobs == 2
        assert p.batch_size == 10
        assert p.target_sr == 44100
