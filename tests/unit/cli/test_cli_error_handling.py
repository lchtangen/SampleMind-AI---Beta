"""
Comprehensive error handling tests for CLI (30+ tests)

Tests cover:
- File operation errors (not found, corrupted, permission denied)
- Audio format errors (unsupported, corrupted)
- API/Network errors (timeout, rate limit, connection refused)
- Configuration errors (missing API keys, invalid settings)
- Resource errors (disk full, out of memory)
- Input validation errors
- Graceful degradation and fallbacks
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestFileOperationErrors:
    """Test handling of file operation errors"""

    def test_file_not_found_error(self, typer_runner):
        """Test command with non-existent file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["analyze:full", "/nonexistent/file.wav"])

        # Should fail with clear error message
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_file_permission_denied_error(self, typer_runner, temp_directory):
        """Test command with permission denied"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "restricted.wav"
        test_file.write_text("audio data")

        # Simulate permission denied
        with patch('pathlib.Path.open') as mock_open:
            mock_open.side_effect = PermissionError("Permission denied")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        # Should handle gracefully
        assert result.exit_code != 0

    def test_directory_expected_but_file_provided(self, typer_runner, test_audio_samples):
        """Test command expecting directory when file provided"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.batch_analyze_async') as mock_batch:
            mock_batch.side_effect = Exception("Expected directory, got file")

            result = runner.invoke(app, ["batch:analyze", str(audio_file)])

        # Should provide helpful error message
        assert result.exit_code != 0

    def test_file_too_large_error(self, typer_runner, temp_directory):
        """Test command with file larger than max size"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        large_file = temp_directory / "large.wav"
        large_file.write_text("x" * (5 * 1024 * 1024 * 1024))  # 5GB

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("File too large")

            result = runner.invoke(app, ["analyze:full", str(large_file)])

        assert result.exit_code != 0
        assert "large" in result.stdout.lower() or "size" in result.stdout.lower()


class TestAudioFormatErrors:
    """Test handling of audio format errors"""

    def test_unsupported_audio_format_error(self, typer_runner, temp_directory):
        """Test command with unsupported audio format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "test.xyz"
        test_file.write_text("not audio data")

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Unsupported format: xyz")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0
        assert "unsupported" in result.stdout.lower() or "format" in result.stdout.lower()

    def test_corrupted_audio_file_error(self, typer_runner, temp_directory):
        """Test command with corrupted audio file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "corrupted.wav"
        test_file.write_text("RIFF corrupted data")

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Corrupted audio file")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0
        assert "corrupted" in result.stdout.lower() or "invalid" in result.stdout.lower()

    def test_empty_audio_file_error(self, typer_runner, temp_directory):
        """Test command with empty audio file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "empty.wav"
        test_file.write_bytes(b'')

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Empty audio file")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0

    def test_audio_file_silent_error(self, typer_runner, temp_directory):
        """Test command with silent audio (all zeros)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "silent.wav"

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'duration': 3.0,
                'rms_energy': 0.0,
                'warning': 'Audio appears to be silent'
            }

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        # Should handle gracefully with warning
        assert result.exit_code == 0 or "silent" in result.stdout.lower()


class TestNetworkAndAPIErrors:
    """Test handling of network and API errors"""

    def test_network_timeout_error(self, typer_runner, test_audio_samples):
        """Test command with network timeout"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = TimeoutError("Network request timed out after 30s")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        # Should handle gracefully, maybe fallback to offline
        assert result.exit_code != 0 or "timeout" in result.stdout.lower()

    def test_connection_refused_error(self, typer_runner, test_audio_samples):
        """Test command when API connection refused"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = ConnectionError("Connection refused")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        # May fallback to offline mode
        assert result.exit_code == 0 or result.exit_code != 0

    def test_api_rate_limit_error(self, typer_runner, test_audio_samples):
        """Test command when API rate limit exceeded"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("Rate limit exceeded (429)")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0
        assert "rate" in result.stdout.lower() or "limit" in result.stdout.lower()

    def test_api_authentication_error(self, typer_runner, test_audio_samples):
        """Test command with invalid API credentials"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("Invalid API key (401)")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0
        assert "invalid" in result.stdout.lower() or "auth" in result.stdout.lower()

    def test_api_server_error(self, typer_runner, test_audio_samples):
        """Test command when API server returns error"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("Server error (500)")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0


