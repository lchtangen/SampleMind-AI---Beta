#!/usr/bin/env python3
"""
Unit tests for Google AI (Gemini) Integration
Tests Gemini API integration, music analysis, and error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.integrations.google_ai_integration import (
    GoogleAIMusicProducer,
    MusicAnalysisType,
    AdvancedMusicAnalysis,
    GeminiModel
)


class TestAdvancedMusicAnalysis:
    """Test AdvancedMusicAnalysis dataclass"""

    def test_create_result(self):
        """Test creating analysis result"""
        result = AdvancedMusicAnalysis(
            primary_genre="Electronic",
            sub_genres=["House", "Techno"],
            primary_mood="Energetic",
            mood_tags=["Happy", "Uplifting"],
            energy_level=8,
            danceability=9,
            model_used=GeminiModel.GEMINI_2_5_PRO,
            processing_time=1.5
        )

        assert result.primary_genre == "Electronic"
        assert len(result.sub_genres) == 2
        assert result.energy_level == 8
        assert result.model_used == GeminiModel.GEMINI_2_5_PRO
        assert result.processing_time == 1.5

    def test_default_values(self):
        """Test default result values"""
        result = AdvancedMusicAnalysis(
            model_used=GeminiModel.GEMINI_2_5_PRO,
            processing_time=0.5
        )

        assert result.primary_genre == ""
        assert result.sub_genres == []
        assert result.mood_tags == []
        assert result.energy_level == 0
        assert result.danceability == 0


class TestGoogleAIMusicProducer:
    """Test GoogleAIMusicProducer main functionality"""

    def test_initialization_with_api_key(self):
        """Test producer initializes with API key"""
        producer = GoogleAIMusicProducer(api_key="test_api_key_123")

        assert producer.api_key == "test_api_key_123"
        assert producer.default_model == GeminiModel.GEMINI_2_5_PRO
        assert producer.total_analyses == 0
        assert producer.total_tokens_used == 0

    def test_initialization_with_custom_model(self):
        """Test producer with custom model"""
        producer = GoogleAIMusicProducer(
            api_key="test_key",
            model=GeminiModel.GEMINI_2_5_FLASH
        )

        assert producer.default_model == GeminiModel.GEMINI_2_5_FLASH

    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_initialization_configures_genai(self, mock_model, mock_configure):
        """Test that initialization configures Google AI SDK"""
        producer = GoogleAIMusicProducer(api_key="test_key")

        # Should configure with API key
        mock_configure.assert_called_once_with(api_key="test_key")

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_analyze_music_comprehensive_success(self, mock_model_class):
        """Test successful comprehensive music analysis"""
        # Mock the Gemini response
        mock_response = Mock()
        mock_response.text = """
        Genre: Electronic Dance Music
        Sub-genres: Progressive House, Deep House
        Mood: Energetic and Uplifting
        Mood Tags: Happy, Euphoric, Driving
        Energy: 8
        Danceability: 9
        BPM: 128
        Key: C Major
        """

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        test_features = {
            'duration': 180.0,
            'tempo': 128.0,
            'key': 'C',
            'mode': 'major'
        }

        result = await producer.analyze_music_comprehensive(
            test_features,
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Verify result structure
        assert isinstance(result, AdvancedMusicAnalysis)
        assert result.model_used == GeminiModel.GEMINI_2_5_PRO
        assert result.processing_time > 0

        # Verify the model was called
        mock_model.generate_content_async.assert_called_once()

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_analyze_music_with_creative_suggestions(self, mock_model_class):
        """Test creative suggestions analysis"""
        mock_response = Mock()
        mock_response.text = """
        Creative Ideas:
        1. Add a breakdown at 2:00
        2. Layer vocals with reverb
        3. Introduce a new synth melody

        FL Studio Plugins:
        - Serum for main synth
        - Fruity Reverb 2 for atmosphere
        - Sidechain Compressor for pumping effect
        """

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        result = await producer.analyze_music_comprehensive(
            {'duration': 200.0},
            MusicAnalysisType.CREATIVE_PRODUCTION
        )

        assert isinstance(result, AdvancedMusicAnalysis)
        assert len(result.creative_ideas) > 0 or len(result.fl_plugin_recommendations) > 0

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_analyze_music_handles_api_error(self, mock_model_class):
        """Test error handling when Gemini API fails"""
        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(
            side_effect=Exception("API Error: Rate limit exceeded")
        )
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        with pytest.raises(Exception) as exc_info:
            await producer.analyze_music_comprehensive(
                {'duration': 180.0},
                MusicAnalysisType.COMPREHENSIVE_ANALYSIS
            )

        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_multiple_analyses_track_stats(self, mock_model_class):
        """Test that multiple analyses update statistics"""
        mock_response = Mock()
        mock_response.text = "Genre: Electronic"

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        # Run 3 analyses
        for _ in range(3):
            await producer.analyze_music_comprehensive(
                {'duration': 180.0},
                MusicAnalysisType.QUICK_ANALYSIS
            )

        stats = producer.get_performance_stats()

        assert stats['total_analyses'] == 3
        assert stats['avg_response_time'] > 0
        assert 'cost_estimate_usd' in stats

    def test_get_performance_stats(self):
        """Test performance statistics retrieval"""
        producer = GoogleAIMusicProducer(api_key="test_key")

        stats = producer.get_performance_stats()

        assert 'total_analyses' in stats
        assert 'avg_response_time' in stats
        assert 'total_tokens_used' in stats
        assert 'cost_estimate_usd' in stats
        assert 'model_used' in stats

        assert stats['total_analyses'] == 0
        assert stats['avg_response_time'] == 0.0

    def test_shutdown(self):
        """Test producer shutdown"""
        producer = GoogleAIMusicProducer(api_key="test_key")

        # Should not raise any exceptions
        producer.shutdown()

        # Can be called multiple times safely
        producer.shutdown()

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_build_analysis_prompt_comprehensive(self, mock_model_class):
        """Test prompt building for comprehensive analysis"""
        mock_response = Mock()
        mock_response.text = "Genre: Test"

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        features = {
            'duration': 240.0,
            'tempo': 140.0,
            'key': 'A',
            'mode': 'minor',
            'spectral_centroid': [2000, 2100, 2050],
            'energy_level': 7
        }

        await producer.analyze_music_comprehensive(
            features,
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Verify the prompt contains feature data
        call_args = mock_model.generate_content_async.call_args
        prompt = call_args[0][0]

        assert '240' in prompt  # duration
        assert '140' in prompt  # tempo
        assert 'A' in prompt    # key
        assert 'minor' in prompt  # mode

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_parse_gemini_response(self, mock_model_class):
        """Test parsing of Gemini API response"""
        mock_response = Mock()
        mock_response.text = """
        Primary Genre: Electronic Dance Music
        Sub-Genres: Techno, Minimal
        Mood: Dark and Atmospheric
        Mood Tags: Mysterious, Intense, Hypnotic
        Energy Level: 7/10
        Danceability: 8/10
        BPM: 130
        Key: D Minor
        Production Quality: Professional
        Mix Balance: Good
        """

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        result = await producer.analyze_music_comprehensive(
            {'tempo': 130},
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Should parse the structured response
        assert isinstance(result, AdvancedMusicAnalysis)
        assert result.primary_genre != ""
        assert result.processing_time > 0


class TestMusicAnalysisType:
    """Test MusicAnalysisType enum"""

    def test_analysis_types_exist(self):
        """Test all analysis types are defined"""
        assert MusicAnalysisType.QUICK_ANALYSIS
        assert MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        assert MusicAnalysisType.CREATIVE_PRODUCTION
        assert MusicAnalysisType.REAL_TIME_COACHING
        assert MusicAnalysisType.FL_STUDIO_INTEGRATION

    def test_analysis_type_values(self):
        """Test analysis type string values"""
        assert MusicAnalysisType.QUICK_ANALYSIS.value == "quick_analysis"
        assert MusicAnalysisType.COMPREHENSIVE_ANALYSIS.value == "comprehensive_analysis"


class TestGeminiModel:
    """Test GeminiModel enum"""

    def test_models_exist(self):
        """Test all models are defined"""
        assert GeminiModel.GEMINI_2_5_PRO
        assert GeminiModel.GEMINI_2_5_FLASH

    def test_model_values(self):
        """Test model string values"""
        assert "gemini" in GeminiModel.GEMINI_2_5_PRO.value.lower()
        assert "gemini" in GeminiModel.GEMINI_2_5_FLASH.value.lower()


class TestCostEstimation:
    """Test cost estimation for API usage"""

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_cost_estimate_calculation(self, mock_model_class):
        """Test that cost estimates are calculated"""
        mock_response = Mock()
        mock_response.text = "Genre: Electronic"

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        await producer.analyze_music_comprehensive(
            {'duration': 180.0},
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        stats = producer.get_performance_stats()

        # Should have some cost estimate (even if minimal)
        assert 'cost_estimate_usd' in stats
        assert isinstance(stats['cost_estimate_usd'], (int, float))
        assert stats['cost_estimate_usd'] >= 0


class TestErrorHandling:
    """Test error handling scenarios"""

    def test_initialization_without_api_key_raises_error(self):
        """Test that missing API key raises appropriate error"""
        with pytest.raises((ValueError, TypeError)):
            GoogleAIMusicProducer(api_key=None)

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_empty_features_handled(self, mock_model_class):
        """Test handling of empty feature dictionary"""
        mock_response = Mock()
        mock_response.text = "Genre: Unknown"

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        # Should handle empty features gracefully
        result = await producer.analyze_music_comprehensive(
            {},
            MusicAnalysisType.QUICK_ANALYSIS
        )

        assert isinstance(result, AdvancedMusicAnalysis)

    @pytest.mark.asyncio
    @patch('google.generativeai.GenerativeModel')
    async def test_malformed_response_handled(self, mock_model_class):
        """Test handling of unexpected API response format"""
        mock_response = Mock()
        mock_response.text = "This is not a structured response at all!"

        mock_model = Mock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)
        mock_model_class.return_value = mock_model

        producer = GoogleAIMusicProducer(api_key="test_key")

        # Should not crash on malformed response
        result = await producer.analyze_music_comprehensive(
            {'duration': 180.0},
            MusicAnalysisType.COMPREHENSIVE_ANALYSIS
        )

        # Should return a result even if mostly empty
        assert isinstance(result, AdvancedMusicAnalysis)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
