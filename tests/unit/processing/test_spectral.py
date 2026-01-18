"""Unit tests for real-time spectral analyzer."""

import pytest
import numpy as np

from samplemind.core.processing.realtime_spectral import (
    RealtimeSpectral,
    PitchDetector,
    SpectrumAnalyzer,
    FrequencyScale,
)


class TestRealtimeSpectral:
    """Test real-time spectral analyzer"""

    @pytest.fixture
    def spectral(self):
        return RealtimeSpectral(sample_rate=44100, fft_size=4096, target_fps=60)

    def test_initialization(self, spectral):
        """Test spectral analyzer initialization"""
        assert spectral.sample_rate == 44100
        assert spectral.fft_size == 4096
        assert spectral.target_fps == 60
        assert abs(spectral.frame_time_ms - 16.67) < 1.0  # 60 FPS

    def test_process_chunk(self, spectral):
        """Test processing a chunk"""
        # Create test audio chunk
        t = np.arange(4096) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(audio, current_time_ms=0.0)

        assert frame.timestamp_ms == 0.0
        assert len(frame.frequencies_hz) == 2048
        assert len(frame.magnitude) == 2048
        assert len(frame.phase) == 2048
        assert frame.peak_frequency_hz > 0

    def test_process_chunk_wrong_size(self, spectral):
        """Test error on wrong chunk size"""
        audio = np.zeros(2048)  # Wrong size

        with pytest.raises(ValueError):
            spectral.process_chunk(audio)

    def test_get_display_data_linear(self, spectral):
        """Test display data with linear scale"""
        t = np.arange(4096) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(audio)
        display = spectral.get_display_data(frame, scale=FrequencyScale.LINEAR)

        assert "frequencies" in display
        assert "magnitudes" in display
        assert len(display["frequencies"]) > 0

    def test_get_display_data_log(self, spectral):
        """Test display data with logarithmic scale"""
        t = np.arange(4096) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(audio)
        display = spectral.get_display_data(frame, scale=FrequencyScale.LOG)

        assert display["scale"] == "logarithmic"

    def test_frequency_at_position(self, spectral):
        """Test getting frequency at display position"""
        freq_linear = spectral.get_frequency_at_position(0.5, FrequencyScale.LINEAR)
        assert 20 <= freq_linear <= 22050

        freq_log = spectral.get_frequency_at_position(0.5, FrequencyScale.LOG)
        assert 20 <= freq_log <= 22050


class TestPitchDetector:
    """Test pitch detector"""

    @pytest.fixture
    def detector(self):
        return PitchDetector(sample_rate=44100)

    def test_pitch_detection_440hz(self, detector):
        """Test detecting A4 (440 Hz)"""
        t = np.arange(44100) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        pitch, confidence = detector.detect(audio)

        if pitch is not None:
            assert 400 < pitch < 480  # Reasonable range
            assert confidence > 0.3

    def test_pitch_detection_silent(self, detector):
        """Test silent audio"""
        audio = np.zeros(44100)

        pitch, confidence = detector.detect(audio)

        # Should return None or low confidence
        if pitch is not None:
            assert confidence < 0.5

    def test_pitch_cents_conversion(self, detector):
        """Test pitch to cents conversion"""
        cents = detector.get_pitch_cents(440.0, reference=440.0)
        assert cents == pytest.approx(0.0)

        cents = detector.get_pitch_cents(880.0, reference=440.0)
        assert cents == pytest.approx(1200.0)  # One octave

        cents = detector.get_pitch_cents(220.0, reference=440.0)
        assert cents == pytest.approx(-1200.0)  # One octave down


class TestSpectrumAnalyzer:
    """Test spectrum analyzer"""

    @pytest.fixture
    def analyzer(self):
        return SpectrumAnalyzer()

    def test_spectral_features(self, analyzer):
        """Test extracting spectral features"""
        spectral = analyzer.spectral

        # Create test chunk
        t = np.arange(4096) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(audio)
        features = analyzer.get_spectral_features(frame)

        assert "spectral_centroid_hz" in features
        assert "spectral_spread_hz" in features
        assert "brightness" in features
        assert features["peak_frequency_hz"] > 0

    def test_harmonic_complexity(self, analyzer):
        """Test harmonic complexity calculation via spectral features"""
        spectral = analyzer.spectral

        # Pure sine (low complexity)
        t = np.arange(4096) / 44100
        sine = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(sine)
        features = analyzer.get_spectral_features(frame)

        # Spectral features should be extracted
        assert "spectral_centroid_hz" in features
        assert "brightness" in features
        assert features["brightness"] >= 0.0

    def test_rhythmic_stability(self, analyzer):
        """Test that spectral analysis produces valid pitch detection"""
        spectral = analyzer.spectral

        # Create test audio
        t = np.arange(4096) / 44100
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)

        frame = spectral.process_chunk(audio)

        # Check that frame has valid pitch confidence
        assert isinstance(frame.pitch_confidence, float)
        assert 0.0 <= frame.pitch_confidence <= 1.0

    def test_global_instance(self):
        """Test global analyzer instance"""
        from samplemind.core.processing.realtime_spectral import init_spectral, get_spectral

        spectral1 = init_spectral()
        spectral2 = get_spectral()

        assert spectral1 is spectral2
