
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
