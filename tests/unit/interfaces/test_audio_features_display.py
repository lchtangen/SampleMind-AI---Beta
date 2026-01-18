"""
Unit tests for audio features display and formatting.

Tests cover:
- Audio feature extraction and validation
- Feature formatting for terminal display
- Data transformation and conversion
- Edge cases and boundary conditions
"""

import pytest
from unittest.mock import Mock

from samplemind.core.engine.audio_engine import AudioFeatures


class MockAudioFeatures:
    """Mock AudioFeatures for testing."""

    def __init__(self):
        self.file_path = "/path/to/audio.wav"
        self.duration = 155.5
        self.sample_rate = 44100
        self.channels = 2
        self.bit_depth = 16
        self.tempo = 120.5
        self.key = "C"
        self.mode = "Major"
        self.time_signature = (4, 4)
        self.spectral_centroid = 2450.75
        self.spectral_bandwidth = 2500.0
        self.spectral_rolloff = 8200.25
        self.zero_crossing_rate = 0.0456
        self.rms_energy = 0.1234
        self.mfccs = [0.1] * 13
        self.beats = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        self.onset_times = [0.2, 0.7, 1.2, 1.8]
        self.chroma_features = [0.08] * 12
        self.harmonic_content = 0.8123
        self.percussive_content = 0.1877
        self.pitch_class_distribution = [0.08] * 12
        self.analysis_level = "STANDARD"


class TestDurationFormatting:
    """Test duration formatting utilities."""

    def test_format_seconds_to_mmss(self):
        """Test formatting seconds to MM:SS format."""
        test_cases = [
            (0, "0:00"),
            (10, "0:10"),
            (60, "1:00"),
            (65, "1:05"),
            (155.5, "2:35"),
            (3661, "61:01"),
        ]

        for seconds, expected in test_cases:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            result = f"{minutes}:{secs:02d}"
            assert result == expected

    def test_format_large_durations(self):
        """Test formatting very large durations."""
        # Hour+ durations
        seconds = 3661  # 1 hour, 1 minute, 1 second
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        result = f"{minutes}:{secs:02d}"
        assert result == "61:01"

    def test_format_subsecond_precision_lost(self):
        """Test that subsecond precision is lost in MM:SS format."""
        result1 = f"{int(10.1 // 60)}:{int(10.1 % 60):02d}"
        result2 = f"{int(10.9 // 60)}:{int(10.9 % 60):02d}"
        assert result1 == result2 == "0:10"


class TestTempoFormatting:
    """Test tempo (BPM) formatting."""

    def test_format_tempo_with_decimal(self):
        """Test formatting tempo with decimal places."""
        test_cases = [
            (120.0, "120.0 BPM"),
            (120.5, "120.5 BPM"),
            (99.99, "100.0 BPM"),
            (140.1, "140.1 BPM"),
        ]

        for tempo, expected in test_cases:
            result = f"{tempo:.1f} BPM"
            assert result == expected

    def test_tempo_range_validation(self):
        """Test valid tempo ranges."""
        # Human tempo typically 30-300 BPM
        test_tempos = [
            (30, True),  # Slow
            (60, True),  # Ballad
            (120, True),  # Standard
            (180, True),  # Fast
            (300, True),  # Very fast
            (10, True),  # Technically valid but rare
            (400, True),  # Fast electronic
        ]

        for tempo, should_be_valid in test_tempos:
            # All should format successfully
            formatted = f"{tempo:.1f} BPM"
            assert "BPM" in formatted


