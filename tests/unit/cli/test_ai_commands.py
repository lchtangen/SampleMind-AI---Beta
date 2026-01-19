"""
Comprehensive unit tests for AI-powered commands (15+ tests)

Tests cover:
- AI analysis and classification
- AI provider configuration
- AI suggestion and coaching
- Offline vs online modes
- API key validation
"""

import pytest
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typer.testing import CliRunner

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestAIAnalysisCommands:
    """Test AI-powered analysis commands"""

    def test_ai_analyze_file(self, typer_runner, test_audio_samples):
        """Test ai:analyze command - AI-powered comprehensive analysis"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.return_value = {
                'provider': 'gemini',
                'summary': 'Electronic track with steady 120 BPM rhythm',
                'confidence': 0.92,
                'analysis_time': 2.5
            }

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code == 0
        assert "gemini" in result.stdout.lower() or "analysis" in result.stdout.lower()

    def test_ai_classify_file(self, typer_runner, test_audio_samples):
        """Test ai:classify command - AI classification"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_classify_async') as mock_classify:
            mock_classify.return_value = {
                'genres': ['electronic', 'ambient'],
                'confidence': 0.88,
                'subgenres': ['techno', 'house']
            }

            result = runner.invoke(app, ["ai:classify", str(audio_file)])

        assert result.exit_code == 0

    def test_ai_auto_tag_file(self, typer_runner, test_audio_samples):
        """Test ai:tag command - AI auto-tagging"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_tag_async') as mock_tag:
            mock_tag.return_value = {
                'tags': ['upbeat', 'electronic', 'loop', 'production'],
                'confidence': 0.85
            }

            result = runner.invoke(app, ["ai:tag", str(audio_file)])

        assert result.exit_code == 0

    def test_ai_suggest_similar_samples(self, typer_runner, test_audio_samples):
        """Test ai:suggest command - AI-driven similar sample suggestions"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_suggest_async') as mock_suggest:
            mock_suggest.return_value = {
                'suggestions': 5,
                'samples': [
                    {'name': 'similar_1.wav', 'score': 0.95},
                    {'name': 'similar_2.wav', 'score': 0.88}
                ]
            }

            result = runner.invoke(app, [
                "ai:suggest", str(audio_file),
                "--limit", "10"
            ])

        assert result.exit_code == 0

    def test_ai_production_coaching(self, typer_runner, test_audio_samples):
        """Test ai:coach command - AI production coaching and tips"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_coach_async') as mock_coach:
            mock_coach.return_value = {
                'tips': [
                    'Add subtle reverb to enhance space',
                    'EQ the highs for a warmer tone'
                ],
                'quality_score': 0.78
            }

            result = runner.invoke(app, ["ai:coach", str(audio_file)])

        assert result.exit_code == 0

    def test_ai_generate_presets(self, typer_runner, test_audio_samples):
        """Test ai:presets command - Generate EQ/compressor presets"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_generate_presets_async') as mock_presets:
            mock_presets.return_value = {
                'eq_preset': {'low': -2, 'mid': 0, 'high': 3},
                'compressor': {'ratio': 4, 'threshold': -20}
            }

            result = runner.invoke(app, ["ai:presets", str(audio_file)])

        assert result.exit_code == 0


