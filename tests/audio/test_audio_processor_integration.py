"""
Integration tests for the AudioProcessor class with effects and noise reduction.
"""
import os
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from samplemind.audio.processor import AudioProcessor, AudioFormat
from samplemind.audio.effects import EffectType

# Test audio files directory
TEST_AUDIO_DIR = Path(__file__).parent.parent.parent / "test_audio_samples"
SAMPLE_FILE = TEST_AUDIO_DIR / "test_chord_120bpm.wav"
NOISE_FILE = TEST_AUDIO_DIR / "test_noise.wav"
VOCAL_FILE = TEST_AUDIO_DIR / "test_vocal.wav"

# Skip tests if test audio files are not available
pytestmark = pytest.mark.skipif(
    not all(f.exists() for f in [SAMPLE_FILE, NOISE_FILE, VOCAL_FILE]),
    reason="Test audio files not found"
)

class TestAudioProcessorIntegration:
    """Integration tests for AudioProcessor with effects and noise reduction."""
    
    @pytest.fixture
    def processor(self):
        """Create a new AudioProcessor instance for each test."""
        return AudioProcessor(sample_rate=44100, enable_gpu=False)
    
    def test_effects_chain(self, processor, tmp_path):
        """Test applying multiple effects in sequence."""
        # Load test audio
        y, sr = processor.load_audio(SAMPLE_FILE)
        
        # Add effects to the chain
        processor.add_effect(EffectType.TIME_STRETCH, {"rate": 1.2})
        processor.add_effect(EffectType.PITCH_SHIFT, {"n_steps": 2})
        
        # Process audio
        processed = processor.process_effects(y, sr)
        
        # Verify the output
        assert len(processed) > 0
        assert not np.array_equal(processed, y)  # Should be different from original
        
        # Save the result for manual verification
        output_path = tmp_path / "processed_effects.wav"
        sf.write(output_path, processed, sr)
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    
    def test_noise_reduction(self, processor, tmp_path):
        """Test noise reduction with learned noise profile."""
        # Load noise profile from noise-only segment
        noise, sr = processor.load_audio(NOISE_FILE)
        processor.learn_noise_profile(noise[:sr*2])  # Use first 2 seconds as noise profile
        
        # Load noisy audio (in a real test, this would be a file with actual noise)
        y, _ = processor.load_audio(SAMPLE_FILE)
        
        # Add some artificial noise
        np.random.seed(42)
        noise_amplitude = 0.1 * np.max(np.abs(y))
        noisy = y + noise_amplitude * np.random.normal(0, 1, len(y))
        
        # Reduce noise
        denoised = processor.reduce_noise(noisy, reduction_db=12.0)
        
        # Verify noise was reduced
        noise_before = np.mean(np.abs(noisy - y))
        noise_after = np.mean(np.abs(denoised - y))
        assert noise_after < noise_before * 0.7  # At least 30% noise reduction
        
        # Save results for manual verification
        noisy_path = tmp_path / "noisy.wav"
        denoised_path = tmp_path / "denoised.wav"
        sf.write(noisy_path, noisy, sr)
        sf.write(denoised_path, denoised, sr)
    
    def test_click_removal(self, processor, tmp_path):
        """Test click and pop removal."""
        # Load audio
        y, sr = processor.load_audio(SAMPLE_FILE)
        
        # Add artificial clicks
        y_clicks = y.copy()
        click_indices = np.random.choice(len(y), size=min(100, len(y)//1000), replace=False)
        y_clicks[click_indices] = 0.5 * np.max(np.abs(y))  # Add clicks at 50% of max amplitude
        
        # Remove clicks
        cleaned = processor.remove_clicks(y_clicks, sr)
        
        # Verify clicks were reduced
        click_energy = np.sum(np.abs(y_clicks[click_indices] - y[click_indices]))
        clean_energy = np.sum(np.abs(cleaned[click_indices] - y[click_indices]))
        assert clean_energy < click_energy * 0.5  # At least 50% reduction in click energy
        
        # Save results for manual verification
        clicks_path = tmp_path / "with_clicks.wav"
        cleaned_path = tmp_path / "cleaned.wav"
        sf.write(clicks_path, y_clicks, sr)
        sf.write(cleaned_path, cleaned, sr)
    
    def test_de_essing(self, processor, tmp_path):
        """Test de-essing on vocal audio."""
        # Skip if vocal file is not available
        if not VOCAL_FILE.exists():
            pytest.skip("Vocal test file not found")
        
        # Load vocal audio
        y, sr = processor.load_audio(VOCAL_FILE)
        
        # Apply de-essing
        de_essed = processor.de_ess(y, sr, threshold=0.15, ratio=4.0)
        
        # Verify the output
        assert len(de_essed) == len(y)
        
        # Save results for manual verification
        original_path = tmp_path / "original_vocal.wav"
        de_essed_path = tmp_path / "de_essed.wav"
        sf.write(original_path, y, sr)
        sf.write(de_essed_path, de_essed, sr)
    
    def test_batch_processing_with_effects(self, processor, tmp_path):
        """Test batch processing with effects applied."""
        # Create a test directory with multiple audio files
        test_dir = tmp_path / "test_audio"
        test_dir.mkdir()
        
        # Create some test files
        y, sr = processor.load_audio(SAMPLE_FILE)
        for i in range(3):
            sf.write(test_dir / f"test_{i}.wav", y, sr)
        
        # Add some effects
        processor.add_effect(EffectType.PITCH_SHIFT, {"n_steps": 2})
        
        # Process the batch
        output_dir = tmp_path / "output"
        results = processor.process_batch(
            input_paths=str(test_dir),
            output_dir=str(output_dir),
            output_format=AudioFormat.WAV,
            overwrite=True
        )
        
        # Verify results
        assert len(results) == 3
        for result in results:
            assert result["status"] == "completed"
            assert Path(result["output_path"]).exists()
            assert "processing_time" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
