---
name: audio-analysis
description: Guide for implementing audio analysis features using librosa, CLAP, and the audio engine. Use when working on BPM detection, key detection, spectral analysis, or audio feature extraction.
---

## Audio Analysis Implementation

When implementing audio analysis features:

1. **Use the existing engine** — `src/samplemind/core/engine/audio_engine.py`
2. **Feature extraction** — librosa for BPM, key, MFCC, chroma, spectral features
3. **CLAP embeddings** — 512-dim vectors from `laion/clap-htsat-unfused`
4. **Always async** — wrap librosa calls in ThreadPoolExecutor

### Analysis Levels
- BASIC: BPM, key, duration (<0.5s)
- STANDARD: + MFCC, chroma, spectral (<1s)
- DETAILED: + harmonic/percussive separation (<2s)
- PROFESSIONAL: + AI analysis, CLAP classification, embeddings (<5s)

### Pattern
```python
from samplemind.core.engine.audio_engine import AudioEngine

engine = AudioEngine()
result = await engine.analyze(file_path, level="STANDARD")
```

### Libraries
- `librosa` — Core feature extraction
- `soundfile` — Audio I/O
- `numpy` — Array operations
- `torch` + `transformers` — CLAP model