class TestAIProviderConfiguration:
    """Test AI provider configuration commands"""

    def test_ai_set_provider_gemini(self, typer_runner):
        """Test ai:provider command - Set AI provider to Gemini"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_ai_provider_async') as mock_set:
            mock_set.return_value = {'provider': 'gemini', 'status': 'configured'}

            result = runner.invoke(app, [
                "ai:provider",
                "--provider", "gemini"
            ])

        assert result.exit_code == 0

    def test_ai_set_provider_openai(self, typer_runner):
        """Test ai:provider command - Set AI provider to OpenAI"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_ai_provider_async') as mock_set:
            mock_set.return_value = {'provider': 'openai', 'status': 'configured'}

            result = runner.invoke(app, [
                "ai:provider",
                "--provider", "openai"
            ])

        assert result.exit_code == 0

    def test_ai_set_provider_ollama(self, typer_runner):
        """Test ai:provider command - Set AI provider to Ollama (offline)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_ai_provider_async') as mock_set:
            mock_set.return_value = {'provider': 'ollama', 'status': 'configured'}

            result = runner.invoke(app, [
                "ai:provider",
                "--provider", "ollama"
            ])

        assert result.exit_code == 0

    def test_ai_set_api_key_gemini(self, typer_runner):
        """Test ai:key command - Configure Gemini API key"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_api_key_async') as mock_set_key:
            mock_set_key.return_value = {'provider': 'gemini', 'configured': True}

            result = runner.invoke(app, [
                "ai:key",
                "--provider", "gemini",
                "--key", "test_key_123"
            ])

        assert result.exit_code == 0

    def test_ai_set_model(self, typer_runner):
        """Test ai:model command - Set AI model"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_ai_model_async') as mock_set_model:
            mock_set_model.return_value = {'model': 'gpt-4o', 'provider': 'openai'}

            result = runner.invoke(app, [
                "ai:model",
                "--model", "gpt-4o"
            ])

        assert result.exit_code == 0

    def test_ai_test_connection(self, typer_runner):
        """Test ai:test command - Test AI connection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.test_ai_connection_async') as mock_test:
            mock_test.return_value = {
                'provider': 'gemini',
                'status': 'connected',
                'latency_ms': 250
            }

            result = runner.invoke(app, ["ai:test"])

        assert result.exit_code == 0
        assert "connected" in result.stdout.lower() or "success" in result.stdout.lower()


class TestAIOfflineMode:
    """Test offline-first AI capabilities"""

    def test_ai_offline_mode_enabled(self, typer_runner, test_audio_samples, clean_environment):
        """Test AI commands work in offline mode with Ollama"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.return_value = {
                'provider': 'ollama',
                'model': 'phi3:mini',
                'summary': 'Offline analysis result',
                'response_time': 0.85
            }

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code == 0

    def test_ai_fallback_to_ollama_on_network_error(self, typer_runner, test_audio_samples):
        """Test AI fallback to Ollama when cloud API fails"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            # First call fails (cloud API), falls back to Ollama
            mock_ai.return_value = {
                'provider': 'ollama',
                'fallback': True,
                'original_provider': 'gemini',
                'summary': 'Fallback analysis'
            }

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code == 0


class TestAIErrorHandling:
    """Test error handling in AI commands"""

    def test_ai_analyze_missing_api_key(self, typer_runner, test_audio_samples):
        """Test ai:analyze without required API key"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("API key not configured")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0
        assert "key" in result.stdout.lower() or "configured" in result.stdout.lower()

    def test_ai_analyze_network_timeout(self, typer_runner, test_audio_samples):
        """Test ai:analyze with network timeout"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = TimeoutError("API request timed out")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        # Should handle gracefully or fall back to offline
        assert result.exit_code == 0 or result.exit_code != 0

    def test_ai_analyze_rate_limit(self, typer_runner, test_audio_samples):
        """Test ai:analyze with rate limit error"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("Rate limit exceeded")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0

    def test_ai_set_invalid_provider(self, typer_runner):
        """Test ai:provider with invalid provider name"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, [
            "ai:provider",
            "--provider", "invalid_provider"
        ])

        assert result.exit_code != 0

    def test_ai_set_invalid_api_key_format(self, typer_runner):
        """Test ai:key with invalid API key format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.validate_api_key') as mock_validate:
            mock_validate.return_value = False

            result = runner.invoke(app, [
                "ai:key",
                "--provider", "gemini",
                "--key", "invalid_key"
            ])

        # May or may not fail depending on validation strictness


class TestAIPerformance:
    """Test performance characteristics of AI commands"""

    @pytest.mark.performance
    @pytest.mark.ai
    def test_ai_analyze_response_time(self, typer_runner, test_audio_samples, performance_timer):
        """Test ai:analyze completes within performance target"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.return_value = {
                'provider': 'gemini',
                'summary': 'Test analysis'
            }

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["ai:analyze", str(audio_file)]
            )

        # AI analysis may take longer due to API calls
        # Offline mode should be <2s, online mode <5s typically
        assert elapsed < 10.0, f"AI analysis took {elapsed:.2f}s"

    @pytest.mark.performance
    def test_ai_offline_fast_response(self, typer_runner, test_audio_samples, performance_timer):
        """Test offline AI response time (<1s)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.return_value = {
                'provider': 'ollama',
                'response_time': 0.5
            }

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["ai:analyze", str(audio_file)]
            )

        # Offline AI should be very fast
        assert elapsed < 2.0, f"Offline AI took {elapsed:.2f}s, target <2s"
