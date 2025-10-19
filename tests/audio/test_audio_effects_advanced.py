import os
import numpy as np
import pytest
import soundfile as sf
from pathlib import Path
from scipy import signal, fft
import matplotlib.pyplot as plt

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from samplemind.audio.effects import AudioEffectsProcessor, EffectType

# Test parameters
SAMPLE_RATE = 44100
DURATION = 2.0  # seconds
FREQ = 440.0  # Hz
TEST_OUTPUT_DIR = Path(__file__).parent / "test_output"
TEST_OUTPUT_DIR.mkdir(exist_ok=True)

# Helper functions
def generate_test_signal(duration=DURATION, freq=FREQ, sample_rate=SAMPLE_RATE, noise_level=0.0):
    """Generate a test signal with optional noise."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = np.sin(2 * np.pi * freq * t)
    if noise_level > 0:
        signal += np.random.normal(0, noise_level, len(t))
    return signal

def analyze_frequency_content(y, sr, n_fft=2048):
    """Analyze frequency content of a signal."""
    D = np.abs(fft.fft(y, n=n_fft))
    freqs = fft.fftfreq(n_fft, 1/sr)
    return freqs[:n_fft//2], D[:n_fft//2]

class TestAudioEffectsProcessor:
    """Test the AudioEffectsProcessor class."""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh AudioEffectsProcessor instance for each test."""
        return AudioEffectsProcessor(sample_rate=SAMPLE_RATE)
    
    def test_time_stretch(self, processor):
        """Test time stretching functionality."""
        # Generate test signal
        y = generate_test_signal(duration=1.0)  # 1 second of 440Hz sine
        
        # Test stretching to 1.5x length
        y_stretched = processor.time_stretch(y, SAMPLE_RATE, rate=1.5)
        
        # Should be approximately 1.5x longer
        assert len(y_stretched) == int(len(y) * 1.5)
        
        # Frequency content should be the same
        f_orig, Pxx_orig = signal.welch(y, SAMPLE_RATE)
        f_stretch, Pxx_stretch = signal.welch(y_stretched, SAMPLE_RATE)
        
        # Find peak frequency
        peak_orig = f_orig[np.argmax(Pxx_orig)]
        peak_stretch = f_stretch[np.argmax(Pxx_stretch)]
        
        # Peak frequency should be similar (within 5%)
        assert abs(peak_orig - peak_stretch) < (0.05 * peak_orig)
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_stretch_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_stretch_processed.wav", y_stretched, SAMPLE_RATE)
    
    def test_pitch_shift(self, processor):
        """Test pitch shifting functionality."""
        # Generate test signal
        y = generate_test_signal(freq=440.0)  # A4 note
        
        # Shift up a perfect fifth (7 semitones)
        y_shifted = processor.pitch_shift(y, SAMPLE_RATE, n_steps=7.0)
        
        # Frequency should be higher (440 * 2^(7/12) ≈ 659.25 Hz)
        f, Pxx = signal.welch(y_shifted, SAMPLE_RATE)
        peak_freq = f[np.argmax(Pxx)]
        
        # Check if peak is near expected frequency (within 2%)
        expected_freq = 440.0 * (2 ** (7/12))
        assert abs(peak_freq - expected_freq) < (0.02 * expected_freq)
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_pitch_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_pitch_shifted.wav", y_shifted, SAMPLE_RATE)
    
    def test_reverb_effect(self, processor):
        """Test reverb effect."""
        # Generate test signal (short click)
        y = np.zeros(SAMPLE_RATE)  # 1 second of silence
        y[1000] = 1.0  # Impulse at 1ms
        
        # Apply reverb
        y_reverb = processor.apply_reverb(
            y, SAMPLE_RATE,
            room_size=0.8,
            damping=0.5,
            wet_level=0.5,
            dry_level=0.5
        )
        
        # Verify reverb tail
        energy_original = np.sum(y[1000:]**2)
        energy_reverb = np.sum(y_reverb[1000:]**2)
        assert energy_reverb > energy_original * 10  # Should have significant reverb
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_reverb_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_reverb_processed.wav", y_reverb, SAMPLE_RATE)
    
    def test_delay_effect(self, processor):
        """Test delay/echo effect."""
        # Generate test signal (short click)
        y = np.zeros(SAMPLE_RATE)  # 1 second of silence
        y[1000] = 1.0  # Impulse at 1ms
        
        # Apply delay
        delay_time = 0.3  # 300ms delay
        y_delayed = processor.apply_delay(
            y, SAMPLE_RATE,
            delay_seconds=delay_time,
            feedback=0.5,
            mix=0.5
        )
        
        # Find peaks in the output
        peaks, _ = signal.find_peaks(np.abs(y_delayed), height=0.1)
        
        # Should have at least the original and one echo
        assert len(peaks) >= 2
        
        # Check echo timing (should be ~300ms apart)
        delay_samples = int(delay_time * SAMPLE_RATE)
        peak_diff = np.diff(peaks)
        assert np.any(np.abs(peak_diff - delay_samples) < (0.05 * delay_samples))  # Within 5%
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_delay_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_delay_processed.wav", y_delayed, SAMPLE_RATE)
    
    def test_compression_effect(self, processor):
        """Test dynamic range compression."""
        # Generate test signal with varying amplitude
        t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION))
        y = np.sin(2 * np.pi * FREQ * t) * np.linspace(0.1, 1.0, len(t))
        
        # Apply compression
        y_compressed = processor.apply_compression(
            y, SAMPLE_RATE,
            threshold=-20.0,  # dB
            ratio=4.0,        # 4:1 compression
            attack=0.01,      # 10ms attack
            release=0.1       # 100ms release
        )
        
        # Calculate dynamic range (peak-to-RMS ratio)
        def dynamic_range(signal):
            return np.max(np.abs(signal)) / np.sqrt(np.mean(signal**2))
        
        dr_original = dynamic_range(y)
        dr_compressed = dynamic_range(y_compressed)
        
        # Compressed signal should have lower dynamic range
        assert dr_compressed < dr_original * 0.8  # At least 20% reduction
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_comp_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_comp_compressed.wav", y_compressed, SAMPLE_RATE)
    
    def test_effect_chaining(self, processor):
        """Test chaining multiple effects."""
        # Generate test signal
        y = generate_test_signal()
        
        # Create an effects chain
        processor.add_effect(EffectType.PITCH_SHIFT, {'n_steps': 5.0})  # Up a fourth
        processor.add_effect(EffectType.REVERB, {'wet_level': 0.3, 'room_size': 0.6})
        processor.add_effect(EffectType.DELAY, {'delay_seconds': 0.2, 'mix': 0.2})
        
        # Process the signal
        y_processed = processor.process(y, SAMPLE_RATE)
        
        # Basic validation
        assert len(y_processed) > 0
        assert not np.allclose(y_processed, y)
        
        # Check if pitch was shifted
        f_orig, Pxx_orig = signal.welch(y, SAMPLE_RATE)
        f_proc, Pxx_proc = signal.welch(y_processed, SAMPLE_RATE)
        
        peak_orig = f_orig[np.argmax(Pxx_orig)]
        peak_proc = f_proc[np.argmax(Pxx_proc)]
        
        # Should be shifted up by approximately 5 semitones
        expected_ratio = 2 ** (5/12)
        actual_ratio = peak_proc / peak_orig
        assert abs(actual_ratio - expected_ratio) < 0.05  # Within 5%
        
        # Save test files for manual inspection
        if not os.environ.get("CI"):
            sf.write(TEST_OUTPUT_DIR / "test_chain_original.wav", y, SAMPLE_RATE)
            sf.write(TEST_OUTPUT_DIR / "test_chain_processed.wav", y_processed, SAMPLE_RATE)


if __name__ == "__main__":
    # Generate test plots if run directly
    import matplotlib.pyplot as plt
    
    # Create test signals
    t = np.linspace(0, 1.0, SAMPLE_RATE)
    y_sine = np.sin(2 * np.pi * 440 * t)
    y_noise = np.random.normal(0, 0.1, len(t))
    
    # Plot example
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t[:1000], y_sine[:1000])
    plt.title("Clean 440Hz Sine Wave")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    plt.subplot(2, 1, 2)
    plt.plot(t[:1000], y_sine[:1000] + y_noise[:1000])
    plt.title("Noisy Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    plt.tight_layout()
    plt.savefig(TEST_OUTPUT_DIR / "test_signals_advanced.png")
    plt.close()
    
    print(f"Test signals and plots saved to {TEST_OUTPUT_DIR}")
    print("Run 'pytest test_audio_effects_advanced.py -v' to execute tests.")
