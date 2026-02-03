"""Unit tests for audio effects module."""

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from samplemind.core.processing.audio_effects import (
    AudioEffectsProcessor,
)


class TestAudioEffectsProcessor:
    """Test AudioEffectsProcessor class"""

    @pytest.fixture
    def processor(self):
        return AudioEffectsProcessor(sample_rate=44100)

    @pytest.fixture
    def audio_chunk(self):
        # 1 second of silence/noise
        np.random.seed(42)
        return np.random.rand(44100).astype(np.float32) * 0.1 # normalize somewhat

    @pytest.fixture
    def stereo_chunk(self):
        # 1 second stereo
        np.random.seed(42)
        return np.random.rand(2, 44100).astype(np.float32) * 0.1

    def test_initialization(self, processor):
        assert processor.sample_rate == 44100

    def test_apply_eq(self, processor, audio_chunk):
        # Test default EQ (flat)
        processed = processor.apply_eq(audio_chunk)
        assert processed.shape == audio_chunk.shape

        # Test with heavy boost
        gains = [10.0] * 10
        processed_boosted = processor.apply_eq(audio_chunk, gains=gains)
        assert processed_boosted.shape == audio_chunk.shape
        # Check if energy increased
        assert np.mean(np.abs(processed_boosted)) > np.mean(np.abs(audio_chunk))

    def test_apply_compression(self, processor):
        # Test compression
        # Create a signal with peaks
        signal = np.zeros(44100)
        signal[1000:2000] = 10.0 # High peak

        compressed = processor.apply_compression(
            signal,
            ratio=10.0,
            threshold_db=-20.0, # -20dB is 0.1
            attack_ms=0.1,
            release_ms=0.1
        )

        # Peak should be reduced. 10.0 is +20dB relative to 1.0 (0dB = 1.0 usually in audio DSP, or whatever reference)
        # Actually 20*log10(10) = 20dB.
        # Threshold -20dB = 0.1
        # Input level 10.0.
        # Reduction ratio for amount over threshold.
        assert np.max(compressed) < 9.0

    def test_apply_distortion(self, processor, audio_chunk):
        # Test distortion
        processed = processor.apply_distortion(audio_chunk, drive=100.0)
        # Should be clipped/limited roughly between -1 and 1 via tanh
        # output gain is 0dB (1.0)
        assert np.max(np.abs(processed)) <= 1.0 + 0.1

    def test_apply_reverb(self, processor, audio_chunk):
        processed = processor.apply_reverb(audio_chunk)
        assert processed.shape == audio_chunk.shape

    def test_apply_limiting(self, processor, audio_chunk):
        # Create loud signal
        signal = audio_chunk * 10
        limited = processor.apply_limiting(signal, threshold_db=-1.0)

        assert np.max(np.abs(limited)) < np.max(np.abs(signal))

    def test_presets(self, processor, audio_chunk):
        presets = ["vocal", "drums", "bass", "master", "vintage"]
        for preset in presets:
            processed = processor.apply_preset(audio_chunk, preset)
            assert processed.shape == audio_chunk.shape
            assert not np.array_equal(processed, audio_chunk)

    @patch("samplemind.core.processing.audio_effects.librosa")
    def test_load_audio(self, mock_librosa, processor):
        mock_librosa.load.return_value = (np.zeros(100), 44100)
        audio, sr = processor.load_audio(Path("test.wav"))
        assert sr == 44100
        assert len(audio) == 100

    @patch("samplemind.core.processing.audio_effects.sf")
    def test_save_audio(self, mock_sf, processor, audio_chunk):
        path = Path("output.wav")
        processor.save_audio(audio_chunk, path)
        mock_sf.write.assert_called_once()
        args = mock_sf.write.call_args
        assert str(args[0][0]) == "output.wav"
