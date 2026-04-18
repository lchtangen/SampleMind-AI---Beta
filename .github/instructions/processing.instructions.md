---
applyTo: "src/samplemind/core/processing/**/*.py"
---

# Audio Processing Instructions

- Realtime effects: `core/processing/realtime_effects.py` — 10 pedalboard effects chain
- Effects available: EQ, compressor, reverb, delay, chorus, distortion, limiter, gain, highpass, lowpass
- Serializable chain config for preset management
- Process files and in-memory buffers
- Auto categorizer, transient shaper, spectral morph, audio DNA all in `core/processing/`
- API endpoints at `/api/v1/processing/` — micro-timing, transient-shape, audio-dna, categorize, spectral-morph
- Always preserve original sample rate during processing
- Use numpy arrays for audio buffer operations
- pedalboard (Spotify) is the preferred effects library
