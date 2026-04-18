---
name: pedalboard-effects
description: Guide for audio effects processing with pedalboard (Spotify). Use when implementing or modifying audio effects.
---

## Pedalboard Audio Effects

### Location
`src/samplemind/core/processing/realtime_effects.py`

### Available Effects
1. **EQ** — Parametric equalizer (frequency, gain_db, q)
2. **Compressor** — Dynamic range compression (threshold, ratio, attack, release)
3. **Reverb** — Room simulation (room_size, damping, wet_level)
4. **Delay** — Echo effect (delay_seconds, feedback, mix)
5. **Chorus** — Modulation (rate_hz, depth, mix)
6. **Distortion** — Overdrive/saturation (drive_db)
7. **Limiter** — Peak limiting (threshold_db, release_ms)
8. **Gain** — Volume adjustment (gain_db)
9. **Highpass** — High-pass filter (cutoff_hz)
10. **Lowpass** — Low-pass filter (cutoff_hz)

### Usage
```python
from samplemind.core.processing.realtime_effects import EffectsChain, EffectConfig

chain = EffectsChain()
chain.add_effect(EffectConfig(type="reverb", params={"room_size": 0.8, "wet_level": 0.3}))
chain.add_effect(EffectConfig(type="compressor", params={"threshold": -20, "ratio": 4}))

# Process file
output = chain.process_file("input.wav", "output.wav")

# Process buffer
output_buffer = chain.process_buffer(audio_array, sample_rate=44100)
```
