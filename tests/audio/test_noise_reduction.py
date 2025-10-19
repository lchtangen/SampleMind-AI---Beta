import os
import numpy as np
import pytest
import soundfile as sf
from pathlib import Path
from scipy import signal

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from samplemind.audio.effects import NoiseReduction, AudioEffectsProcessor
from samplemind.audio.processor import AudioProcessor

# Test parameters
SAMPLE_RATE = 44100
DURATION = 2.0  # seconds
FREQ = 440.0  # Hz
NOISE_LEVEL = 0.1
CLICK_COUNT = 5

# Create test directory for output files
TEST_OUTPUT_DIR = Path(__file__).parent / "test_output"
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

@pytest.fixture
def clean_sine_wave():
    """Generate a clean sine wave for testing."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    return np.sin(2 * np.pi * FREQ * t)

@pytest.fixture
def noisy_signal(clean_sine_wave):
    """Generate a noisy signal by adding white noise."""
    noise = np.random.normal(0, NOISE_LEVEL, len(clean_sine_wave))
    return clean_sine_wave + noise

@pytest.fixture
def clicky_signal(clean_sine_wave):
    """Generate a signal with artificial clicks."""
    signal = clean_sine_wave.copy()
    click_indices = np.random.randint(0, len(signal), CLICK_COUNT)
    signal[click_indices] += 0.5  # Add clicks
    return signal

@pytest.fixture
def sibilant_signal():
    """Generate a signal with sibilant sounds."""
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    # Create a sibilant-like signal (high-frequency content)
    sibilant = np.sin(2 * np.pi * 6000 * t) * 0.5
    # Add some modulation
    sibilant *= (1 + 0.5 * np.sin(2 * np.pi * 5 * t))
    return sibilant

class TestNoiseReduction:
    """Test the NoiseReduction class functionality."""
    
    def test_learn_noise_profile(self, noisy_signal):
        """Test learning a noise profile."""
        nr = NoiseReduction(SAMPLE_RATE)
        nr.learn_noise_profile(noisy_signal[:1000])  # Use first 1000 samples as noise
        
        assert nr.noise_profile is not None
        assert 'mean' in nr.noise_profile
        assert 'std' in nr.noise_profile
        assert 'psd_mean' in nr.noise_profile
        
    def test_spectral_reduction(self, noisy_signal, clean_sine_wave):
        """Test spectral subtraction noise reduction."""
        nr = NoiseReduction(SAMPLE_RATE)
        
        # Learn noise from first 100ms
        noise_segment = noisy_signal[:int(0.1 * SAMPLE_RATE)]
        nr.learn_noise_profile(noise_segment)
        
        # Process the signal
        denoised = nr.reduce_noise(
            noisy_signal, 
            method='spectral',
            reduction_db=12.0
        )
        
        # Verify the output
        assert len(denoised) == len(noisy_signal)
        assert not np.allclose(denoised, noisy_signal)  # Should be different
        
        # Check if noise was reduced (RMS of difference should be lower)
        original_noise = np.sqrt(np.mean((noisy_signal - clean_sine_wave) ** 2))
        processed_noise = np.sqrt(np.mean((denoised - clean_sine_wave) ** 2))
        
        assert processed_noise < original_noise * 0.8  # At least 20% reduction
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):  # Don't save files in CI
            sf.write(TEST_OUTPUT_DIR / "test_spectral_original.wav", noisy_signal, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_spectral_denoised.wav", denoised, SAMPLE_RATE)
    
    def test_wiener_reduction(self, noisy_signal):
        """Test Wiener filter noise reduction."""
        nr = NoiseReduction(SAMPLE_RATE)
        
        # Learn noise from first 100ms
        noise_segment = noisy_signal[:int(0.1 * SAMPLE_RATE)]
        nr.learn_noise_profile(noise_segment)
        
        # Process the signal
        denoised = nr.reduce_noise(
            noisy_signal, 
            method='wiener',
            reduction_db=12.0
        )
        
        # Basic validation
        assert len(denoised) == len(noisy_signal)
        assert not np.allclose(denoised, noisy_signal)
        
    def test_click_removal(self, clicky_signal):
        """Test click/pop removal."""
        nr = NoiseReduction(SAMPLE_RATE)
        
        # Process with different methods
        for method in ['median', 'linear', 'spline']:
            cleaned = nr.remove_clicks(
                clicky_signal,
                threshold=0.1,
                method=method
            )
            
            # Basic validation
            assert len(cleaned) == len(clicky_signal)
            
            # Save test files for manual inspection
            if not os.environ.get("CI"):
                sf.write(
                    TEST_OUTPUT_DIR / f"test_clicks_{method}.wav", 
                    cleaned, 
                    SAMPLE_RATE
                )
    
    def test_de_essing(self, sibilant_signal):
        """Test de-essing functionality."""
        nr = NoiseReduction(SAMPLE_RATE)
        
        # Apply de-essing
        deessed = nr.de_ess(
            sibilant_signal,
            threshold=0.15,
            ratio=6.0
        )
        
        # Basic validation
        assert len(deessed) == len(sibilant_signal)
        
        # Check if high frequencies were reduced
        f_orig, Pxx_orig = signal.welch(sibilant_signal, SAMPLE_RATE)
        f_deess, Pxx_deess = signal.welch(deessed, SAMPLE_RATE)
        
        # Get energy in sibilant range (4-10kHz)
        mask = (f_orig >= 4000) & (f_orig <= 10000)
        energy_orig = np.trapz(Pxx_orig[mask], f_orig[mask])
        energy_deess = np.trapz(Pxx_deess[mask], f_orig[mask])
        
        # De-essed signal should have less high-frequency energy
        assert energy_deess < energy_orig * 0.8
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_deess_original.wav", sibilant_signal, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_deess_processed.wav", deessed, SAMPLE_RATE)
    
    def test_stereo_processing(self):
        """Test processing of stereo signals."""
        # Create stereo signal (left and right channels)
        t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
        left = np.sin(2 * np.pi * 440 * t)
        right = np.sin(2 * np.pi * 660 * t)
        stereo = np.column_stack((left, right))
        
        # Add noise
        noise = np.random.normal(0, 0.1, stereo.shape)
        noisy_stereo = stereo + noise
        
        # Process
        nr = NoiseReduction(SAMPLE_RATE)
        nr.learn_noise_profile(noise[:, 0])  # Learn from one channel
        
        # Test different methods
        denoised = nr.reduce_noise(noisy_stereo, method='spectral')
        
        # Verify output shape and basic properties
        assert denoised.shape == noisy_stereo.shape
        assert not np.allclose(denoised, noisy_stereo)
        
        # Check that left and right channels were processed independently
        assert not np.allclose(denoised[:, 0], denoised[:, 1])


class TestAudioEffectsIntegration:
    """Test integration of audio effects with the processor."""
    
    def test_effects_chain(self, clean_sine_wave):
        """Test chaining multiple effects."""
        # Create processor with effects
        processor = AudioProcessor(sample_rate=SAMPLE_RATE)
        
        # Add effects
        processor.add_effect('pitch_shift', {'n_steps': 2.0})  # Shift up a whole step
        processor.add_effect('reverb', {'room_size': 0.5, 'wet_level': 0.3})
        
        # Process audio
        processed = processor.process_effects(clean_sine_wave, SAMPLE_RATE)
        
        # Basic validation
        assert len(processed) > 0
        assert not np.allclose(processed, clean_sine_wave)
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_effects_original.wav", clean_sine_wave, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_effects_processed.wav", processed, SAMPLE_RATE)
    
    def test_batch_processing(self, tmp_path):
        """Test batch processing of multiple files."""
        # Create test files
        test_files = []
        for i in range(3):
            t = np.linspace(0, 1.0, SAMPLE_RATE)
            y = np.sin(2 * np.pi * (440 + i * 100) * t)
            path = tmp_path / f"test_{i}.wav"
            sf.write(path, y, SAMPLE_RATE)
            test_files.append(str(path))
        
        # Process batch
        processor = AudioProcessor(sample_rate=SAMPLE_RATE)
        processor.add_effect('pitch_shift', {'n_steps': -2.0})  # Shift down a whole step
        
        results = []
        for file in test_files:
            y, sr = sf.read(file)
            processed = processor.process_effects(y, sr)
            results.append(processed)
        
        # Verify results
        assert len(results) == 3
        for i, result in enumerate(results):
            assert len(result) > 0
            y, _ = sf.read(test_files[i])
            assert not np.allclose(result, y)  # Should be different due to pitch shift


if __name__ == "__main__":
    # Generate test signals if run directly
    import matplotlib.pyplot as plt
    
    # Create test signals
    t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), endpoint=False)
    clean = np.sin(2 * np.pi * FREQ * t)
    noisy = clean + np.random.normal(0, NOISE_LEVEL, len(t))
    
    # Plot example
    plt.figure(figsize=(12, 6))
    plt.plot(t[:1000], clean[:1000], label='Clean')
    plt.plot(t[:1000], noisy[:1000], alpha=0.6, label='Noisy')
    plt.legend()
    plt.title("Test Signals")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(TEST_OUTPUT_DIR / "test_signals.png")
    plt.close()
    
    print(f"Test signals saved to {TEST_OUTPUT_DIR}")
    print("Run 'pytest test_noise_reduction.py -v' to execute tests.")
