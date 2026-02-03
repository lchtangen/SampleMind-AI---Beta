"""Tests for the Neural Audio Generation Manager (Phase 4.3)"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from samplemind.core.generation.generation_manager import (
    GenerationManager,
    GenerationRequest,
    GenerationResult,
    GenerationMode,
    GenerationStatus,
)


@pytest.fixture
def manager():
    return GenerationManager()


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestGenerationRequest:
    def test_request_creation(self):
        req = GenerationRequest(prompt="upbeat electronic drums")
        assert req.prompt == "upbeat electronic drums"
        assert req.mode == GenerationMode.TEXT_TO_SAMPLE
        assert req.status == GenerationStatus.PENDING
        assert req.id is not None

    def test_request_to_dict(self):
        req = GenerationRequest(
            prompt="dark ambient pad",
            mode=GenerationMode.CONTEXT_SUGGEST,
        )
        d = req.to_dict()
        assert d["prompt"] == "dark ambient pad"
        assert d["mode"] == "context_suggest"
        assert d["status"] == "pending"

    def test_request_with_source_audio(self):
        req = GenerationRequest(
            mode=GenerationMode.AUDIO_VARIATION,
            source_audio=Path("/tmp/test.wav"),
        )
        assert req.source_audio == Path("/tmp/test.wav")

    def test_request_with_parameters(self):
        req = GenerationRequest(
            prompt="test",
            parameters={"num_results": 5, "temperature": 0.8},
        )
        assert req.parameters["num_results"] == 5
        assert req.parameters["temperature"] == 0.8


class TestGenerationResult:
    def test_result_creation(self):
        result = GenerationResult(
            request_id="abc123",
            mode=GenerationMode.TEXT_TO_SAMPLE,
        )
        assert result.request_id == "abc123"
        assert result.matches == []
        assert result.suggestions == []
        assert result.processing_time == 0.0

    def test_result_to_dict(self):
        result = GenerationResult(
            request_id="xyz",
            mode=GenerationMode.STEM_REMIX,
            suggestions=[{"name": "test"}],
            processing_time=1.5,
        )
        d = result.to_dict()
        assert d["request_id"] == "xyz"
        assert d["mode"] == "stem_remix"
        assert d["processing_time"] == 1.5
        assert len(d["suggestions"]) == 1


class TestGenerationManager:
    def test_manager_initialization(self, manager):
        assert manager._neural_engine is None
        assert manager._stem_engine is None
        assert manager._requests == {}
        assert manager._results == {}

    def test_text_to_sample(self, manager):
        req = GenerationRequest(
            prompt="heavy bass drum 808",
            mode=GenerationMode.TEXT_TO_SAMPLE,
            parameters={"num_results": 5},
        )
        result = run_async(manager.generate(req))
        assert result.request_id == req.id
        assert result.mode == GenerationMode.TEXT_TO_SAMPLE
        assert result.processing_time > 0
        assert req.status == GenerationStatus.COMPLETED

    def test_context_suggest(self, manager):
        req = GenerationRequest(
            mode=GenerationMode.CONTEXT_SUGGEST,
            parameters={
                "context": {
                    "key": "Am",
                    "tempo": 128,
                    "genre": "electronic",
                }
            },
        )
        result = run_async(manager.generate(req))
        assert len(result.suggestions) == 3
        assert result.suggestions[0]["type"] == "complementary_sample"
        assert result.suggestions[1]["type"] == "harmonic_match"
        assert result.suggestions[2]["type"] == "processing_chain"

    def test_audio_variation_no_source(self, manager):
        req = GenerationRequest(
            mode=GenerationMode.AUDIO_VARIATION,
        )
        result = run_async(manager.generate(req))
        assert "error" in result.metadata

    def test_stem_remix_insufficient_sources(self, manager):
        req = GenerationRequest(
            mode=GenerationMode.STEM_REMIX,
            parameters={"sources": ["/tmp/a.wav"]},
        )
        result = run_async(manager.generate(req))
        assert "error" in result.metadata

    def test_stem_remix_with_sources(self, manager):
        req = GenerationRequest(
            mode=GenerationMode.STEM_REMIX,
            parameters={"sources": ["/tmp/a.wav", "/tmp/b.wav", "/tmp/c.wav"]},
        )
        result = run_async(manager.generate(req))
        assert len(result.suggestions) == 3
        assert result.metadata["num_sources"] == 3

    def test_get_request_status(self, manager):
        req = GenerationRequest(prompt="test")
        run_async(manager.generate(req))
        status = manager.get_request_status(req.id)
        assert status is not None
        assert status["status"] == "completed"

    def test_get_nonexistent_status(self, manager):
        assert manager.get_request_status("nonexistent") is None

    def test_list_requests(self, manager):
        req1 = GenerationRequest(prompt="test1")
        req2 = GenerationRequest(
            mode=GenerationMode.CONTEXT_SUGGEST,
            parameters={"context": {"key": "C", "tempo": 120, "genre": "ambient"}},
        )
        run_async(manager.generate(req1))
        run_async(manager.generate(req2))
        requests = manager.list_requests()
        assert len(requests) == 2

    def test_compatible_keys(self, manager):
        keys = manager._get_compatible_keys("C")
        assert "G" in keys or "F" in keys

    def test_compatible_keys_unknown(self, manager):
        keys = manager._get_compatible_keys("X#")
        assert keys == ["C", "G", "Am"]

    def test_processing_chain_electronic(self, manager):
        chain = manager._suggest_processing_chain("electronic")
        assert len(chain) == 3
        assert chain[0]["plugin"] == "EQ"

    def test_processing_chain_hiphop(self, manager):
        chain = manager._suggest_processing_chain("hip-hop")
        assert len(chain) == 3

    def test_processing_chain_unknown_genre(self, manager):
        chain = manager._suggest_processing_chain("polka")
        assert len(chain) == 3  # Falls back to electronic

    def test_suggest_transforms(self, manager):
        mock_features = MagicMock()
        transforms = manager._suggest_transforms(mock_features, 0)
        assert len(transforms) == 2
        assert transforms[0]["type"] in ["pitch_shift", "time_stretch", "reverb", "filter"]
