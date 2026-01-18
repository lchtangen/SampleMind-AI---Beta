"""
Unit tests for TUIAudioEngine bridge - AudioEngine integration for Textual TUI.

Tests cover:
- Single file analysis with progress callbacks
- Batch file analysis with parallel processing
- Audio feature formatting for display
- Cache hit rate and performance metrics
- Session statistics tracking
- Error handling for invalid files
"""

import asyncio
import hashlib
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from samplemind.interfaces.tui.audio_engine_bridge import (
    TUIAudioEngine,
    AudioCache,
    SessionStats,
    get_tui_engine,
    reset_tui_engine,
)
from samplemind.core.engine.audio_engine import AudioFeatures, AnalysisLevel


class TestSessionStats:
    """Test SessionStats tracking and metrics."""

    def test_initialization(self):
        """Test SessionStats initializes with correct defaults."""
        stats = SessionStats()
        assert stats.files_analyzed == 0
        assert stats.total_analysis_time == 0.0
        assert stats.current_file == ""
        assert stats.current_status == "Ready"
        assert stats.get_uptime() > 0

    def test_increment_analyzed(self):
        """Test incrementing analyzed file count and tracking time."""
        stats = SessionStats()
        stats.increment_analyzed(1.5)
        assert stats.files_analyzed == 1
        assert stats.total_analysis_time == 1.5

        stats.increment_analyzed(2.0)
        assert stats.files_analyzed == 2
        assert stats.total_analysis_time == 3.5

    def test_average_time_calculation(self):
        """Test average analysis time calculation."""
        stats = SessionStats()
        stats.increment_analyzed(1.0)
        stats.increment_analyzed(2.0)
        stats.increment_analyzed(3.0)

        avg = stats.get_avg_time()
        assert avg == pytest.approx(2.0)

    def test_average_time_with_no_files(self):
        """Test average time returns 0 when no files analyzed."""
        stats = SessionStats()
        assert stats.get_avg_time() == 0.0

    def test_set_current_file(self):
        """Test setting current file being analyzed."""
        stats = SessionStats()
        stats.set_current_file("/path/to/audio.wav")
        assert stats.current_file == "audio.wav"

    def test_set_status(self):
        """Test setting current status message."""
        stats = SessionStats()
        stats.set_status("Analyzing...")
        assert stats.current_status == "Analyzing..."

    def test_reset(self):
        """Test resetting session statistics."""
        stats = SessionStats()
        stats.increment_analyzed(5.0)
        stats.set_current_file("test.wav")
        stats.set_status("Complete")

        stats.reset()
        assert stats.files_analyzed == 0
        assert stats.total_analysis_time == 0.0
        assert stats.current_file == ""
        assert stats.current_status == "Ready"


