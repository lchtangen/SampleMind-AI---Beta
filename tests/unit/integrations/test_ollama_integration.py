#!/usr/bin/env python3
"""
Unit tests for Ollama local AI integration — v3.0
Tests offline-capable inference with locally-running Ollama models.
All tests use mocks — no real Ollama server required.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.integrations.ollama_integration import (
    OllamaMusicProducer,
    OllamaMusicAnalysis,
    OllamaModel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ollama_client():
    """Mock ollama.AsyncClient with a standard successful response"""
    with patch("ollama.AsyncClient") as mock_cls:
        instance = AsyncMock()
        instance.chat.return_value = {
            "message": {
                "content": (
                    "Great electronic track with driving energy.\n"
                    "1. Add sidechain compression to the kick\n"
                    "2. Cut the low end below 80Hz\n"
                    "3. Try a short reverb on the snare\n"
                    "4. Layer atmospheric pads in the background\n"
                    "5. Automate the filter cutoff for movement"
                )
            }
        }
        instance.list.return_value = {
            "models": [
                {"name": "qwen2.5:7b-instruct"},
                {"name": "phi3:mini"},
            ]
        }
        mock_cls.return_value = instance
        yield instance


@pytest.fixture
def producer(mock_ollama_client):
    with patch("ollama.AsyncClient", return_value=mock_ollama_client):
        prod = OllamaMusicProducer(host="http://localhost:11434")
    prod._client = mock_ollama_client
    return prod


@pytest.fixture
def sample_features():
    return {
        "tempo": 128.0,
        "key": "C",
        "mode": "minor",
        "duration": 180.0,
    }


# ---------------------------------------------------------------------------
# TestOllamaModel
# ---------------------------------------------------------------------------

class TestOllamaModel:
    def test_qwen_model_exists(self):
        assert OllamaModel.QWEN_2_5_7B
        assert OllamaModel.QWEN_2_5_7B.value == "qwen2.5:7b-instruct"

    def test_phi3_model_exists(self):
        assert OllamaModel.PHI3_MINI
        assert OllamaModel.PHI3_MINI.value == "phi3:mini"

    def test_gemma2_model_exists(self):
        assert OllamaModel.GEMMA2_2B
        assert OllamaModel.GEMMA2_2B.value == "gemma2:2b"

    def test_default_model_is_qwen(self):
        with patch("ollama.AsyncClient"):
            prod = OllamaMusicProducer()
        assert prod.default_model == OllamaModel.QWEN_2_5_7B


# ---------------------------------------------------------------------------
# TestOllamaMusicProducer — Init
# ---------------------------------------------------------------------------

class TestOllamaMusicProducerInit:
    def test_reads_ollama_host_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://custom-host:11434")
        with patch("ollama.AsyncClient") as mock_cls:
            mock_cls.return_value = AsyncMock()
            prod = OllamaMusicProducer()
        assert prod.host == "http://custom-host:11434"

    def test_default_host_is_localhost(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_HOST", raising=False)
        with patch("ollama.AsyncClient"):
            prod = OllamaMusicProducer()
        assert "localhost" in prod.host or "11434" in prod.host

    def test_explicit_host_overrides_env(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://env-host:11434")
        with patch("ollama.AsyncClient"):
            prod = OllamaMusicProducer(host="http://explicit:11434")
        assert prod.host == "http://explicit:11434"

    def test_custom_model(self):
        with patch("ollama.AsyncClient"):
            prod = OllamaMusicProducer(default_model=OllamaModel.PHI3_MINI)
        assert prod.default_model == OllamaModel.PHI3_MINI


# ---------------------------------------------------------------------------
# TestAnalyzeMusic
# ---------------------------------------------------------------------------

class TestAnalyzeMusic:
    @pytest.mark.asyncio
    async def test_returns_ollama_music_analysis(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert isinstance(result, OllamaMusicAnalysis)

    @pytest.mark.asyncio
    async def test_summary_populated(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert len(result.summary) > 0
        assert "Great electronic track" in result.summary

    @pytest.mark.asyncio
    async def test_production_tips_populated(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert len(result.production_tips) > 0

    @pytest.mark.asyncio
    async def test_creative_ideas_populated(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert len(result.creative_ideas) > 0

    @pytest.mark.asyncio
    async def test_processing_time_recorded(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert result.processing_time >= 0

    @pytest.mark.asyncio
    async def test_model_used_set(self, producer, sample_features):
        result = await producer.analyze_music_comprehensive(sample_features)
        assert result.model_used == OllamaModel.QWEN_2_5_7B

    @pytest.mark.asyncio
    async def test_chat_called_with_correct_model(self, producer, mock_ollama_client, sample_features):
        await producer.analyze_music_comprehensive(sample_features)
        mock_ollama_client.chat.assert_called_once()
        call_kwargs = mock_ollama_client.chat.call_args.kwargs
        assert call_kwargs["model"] == OllamaModel.QWEN_2_5_7B.value

    @pytest.mark.asyncio
    async def test_api_error_propagates(self, producer, sample_features):
        producer._client.chat = AsyncMock(side_effect=ConnectionError("Ollama not running"))
        with pytest.raises(ConnectionError):
            await producer.analyze_music_comprehensive(sample_features)


# ---------------------------------------------------------------------------
# TestCheckAvailability
# ---------------------------------------------------------------------------

class TestCheckAvailability:
    @pytest.mark.asyncio
    async def test_returns_true_when_model_available(self, producer):
        result = await producer.check_availability()
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_model_not_in_list(self, producer):
        producer._client.list = AsyncMock(return_value={
            "models": [{"name": "phi3:mini"}]
        })
        # default model is qwen2.5:7b-instruct, not in list
        result = await producer.check_availability()
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self, producer):
        producer._client.list = AsyncMock(side_effect=ConnectionError("not running"))
        result = await producer.check_availability()
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_empty_model_list(self, producer):
        producer._client.list = AsyncMock(return_value={"models": []})
        result = await producer.check_availability()
        assert result is False


# ---------------------------------------------------------------------------
# TestPromptBuilding
# ---------------------------------------------------------------------------

class TestPromptBuilding:
    def test_tempo_in_prompt(self, producer, sample_features):
        prompt = producer._build_prompt(sample_features, None)
        assert "128" in prompt

    def test_key_in_prompt(self, producer, sample_features):
        prompt = producer._build_prompt(sample_features, None)
        assert "C" in prompt

    def test_mode_in_prompt(self, producer, sample_features):
        prompt = producer._build_prompt(sample_features, None)
        assert "minor" in prompt

    def test_duration_in_prompt(self, producer, sample_features):
        prompt = producer._build_prompt(sample_features, None)
        assert "180" in prompt

    def test_empty_features_handled(self, producer):
        prompt = producer._build_prompt({}, None)
        assert isinstance(prompt, str)
        assert len(prompt) > 0


# ---------------------------------------------------------------------------
# TestResponseParsing
# ---------------------------------------------------------------------------

class TestResponseParsing:
    def test_first_line_is_summary(self, producer):
        text = "Great track.\n1. Tip one\n2. Tip two\n3. Tip three\n4. Idea one\n5. Idea two"
        result = producer._parse_response(text)
        assert result.summary == "Great track."

    def test_tips_extracted(self, producer):
        text = "Summary line.\n1. First tip\n2. Second tip\n3. Third tip\n4. First idea"
        result = producer._parse_response(text)
        assert len(result.production_tips) >= 1
        assert "First tip" in result.production_tips[0]

    def test_ideas_extracted(self, producer):
        text = (
            "Summary.\n1. Tip A\n2. Tip B\n3. Tip C\n"
            "4. Creative idea one\n5. Creative idea two"
        )
        result = producer._parse_response(text)
        assert len(result.creative_ideas) >= 1

    def test_short_response_handled(self, producer):
        result = producer._parse_response("Just one line.")
        assert result.summary == "Just one line."
        assert result.production_tips == []
        assert result.creative_ideas == []

    def test_empty_response_handled(self, producer):
        result = producer._parse_response("")
        assert isinstance(result, OllamaMusicAnalysis)


# ---------------------------------------------------------------------------
# TestOllamaMusicAnalysis
# ---------------------------------------------------------------------------

class TestOllamaMusicAnalysis:
    def test_default_confidence_is_conservative(self):
        result = OllamaMusicAnalysis()
        assert result.confidence_score == 0.5

    def test_fields_have_sensible_defaults(self):
        result = OllamaMusicAnalysis()
        assert result.summary == ""
        assert result.production_tips == []
        assert result.creative_ideas == []


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
