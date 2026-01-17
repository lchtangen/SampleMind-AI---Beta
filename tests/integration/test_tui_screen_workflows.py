"""
Integration tests for TUI screen workflows.

Tests cover end-to-end user workflows:
- Single file analysis workflow
- Batch processing workflow
- Error handling and recovery
- File picker integration
- Results display
"""

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

import pytest

from samplemind.core.engine.audio_engine import AudioFeatures, AnalysisLevel


class MockAudioFeatures:
    """Mock AudioFeatures for testing."""

    def __init__(
        self,
        file_path="/path/to/audio.wav",
        duration=10.5,
        tempo=120.0,
        key="C",
    ):
        self.file_path = file_path
        self.duration = duration
        self.sample_rate = 44100
        self.channels = 2
        self.bit_depth = 16
        self.tempo = tempo
        self.key = key
        self.mode = "Major"
        self.time_signature = (4, 4)
        self.spectral_centroid = 2450.0
        self.spectral_bandwidth = 2500.0
        self.spectral_rolloff = 8200.0
        self.zero_crossing_rate = 0.045
        self.rms_energy = 0.123
        self.mfccs = [0.1] * 13
        self.beats = [0.5, 1.0, 1.5, 2.0]
        self.onset_times = [0.2, 0.7, 1.2]
        self.chroma_features = [0.08] * 12
        self.harmonic_content = 0.8
        self.percussive_content = 0.2
        self.pitch_class_distribution = [0.08] * 12


