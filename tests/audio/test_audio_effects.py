"""
Tests for audio effects processing.
"""
import os
import pytest
import numpy as np
from pathlib import Path
from samplemind.audio.effects import AudioEffectsProcessor, NoiseReduction, EffectType

# Test audio files directory
TEST_AUDIO_DIR = Path(__file__).parent.parent.parent / "test_audio_samples"
SAMPLE_FILE = TEST_AUDIO_DIR / "test_chord_120bpm.wav"

# Skip tests if test audio files are not available
pytestmark = pytest.mark.skipif(
    not SAMPLE_FILE.exists(),
    reason="Test audio files not found"
)

class TestAudioEffects:
    """Test cases for audio effects processing."""
    
    @pytest.fixture
    def audio_data(self):
        """Load test audio data."""
        import librosa
        y, sr = librosa.load(SAMPLE_FILE, sr=None)
        return y, sr
    
    def test_time_stretch(self, audio_data):
        """Test time stretching."""
        y, sr = audio_data
        processor = AudioEffectsProcessor(sr)
        
        # Test stretching to 1.5x length
        y_stretched = processor.time_stretch(y, sr, rate=1.5)
        assert len(y_stretched) > len(y) * 1.4  # Allow some tolerance
        
        # Test compressing to 0.75x length
        y_compressed = processor.time_stretch(y, sr, rate=0.75)
        assert len(y_compressed) < len(y) * 0.8  # Allow some tolerance
    
    def test_pitch_shift(self, audio_data):
        """Test pitch shifting."""
        y, sr = audio_data
        processor = AudioEffectsProcessor(sr)
        
        # Test shifting up 2 semitones
        y_shifted = processor.pitch_shift(y, sr, n_steps=2)
        assert len(y_shifted) == len(y)
        
        # Test shifting down 3 semitones
        y_shifted = processor.pitch_shift(y, sr, n_steps=-3)
        assert len(y_shifted) == len(y)
    
    def test_effects_chain(self, audio_data):
        """Test chaining multiple effects."""
        y, sr = audio_data
        processor = AudioEffectsProcessor(sr)
        
        # Create an effects chain
        processor.add_effect(EffectType.TIME_STRETCH, {'rate': 1.2})
        processor.add_effect(EffectType.PITCH_SHIFT, {'n_steps': 2})
        
        # Process audio
        y_processed = processor.process(y, sr)
        assert len(y_processed) > 0
        assert len(y_processed) > len(y) * 1.1  # Should be longer due to time stretch
    
    def test_noise_reduction(self, audio_data):
        """Test noise reduction."""
        y, sr = audio_data
        
        # Add some noise to the signal
        np.random.seed(42)
        noise = np.random.normal(0, 0.01, len(y))
        y_noisy = y + noise
        
        # Create noise profile from a segment of noise
        nr = NoiseReduction(sr)
        nr.learn_noise_profile(noise[:sr])  # Use first second as noise profile
        
        # Reduce noise
        y_denoised = nr.reduce_noise(y_noisy, sr, reduction_db=12.0)
        
        # Check that noise was reduced
        noise_before = np.mean(np.abs(noisy - y))
        noise_after = np.mean(np.abs(y_denoised - y))
        assert noise_after < noise_before * 0.7  # At least 30% noise reduction
    
    def test_click_removal(self, audio_data):
        """Test click and pop removal."""
        y, sr = audio_data
        
        # Add some clicks to the signal
        y_clicks = y.copy()
        click_indices = np.random.choice(len(y), size=10, replace=False)
        y_clicks[click_indices] = 0.5  # Add clicks
        
        # Remove clicks
        nr = NoiseReduction(sr)
        y_clean = nr.remove_clicks(y_clicks, sr)
        
        # Check that clicks were reduced
        click_energy = np.sum(np.abs(y_clicks[click_indices]))
        clean_energy = np.sum(np.abs(y_clean[click_indices]))
        assert clean_energy < click_energy * 0.5  # At least 50% reduction in click energy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
