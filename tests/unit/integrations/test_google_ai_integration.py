#!/usr/bin/env python3
"""
Unit tests for Google AI (Gemini) integration — v3.0
Tests the google-genai SDK migration. All tests use mocks — no real API calls.

Key changes from old tests:
- Removed pytest.skip() gate — tests always run
- Uses google-genai SDK pattern: genai.Client, client.aio.models.generate_content
- Updated GeminiModel enum: GEMINI_2_0_FLASH is now primary
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.integrations.google_ai_integration import (
    AdvancedMusicAnalysis,
    GeminiModel,
    GoogleAIMusicProducer,
    MusicAnalysisType,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_genai_response():
    """Mock google-genai API response"""
    mock_response = MagicMock()
    mock_response.text = json.dumps(
        {
            "comprehensive_analysis": {
                "detailed_description": "Electronic track with strong beat.",
                "technical_summary": "Well-produced with clear mix.",
                "creative_interpretation": "Energetic and forward-moving.",
            },
            "genre_classification": {
                "primary_genre": "Electronic",
                "secondary_genres": ["House", "Techno"],
                "confidence": 0.92,
                "style_influences": ["Chicago House", "Berlin Techno"],
                "era_period": "2020s",
                "regional_style": "European",
            },
            "emotional_analysis": {
                "primary_mood": "Energetic",
                "emotional_descriptors": ["Driving", "Hypnotic"],
                "valence_score": 0.7,
                "arousal_score": 0.85,
                "emotional_intensity": 0.8,
                "emotional_journey": ["building", "peak", "resolution"],
            },
        }
    )
    mock_response.usage_metadata = MagicMock()
    mock_response.usage_metadata.total_token_count = 150
    return mock_response


@pytest.fixture
def producer(mock_genai_response):
    """GoogleAIMusicProducer with mocked google-genai Client"""
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.aio = MagicMock()
        mock_client.aio.models = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock(
            return_value=mock_genai_response
        )
        mock_client_cls.return_value = mock_client
        prod = GoogleAIMusicProducer(api_key="test-key")
        prod.client = mock_client
        yield prod


@pytest.fixture
def sample_features():
    return {
        "duration": 180.0,
        "tempo": 128.0,
        "key": "C",
        "mode": "major",
        "energy": 0.8,
    }


# ---------------------------------------------------------------------------
# TestGeminiModel
# ---------------------------------------------------------------------------


class TestGeminiModel:
    def test_gemini_2_0_flash_is_primary(self):
        """GEMINI_2_0_FLASH must be the primary model in v3.0"""
        assert GeminiModel.GEMINI_2_0_FLASH
        assert GeminiModel.GEMINI_2_0_FLASH.value == "gemini-2.0-flash"

    def test_default_model_is_gemini_2_0_flash(self):
        """Default model must be GEMINI_2_0_FLASH for v3.0"""
        with patch("google.genai.Client"):
            prod = GoogleAIMusicProducer(api_key="test")
        assert prod.default_model == GeminiModel.GEMINI_2_0_FLASH

    def test_legacy_models_still_available(self):
        assert GeminiModel.GEMINI_1_5_PRO
        assert GeminiModel.GEMINI_1_5_FLASH

    def test_all_model_values_contain_gemini(self):
        for model in GeminiModel:
            assert "gemini" in model.value.lower()


# ---------------------------------------------------------------------------
# TestAdvancedMusicAnalysis
# ---------------------------------------------------------------------------


class TestAdvancedMusicAnalysis:
    def test_create_with_required_fields(self):
        result = AdvancedMusicAnalysis(
            analysis_type=MusicAnalysisType.COMPREHENSIVE_ANALYSIS,
            model_used=GeminiModel.GEMINI_2_0_FLASH,
        )
        assert result.analysis_type == MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        assert result.model_used == GeminiModel.GEMINI_2_0_FLASH

    def test_default_string_fields_empty(self):
        result = AdvancedMusicAnalysis(
            analysis_type=MusicAnalysisType.GENRE_CLASSIFICATION,
            model_used=GeminiModel.GEMINI_2_0_FLASH,
        )
        assert result.primary_genre == ""
        assert result.primary_mood == ""
        assert result.secondary_genres == []

    def test_to_dict_returns_serializable(self):
        result = AdvancedMusicAnalysis(
            analysis_type=MusicAnalysisType.COMPREHENSIVE_ANALYSIS,
            model_used=GeminiModel.GEMINI_2_0_FLASH,
            primary_genre="Electronic",
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["primary_genre"] == "Electronic"
        # Enum values should be their string values
        assert d["model_used"] == "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# TestGoogleAIMusicProducerInit
# ---------------------------------------------------------------------------


class TestGoogleAIMusicProducerInit:
    def test_creates_genai_client_not_configure(self):
        """v3.0 uses genai.Client(), NOT genai.configure()"""
        with patch("google.genai.Client") as mock_client_cls:
            mock_client_cls.return_value = MagicMock()
            GoogleAIMusicProducer(api_key="my-key")
            mock_client_cls.assert_called_once_with(api_key="my-key")

    def test_no_genai_configure_called(self):
        """genai.configure() must NOT be called in v3.0"""
        with (
            patch("google.genai.Client") as mock_client_cls,
            patch("google.genai.configure", create=True) as mock_configure,
        ):
            mock_client_cls.return_value = MagicMock()
            GoogleAIMusicProducer(api_key="test")
            mock_configure.assert_not_called()

    def test_raises_without_api_key(self):
        import os

        with patch.dict(os.environ, {}, clear=True):
            with patch("google.genai.Client"):
                with pytest.raises(ValueError, match="API key"):
                    GoogleAIMusicProducer(api_key=None)

    def test_stats_initialized(self):
        with patch("google.genai.Client") as mock_cls:
            mock_cls.return_value = MagicMock()
            prod = GoogleAIMusicProducer(api_key="test")
        assert prod.analysis_count == 0
        assert prod.total_tokens_used == 0
        assert prod.avg_response_time == 0.0


# ---------------------------------------------------------------------------
# TestGenerateContent
# ---------------------------------------------------------------------------


class TestGenerateContent:
    @pytest.mark.asyncio
    async def test_uses_aio_models_generate_content(self, producer, sample_features):
        """Must call client.aio.models.generate_content (new SDK pattern)"""
        result = await producer.analyze_music_comprehensive(sample_features)

        assert isinstance(result, AdvancedMusicAnalysis)
        producer.client.aio.models.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_correct_model_name_sent(self, producer, sample_features):
        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.client.aio.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == GeminiModel.GEMINI_2_0_FLASH.value

    @pytest.mark.asyncio
    async def test_config_object_passed(self, producer, sample_features):
        """Config must be passed as genai_types.GenerateContentConfig"""
        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.client.aio.models.generate_content.call_args.kwargs
        assert "config" in call_kwargs

    @pytest.mark.asyncio
    async def test_prompt_contains_audio_features(self, producer, sample_features):
        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.client.aio.models.generate_content.call_args.kwargs
        prompt = call_kwargs["contents"]
        assert "128" in prompt  # tempo
        assert "180" in prompt  # duration


# ---------------------------------------------------------------------------
# TestTokenUsage
# ---------------------------------------------------------------------------


class TestTokenUsage:
    @pytest.mark.asyncio
    async def test_token_count_from_usage_metadata(self, producer, sample_features):
        """Must read tokens from response.usage_metadata.total_token_count"""
        result = await producer.analyze_music_comprehensive(sample_features)

        # token_usage dict should be populated from usage_metadata
        assert result.token_usage.get("total_token_count", -1) == 150

    @pytest.mark.asyncio
    async def test_performance_metrics_updated(self, producer, sample_features):
        await producer.analyze_music_comprehensive(sample_features)

        assert producer.analysis_count == 1
        assert producer.total_tokens_used == 150
        assert producer.avg_response_time > 0


# ---------------------------------------------------------------------------
# TestSafetySettings
# ---------------------------------------------------------------------------


class TestSafetySettings:
    @pytest.mark.asyncio
    async def test_safety_settings_passed_in_config(self, producer, sample_features):
        """Safety settings must be passed via config object, not as separate param"""
        await producer.analyze_music_comprehensive(sample_features)

        call_kwargs = producer.client.aio.models.generate_content.call_args.kwargs
        config = call_kwargs["config"]
        # Config should have safety_settings attribute
        assert hasattr(config, "safety_settings")
        assert len(config.safety_settings) > 0


# ---------------------------------------------------------------------------
# TestErrorHandling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_api_error_returns_error_analysis(self, sample_features):
        """On API error, analyze_music_comprehensive should return an error result"""
        with patch("google.genai.Client") as mock_cls:
            mock_client = MagicMock()
            mock_client.aio.models.generate_content = AsyncMock(
                side_effect=Exception("API rate limit exceeded")
            )
            mock_cls.return_value = mock_client
            prod = GoogleAIMusicProducer(api_key="test-key")

        result = await prod.analyze_music_comprehensive(sample_features)

        assert isinstance(result, AdvancedMusicAnalysis)
        assert (
            "failed" in result.detailed_description.lower()
            or "error" in result.raw_response.lower()
        )

    @pytest.mark.asyncio
    async def test_empty_features_handled(self, producer):
        result = await producer.analyze_music_comprehensive({})
        assert isinstance(result, AdvancedMusicAnalysis)

    @pytest.mark.asyncio
    async def test_malformed_json_response_handled(self, sample_features):
        with patch("google.genai.Client") as mock_cls:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.text = "This is not JSON at all!"
            mock_response.usage_metadata = None
            mock_client.aio.models.generate_content = AsyncMock(
                return_value=mock_response
            )
            mock_cls.return_value = mock_client
            prod = GoogleAIMusicProducer(api_key="test-key")

        result = await prod.analyze_music_comprehensive(sample_features)
        assert isinstance(result, AdvancedMusicAnalysis)


# ---------------------------------------------------------------------------
# TestMusicAnalysisType
# ---------------------------------------------------------------------------


class TestMusicAnalysisType:
    def test_required_types_exist(self):
        assert MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        assert MusicAnalysisType.GENRE_CLASSIFICATION
        assert MusicAnalysisType.CREATIVE_PRODUCTION
        assert MusicAnalysisType.REAL_TIME_COACHING
        assert MusicAnalysisType.FL_STUDIO_INTEGRATION

    def test_type_values_are_strings(self):
        assert (
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS.value == "comprehensive_analysis"
        )
        assert MusicAnalysisType.GENRE_CLASSIFICATION.value == "genre_classification"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
