"""
Unit tests for samplemind.core.processing.realtime_spectral

Module under test:
    samplemind.core.processing.realtime_spectral
        — RealtimeSpectral (FFT-based real-time spectral analyser)

Key test scenarios:
    - A pure 440 Hz sine wave processed through a 2048-point FFT at
      44 100 Hz sample rate.  Asserts that:
        * peak_frequency_hz is within ±25 Hz of 440 Hz (one FFT-bin
          tolerance at ~21.5 Hz resolution).
        * pitch_hz, when detected, is within ±5 Hz of 440 Hz.
"""
import numpy as np

from samplemind.core.processing.realtime_spectral import RealtimeSpectral


def test_realtime_spectral_sine_wave():
    """Test spectral analysis on a pure sine wave."""
    sample_rate = 44100
    frequency = 440.0  # A4

    # Generate chunks
    analyzer = RealtimeSpectral(sample_rate=sample_rate, fft_size=2048)

    # Create a sine wave chunk exactly matching fft_size
    t = np.linspace(
        0, analyzer.fft_size / sample_rate, analyzer.fft_size, endpoint=False
    )
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