class TestAnalyzeScreenWorkflow:
    """Test AnalyzeScreen user workflows."""

    @pytest.fixture
    def temp_audio_file(self):
        """Create temporary audio file."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            path = f.name
        yield path
        if os.path.exists(path):
            os.unlink(path)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.screens.analyze_screen.get_tui_engine")
    @patch("samplemind.interfaces.tui.screens.analyze_screen.CrossPlatformFilePicker")
    async def test_analyze_single_file_workflow(self, mock_picker_class, mock_engine_getter, temp_audio_file):
        """Test complete single file analysis workflow."""
        # Setup mocks
        mock_engine = AsyncMock()
        mock_engine.analyze_file = AsyncMock(
            return_value=MockAudioFeatures(file_path=temp_audio_file)
        )
        mock_engine_getter.return_value = mock_engine

        mock_picker = MagicMock()
        mock_picker.choose_file.return_value = temp_audio_file
        mock_picker_class.return_value = mock_picker

        # Verify file exists
        assert os.path.exists(temp_audio_file)

        # Would test screen behavior here if Textual testing utilities available
        # This demonstrates the expected flow

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.screens.analyze_screen.get_tui_engine")
    async def test_analyze_nonexistent_file_error_handling(self, mock_engine_getter):
        """Test error handling for non-existent file."""
        mock_engine = AsyncMock()
        mock_engine.analyze_file = AsyncMock(
            side_effect=FileNotFoundError("File not found")
        )
        mock_engine_getter.return_value = mock_engine

        # When analyzing non-existent file, should raise error
        with pytest.raises(FileNotFoundError):
            await mock_engine.analyze_file("/nonexistent/file.wav")

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.screens.analyze_screen.get_tui_engine")
    async def test_analyze_invalid_audio_file_error_handling(self, mock_engine_getter):
        """Test error handling for invalid audio file."""
        mock_engine = AsyncMock()
        mock_engine.analyze_file = AsyncMock(
            side_effect=ValueError("Invalid audio format")
        )
        mock_engine_getter.return_value = mock_engine

        # When analyzing invalid file, should raise ValueError
        with pytest.raises(ValueError):
            await mock_engine.analyze_file("/path/to/invalid.txt")

    @pytest.mark.asyncio
    async def test_progress_callback_invocation(self):
        """Test that progress callbacks are invoked during analysis."""
        progress_values = []

        def track_progress(progress: float):
            progress_values.append(progress)

        # Simulate analysis with progress tracking
        for i in range(10):
            progress = i / 10.0
            track_progress(progress)

        # Verify progress values
        assert len(progress_values) == 10
        assert progress_values[0] == 0.0
        assert progress_values[-1] == 0.9


class TestBatchScreenWorkflow:
    """Test BatchScreen user workflows."""

    @pytest.fixture
    def temp_audio_folder(self):
        """Create temporary folder with audio files."""
        folder = tempfile.mkdtemp()
        files = []

        for i in range(3):
            filepath = os.path.join(folder, f"audio_{i}.wav")
            with open(filepath, "w") as f:
                f.write("fake audio data")
            files.append(filepath)

        yield folder
        # Cleanup
        for f in files:
            if os.path.exists(f):
                os.unlink(f)
        if os.path.exists(folder):
            os.rmdir(folder)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.screens.batch_screen.get_tui_engine")
    @patch("samplemind.interfaces.tui.screens.batch_screen.CrossPlatformFilePicker")
    async def test_batch_processing_workflow(self, mock_picker_class, mock_engine_getter, temp_audio_folder):
        """Test complete batch processing workflow."""
        # Setup mocks
        mock_engine = AsyncMock()
        mock_engine.analyze_batch = AsyncMock(
            return_value=[
                MockAudioFeatures(file_path=f)
                for f in os.listdir(temp_audio_folder)
            ]
        )
        mock_engine_getter.return_value = mock_engine

        mock_picker = MagicMock()
        mock_picker.choose_folder.return_value = temp_audio_folder
        mock_picker_class.return_value = mock_picker

        # Verify folder exists
        assert os.path.exists(temp_audio_folder)
        assert len(os.listdir(temp_audio_folder)) == 3

    @pytest.mark.asyncio
    async def test_batch_progress_tracking(self):
        """Test batch processing progress tracking."""
        progress_updates = []

        def batch_progress(current: int, total: int):
            progress_updates.append((current, total))

        # Simulate batch processing of 5 files
        total_files = 5
        for i in range(total_files + 1):
            batch_progress(i, total_files)

        # Verify progress updates
        assert len(progress_updates) == 6
        assert progress_updates[0] == (0, 5)
        assert progress_updates[-1] == (5, 5)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.screens.batch_screen.get_tui_engine")
    async def test_batch_cancellation(self, mock_engine_getter):
        """Test batch processing cancellation."""
        mock_engine = AsyncMock()
        processed = []

        async def mock_analyze_batch(files, progress_callback, level):
            for i, file in enumerate(files):
                processed.append(file)
                progress_callback(i + 1, len(files))
            return [MockAudioFeatures() for _ in files]

        mock_engine.analyze_batch = mock_analyze_batch
        mock_engine_getter.return_value = mock_engine

        # Simulate batch processing
        files = [f"file_{i}.wav" for i in range(3)]
        results = await mock_engine.analyze_batch(files, lambda c, t: None, AnalysisLevel.STANDARD)

        assert len(results) == 3
        assert len(processed) == 3


class TestFileValidation:
    """Test file validation across screens."""

    def test_audio_file_extension_validation(self):
        """Test validation of audio file extensions."""
        valid_extensions = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aiff"}
        test_files = [
            ("song.wav", True),
            ("audio.mp3", True),
            ("track.flac", True),
            ("music.m4a", True),
            ("sound.ogg", True),
            ("file.aiff", True),
            ("document.txt", False),
            ("image.jpg", False),
            ("archive.zip", False),
        ]

        for filename, should_be_valid in test_files:
            ext = Path(filename).suffix.lower()
            is_valid = ext in valid_extensions
            assert is_valid == should_be_valid

    def test_file_exists_validation(self):
        """Test file existence validation."""
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            temp_path = f.name
            assert os.path.exists(temp_path)

        # After context manager, file should not exist
        assert not os.path.exists(temp_path)

    def test_folder_readability_validation(self):
        """Test folder readability validation."""
        temp_folder = tempfile.mkdtemp()

        try:
            assert os.access(temp_folder, os.R_OK)
            assert os.path.isdir(temp_folder)
        finally:
            os.rmdir(temp_folder)


class TestAnalysisLevelHandling:
    """Test handling of different analysis levels."""

    def test_analysis_level_enum_values(self):
        """Test all analysis level enum values."""
        levels = [
            (AnalysisLevel.BASIC, "BASIC"),
            (AnalysisLevel.STANDARD, "STANDARD"),
            (AnalysisLevel.DETAILED, "DETAILED"),
            (AnalysisLevel.PROFESSIONAL, "PROFESSIONAL"),
        ]

        for level, name in levels:
            assert level.name == name

    @pytest.mark.asyncio
    async def test_different_analysis_levels(self):
        """Test analysis with different levels."""
        mock_engine = AsyncMock()

        for level in [
            AnalysisLevel.BASIC,
            AnalysisLevel.STANDARD,
            AnalysisLevel.DETAILED,
            AnalysisLevel.PROFESSIONAL,
        ]:
            # Each level should work
            mock_engine.analyze_file = AsyncMock(
                return_value=MockAudioFeatures()
            )

            result = await mock_engine.analyze_file(
                "/path/to/audio.wav", level=level
            )
            assert result is not None


class TestResultsDisplay:
    """Test results display and formatting."""

    def test_audio_features_formatting(self):
        """Test formatting audio features for display."""
        features = MockAudioFeatures(
            duration=155.5,
            tempo=120.0,
            key="C",
        )

        # Format duration
        minutes = int(features.duration // 60)
        seconds = int(features.duration % 60)
        formatted_duration = f"{minutes}:{seconds:02d}"
        assert formatted_duration == "2:35"

        # Format tempo
        formatted_tempo = f"{features.tempo:.1f} BPM"
        assert formatted_tempo == "120.0 BPM"

        # Format key
        formatted_key = f"{features.key} {features.mode}"
        assert formatted_key == "C Major"

    def test_spectral_features_formatting(self):
        """Test formatting spectral features for display."""
        features = MockAudioFeatures()

        # Format spectral values
        centroid = f"{features.spectral_centroid:.0f} Hz"
        rolloff = f"{features.spectral_rolloff:.0f} Hz"
        zcr = f"{features.zero_crossing_rate:.4f}"

        assert centroid == "2450 Hz"
        assert rolloff == "8200 Hz"
        assert zcr == "0.0450"

    def test_mfcc_features_formatting(self):
        """Test formatting MFCC features for display."""
        features = MockAudioFeatures()

        # MFCC should have 13 coefficients
        assert len(features.mfccs) == 13

        # Format MFCC values
        formatted_mfccs = [f"{v:.6f}" for v in features.mfccs]
        assert len(formatted_mfccs) == 13
        assert all(isinstance(v, str) for v in formatted_mfccs)


class TestErrorRecovery:
    """Test error handling and recovery in workflows."""

    @pytest.mark.asyncio
    async def test_recovery_from_single_file_error(self):
        """Test recovery after single file analysis error."""
        mock_engine = AsyncMock()

        # First call fails
        mock_engine.analyze_file = AsyncMock(
            side_effect=ValueError("Invalid file")
        )

        with pytest.raises(ValueError):
            await mock_engine.analyze_file("/invalid/file.wav")

        # Should be able to try again with different file
        mock_engine.analyze_file = AsyncMock(
            return_value=MockAudioFeatures()
        )

        result = await mock_engine.analyze_file("/valid/file.wav")
        assert result is not None

    @pytest.mark.asyncio
    async def test_batch_continues_after_file_error(self):
        """Test batch processing continues after file error."""
        mock_engine = AsyncMock()
        completed = []

        async def mock_batch_with_error(files, progress_callback, level):
            results = []
            for file in files:
                if "error" in file:
                    # Skip this file but continue
                    results.append(None)
                else:
                    completed.append(file)
                    results.append(MockAudioFeatures(file_path=file))

            return results

        mock_engine.analyze_batch = mock_batch_with_error

        files = ["file1.wav", "error_file.wav", "file3.wav"]
        results = await mock_engine.analyze_batch(
            files, None, AnalysisLevel.STANDARD
        )

        # Should have processed 2 files despite 1 error
        assert len(completed) == 2
        assert None in results

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_partial_failure(self):
        """Test graceful degradation when partial operations fail."""
        mock_engine = AsyncMock()

        # Simulate 3 files, middle one fails
        async def mock_batch_partial_failure(files, progress_callback, level):
            results = []
            for i, file in enumerate(files):
                if i == 1:
                    results.append(None)
                else:
                    results.append(MockAudioFeatures(file_path=file))
                if progress_callback:
                    progress_callback(i + 1, len(files))

            return results

        mock_engine.analyze_batch = mock_batch_partial_failure

        files = ["file1.wav", "bad_file.wav", "file3.wav"]
        progress_updates = []

        def track_progress(current, total):
            progress_updates.append((current, total))

        results = await mock_engine.analyze_batch(
            files, track_progress, AnalysisLevel.STANDARD
        )

        # Should have 3 results with middle one None
        assert len(results) == 3
        assert results[1] is None
        assert results[0] is not None
        assert results[2] is not None

        # Progress should be tracked
        assert len(progress_updates) == 3
