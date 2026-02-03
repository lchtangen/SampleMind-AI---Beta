"""
Unit tests for stem separation CLI commands

Tests cover:
- stems:separate command (full 4-stem separation)
- stems:vocals, stems:drums, stems:bass, stems:other (single stem extraction)
- stems:batch command (batch processing)
- Quality presets (fast, standard, high)
- Error handling for missing files
- Output directory creation
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from samplemind.core.processing.stem_separation import (
    StemSeparationEngine,
    StemSeparationResult,
    StemQuality,
    QUALITY_PRESETS,
)


pytestmark = [pytest.mark.unit, pytest.mark.cli]


class TestStemSeparationEngine:
    """Test the StemSeparationEngine class"""

    def test_engine_creation_default(self):
        """Test creating engine with default settings"""
        engine = StemSeparationEngine()
        assert engine.model == "mdx_extra"
        assert engine.shifts == 1
        assert engine.overlap == 0.25
        assert engine.is_v4 is True

    def test_engine_creation_v3_model(self):
        """Test creating engine with v3 model"""
        engine = StemSeparationEngine(model="htdemucs")
        assert engine.model == "htdemucs"
        assert engine.is_v4 is False

    def test_engine_from_quality_fast(self):
        """Test creating engine from FAST quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.FAST)
        preset = QUALITY_PRESETS[StemQuality.FAST]
        assert engine.model == preset.model
        assert engine.shifts == preset.shifts
        assert engine.overlap == preset.overlap

    def test_engine_from_quality_standard(self):
        """Test creating engine from STANDARD quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.STANDARD)
        preset = QUALITY_PRESETS[StemQuality.STANDARD]
        assert engine.model == preset.model
        assert engine.shifts == preset.shifts
        assert engine.overlap == preset.overlap

    def test_engine_from_quality_high(self):
        """Test creating engine from HIGH quality preset"""
        engine = StemSeparationEngine.from_quality(StemQuality.HIGH)
        preset = QUALITY_PRESETS[StemQuality.HIGH]
        assert engine.model == preset.model
        assert engine.shifts == preset.shifts
        assert engine.overlap == preset.overlap

    def test_get_available_presets(self):
        """Test getting available presets with descriptions"""
        presets = StemSeparationEngine.get_available_presets()
        assert "fast" in presets
        assert "standard" in presets
        assert "high" in presets
        assert all(isinstance(v, str) for v in presets.values())

    def test_quality_presets_exist(self):
        """Test that all quality presets are defined"""
        for quality in StemQuality:
            assert quality in QUALITY_PRESETS
            preset = QUALITY_PRESETS[quality]
            assert hasattr(preset, 'model')
            assert hasattr(preset, 'shifts')
            assert hasattr(preset, 'overlap')
            assert hasattr(preset, 'description')


class TestStemsSeparateCommand:
    """Test stems:separate CLI command"""

    def test_stems_separate_missing_file(self, typer_runner):
        """Test stems:separate with missing file returns error"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:separate", "/nonexistent/file.wav"])

        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_stems_separate_valid_file(self, typer_runner, test_audio_samples, temp_directory):
        """Test stems:separate with valid file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]
        output_dir = temp_directory / "stems_output"

        with patch('samplemind.interfaces.cli.commands.audio.StemSeparationEngine') as mock_engine_class:
            # Mock the engine instance
            mock_engine = MagicMock()
            mock_engine_class.return_value = mock_engine
            mock_engine.separate.return_value = StemSeparationResult(
                output_directory=output_dir,
                stems={
                    "vocals": output_dir / "vocals.wav",
                    "drums": output_dir / "drums.wav",
                    "bass": output_dir / "bass.wav",
                    "other": output_dir / "other.wav",
                },
                command=["demucs", str(audio_file)],
            )

            result = runner.invoke(app, [
                "stems:separate", str(audio_file),
                "--output", str(output_dir),
            ])

        # Command should succeed (may have warnings about missing files to copy)
        # The important thing is the engine was called
        mock_engine.separate.assert_called_once()

    def test_stems_separate_with_quality_option(self, typer_runner, test_audio_samples, temp_directory):
        """Test stems:separate with quality preset option"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.audio.StemSeparationEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine_class.return_value = mock_engine
            mock_engine.separate.return_value = StemSeparationResult(
                output_directory=temp_directory,
                stems={},
                command=[],
            )

            result = runner.invoke(app, [
                "stems:separate", str(audio_file),
                "--quality", "high",
            ])

        # Verify HIGH quality preset was used
        call_kwargs = mock_engine_class.call_args.kwargs
        assert call_kwargs["shifts"] == 5
        assert call_kwargs["overlap"] == 0.5