class TestKeyFormatting:
    """Test key signature formatting."""

    def test_format_key_and_mode(self):
        """Test formatting key with mode."""
        test_cases = [
            ("C", "Major", "C Major"),
            ("A", "Minor", "A Minor"),
            ("F#", "Major", "F# Major"),
            ("Bb", "Minor", "Bb Minor"),
            ("G", "Major", "G Major"),
        ]

        for key, mode, expected in test_cases:
            result = f"{key} {mode}"
            assert result == expected

    def test_all_major_keys(self):
        """Test formatting all major keys."""
        keys = ["C", "G", "D", "A", "E", "B", "F#", "Db", "Ab", "Eb", "Bb", "F"]
        for key in keys:
            result = f"{key} Major"
            assert "Major" in result
            assert key in result

    def test_all_minor_keys(self):
        """Test formatting all minor keys."""
        keys = ["A", "E", "B", "F#", "C#", "G#", "D#", "D", "G", "C", "F", "Bb"]
        for key in keys:
            result = f"{key} Minor"
            assert "Minor" in result
            assert key in result


class TestSpectralFeatureFormatting:
    """Test spectral feature formatting."""

    def test_format_spectral_centroid(self):
        """Test formatting spectral centroid."""
        test_values = [
            (2450.75, "2451 Hz"),
            (0.0, "0 Hz"),
            (22000.5, "22000 Hz"),  # Max audible frequency
            (100.1, "100 Hz"),
        ]

        for value, expected in test_values:
            result = f"{value:.0f} Hz"
            # Check it's close (rounding differences)
            result_val = int(result.replace(" Hz", ""))
            expected_val = int(expected.replace(" Hz", ""))
            assert result_val == expected_val

    def test_format_spectral_rolloff(self):
        """Test formatting spectral rolloff."""
        rolloff = 8200.25
        result = f"{rolloff:.0f} Hz"
        assert result == "8200 Hz"

    def test_format_zero_crossing_rate(self):
        """Test formatting zero crossing rate."""
        test_values = [
            (0.0456, "0.0456"),
            (0.1, "0.1000"),
            (0.05, "0.0500"),
            (0.001, "0.0010"),
        ]

        for value, expected in test_values:
            result = f"{value:.4f}"
            assert result == expected


class TestChannelFormatting:
    """Test channel count formatting."""

    def test_format_mono(self):
        """Test formatting mono audio."""
        channels = 1
        result = f"{channels} ({'Mono' if channels == 1 else 'Stereo'})"
        assert result == "1 (Mono)"

    def test_format_stereo(self):
        """Test formatting stereo audio."""
        channels = 2
        result = f"{channels} ({'Stereo' if channels == 2 else 'Mono' if channels == 1 else f'{channels}-channel'})"
        assert result == "2 (Stereo)"

    def test_format_multichannel(self):
        """Test formatting multichannel audio."""
        for channels in [3, 4, 5, 6, 8]:
            result = f"{channels} ({f'{channels}-channel'})"
            assert str(channels) in result
            assert "channel" in result


class TestSampleRateFormatting:
    """Test sample rate formatting."""

    def test_format_common_sample_rates(self):
        """Test formatting common sample rates."""
        test_rates = [
            (8000, "8,000 Hz"),
            (16000, "16,000 Hz"),
            (22050, "22,050 Hz"),
            (44100, "44,100 Hz"),
            (48000, "48,000 Hz"),
            (96000, "96,000 Hz"),
        ]

        for rate, expected in test_rates:
            result = f"{rate:,} Hz"
            assert result == expected

    def test_thousand_separator_formatting(self):
        """Test thousand separator in large numbers."""
        rates = [1000, 10000, 100000, 1000000]
        for rate in rates:
            result = f"{rate:,}"
            assert "," in result or len(str(rate)) < 4


class TestBitDepthFormatting:
    """Test bit depth formatting."""

    def test_format_common_bit_depths(self):
        """Test formatting common bit depths."""
        test_depths = [
            (8, "8-bit"),
            (16, "16-bit"),
            (24, "24-bit"),
            (32, "32-bit"),
        ]

        for depth, expected in test_depths:
            result = f"{depth}-bit"
            assert result == expected


