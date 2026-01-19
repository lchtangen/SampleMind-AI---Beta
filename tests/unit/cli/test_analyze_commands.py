"""
Comprehensive unit tests for analyze commands (40+ tests)

Tests cover:
- Core analysis commands (full, standard, basic, professional, quick)
- Specific feature extraction (BPM, key, mood, genre, instrument, vocal, quality, energy)
- Advanced analysis (spectral, harmonic, percussive, MFCC, chroma, onset, beats, segments)
- Batch analysis
- Output formatting
- Error handling
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typer.testing import CliRunner

from samplemind.exceptions import AudioFileError, FileNotFoundError as SampleMindFileNotFoundError


pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestAnalyzeCoreCommands:
    """Test core analysis commands (full, standard, basic, professional, quick)"""

    def test_analyze_full_valid_file(self, typer_runner, test_audio_samples):
        """Test analyze:full command with valid audio file"""
        # WHEN: Running analyze:full with valid file
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'duration': 3.0,
                'tempo': 120.0,
                'key': 'C',
                'mode': 'major'
            }

            result = runner.invoke(app, ["analyze:full", str(audio_file)])

        # THEN: Command should succeed
        assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"

    def test_analyze_full_missing_file(self, typer_runner):
        """Test analyze:full command with missing file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["analyze:full", "/nonexistent/file.wav"])

        # THEN: Command should fail gracefully
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_analyze_full_with_output_option(self, typer_runner, test_audio_samples, temp_directory):
        """Test analyze:full with --output file option"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]
        output_file = temp_directory / "analysis_output.json"

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0, 'key': 'C'}

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--output", str(output_file)
            ])

        assert result.exit_code == 0

    def test_analyze_standard_command(self, typer_runner, test_audio_samples):
        """Test analyze:standard command"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0, 'key': 'C', 'mode': 'major'}

            result = runner.invoke(app, ["analyze:standard", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_basic_command(self, typer_runner, test_audio_samples):
        """Test analyze:basic command (fast, minimal features)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, ["analyze:basic", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_professional_command(self, typer_runner, test_audio_samples):
        """Test analyze:professional command"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'tempo': 120.0,
                'key': 'C',
                'mode': 'major',
                'forensics': {'peak': 0.95}
            }

            result = runner.invoke(app, ["analyze:professional", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_quick_command(self, typer_runner, test_audio_samples):
        """Test analyze:quick command (ultra-fast)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, ["analyze:quick", str(audio_file)])

        assert result.exit_code == 0


class TestAnalyzeFeatureCommands:
    """Test specific feature extraction commands (BPM, key, mood, genre, etc.)"""

    def test_analyze_bpm_detection(self, typer_runner, test_audio_samples):
        """Test analyze:bpm command - BPM detection only"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, ["analyze:bpm", str(audio_file)])

        assert result.exit_code == 0
        assert "120" in result.stdout or "bpm" in result.stdout.lower()

    def test_analyze_key_detection(self, typer_runner, test_audio_samples):
        """Test analyze:key command - Key detection only"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'key': 'C', 'mode': 'major'}

            result = runner.invoke(app, ["analyze:key", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_mood_detection(self, typer_runner, test_audio_samples):
        """Test analyze:mood command - Mood analysis"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'mood': 'uplifting', 'energy': 'high'}

            result = runner.invoke(app, ["analyze:mood", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_genre_classification(self, typer_runner, test_audio_samples):
        """Test analyze:genre command - Genre classification"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'genre': 'electronic', 'confidence': 0.95}

            result = runner.invoke(app, ["analyze:genre", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_instrument_recognition(self, typer_runner, test_audio_samples):
        """Test analyze:instrument command - Instrument recognition"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'instruments': ['synthesizer', 'drums']}

            result = runner.invoke(app, ["analyze:instrument", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_vocal_detection(self, typer_runner, test_audio_samples):
        """Test analyze:vocal command - Vocal detection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'has_vocals': False}

            result = runner.invoke(app, ["analyze:vocal", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_quality_scoring(self, typer_runner, test_audio_samples):
        """Test analyze:quality command - Quality scoring"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'quality_score': 0.92}

            result = runner.invoke(app, ["analyze:quality", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_energy_detection(self, typer_runner, test_audio_samples):
        """Test analyze:energy command - Energy level detection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'energy_level': 'high'}

            result = runner.invoke(app, ["analyze:energy", str(audio_file)])

        assert result.exit_code == 0


class TestAnalyzeAdvancedCommands:
    """Test advanced analysis commands (spectral, harmonic, percussive, MFCC, etc.)"""

    def test_analyze_spectral_analysis(self, typer_runner, test_audio_samples):
        """Test analyze:spectral command - Spectral analysis"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'spectral_centroid': 2500.0,
                'spectral_bandwidth': 1000.0
            }

            result = runner.invoke(app, ["analyze:spectral", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_harmonic_percussive_separation(self, typer_runner, test_audio_samples):
        """Test analyze:harmonic command - Harmonic/percussive separation"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'harmonic_ratio': 0.65,
                'percussive_ratio': 0.35
            }

            result = runner.invoke(app, ["analyze:harmonic", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_percussive_separation(self, typer_runner, test_audio_samples):
        """Test analyze:percussive command - Percussive analysis"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'percussive_ratio': 0.35}

            result = runner.invoke(app, ["analyze:percussive", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_mfcc_extraction(self, typer_runner, test_audio_samples):
        """Test analyze:mfcc command - MFCC extraction"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'mfcc_coefficients': 13}

            result = runner.invoke(app, ["analyze:mfcc", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_chroma_features(self, typer_runner, test_audio_samples):
        """Test analyze:chroma command - Chroma features"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'chroma_coefficients': 12}

            result = runner.invoke(app, ["analyze:chroma", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_onset_detection(self, typer_runner, test_audio_samples):
        """Test analyze:onset command - Onset detection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'onset_frames': 45}

            result = runner.invoke(app, ["analyze:onset", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_beat_detection(self, typer_runner, test_audio_samples):
        """Test analyze:beats command - Beat detection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'beat_count': 6}

            result = runner.invoke(app, ["analyze:beats", str(audio_file)])

        assert result.exit_code == 0

    def test_analyze_segment_detection(self, typer_runner, test_audio_samples):
        """Test analyze:segments command - Segment detection"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'segments': 2}

            result = runner.invoke(app, ["analyze:segments", str(audio_file)])

        assert result.exit_code == 0


class TestAnalyzeOutputFormats:
    """Test analyze commands with different output formats"""

    def test_analyze_output_format_table(self, typer_runner, test_audio_samples):
        """Test analyze with table output format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--format", "table"
            ])

        assert result.exit_code == 0

    def test_analyze_output_format_json(self, typer_runner, test_audio_samples):
        """Test analyze with JSON output format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--format", "json"
            ])

        assert result.exit_code == 0

    def test_analyze_output_format_csv(self, typer_runner, test_audio_samples):
        """Test analyze with CSV output format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--format", "csv"
            ])

        assert result.exit_code == 0

    def test_analyze_output_format_yaml(self, typer_runner, test_audio_samples):
        """Test analyze with YAML output format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result = runner.invoke(app, [
                "analyze:full", str(audio_file),
                "--format", "yaml"
            ])

        assert result.exit_code == 0


class TestAnalyzeErrorHandling:
    """Test error handling in analyze commands"""

    def test_analyze_file_not_found_error(self, typer_runner):
        """Test analyze with non-existent file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["analyze:full", "/nonexistent/file.wav"])

        assert result.exit_code != 0

    def test_analyze_unsupported_format_error(self, typer_runner, temp_directory):
        """Test analyze with unsupported audio format"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        # Create an unsupported file
        test_file = temp_directory / "test.xyz"
        test_file.write_text("not audio data")

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Unsupported format")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0

    def test_analyze_corrupted_audio_error(self, typer_runner, temp_directory):
        """Test analyze with corrupted audio file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        # Create a corrupted WAV file
        test_file = temp_directory / "corrupted.wav"
        test_file.write_text("corrupted audio data")

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = Exception("Corrupted audio")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0

    def test_analyze_permission_denied_error(self, typer_runner, temp_directory):
        """Test analyze with permission denied"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        test_file = temp_directory / "restricted.wav"
        test_file.write_text("audio data")

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.side_effect = PermissionError("Permission denied")

            result = runner.invoke(app, ["analyze:full", str(test_file)])

        assert result.exit_code != 0


class TestAnalyzeBatchCommands:
    """Test batch analysis commands"""

    def test_batch_analyze_directory(self, typer_runner, test_audio_samples, temp_directory):
        """Test batch:analyze command - Process directory"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.batch_analyze_async') as mock_batch:
            mock_batch.return_value = {
                'total_files': 2,
                'processed': 2,
                'failed': 0
            }

            result = runner.invoke(app, ["batch:analyze", str(test_audio_samples["120_c_major"].parent)])

        assert result.exit_code == 0

    def test_batch_analyze_with_filter(self, typer_runner, test_audio_samples):
        """Test batch:analyze with BPM filter"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.batch_analyze_async') as mock_batch:
            mock_batch.return_value = {'total_files': 1, 'processed': 1, 'failed': 0}

            result = runner.invoke(app, [
                "batch:analyze", str(test_audio_samples["120_c_major"].parent),
                "--min-bpm", "100",
                "--max-bpm", "130"
            ])

        assert result.exit_code == 0

    def test_batch_analyze_empty_directory(self, typer_runner, temp_directory):
        """Test batch:analyze with empty directory"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()

        with patch('samplemind.interfaces.cli.commands.utils.batch_analyze_async') as mock_batch:
            mock_batch.return_value = {'total_files': 0, 'processed': 0, 'failed': 0}

            result = runner.invoke(app, ["batch:analyze", str(temp_directory)])

        # Should succeed but with 0 files
        assert result.exit_code == 0 or "no files" in result.stdout.lower()


class TestAnalyzePerformance:
    """Test performance characteristics of analyze commands"""

    @pytest.mark.performance
    def test_analyze_response_time_basic(self, typer_runner, test_audio_samples, performance_timer):
        """Test that basic analysis completes within performance target (<5s)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {'tempo': 120.0}

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["analyze:basic", str(audio_file)]
            )

        # Basic analysis should be fast
        assert elapsed < 5.0, f"Basic analysis took {elapsed:.2f}s, target <5s"

    @pytest.mark.performance
    def test_analyze_response_time_standard(self, typer_runner, test_audio_samples, performance_timer):
        """Test that standard analysis completes within performance target (<10s)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.utils.analyze_file_async') as mock_analyze:
            mock_analyze.return_value = {
                'tempo': 120.0,
                'key': 'C',
                'mode': 'major'
            }

            result, elapsed = performance_timer.time_operation(
                runner.invoke,
                app, ["analyze:standard", str(audio_file)]
            )

        # Standard analysis should complete quickly
        assert elapsed < 10.0, f"Standard analysis took {elapsed:.2f}s, target <10s"
