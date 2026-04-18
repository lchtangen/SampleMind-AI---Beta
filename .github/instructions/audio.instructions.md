---
applyTo: "src/samplemind/core/engine/**/*.py,src/samplemind/ai/**/*.py"
---

# Audio Analysis Instructions

- Audio engine: `core/engine/audio_engine.py` (LibROSA-based)
- Analysis levels: BASIC (BPM/key/duration), STANDARD (+MFCC/chroma/spectral), DETAILED (+harmonic/percussive), PROFESSIONAL (+AI/CLAP/embeddings)
- Audio I/O: `soundfile` for WAV/FLAC/OGG read/write
- Feature extraction: librosa for BPM, key, MFCC, chroma, spectral features
- Stem separation: demucs v4 `htdemucs_6s` model (6-stem)
- MIDI transcription: basic-pitch
- Effects: pedalboard (Spotify) — `core/processing/realtime_effects.py`
- Transcription: faster-whisper — `ai/transcription/whisper_transcriber.py`
- Embeddings: CLAP `laion/clap-htsat-unfused` (512-dim) for semantic search
- Classification: SVM + XGBoost + KNN soft-voting ensemble
- All audio operations must be async or wrapped in ThreadPoolExecutor
- Sample rates: default 44100 Hz, always preserve original when possible
