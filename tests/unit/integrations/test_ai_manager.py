#!/usr/bin/env python3
"""
Unit tests for AI Manager
Tests multi-provider AI routing, fallback logic, and result conversion
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from samplemind.integrations.ai_manager import (
    SampleMindAIManager,
    AIProvider,
    AnalysisType,
    UnifiedAnalysisResult,
    AIProviderConfig,
    AILoadBalancer
)


class TestAIProviderConfig:
    """Test AIProviderConfig dataclass"""

    def test_create_config(self):
        """Test creating provider configuration"""
        config = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key="test_key",
            priority=1
        )

        assert config.provider == AIProvider.GOOGLE_AI
        assert config.api_key == "test_key"
        assert config.priority == 1
        assert config.enabled == True
        assert config.total_requests == 0

    def test_default_values(self):
        """Test default configuration values"""
        config = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="test"
        )

        assert config.enabled == True
        assert config.priority == 1
        assert config.max_requests_per_minute == 60
        assert config.success_rate == 1.0


class TestAILoadBalancer:
    """Test AI load balancing logic"""

    def test_select_provider_by_priority(self):
        """Test provider selection based on priority"""
        provider1 = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key="key1",
            priority=1
        )
        provider2 = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="key2",
            priority=2
        )

        balancer = AILoadBalancer([provider1, provider2])
        selected = balancer.select_provider(AnalysisType.COMPREHENSIVE_ANALYSIS)

        assert selected == AIProvider.GOOGLE_AI

    def test_select_preferred_provider(self):
        """Test explicit provider preference"""
        provider1 = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key="key1",
            priority=1
        )
        provider2 = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="key2",
            priority=2
        )

        balancer = AILoadBalancer([provider1, provider2])
        selected = balancer.select_provider(
            AnalysisType.COMPREHENSIVE_ANALYSIS,
            preferred_provider=AIProvider.OPENAI
        )

        assert selected == AIProvider.OPENAI

    def test_skip_disabled_provider(self):
        """Test that disabled providers are skipped"""
        provider1 = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key="key1",
            priority=1,
            enabled=False
        )
        provider2 = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="key2",
            priority=2,
            enabled=True
        )

        balancer = AILoadBalancer([provider1, provider2])
        selected = balancer.select_provider(AnalysisType.COMPREHENSIVE_ANALYSIS)

        assert selected == AIProvider.OPENAI

    def test_no_available_providers(self):
        """Test error when no providers are available"""
        provider1 = AIProviderConfig(
            provider=AIProvider.GOOGLE_AI,
            api_key="key1",
            enabled=False
        )

        balancer = AILoadBalancer([provider1])

        with pytest.raises(RuntimeError, match="No AI providers available"):
            balancer.select_provider(AnalysisType.COMPREHENSIVE_ANALYSIS)


class TestSampleMindAIManager:
    """Test main AI Manager functionality"""

    @pytest.fixture
    def mock_env_vars(self, monkeypatch):
        """Mock environment variables"""
        monkeypatch.setenv("GOOGLE_AI_API_KEY", "test_gemini_key")
        monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

    @pytest.fixture
    def ai_manager(self, mock_env_vars):
        """Create AI manager instance for testing"""
        return SampleMindAIManager()

    def test_initialization(self, ai_manager):
        """Test AI manager initializes correctly"""
        assert ai_manager is not None
        assert hasattr(ai_manager, 'providers')
        assert hasattr(ai_manager, 'load_balancer')
        assert len(ai_manager.providers) >= 1

    def test_provider_status(self, ai_manager):
        """Test getting provider status"""
        status = ai_manager.get_provider_status()

        assert isinstance(status, dict)
        assert len(status) > 0

        # Check status structure
        for provider, info in status.items():
            assert 'enabled' in info
            assert 'priority' in info
            assert 'total_requests' in info

    def test_global_stats(self, ai_manager):
        """Test global statistics"""
        stats = ai_manager.get_global_stats()

        assert isinstance(stats, dict)
        assert 'total_requests' in stats
        assert 'total_tokens' in stats
        assert 'total_cost' in stats
        assert 'providers_configured' in stats

    @pytest.mark.asyncio
    async def test_analyze_music_mock(self, ai_manager):
        """Test music analysis with mocked AI response"""
        # Mock audio features
        test_features = {
            'duration': 180.0,
            'tempo': 128.0,
            'key': 'C',
            'mode': 'major',
            'sample_rate': 44100
        }

        # Mock the AI provider
        with patch.object(ai_manager, '_analyze_with_provider') as mock_analyze:
            # Create mock result
            mock_result = UnifiedAnalysisResult(
                provider=AIProvider.GOOGLE_AI,
                analysis_type=AnalysisType.COMPREHENSIVE_ANALYSIS,
                model_used="gemini-2.5-pro",
                summary="Test analysis summary",
                processing_time=1.0
            )
            mock_analyze.return_value = mock_result

            # Perform analysis
            result = await ai_manager.analyze_music(
                test_features,
                AnalysisType.COMPREHENSIVE_ANALYSIS
            )

            assert result is not None
            assert result.provider == AIProvider.GOOGLE_AI
            assert result.summary == "Test analysis summary"

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self, ai_manager):
        """Test automatic fallback when primary provider fails"""
        test_features = {'duration': 180.0, 'tempo': 128.0}

        with patch.object(ai_manager, '_analyze_with_provider') as mock_analyze:
            # First call fails, second succeeds
            mock_success = UnifiedAnalysisResult(
                provider=AIProvider.OPENAI,
                analysis_type=AnalysisType.COMPREHENSIVE_ANALYSIS,
                model_used="gpt-5",
                summary="Fallback successful"
            )

            mock_analyze.side_effect = [
                Exception("Primary failed"),
                mock_success
            ]

            # Should succeed with fallback
            result = await ai_manager.analyze_music(
                test_features,
                AnalysisType.COMPREHENSIVE_ANALYSIS,
                enable_fallback=True
            )

            assert result is not None
            assert result.summary == "Fallback successful"

    def test_set_provider_enabled(self, ai_manager):
        """Test enabling/disabling providers"""
        # Get first provider
        provider = list(ai_manager.provider_configs.keys())[0]

        # Disable it
        ai_manager.set_provider_enabled(provider, False)
        assert ai_manager.provider_configs[provider].enabled == False

        # Enable it
        ai_manager.set_provider_enabled(provider, True)
        assert ai_manager.provider_configs[provider].enabled == True

    def test_set_provider_priority(self, ai_manager):
        """Test changing provider priority"""
        provider = list(ai_manager.provider_configs.keys())[0]

        original_priority = ai_manager.provider_configs[provider].priority

        # Change priority
        ai_manager.set_provider_priority(provider, 5)
        assert ai_manager.provider_configs[provider].priority == 5

        # Restore
        ai_manager.set_provider_priority(provider, original_priority)


class TestUnifiedAnalysisResult:
    """Test unified analysis result"""

    def test_create_result(self):
        """Test creating analysis result"""
        result = UnifiedAnalysisResult(
            provider=AIProvider.GOOGLE_AI,
            analysis_type=AnalysisType.COMPREHENSIVE_ANALYSIS,
            model_used="gemini-2.5-pro",
            summary="Test summary",
            processing_time=5.0
        )

        assert result.provider == AIProvider.GOOGLE_AI
        assert result.analysis_type == AnalysisType.COMPREHENSIVE_ANALYSIS
        assert result.summary == "Test summary"
        assert result.processing_time == 5.0

    def test_default_values(self):
        """Test default result values"""
        result = UnifiedAnalysisResult(
            provider=AIProvider.OPENAI,
            analysis_type=AnalysisType.QUICK_ANALYSIS,
            model_used="gpt-5"
        )

        assert result.summary == ""
        assert result.tokens_used == 0
        assert result.confidence_score == 0.0
        assert isinstance(result.production_tips, list)
        assert isinstance(result.creative_ideas, list)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