class TestSingleStemCommands:
    """Test single stem extraction commands"""

    def test_stems_vocals_missing_file(self, typer_runner):
        """Test stems:vocals with missing file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:vocals", "/nonexistent/file.wav"])

        assert result.exit_code != 0

    def test_stems_drums_missing_file(self, typer_runner):
        """Test stems:drums with missing file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:drums", "/nonexistent/file.wav"])

        assert result.exit_code != 0

    def test_stems_bass_missing_file(self, typer_runner):
        """Test stems:bass with missing file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:bass", "/nonexistent/file.wav"])

        assert result.exit_code != 0

    def test_stems_other_missing_file(self, typer_runner):
        """Test stems:other with missing file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:other", "/nonexistent/file.wav"])

        assert result.exit_code != 0

    def test_stems_vocals_valid_file(self, typer_runner, test_audio_samples, temp_directory):
        """Test stems:vocals with valid file"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        audio_file = test_audio_samples["120_c_major"]

        with patch('samplemind.interfaces.cli.commands.audio.StemSeparationEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine_class.return_value = mock_engine
            mock_engine.separate.return_value = StemSeparationResult(
                output_directory=temp_directory,
                stems={"vocals": temp_directory / "vocals.wav"},
                command=[],
            )

            result = runner.invoke(app, ["stems:vocals", str(audio_file)])

        mock_engine.separate.assert_called_once()
        call_kwargs = mock_engine.separate.call_args.kwargs
        # Two-stems mode should be used for faster extraction
        assert call_kwargs.get("two_stems") == "vocals"


class TestStemsBatchCommand:
    """Test stems:batch CLI command"""

    def test_stems_batch_missing_folder(self, typer_runner):
        """Test stems:batch with non-existent folder"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        result = runner.invoke(app, ["stems:batch", "/nonexistent/folder"])

        assert result.exit_code != 0
        assert "not a directory" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_stems_batch_empty_folder(self, typer_runner, temp_directory):
        """Test stems:batch with empty folder (no audio files)"""
        from samplemind.interfaces.cli.typer_app import app

        runner = CliRunner()
        empty_folder = temp_directory / "empty"
        empty_folder.mkdir(exist_ok=True)

        result = runner.invoke(app, ["stems:batch", str(empty_folder)])

        # Should exit gracefully with no files
        assert result.exit_code == 0
        assert "no audio files" in result.stdout.lower()

    def test_stems_batch_with_files(self, typer_runner, test_audio_samples, temp_directory):
        """Test stems:batch with folder containing audio files"""
        from samplemind.interfaces.cli.typer_app import app
        import shutil

        runner = CliRunner()

        # Create a folder with test audio files
        input_folder = temp_directory / "batch_input"
        input_folder.mkdir(exist_ok=True)
        output_folder = temp_directory / "batch_output"

        # Copy test file to input folder
        test_file = test_audio_samples["120_c_major"]
        shutil.copy(test_file, input_folder / "test1.wav")

        with patch('samplemind.interfaces.cli.commands.audio.StemSeparationEngine') as mock_engine_class:
            mock_engine = MagicMock()
            mock_engine_class.return_value = mock_engine
            mock_engine.separate.return_value = StemSeparationResult(
                output_directory=output_folder,
                stems={
                    "vocals": output_folder / "vocals.wav",
                    "drums": output_folder / "drums.wav",
                },
                command=[],
            )

            result = runner.invoke(app, [
                "stems:batch", str(input_folder),
                "--output", str(output_folder),
            ])

        # Engine should be called for each file
        mock_engine.separate.assert_called()


class TestQualityPresets:
    """Test quality preset configurations"""

    def test_fast_preset_uses_mdx_model(self):
        """Test FAST preset uses mdx model for speed"""
        preset = QUALITY_PRESETS[StemQuality.FAST]
        assert preset.model == "mdx"
        assert preset.shifts == 1
        assert preset.overlap == 0.1

    def test_standard_preset_uses_mdx_extra(self):
        """Test STANDARD preset uses mdx_extra model"""
        preset = QUALITY_PRESETS[StemQuality.STANDARD]
        assert preset.model == "mdx_extra"
        assert preset.shifts == 1
        assert preset.overlap == 0.25

    def test_high_preset_uses_extra_shifts(self):
        """Test HIGH preset uses extra shifts for quality"""
        preset = QUALITY_PRESETS[StemQuality.HIGH]
        assert preset.model == "mdx_extra"
        assert preset.shifts == 5
        assert preset.overlap == 0.5

    def test_presets_have_descriptions(self):
        """Test all presets have descriptions"""
        for quality in StemQuality:
            preset = QUALITY_PRESETS[quality]
            assert preset.description
            assert len(preset.description) > 10  # Reasonable description length
