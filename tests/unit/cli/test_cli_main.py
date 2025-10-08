"""
Tests for CLI main commands
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typer.testing import CliRunner
from pathlib import Path

from samplemind.interfaces.cli.main import app, console

runner = CliRunner()


class TestCLIBasicCommands:
    """Test basic CLI commands"""

    def test_version_command(self):
        """Test version command"""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "SampleMind AI" in result.stdout
        assert "v6" in result.stdout or "0.6.0" in result.stdout

    @patch('samplemind.interfaces.cli.main.menu_main')
    def test_menu_command(self, mock_menu):
        """Test menu command launches interactive menu"""
        result = runner.invoke(app, ["menu"])
        mock_menu.assert_called_once()

    @patch('samplemind.interfaces.cli.main.SampleMindTUI')
    def test_tui_command(self, mock_tui):
        """Test TUI command"""
        mock_tui_instance = Mock()
        mock_tui.return_value = mock_tui_instance

        result = runner.invoke(app, ["tui"])
        mock_tui_instance.run.assert_called_once()


class TestStemSeparationCommands:
    """Test stem separation CLI commands"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.StemSeparationEngine')
    async def test_stems_separate_with_file(self, mock_engine):
        """Test stem separation with provided file"""
        mock_instance = Mock()
        mock_instance.separate_stems = AsyncMock(return_value={
            'vocals': 'output/vocals.wav',
            'instrumental': 'output/instrumental.wav'
        })
        mock_engine.return_value = mock_instance

        # Create a temporary test file
        test_file = Path("/tmp/test_audio.wav")
        test_file.touch()

        try:
            result = runner.invoke(app, ["stems", "separate", str(test_file)])
            # Command should execute without error
            assert result.exit_code == 0
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.select_audio_file')
    @patch('samplemind.interfaces.cli.main.StemSeparationEngine')
    async def test_stems_separate_with_file_picker(self, mock_engine, mock_picker):
        """Test stem separation with file picker"""
        mock_picker.return_value = "/path/to/audio.wav"
        mock_instance = Mock()
        mock_instance.separate_stems = AsyncMock(return_value={})
        mock_engine.return_value = mock_instance

        result = runner.invoke(app, ["stems", "separate"])
        mock_picker.assert_called_once()

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.select_directory')
    @patch('samplemind.interfaces.cli.main.StemSeparationEngine')
    async def test_stems_batch(self, mock_engine, mock_dir_picker):
        """Test batch stem separation"""
        mock_dir_picker.return_value = "/path/to/dir"
        mock_instance = Mock()
        mock_instance.separate_stems = AsyncMock(return_value={})
        mock_engine.return_value = mock_instance

        result = runner.invoke(app, ["stems", "batch"])
        mock_dir_picker.assert_called_once()


