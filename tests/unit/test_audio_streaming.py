"""Tests for AudioStreamProcessor (P1-017)."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.processing.audio_streaming import (
    AudioChunk,
    AudioStreamProcessor,
    ChunkResult,
    StreamingResult,
)


class TestAudioStreamProcessor:
    """Tests for AudioStreamProcessor."""

    def test_init_defaults(self) -> None:
        processor = AudioStreamProcessor()
        assert processor.chunk_duration == 10.0
        assert processor.overlap == 1.0
        assert processor.target_sr == 22050

    def test_init_custom(self) -> None:
        processor = AudioStreamProcessor(chunk_duration=5.0, overlap=0.5, target_sr=44100)
        assert processor.chunk_duration == 5.0
        assert processor.overlap == 0.5
        assert processor.target_sr == 44100

    def test_init_invalid_chunk_duration(self) -> None:
        with pytest.raises(ValueError, match="chunk_duration must be positive"):
            AudioStreamProcessor(chunk_duration=0)

    def test_init_negative_overlap(self) -> None:
        with pytest.raises(ValueError, match="overlap must be non-negative"):
            AudioStreamProcessor(overlap=-1.0)

    def test_init_overlap_exceeds_chunk(self) -> None:
        with pytest.raises(ValueError, match="overlap must be less than"):
            AudioStreamProcessor(chunk_duration=5.0, overlap=5.0)

    def test_split_short_audio(self) -> None:
        processor = AudioStreamProcessor(chunk_duration=5.0, overlap=0.5)
        sr = 22050
        y = np.zeros(sr * 3, dtype=np.float32)  # 3 seconds
        chunks = processor.split_audio(y, sr)
        assert len(chunks) >= 1
        assert chunks[0].is_first
        assert chunks[-1].is_last

    def test_split_long_audio(self) -> None:
        processor = AudioStreamProcessor(chunk_duration=5.0, overlap=1.0)
        sr = 22050
        y = np.zeros(sr * 20, dtype=np.float32)  # 20 seconds
        chunks = processor.split_audio(y, sr)
        assert len(chunks) >= 4  # ~20 / (5-1) = 5 chunks

    def test_chunk_properties(self) -> None:
        processor = AudioStreamProcessor(chunk_duration=5.0, overlap=0.0)
        sr = 22050
        y = np.random.randn(sr * 10).astype(np.float32)
        chunks = processor.split_audio(y, sr)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.total_chunks == len(chunks)
            assert chunk.sample_rate == sr
            assert chunk.start_time >= 0
            assert chunk.end_time > chunk.start_time

    def test_empty_audio(self) -> None:
        processor = AudioStreamProcessor(chunk_duration=5.0, overlap=0.0)
        y = np.array([], dtype=np.float32)
        chunks = processor.split_audio(y, 22050)
        assert len(chunks) >= 1  # At least one chunk


class TestStreamingResult:
    """Tests for StreamingResult."""

    def test_to_dict(self) -> None:
        result = StreamingResult(
            file_path="/test.wav",
            total_duration=10.0,
            sample_rate=22050,
            total_chunks=2,
        )
        d = result.to_dict()
        assert d["file_path"] == "/test.wav"
        assert d["total_duration"] == 10.0
        assert d["total_chunks"] == 2


class TestChunkResult:
    """Tests for ChunkResult."""

    def test_defaults(self) -> None:
        cr = ChunkResult(chunk_index=0, total_chunks=5, start_time=0.0, end_time=5.0)
        assert cr.chunk_index == 0
        assert cr.features == {}
        assert cr.errors == []
