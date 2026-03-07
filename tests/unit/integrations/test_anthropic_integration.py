#!/usr/bin/env python3
"""
Unit tests for Anthropic (Claude) integration — v3.0
Tests model enum, client initialization, extended thinking, prompt building,
response parsing, stats tracking, and error handling.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.integrations.anthropic_integration import (
    AnthropicMusicProducer,
    AnthropicMusicAnalysis,
    AnthropicAnalysisType,
    ClaudeModel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_anthropic_response():
    """Mock successful Claude API response with JSON content"""
    mock = MagicMock()
    mock.content = [
        MagicMock(
            text=json.dumps({
                "summary": "Energetic electronic track with driving rhythm.",
                "detailed_analysis": "Full analysis here.",
                "production_tips": ["Add sidechain compression", "Layer pads"],
                "creative_ideas": ["Try a breakdown at 2:00"],
                "fl_studio_recommendations": ["Use Serum for lead"],
                "arrangement_suggestions": ["Add a bridge section"],
                "harmonic_analysis": {"key_info": "C minor", "progressions": ["i-VI-III-VII"]},
                "confidence_score": 0.9,
            })
        )
    ]
    mock.usage = MagicMock()
    mock.usage.input_tokens = 100
    mock.usage.output_tokens = 200
    return mock


@pytest.fixture
def producer():
    """AnthropicMusicProducer with mocked async client"""
    with patch("anthropic.AsyncAnthropic") as mock_cls, \
         patch("anthropic.Anthropic"):
        instance = mock_cls.return_value
        instance.messages = MagicMock()
        instance.messages.create = AsyncMock()
        prod = AnthropicMusicProducer(api_key="test-key")
        prod.async_client = instance
        yield prod


@pytest.fixture
def sample_features():
    return {
        "tempo": 128.0,
        "key": "C",
        "mode": "minor",
        "duration": 180.0,
        "energy": 0.75,
    }


# ---------------------------------------------------------------------------
# TestClaudeModel
# ---------------------------------------------------------------------------

class TestClaudeModel:
    def test_claude_3_7_sonnet_exists(self):
        assert ClaudeModel.CLAUDE_3_7_SONNET
        assert ClaudeModel.CLAUDE_3_7_SONNET.value == "claude-3-7-sonnet-20250219"

    def test_claude_3_5_sonnet_exists(self):
        assert ClaudeModel.CLAUDE_3_5_SONNET
        assert ClaudeModel.CLAUDE_3_5_SONNET.value == "claude-3-5-sonnet-20241022"

    def test_claude_3_5_haiku_exists(self):
        assert ClaudeModel.CLAUDE_3_5_HAIKU
        assert ClaudeModel.CLAUDE_3_5_HAIKU.value == "claude-3-5-haiku-20241022"

    def test_default_model_is_claude_3_7(self):
        """Default model must be claude-3-7-sonnet for v3.0"""
        with patch("anthropic.AsyncAnthropic"), patch("anthropic.Anthropic"):
            prod = AnthropicMusicProducer(api_key="test")
        assert prod.default_model == ClaudeModel.CLAUDE_3_7_SONNET

    def test_legacy_models_still_available(self):
        assert ClaudeModel.CLAUDE_3_OPUS
        assert ClaudeModel.CLAUDE_3_HAIKU


# ---------------------------------------------------------------------------
# TestAnthropicMusicProducer — Initialization
# ---------------------------------------------------------------------------

class TestAnthropicMusicProducer:
    def test_init_with_api_key(self):
        with patch("anthropic.AsyncAnthropic"), patch("anthropic.Anthropic"):
            prod = AnthropicMusicProducer(api_key="sk-test-123")
        assert prod.default_model == ClaudeModel.CLAUDE_3_7_SONNET
        assert prod.max_tokens == 8096
        assert prod.temperature == 1.0

    def test_init_with_custom_model(self):
        with patch("anthropic.AsyncAnthropic"), patch("anthropic.Anthropic"):
            prod = AnthropicMusicProducer(
                api_key="sk-test",
                default_model=ClaudeModel.CLAUDE_3_5_HAIKU,
            )
        assert prod.default_model == ClaudeModel.CLAUDE_3_5_HAIKU

    def test_stats_initialized_to_zero(self):
        with patch("anthropic.AsyncAnthropic"), patch("anthropic.Anthropic"):
            prod = AnthropicMusicProducer(api_key="sk-test")
        assert prod.stats["total_analyses"] == 0
        assert prod.stats["success_count"] == 0
        assert prod.stats["error_count"] == 0


# ---------------------------------------------------------------------------
# TestExtendedThinking
# ---------------------------------------------------------------------------

class TestExtendedThinking:
    @pytest.mark.asyncio
    async def test_extended_thinking_added_for_claude_3_7(
        self, producer, mock_anthropic_response, sample_features
    ):
        """claude-3-7-sonnet must send thinking param, not temperature"""
        producer.default_model = ClaudeModel.CLAUDE_3_7_SONNET
        producer.async_client.messages.create = AsyncMock(
            return_value=mock_anthropic_response
        )

        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.async_client.messages.create.call_args.kwargs
        assert "thinking" in call_kwargs
        assert call_kwargs["thinking"]["type"] == "enabled"
        assert call_kwargs["thinking"]["budget_tokens"] == 5000
        # temperature must NOT be present for extended thinking
        assert "temperature" not in call_kwargs

    @pytest.mark.asyncio
    async def test_temperature_added_for_non_3_7_model(
        self, producer, mock_anthropic_response, sample_features
    ):
        """Non-3.7 models must send temperature, not thinking"""
        producer.default_model = ClaudeModel.CLAUDE_3_5_HAIKU
        producer.async_client.messages.create = AsyncMock(
            return_value=mock_anthropic_response
        )

        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.async_client.messages.create.call_args.kwargs
        assert "temperature" in call_kwargs
        assert "thinking" not in call_kwargs


# ---------------------------------------------------------------------------
# TestPromptBuilding
# ---------------------------------------------------------------------------

class TestPromptBuilding:
    def test_all_analysis_types_produce_nonempty_prompt(self, producer, sample_features):
        for analysis_type in AnthropicAnalysisType:
            prompt = producer._build_prompt(sample_features, analysis_type, None)
            assert isinstance(prompt, str)
            assert len(prompt) > 50

    def test_features_interpolated_in_prompt(self, producer, sample_features):
        prompt = producer._build_prompt(
            sample_features, AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS, None
        )
        assert "128" in prompt  # tempo
        assert "C" in prompt    # key
        assert "minor" in prompt

    def test_user_context_included_when_provided(self, producer, sample_features):
        context = {"skill_level": "expert", "genre_preference": "techno"}
        prompt = producer._build_prompt(
            sample_features, AnthropicAnalysisType.PRODUCTION_COACHING, context
        )
        assert "expert" in prompt or "skill_level" in prompt


# ---------------------------------------------------------------------------
# TestResponseParsing
# ---------------------------------------------------------------------------

class TestResponseParsing:
    def test_valid_json_response_parsed(self, producer, mock_anthropic_response):
        result = producer._parse_response(
            mock_anthropic_response, AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS
        )
        assert isinstance(result, AnthropicMusicAnalysis)
        assert result.summary == "Energetic electronic track with driving rhythm."
        assert len(result.production_tips) == 2
        assert result.confidence_score == 0.9

    def test_malformed_json_falls_back_gracefully(self, producer):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="This is plain text, not JSON.")]
        result = producer._parse_response(
            mock_response, AnthropicAnalysisType.COMPREHENSIVE_ANALYSIS
        )
        assert isinstance(result, AnthropicMusicAnalysis)
        assert "This is plain text" in result.summary or len(result.detailed_analysis) > 0

    def test_json_in_code_block_extracted(self, producer):
        inner = json.dumps({"summary": "Test summary", "production_tips": ["tip1"]})
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=f"```json\n{inner}\n```")]
        result = producer._parse_response(
            mock_response, AnthropicAnalysisType.PRODUCTION_COACHING
        )
        assert result.summary == "Test summary"
        assert result.production_tips == ["tip1"]


# ---------------------------------------------------------------------------
# TestStatsTracking
# ---------------------------------------------------------------------------

class TestStatsTracking:
    @pytest.mark.asyncio
    async def test_success_increments_stats(
        self, producer, mock_anthropic_response, sample_features
    ):
        producer.async_client.messages.create = AsyncMock(
            return_value=mock_anthropic_response
        )
        await producer.analyze_music_comprehensive(sample_features)

        assert producer.stats["total_analyses"] == 1
        assert producer.stats["success_count"] == 1
        assert producer.stats["error_count"] == 0
        assert producer.stats["total_tokens_used"] == 300  # 100 + 200

    @pytest.mark.asyncio
    async def test_failure_increments_error_count(self, producer, sample_features):
        producer.async_client.messages.create = AsyncMock(
            side_effect=Exception("API error")
        )
        with pytest.raises(Exception):
            await producer.analyze_music_comprehensive(sample_features)

        assert producer.stats["error_count"] == 1
        assert producer.stats["success_count"] == 0

    def test_get_performance_stats_structure(self, producer):
        stats = producer.get_performance_stats()
        assert "success_rate" in stats
        assert "avg_tokens_per_analysis" in stats
        assert "cost_per_analysis" in stats


# ---------------------------------------------------------------------------
# TestAnalysisFlow
# ---------------------------------------------------------------------------

class TestAnalysisFlow:
    @pytest.mark.asyncio
    async def test_full_analysis_returns_result(
        self, producer, mock_anthropic_response, sample_features
    ):
        producer.async_client.messages.create = AsyncMock(
            return_value=mock_anthropic_response
        )
        result = await producer.analyze_music_comprehensive(sample_features)

        assert isinstance(result, AnthropicMusicAnalysis)
        assert result.processing_time > 0
        assert result.tokens_used == 300
        assert result.model_used == ClaudeModel.CLAUDE_3_7_SONNET

    @pytest.mark.asyncio
    async def test_api_exception_propagates(self, producer, sample_features):
        producer.async_client.messages.create = AsyncMock(
            side_effect=ConnectionError("Network error")
        )
        with pytest.raises(ConnectionError):
            await producer.analyze_music_comprehensive(sample_features)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
