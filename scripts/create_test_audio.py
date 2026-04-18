"""
SampleMind AI — Test Audio File Generator
===========================================

Creates a short synthetic WAV file for use in unit and integration tests.

Output:
    ``test_audio.wav`` in the current working directory — a 1-second,
    44.1 kHz, 16-bit mono WAV containing a pure 440 Hz sine wave (A4 note).

Usage:
    python scripts/create_test_audio.py

Dependencies:
    numpy, scipy (both are project dependencies).
"""

from pathlib import Path

import numpy as np
import scipy.io.wavfile as wav

# Create 1 second of silence (or sine wave)
sample_rate = 44100
duration = 1.0
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # A4 note

output_path = Path("test_audio.wav")
wav.write(output_path, sample_rate, (audio * 32767).astype(np.int16))
print(f"Created {output_path}")