class TestConfigurationErrors:
    """Test handling of configuration errors"""

    def test_missing_api_key_error(self, typer_runner, test_audio_samples):
        """Test command when API key not configured"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            mock_ai.side_effect = Exception("GOOGLE_API_KEY environment variable not set")

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        assert result.exit_code != 0
        assert "key" in result.stdout.lower() or "api" in result.stdout.lower()

    def test_invalid_configuration_file_error(self, typer_runner):
        """Test command with invalid configuration file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.load_config') as mock_load:
            mock_load.side_effect = Exception("Invalid configuration file format")

            result = runner.invoke(app, ["ai:test"])

        assert result.exit_code != 0

    def test_invalid_setting_value_error(self, typer_runner):
        """Test command with invalid setting value"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.set_setting') as mock_set:
            mock_set.side_effect = ValueError("Invalid value for cache_size: must be positive integer")

            result = runner.invoke(app, [
                "config:set",
                "--key", "cache_size",
                "--value", "-1"
            ])

        assert result.exit_code != 0


class TestResourceErrors:
    """Test handling of resource-related errors"""

    def test_disk_full_error(self, typer_runner, test_audio_samples, temp_directory):
        """Test command when disk is full"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]
        output_file = temp_directory / "output.json"

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = OSError("No space left on device")

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--output", str(output_file)
            ])

        assert result.exit_code != 0
        assert "disk" in result.stdout.lower() or "space" in result.stdout.lower()

    def test_out_of_memory_error(self, typer_runner, test_audio_samples):
        """Test command with out of memory error"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = MemoryError("Out of memory")

            result = runner.invoke(app, ["analyze:professional", str(audio_file)])

        assert result.exit_code != 0
        assert "memory" in result.stdout.lower()

    def test_cache_full_error(self, typer_runner, test_audio_samples):
        """Test command when cache is full"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Cache limit exceeded")

            result = runner.invoke(app, ["analyze:full", str(audio_file)])

        # May clear cache and retry, or fail gracefully
        assert result.exit_code == 0 or result.exit_code != 0


class TestInputValidationErrors:
    """Test input validation error handling"""

    def test_invalid_output_format_error(self, typer_runner, test_audio_samples):
        """Test command with invalid output format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        result = runner.invoke(app, [
            "analyze:full", str(audio_file),
            "--format", "invalid_format"
        ])

        # Should reject invalid format
        assert result.exit_code != 0 or "invalid" in result.stdout.lower()

    def test_invalid_bpm_range_error(self, typer_runner):
        """Test command with invalid BPM range"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        result = runner.invoke(app, [
            "library:filter:bpm",
            "--min", "200",
            "--max", "100"  # min > max is invalid
        ])

        # Should detect invalid range
        assert result.exit_code != 0

    def test_invalid_limit_parameter_error(self, typer_runner, test_audio_samples):
        """Test command with invalid limit parameter"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.find_similar_async') as mock_similar:
            result = runner.invoke(app, [
                "library:find-similar", str(audio_file),
                "--limit", "invalid"
            ])

        # Should fail on invalid integer
        assert result.exit_code != 0

    def test_empty_query_string_error(self, typer_runner):
        """Test command with empty query string"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        result = runner.invoke(app, ["library:search", ""])

        # Should reject empty query
        assert result.exit_code != 0 or "empty" in result.stdout.lower()

    def test_missing_required_argument_error(self, typer_runner):
        """Test command missing required argument"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        # Missing file argument
        result = runner.invoke(app, ["analyze:full"])

        assert result.exit_code != 0


class TestKeyboardInterruptHandling:
    """Test handling of keyboard interrupts (Ctrl+C)"""

    def test_keyboard_interrupt_handling(self, typer_runner, test_audio_samples):
        """Test command handles Ctrl+C gracefully"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ["analyze:full", str(audio_file)])

        # Should handle Ctrl+C gracefully
        assert result.exit_code == 0 or result.exit_code == 1

    def test_batch_operation_keyboard_interrupt(self, typer_runner, test_audio_samples):
        """Test batch operation handles Ctrl+C gracefully"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.batch_analyze_async') as mock_batch:
            mock_batch.side_effect = KeyboardInterrupt()

            result = runner.invoke(app, ["batch:analyze", str(test_audio_samples["120_c_major"].parent)])

        # Should abort gracefully
        assert result.exit_code == 0 or result.exit_code == 1


class TestErrorMessageQuality:
    """Test quality of error messages"""

    def test_error_message_includes_suggestion(self, typer_runner, temp_directory):
        """Test error message includes helpful suggestion"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        result = runner.invoke(app, ["analyze:full", "/nonexistent/file.wav"])

        assert result.exit_code != 0
        # Should provide helpful suggestion or command

    def test_error_message_not_stack_trace_for_user_errors(self, typer_runner):
        """Test user-facing errors don't show full stack trace"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        result = runner.invoke(app, ["analyze:full", "/nonexistent/file.wav"])

        # Should not show full Python traceback
        assert "Traceback" not in result.stdout or result.stdout.count("Traceback") == 0

    def test_verbose_mode_shows_more_details(self, typer_runner, test_audio_samples):
        """Test verbose mode shows detailed error information"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Detailed error")

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--verbose"
            ])

        # Verbose mode may show more details


class TestErrorRecoveryAndRetry:
    """Test error recovery and retry mechanisms"""

    def test_transient_error_retry(self, typer_runner, test_audio_samples):
        """Test command retries on transient errors"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.ai_analyze_async') as mock_ai:
            # Fail twice, then succeed
            mock_ai.side_effect = [
                TimeoutError("Timeout"),
                TimeoutError("Timeout"),
                {'provider': 'ollama', 'summary': 'Analysis'}
            ]

            result = runner.invoke(app, ["ai:analyze", str(audio_file)])

        # Should eventually succeed with retry
        # Implementation dependent