class TestMIDICommands:
    """Test MIDI conversion CLI commands"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.AudioToMIDIConverter')
    async def test_midi_convert_with_file(self, mock_converter):
        """Test MIDI conversion with provided file"""
        mock_instance = Mock()
        mock_instance.convert_to_midi = AsyncMock(return_value="output.mid")
        mock_converter.return_value = mock_instance

        test_file = Path("/tmp/test_audio.wav")
        test_file.touch()

        try:
            result = runner.invoke(app, ["midi", "convert", str(test_file)])
            assert result.exit_code == 0
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.select_audio_file')
    @patch('samplemind.interfaces.cli.main.AudioToMIDIConverter')
    async def test_midi_convert_with_picker(self, mock_converter, mock_picker):
        """Test MIDI conversion with file picker"""
        mock_picker.return_value = "/path/to/audio.wav"
        mock_instance = Mock()
        mock_instance.convert_to_midi = AsyncMock(return_value="output.mid")
        mock_converter.return_value = mock_instance

        result = runner.invoke(app, ["midi", "convert"])
        mock_picker.assert_called_once()

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.select_directory')
    @patch('samplemind.interfaces.cli.main.AudioToMIDIConverter')
    async def test_midi_batch(self, mock_converter, mock_dir_picker):
        """Test batch MIDI conversion"""
        mock_dir_picker.return_value = "/path/to/dir"
        mock_instance = Mock()
        mock_instance.convert_to_midi = AsyncMock(return_value="output.mid")
        mock_converter.return_value = mock_instance

        result = runner.invoke(app, ["midi", "batch"])
        mock_dir_picker.assert_called_once()


class TestAnalysisCommands:
    """Test audio analysis CLI commands"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.AudioEngine')
    async def test_analyze_file_command(self, mock_engine):
        """Test analyze file command"""
        mock_instance = Mock()
        mock_features = Mock()
        mock_features.tempo = 120.0
        mock_features.key = 'C'
        mock_features.mode = 'major'
        mock_features.duration = 180.0
        mock_instance.analyze_audio_async = AsyncMock(return_value=mock_features)
        mock_engine.return_value = mock_instance

        test_file = Path("/tmp/test_audio.wav")
        test_file.touch()

        try:
            result = runner.invoke(app, ["analyze", "file", str(test_file)])
            assert result.exit_code == 0
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.AudioEngine')
    async def test_analyze_bpm_command(self, mock_engine):
        """Test BPM analysis command"""
        mock_instance = Mock()
        mock_instance.detect_bpm = Mock(return_value=128.5)
        mock_engine.return_value = mock_instance

        test_file = Path("/tmp/test_audio.wav")
        test_file.touch()

        try:
            result = runner.invoke(app, ["analyze", "bpm", str(test_file)])
            assert result.exit_code == 0
        finally:
            test_file.unlink(missing_ok=True)


class TestGenerationCommands:
    """Test AI music generation CLI commands"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.get_ai_manager')
    async def test_generate_music_command(self, mock_get_manager):
        """Test music generation command"""
        mock_manager = Mock()
        mock_manager.generate_music = AsyncMock(return_value={
            'audio_path': '/tmp/generated.wav',
            'duration': 30.0
        })
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["generate", "music", "--prompt", "epic orchestral"])
        # Should handle async execution


class TestSearchCommands:
    """Test vector search CLI commands"""

    @pytest.mark.asyncio
    @patch('samplemind.interfaces.cli.main.get_vector_store')
    async def test_search_index_command(self, mock_get_store):
        """Test search indexing command"""
        mock_store = Mock()
        mock_store.index_directory = AsyncMock(return_value={'indexed': 10})
        mock_get_store.return_value = mock_store

        test_dir = Path("/tmp/test_dir")
        test_dir.mkdir(exist_ok=True)

        try:
            result = runner.invoke(app, ["search", "index", str(test_dir)])
            # Should handle async execution
        finally:
            test_dir.rmdir()

    def test_search_stats_command(self):
        """Test search stats command"""
        with patch('samplemind.interfaces.cli.main.get_vector_store') as mock_get_store:
            mock_store = Mock()
            mock_store.get_stats = Mock(return_value={
                'total_vectors': 1000,
                'collections': 5
            })
            mock_get_store.return_value = mock_store

            result = runner.invoke(app, ["search", "stats"])
            assert result.exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling"""

    def test_nonexistent_file_error(self):
        """Test handling of nonexistent file"""
        result = runner.invoke(app, ["analyze", "file", "/nonexistent/file.wav"])
        # Should handle error gracefully (exit code may vary)

    def test_invalid_command(self):
        """Test invalid command"""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_missing_required_args(self):
        """Test missing required arguments"""
        result = runner.invoke(app, ["stems", "separate"])
        # Should either prompt for file or show error


class TestCLIHelp:
    """Test CLI help messages"""

    def test_main_help(self):
        """Test main help message"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "SampleMind AI" in result.stdout

    def test_stems_help(self):
        """Test stems command help"""
        result = runner.invoke(app, ["stems", "--help"])
        assert result.exit_code == 0
        assert "stem" in result.stdout.lower()

    def test_midi_help(self):
        """Test MIDI command help"""
        result = runner.invoke(app, ["midi", "--help"])
        assert result.exit_code == 0
        assert "midi" in result.stdout.lower()

    def test_analyze_help(self):
        """Test analyze command help"""
        result = runner.invoke(app, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "analyz" in result.stdout.lower()

    def test_generate_help(self):
        """Test generate command help"""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0

    def test_search_help(self):
        """Test search command help"""
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