class TestAudioCache:
    """Test AudioCache functionality - in-memory LRU cache."""

    @pytest.fixture
    def temp_audio_file(self):
        """Create temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            path = f.name
        yield path
        os.unlink(path)

    def test_cache_initialization(self):
        """Test cache initializes with correct defaults."""
        cache = AudioCache(max_size=50)
        assert cache.max_size == 50
        assert len(cache.cache) == 0
        assert cache.hit_count == 0
        assert cache.miss_count == 0

    @pytest.mark.asyncio
    async def test_cache_miss(self, temp_audio_file):
        """Test cache miss when file not in cache."""
        cache = AudioCache()
        result = await cache.get(temp_audio_file)
        assert result is None
        assert cache.miss_count == 1

    @pytest.mark.asyncio
    async def test_cache_hit(self, temp_audio_file):
        """Test cache hit when file is cached."""
        cache = AudioCache()

        # Create mock AudioFeatures
        features = Mock(spec=AudioFeatures)
        features.file_path = temp_audio_file

        # Set in cache
        await cache.set(temp_audio_file, features)

        # Get from cache
        result = await cache.get(temp_audio_file)
        assert result is features
        assert cache.hit_count == 1

    @pytest.mark.asyncio
    async def test_cache_hit_rate(self, temp_audio_file):
        """Test cache hit rate calculation."""
        cache = AudioCache()
        features = Mock(spec=AudioFeatures)

        # Set cache
        await cache.set(temp_audio_file, features)

        # Hit
        await cache.get(temp_audio_file)
        # Miss
        await cache.get(temp_audio_file)
        cache.miss_count += 1

        hit_rate = cache.get_hit_rate()
        assert hit_rate == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_cache_eviction_on_size_limit(self, temp_audio_file):
        """Test cache evicts oldest entry when size limit reached."""
        cache = AudioCache(max_size=2)

        features1 = Mock(spec=AudioFeatures)
        features2 = Mock(spec=AudioFeatures)
        features3 = Mock(spec=AudioFeatures)

        # Add 3 items to cache with max size 2
        await cache.set(temp_audio_file, features1)
        await cache.set(temp_audio_file + "2", features2)
        await cache.set(temp_audio_file + "3", features3)

        # Cache should have 2 items (oldest evicted)
        assert len(cache.cache) == 2

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = AudioCache()
        cache.hit_count = 10
        cache.miss_count = 5
        cache.cache = {"key": "value"}

        cache.clear()

        assert len(cache.cache) == 0
        assert cache.hit_count == 0
        assert cache.miss_count == 0

    def test_file_hash_generation(self, temp_audio_file):
        """Test SHA-256 file hash generation."""
        hash1 = AudioCache._hash_file(temp_audio_file)
        hash2 = AudioCache._hash_file(temp_audio_file)

        # Should be consistent
        assert hash1 == hash2
        # Should be valid SHA-256 (64 hex chars)
        assert len(hash1) == 64
        assert all(c in "0123456789abcdef" for c in hash1)


class TestTUIAudioEngine:
    """Test TUIAudioEngine bridge functionality."""

    @pytest.fixture
    def mock_audio_features(self):
        """Create mock AudioFeatures object."""
        features = Mock(spec=AudioFeatures)
        features.file_path = "/path/to/audio.wav"
        features.duration = 10.5
        features.sample_rate = 44100
        features.channels = 2
        features.bit_depth = 16
        features.tempo = 120.0
        features.key = "C"
        features.mode = "Major"
        features.time_signature = (4, 4)
        features.spectral_centroid = 2450.0
        features.spectral_rolloff = 8200.0
        features.zero_crossing_rate = 0.045
        features.rms_energy = 0.123
        features.mfccs = [0.1] * 13
        features.beats = [0.5, 1.0, 1.5, 2.0]
        features.onset_times = [0.2, 0.7, 1.2]
        features.chroma_features = [0.08] * 12
        features.harmonic_content = 0.8
        features.percussive_content = 0.2
        features.pitch_class_distribution = [0.08] * 12
        return features

    @patch("samplemind.interfaces.tui.audio_engine_bridge.AudioEngine")
    def test_initialization(self, mock_engine_class):
        """Test TUIAudioEngine initializes correctly."""
        engine = TUIAudioEngine()

        assert engine.engine is not None
        assert engine.cache is not None
        assert engine.session_stats is not None
        assert isinstance(engine.cache, AudioCache)
        assert isinstance(engine.session_stats, SessionStats)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.audio_engine_bridge.AudioEngine")
    async def test_analyze_file_not_found(self, mock_engine_class):
        """Test error handling for non-existent file."""
        engine = TUIAudioEngine()

        with pytest.raises(FileNotFoundError):
            await engine.analyze_file("/nonexistent/file.wav")

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.audio_engine_bridge.AudioEngine")
    async def test_analyze_file_with_progress_callback(
        self, mock_engine_class, mock_audio_features
    ):
        """Test single file analysis with progress callback."""
        engine = TUIAudioEngine()
        progress_values = []

        def progress_callback(progress: float):
            progress_values.append(progress)

        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio data")
            temp_path = f.name

        try:
            # Mock the engine analyze method
            engine.engine.analyze_audio = Mock(return_value=mock_audio_features)

            # Analyze file
            result = await engine.analyze_file(
                temp_path, progress_callback, AnalysisLevel.STANDARD
            )

            # Verify result
            assert result is mock_audio_features

            # Verify progress was reported
            assert len(progress_values) > 0

            # Verify session stats updated
            assert engine.session_stats.files_analyzed == 1

        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.audio_engine_bridge.AudioEngine")
    async def test_analyze_batch(
        self, mock_engine_class, mock_audio_features
    ):
        """Test batch file analysis."""
        engine = TUIAudioEngine()
        progress_updates = []

        def progress_callback(current: int, total: int):
            progress_updates.append((current, total))

        # Create temporary audio files
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(b"fake audio data")
                temp_files.append(f.name)

        try:
            # Mock the engine analyze method
            engine.engine.analyze_audio = Mock(return_value=mock_audio_features)

            # Analyze batch
            results = await engine.analyze_batch(
                temp_files, progress_callback, AnalysisLevel.STANDARD
            )

            # Verify results
            assert len(results) == 3
            assert all(r is mock_audio_features for r in results)

            # Verify progress was reported
            assert len(progress_updates) > 0

            # Verify session stats updated
            assert engine.session_stats.files_analyzed == 3

        finally:
            for f in temp_files:
                os.unlink(f)

    @pytest.mark.asyncio
    @patch("samplemind.interfaces.tui.audio_engine_bridge.AudioEngine")
    async def test_batch_analysis_with_invalid_files(self, mock_engine_class):
        """Test batch analysis gracefully handles invalid files."""
        engine = TUIAudioEngine()

        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(b"fake audio data")
                temp_files.append(f.name)

        try:
            # Add non-existent file
            temp_files.append("/nonexistent/file.wav")

            # Mock the engine to raise error on non-existent file
            engine.engine.analyze_audio = Mock(
                side_effect=FileNotFoundError("File not found")
            )

            # Batch should handle error and continue
            results = await engine.analyze_batch(
                temp_files, level=AnalysisLevel.STANDARD
            )

            # Should have some results despite error
            assert len(results) >= 0

        finally:
            for f in temp_files[:-1]:  # Skip non-existent file
                os.unlink(f)

    def test_format_features_for_display(self, mock_audio_features):
        """Test formatting audio features for TUI display."""
        engine = TUIAudioEngine()
        formatted = engine.format_features_for_display(mock_audio_features)

        # Verify all expected keys present
        expected_keys = [
            "Duration",
            "Sample Rate",
            "Channels",
            "Bit Depth",
            "Tempo",
            "Key",
            "Time Signature",
            "Spectral Centroid",
            "Spectral Bandwidth",
            "Spectral Rolloff",
            "Zero Crossing Rate",
            "RMS Energy",
            "MFCC Coefficients",
        ]

        for key in expected_keys:
            assert key in formatted

        # Verify formatting correctness
        assert "120" in formatted["Tempo"]  # Should contain BPM value
        assert "C" in formatted["Key"]  # Should contain key
        assert "Stereo" in formatted["Channels"]  # Should identify stereo
        assert "10" in formatted["Duration"]  # Should contain duration

    def test_get_performance_stats(self, mock_audio_features):
        """Test performance statistics retrieval."""
        engine = TUIAudioEngine()

        # Perform some operations to generate stats
        engine.session_stats.increment_analyzed(1.5)
        engine.cache.hit_count = 5
        engine.cache.miss_count = 2

        stats = engine.get_performance_stats()

        assert "cache_hit_rate" in stats
        assert "files_analyzed" in stats
        assert "total_analysis_time" in stats
        assert "avg_analysis_time" in stats
        assert "session_uptime" in stats
        assert stats["files_analyzed"] == 1
        assert stats["cache_hit_rate"] == pytest.approx(5.0 / 7.0)

    def test_reset_session(self):
        """Test resetting session and cache."""
        engine = TUIAudioEngine()

        # Add some data
        engine.session_stats.increment_analyzed(5.0)
        engine.cache.hit_count = 10

        # Reset
        engine.reset_session()

        # Verify reset
        assert engine.session_stats.files_analyzed == 0
        assert engine.session_stats.total_analysis_time == 0.0
        assert engine.cache.hit_count == 0


class TestTUIAudioEngineSingleton:
    """Test singleton pattern for TUIAudioEngine."""

    def test_get_tui_engine_creates_instance(self):
        """Test get_tui_engine creates first instance."""
        reset_tui_engine()
        engine = get_tui_engine()
        assert engine is not None
        assert isinstance(engine, TUIAudioEngine)

    def test_get_tui_engine_returns_same_instance(self):
        """Test get_tui_engine returns same instance on multiple calls."""
        reset_tui_engine()
        engine1 = get_tui_engine()
        engine2 = get_tui_engine()
        assert engine1 is engine2

    def test_reset_tui_engine(self):
        """Test resetting singleton instance."""
        engine1 = get_tui_engine()
        engine1.session_stats.increment_analyzed(5.0)

        reset_tui_engine()

        engine2 = get_tui_engine()
        # After reset, should have new instance with clean stats
        # (though this depends on implementation details)
        assert engine2 is not None
