
import numpy as np
import pytest
from samplemind.core.processing.realtime_spectral import RealtimeSpectral, SpectralFrame

def test_realtime_spectral_sine_wave():
    """Test spectral analysis on a pure sine wave."""
    sample_rate = 44100
    frequency = 440.0 # A4

    # Generate chunks
    analyzer = RealtimeSpectral(sample_rate=sample_rate, fft_size=2048)

    # Create a sine wave chunk exactly matching fft_size
    t = np.linspace(0, analyzer.fft_size/sample_rate, analyzer.fft_size, endpoint=False)
    sine_wave = 0.5 * np.sin(2 * np.pi * frequency * t)

    frame = analyzer.process_chunk(sine_wave)

    # Check peak frequency
    # Resolution = sample_rate / fft_size = 44100 / 2048 ~= 21.5 Hz
    # Peak should be close to 440
    print(f"Peak Frequency: {frame.peak_frequency_hz} Hz")

    # Allow some margin due to bin width
    assert abs(frame.peak_frequency_hz - frequency) < 25.0

    # Check pitch detection
    if frame.pitch_hz:
        print(f"Detected Pitch: {frame.pitch_hz} Hz")
        assert abs(frame.pitch_hz - frequency) < 5.0

if __name__ == "__main__":
    test_realtime_spectral_sine_wave()
