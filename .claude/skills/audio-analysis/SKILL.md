---
name: audio-analysis
description: Audio analysis with librosa, CLAP embeddings, and 4-level analysis pipeline
---

## Audio Analysis

### Analysis Levels
1. **BASIC:** BPM, key, duration (librosa)
2. **STANDARD:** + MFCC, chroma, spectral centroid/bandwidth/rolloff
3. **DETAILED:** + harmonic/percussive separation, onset detection
4. **PROFESSIONAL:** + AI classification (SVM+XGBoost+KNN), CLAP 512-dim embeddings

### Engine Location
- `src/samplemind/core/engine/audio_engine.py` — main analysis engine

### CLAP Embeddings
```python
# 512-dim embeddings using laion/clap-htsat-unfused
from samplemind.core.search.faiss_index import get_index
index = get_index(auto_load=True)
results = index.search_text("dark trap kick", top_k=20)
```

### Rules
- Default sample rate: 44100 Hz — preserve original when possible
- Audio I/O via `soundfile` (WAV, FLAC, OGG)
- All operations: `async def` or `ThreadPoolExecutor`
- Lazy-import: torch, librosa, transformers, demucs
- Use numpy arrays for audio buffer operations
- Validate file exists and format before processing
