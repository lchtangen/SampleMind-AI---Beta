---
applyTo: "src/samplemind/ai/classification/**/*.py,src/samplemind/ai/curation/**/*.py"
---

# AI Classification & Curation Instructions

- Ensemble classifier: `ai/classification/ensemble.py` — SVM + XGBoost + KNN soft-voting
- Genre classifier: `ai/classification/multi_label_genre.py` — 400+ genre taxonomy
- Mood detector: `ai/classification/mood_detector.py` — Russell circumplex model
- Instrument detector: `ai/classification/instrument_detector.py` — 128-class GM instruments
- Playlist generator: `ai/curation/playlist_generator.py` — energy arc + Camelot Wheel scoring
- Gap analyzer: `ai/curation/gap_analyzer.py` — library coverage + LiteLLM suggestions
- Similar sample: `ai/generation/similar_sample.py` — FAISS + 4 variation strategies
- All classifiers should accept numpy arrays and return typed results
- Use scikit-learn pipelines for preprocessing consistency
