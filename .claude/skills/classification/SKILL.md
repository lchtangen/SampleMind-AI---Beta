---
name: classification
description: Ensemble SVM+XGBoost+KNN classifier with 400+ genres and Russell mood model
---

## AI Classification

### Classifiers
| Module | Purpose |
|--------|---------|
| `ai/classification/ensemble.py` | SVM + XGBoost + KNN soft-voting |
| `ai/classification/multi_label_genre.py` | 400+ genre taxonomy |
| `ai/classification/mood_detector.py` | Russell circumplex model (valence × arousal) |
| `ai/classification/instrument_detector.py` | 128-class General MIDI instruments |

### Ensemble Pattern
```python
from samplemind.ai.classification.ensemble import EnsembleClassifier

classifier = EnsembleClassifier()
predictions = classifier.predict(audio_features)
# Returns: {"genre": "trap", "mood": "dark", "instrument": "808", "confidence": 0.87}
```

### Curation
- `ai/curation/playlist_generator.py` — energy arc + Camelot Wheel key scoring
- `ai/curation/gap_analyzer.py` — library coverage analysis + LiteLLM suggestions

### Similar Sample Generation
`ai/generation/similar_sample.py` — FAISS + 4 variation strategies:
1. Pitch shift
2. Time stretch
3. Spectral morphing
4. Style transfer (demucs-based)

### Rules
- Accept numpy arrays, return typed results
- Use scikit-learn pipelines for preprocessing
- Lazy-import heavy ML libraries
