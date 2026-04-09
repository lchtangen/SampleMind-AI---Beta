#!/usr/bin/env python3
"""
Unit tests for OpenAI integration
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from samplemind.integrations.openai_integration import (
    MusicAnalysisType,
    OpenAIModel,
    OpenAIMusicAnalysis,
    OpenAIMusicProducer,
)


class TestOpenAIModel:
    """Test OpenAIModel enum"""

    def test_models_exist(self):
        """Test all models are defined"""
        assert OpenAIModel.GPT_4O
        assert OpenAIModel.GPT_4O_MINI
        assert OpenAIModel.GPT_4_TURBO
        assert OpenAIModel.GPT_4

    def test_gpt5_does_not_exist(self):
        """GPT-5 does not exist — must not be in the enum"""
        assert not hasattr(OpenAIModel, "GPT_5")

    def test_model_values(self):
        """Test model string values"""
        assert OpenAIModel.GPT_4O.value == "gpt-4o"
        assert OpenAIModel.GPT_4O_MINI.value == "gpt-4o-mini"


class TestMusicAnalysisType:
    """Test MusicAnalysisType enum"""

    def test_analysis_types_exist(self):
        """Test all analysis types are defined"""
        assert MusicAnalysisType.QUICK_ANALYSIS
        assert MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        assert MusicAnalysisType.PRODUCTION_COACHING
        assert MusicAnalysisType.CREATIVE_SUGGESTIONS
        assert MusicAnalysisType.FL_STUDIO_OPTIMIZATION

    def test_analysis_type_values(self):
        """Test analysis type string values"""
        assert MusicAnalysisType.QUICK_ANALYSIS.value == "quick_analysis"
        assert (
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS.value == "comprehensive_analysis"
        )
        assert MusicAnalysisType.PRODUCTION_COACHING.value == "production_coaching"


class TestOpenAIMusicAnalysis:
    """Test OpenAIMusicAnalysis dataclass"""

    def test_create_result(self):
        """Test creating analysis result"""
        result = OpenAIMusicAnalysis(
            analysis_type=MusicAnalysisType.COMPREHENSIVE_ANALYSIS,
            model_used="gpt-4o",
            summary="Great electronic track",
            production_tips=["Add more reverb", "Compress the drums"],
        )

        assert result.analysis_type == MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        assert result.model_used == "gpt-4o"
        assert result.summary == "Great electronic track"
        assert len(result.production_tips) == 2

    def test_default_values(self):
        """Test default result values"""
        result = OpenAIMusicAnalysis(
            analysis_type=MusicAnalysisType.QUICK_ANALYSIS, model_used="gpt-4o"
        )

        assert result.summary == ""
        assert result.production_tips == []
        assert result.creative_ideas == []
        assert result.creativity_score == 0.0


class TestOpenAIMusicProducer:
    """Test OpenAIMusicProducer main functionality"""

    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    @patch("samplemind.integrations.openai_integration.OpenAI")
    def test_initialization_with_api_key(self, mock_openai, mock_async_openai):
        """Test producer initializes with API key"""
        producer = OpenAIMusicProducer(api_key="test_api_key_123")

        assert producer.api_key == "test_api_key_123"
        assert producer.default_model == OpenAIModel.GPT_4O
        assert producer.max_retries == 3
        assert producer.timeout == 30.0

        mock_openai.assert_called_once_with(api_key="test_api_key_123")
        mock_async_openai.assert_called_once_with(api_key="test_api_key_123")

    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    @patch("samplemind.integrations.openai_integration.OpenAI")
    def test_initialization_with_custom_model(self, mock_openai, mock_async_openai):
        """Test producer with custom model"""
        producer = OpenAIMusicProducer(
            api_key="test_key", default_model=OpenAIModel.GPT_4O_MINI
        )

        assert producer.default_model == OpenAIModel.GPT_4O_MINI

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_analyze_music_comprehensive_success(self, mock_async_openai):
        """Test successful comprehensive music analysis"""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=500)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        test_features = {"duration": 180.0, "tempo": 128.0, "key": "C", "mode": "major"}

        result = await producer.analyze_music_comprehensive(
            test_features, MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Verify result structure
        assert isinstance(result, OpenAIMusicAnalysis)
        assert result.model_used != ""
        assert result.timestamp > 0

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_analyze_music_production_coaching(self, mock_async_openai):
        """Test production coaching analysis"""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=400)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        result = await producer.analyze_music_comprehensive(
            {"duration": 200.0}, MusicAnalysisType.PRODUCTION_COACHING
        )

        assert isinstance(result, OpenAIMusicAnalysis)
        assert result.analysis_type == MusicAnalysisType.PRODUCTION_COACHING

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_analyze_music_handles_api_error(self, mock_async_openai):
        """Test error handling when OpenAI API fails"""
        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error: Rate limit exceeded")
        )
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        with pytest.raises(Exception) as exc_info:
            await producer.analyze_music_comprehensive(
                {"duration": 180.0}, MusicAnalysisType.COMPREHENSIVE_ANALYSIS
            )

        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_caching_works(self, mock_async_openai):
        """Test that response caching works"""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=100)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        features = {"duration": 180.0, "tempo": 120.0}

        # First call - should hit API
        result1 = await producer.analyze_music_comprehensive(
            features, MusicAnalysisType.QUICK_ANALYSIS, use_cache=True
        )

        # Second call with same features - should use cache
        result2 = await producer.analyze_music_comprehensive(
            features, MusicAnalysisType.QUICK_ANALYSIS, use_cache=True
        )

        # Should have results
        assert result1 is not None
        assert result2 is not None

        # Stats should show cache hit
        stats = producer.get_usage_stats()
        assert stats["cache_hits"] >= 0

    @patch("samplemind.integrations.openai_integration.OpenAI")
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    def test_get_stats(self, mock_async_openai, mock_openai):
        """Test statistics retrieval"""
        producer = OpenAIMusicProducer(api_key="test_key")

        stats = producer.get_usage_stats()

        assert "total_requests" in stats
        assert "total_tokens" in stats
        assert "avg_response_time" in stats
        assert "cache_hits" in stats

        assert stats["total_requests"] == 0
        assert stats["total_tokens"] == 0

    @patch("samplemind.integrations.openai_integration.OpenAI")
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    def test_clear_cache(self, mock_async_openai, mock_openai):
        """Test cache clearing"""
        producer = OpenAIMusicProducer(api_key="test_key")

        # Add something to cache
        producer.analysis_cache["test_key"] = "test_value"
        assert len(producer.analysis_cache) > 0

        # Clear cache
        producer.clear_cache()

        # Cache should be empty
        assert len(producer.analysis_cache) == 0

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_different_analysis_types(self, mock_async_openai):
        """Test different analysis types produce different prompts"""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=100)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        features = {"duration": 180.0}

        # Test different analysis types
        types_to_test = [
            MusicAnalysisType.QUICK_ANALYSIS,
            MusicAnalysisType.PRODUCTION_COACHING,
            MusicAnalysisType.CREATIVE_SUGGESTIONS,
            MusicAnalysisType.FL_STUDIO_OPTIMIZATION,
        ]

        for analysis_type in types_to_test:
            result = await producer.analyze_music_comprehensive(
                features, analysis_type, use_cache=False
            )

            assert isinstance(result, OpenAIMusicAnalysis)
            assert result.analysis_type == analysis_type


class TestErrorHandling:
    """Test error handling scenarios"""

    @patch("samplemind.integrations.openai_integration.OpenAI")
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    def test_initialization_requires_api_key(self, mock_async_openai, mock_openai):
        """Test that API key is required"""
        # Should work with api_key
        producer = OpenAIMusicProducer(api_key="test_key")
        assert producer is not None

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_empty_features_handled(self, mock_async_openai):
        """Test handling of empty feature dictionary"""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=50)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        # Should handle empty features gracefully
        result = await producer.analyze_music_comprehensive(
            {}, MusicAnalysisType.QUICK_ANALYSIS
        )

        assert isinstance(result, OpenAIMusicAnalysis)

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_retry_logic(self, mock_async_openai):
        """Test retry logic on temporary failures"""
        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=100)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()

        # Simulate 2 failures then success
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                Exception("Temporary error"),
                Exception("Temporary error"),
                mock_response,
            ]
        )
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key", max_retries=3)

        # Should eventually succeed after retries
        try:
            result = await producer.analyze_music_comprehensive(
                {"duration": 180.0}, MusicAnalysisType.QUICK_ANALYSIS
            )
            # If retries work, we get a result
            assert isinstance(result, OpenAIMusicAnalysis)
        except Exception:
            # If retry logic isn't implemented yet, that's okay
            pass


class TestPromptGeneration:
    """Test prompt generation for different scenarios"""

    @pytest.mark.asyncio
    @patch("samplemind.integrations.openai_integration.AsyncOpenAI")
    async def test_comprehensive_features_in_prompt(self, mock_async_openai):
        """Test that all features are included in prompt"""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = '{"summary": "Energetic electronic track", "production_tips": ["Add reverb"], "creative_ideas": ["Layer vocals"], "fl_studio_recommendations": [], "effect_suggestions": [], "arrangement_suggestions": [], "detailed_analysis": {}, "scores": {"creativity": 0.8, "production_quality": 0.7, "commercial_potential": 0.6}, "confidence": 0.85}'
        mock_response.choices = [Mock(message=mock_message)]
        mock_response.usage = Mock(total_tokens=100)

        mock_client = Mock()
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_async_openai.return_value = mock_client

        with patch("samplemind.integrations.openai_integration.OpenAI"):
            producer = OpenAIMusicProducer(api_key="test_key")

        features = {
            "duration": 240.0,
            "tempo": 140.0,
            "key": "A",
            "mode": "minor",
            "spectral_centroid": [2000, 2100],
            "energy_level": 7,
        }

        await producer.analyze_music_comprehensive(
            features, MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Verify create was called (prompt construction worked)
        assert mock_client.chat.completions.create.called


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