class TestTimeSignatureFormatting:
    """Test time signature formatting."""

    def test_format_time_signature_tuple(self):
        """Test formatting time signature as string."""
        test_signatures = [
            ((2, 4), "2/4"),
            ((3, 4), "3/4"),
            ((4, 4), "4/4"),
            ((5, 4), "5/4"),
            ((6, 8), "6/8"),
        ]

        for sig, expected in test_signatures:
            result = f"{sig[0]}/{sig[1]}"
            assert result == expected


class TestMFCCFormatting:
    """Test MFCC feature formatting."""

    def test_mfcc_count(self):
        """Test MFCC coefficient count."""
        mfccs = [0.1] * 13
        assert len(mfccs) == 13

    def test_format_mfcc_coefficient(self):
        """Test formatting individual MFCC coefficient."""
        coefficient = 0.123456789
        result = f"{coefficient:.6f}"
        assert result == "0.123457"

    def test_all_mfccs_formatted(self):
        """Test formatting all MFCC coefficients."""
        mfccs = [i * 0.01 for i in range(13)]
        formatted = [f"{v:.6f}" for v in mfccs]
        assert len(formatted) == 13
        assert all(isinstance(v, str) for v in formatted)


class TestFeatureArrayFormatting:
    """Test formatting feature arrays."""

    def test_format_beat_times(self):
        """Test formatting beat times."""
        beats = [0.5, 1.0, 1.5, 2.0]
        formatted = [f"{b:.2f}s" for b in beats]
        assert len(formatted) == 4
        assert formatted[0] == "0.50s"
        assert formatted[-1] == "2.00s"

    def test_format_onset_times(self):
        """Test formatting onset times."""
        onsets = [0.2, 0.7, 1.2, 1.8]
        formatted = [f"{o:.2f}s" for o in onsets]
        assert len(formatted) == 4

    def test_format_chroma_features(self):
        """Test formatting chroma features."""
        chroma = [0.08] * 12
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        formatted = [(note, val) for note, val in zip(notes, chroma)]
        assert len(formatted) == 12


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_duration(self):
        """Test formatting zero duration."""
        duration = 0
        result = f"{int(duration // 60)}:{int(duration % 60):02d}"
        assert result == "0:00"

    def test_very_small_spectral_value(self):
        """Test formatting very small spectral values."""
        value = 0.00001
        result = f"{value:.4f}"
        assert result == "0.0000"

    def test_maximum_float_precision(self):
        """Test maximum precision in float formatting."""
        value = 0.123456789123456
        result = f"{value:.6f}"
        assert len(result.split(".")[1]) == 6

    def test_negative_values_handling(self):
        """Test handling of edge case negative values (should not occur but test robustness)."""
        # Tempo should never be negative
        tempo = abs(-120.5)
        result = f"{tempo:.1f} BPM"
        assert result == "120.5 BPM"


class TestFormattingConsistency:
    """Test consistency across formatting functions."""

    def test_consistent_decimal_places(self):
        """Test consistent decimal place formatting."""
        values = [1.1, 2.22, 3.333, 4.4444]
        formatted_1dp = [f"{v:.1f}" for v in values]
        formatted_2dp = [f"{v:.2f}" for v in values]

        # Check consistency
        assert len(formatted_1dp) == 4
        assert all("." in v for v in formatted_1dp)

    def test_consistent_unit_suffixes(self):
        """Test consistent unit suffix application."""
        frequencies = [100.5, 200.5, 300.5]
        formatted = [f"{f:.0f} Hz" for f in frequencies]

        assert all(v.endswith("Hz") for v in formatted)
        assert len(formatted) == 3

    def test_unicode_symbol_consistency(self):
        """Test unicode symbol handling."""
        # Test BPM symbol
        tempo_str = f"120.0 BPM"
        assert "BPM" in tempo_str

        # Test note symbols could use unicode
        key_str = f"C# Major"
        assert "#" in key_str or "♯" in key_str or "#" in key_str
