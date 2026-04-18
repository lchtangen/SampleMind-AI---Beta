---
name: pedalboard-effects
description: Spotify pedalboard 10-effect chain with numpy audio buffers
---

## Pedalboard Effects

### Location
`src/samplemind/core/processing/realtime_effects.py`

### 10 Effects Chain
1. EQ (parametric)
2. Compressor
3. Reverb
4. Delay
5. Chorus
6. Distortion
7. Limiter
8. Gain
9. Highpass filter
10. Lowpass filter

### Usage Pattern
```python
from pedalboard import Pedalboard, Reverb, Compressor, Gain
import numpy as np

board = Pedalboard([
    Compressor(threshold_db=-20, ratio=4),
    Reverb(room_size=0.5),
    Gain(gain_db=3.0),
])

# Process audio buffer
output = board(input_audio, sample_rate=44100)
```

### Rules
- Always preserve original sample rate during processing
- Use numpy arrays for audio buffer operations
- Serializable chain config for preset management
- Process both files and in-memory buffers
- API endpoints at `/api/v1/processing/`
- Validate audio format before applying effects
