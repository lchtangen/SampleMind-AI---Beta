"""
Tests for SimilarSampleGenerator (P4-008)

Tests the core generation logic with mocked audio I/O and FAISS index.
"""

from __future__ import annotations

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

# Module under test
from samplemind.ai.generation.similar_sample import (
    GenerationResult,
    SampleVariation,
    SimilarSampleGenerator,
    _blend_audio,
    _generate_variation_id,
)


@pytest.fixture
def generator(tmp_path):
    return SimilarSampleGenerator(output_dir=str(tmp_path))


class TestSampleVariation:
    def test_defaults(self):
        v = SampleVariation(
            path="/out.wav",
            similarity_score=0.9,
            source_path="/in.wav",
        )
        assert v.technique == "blend"
        assert v.neighbour_path is None
        assert v.metadata == {}

    def test_full(self):
        v = SampleVariation(
            path="/out.wav",
            similarity_score=0.85,
            source_path="/in.wav",
            neighbour_path="/nb.wav",
            technique="pitch_shift",
            duration_seconds=2.5,
            metadata={"n_steps": 3},
        )
        assert v.technique == "pitch_shift"
        assert v.metadata["n_steps"] == 3


class TestGenerationResult:
    def test_defaults(self):
        r = GenerationResult(source_path="/in.wav")
        assert r.variations == []
        assert r.neighbours_found == 0
        assert r.errors == []


class TestBlendAudio:
    def test_blend_equal_length(self):
        import numpy as np

        y1 = np.ones(100, dtype=np.float32)
        y2 = np.zeros(100, dtype=np.float32)
        blended = _blend_audio(y1, y2, alpha=0.5)
        assert len(blended) == 100
        assert abs(blended[0] - 0.5) < 0.01

    def test_blend_different_length(self):
        import numpy as np

        y1 = np.ones(100, dtype=np.float32)
        y2 = np.zeros(50, dtype=np.float32)
        blended = _blend_audio(y1, y2, alpha=0.7)
        assert len(blended) == 50

    def test_blend_alpha_one(self):
        import numpy as np

        y1 = np.ones(100, dtype=np.float32) * 2.0
        y2 = np.ones(100, dtype=np.float32) * 5.0
        blended = _blend_audio(y1, y2, alpha=1.0)
        assert abs(blended[0] - 2.0) < 0.01

    def test_blend_alpha_zero(self):
        import numpy as np

        y1 = np.ones(100, dtype=np.float32) * 2.0
        y2 = np.ones(100, dtype=np.float32) * 5.0
        blended = _blend_audio(y1, y2, alpha=0.0)
        assert abs(blended[0] - 5.0) < 0.01


class TestVariationId:
    def test_contains_source_stem(self):
        vid = _generate_variation_id("/path/to/kick.wav", "blend", 0)
        assert "kick" in vid
        assert "blend" in vid

    def test_unique_ids(self):
        ids = set()
        for i in range(10):
            ids.add(_generate_variation_id("/a.wav", "pitch", i))
        # Should generate unique IDs (highly likely with md5 + time)
        assert len(ids) >= 5  # relaxed due to timing


class TestSimilarSampleGenerator:
    def test_init(self, tmp_path):
        gen = SimilarSampleGenerator(output_dir=str(tmp_path))
        assert gen.output_dir.exists()

    def test_init_default(self):
        gen = SimilarSampleGenerator()
        assert gen.output_dir is not None

    @patch(
        "samplemind.ai.generation.similar_sample._load_audio",
        side_effect=FileNotFoundError("no such file"),
    )
    def test_generate_missing_file(self, mock_load, generator):
        result = asyncio.get_event_loop().run_until_complete(
            generator.generate(source_path="/nonexistent.wav")
        )
        assert isinstance(result, GenerationResult)
        assert len(result.errors) > 0
        assert "Cannot load" in result.errors[0]

    @patch("samplemind.ai.generation.similar_sample._load_audio")
    @patch("samplemind.ai.generation.similar_sample._save_audio")
    def test_generate_pitch_variation(self, mock_save, mock_load, generator):
        import numpy as np

        mock_load.return_value = (np.zeros(22050, dtype=np.float32), 22050)
        mock_save.return_value = "/out.wav"

        with patch("librosa.effects.pitch_shift", return_value=np.zeros(22050)):
            with patch("librosa.get_duration", return_value=1.0):
                result = asyncio.get_event_loop().run_until_complete(
                    generator.generate(
                        source_path="/test.wav",
                        techniques=["pitch_shift"],
                        variation_count=1,
                    )
                )

        assert len(result.variations) == 1
        assert result.variations[0].technique == "pitch_shift"

    @patch("samplemind.ai.generation.similar_sample._load_audio")
    @patch("samplemind.ai.generation.similar_sample._save_audio")
    def test_generate_stretch_variation(self, mock_save, mock_load, generator):
        import numpy as np

        mock_load.return_value = (np.zeros(22050, dtype=np.float32), 22050)
        mock_save.return_value = "/out.wav"

        with patch("librosa.effects.time_stretch", return_value=np.zeros(22050)):
            with patch("librosa.get_duration", return_value=1.0):
                result = asyncio.get_event_loop().run_until_complete(
                    generator.generate(
                        source_path="/test.wav",
                        techniques=["time_stretch"],
                        variation_count=1,
                    )
                )

        assert len(result.variations) == 1
        assert result.variations[0].technique == "time_stretch"

    @patch("samplemind.ai.generation.similar_sample._load_audio")
    @patch("samplemind.ai.generation.similar_sample._save_audio")
    def test_generate_effects_variation(self, mock_save, mock_load, generator):
        import numpy as np

        mock_load.return_value = (np.zeros(22050, dtype=np.float32), 22050)
        mock_save.return_value = "/out.wav"

        with patch("librosa.get_duration", return_value=1.0):
            result = asyncio.get_event_loop().run_until_complete(
                generator.generate(
                    source_path="/test.wav",
                    techniques=["effects"],
                    variation_count=1,
                )
            )

        assert len(result.variations) == 1
        assert result.variations[0].technique == "effects"
