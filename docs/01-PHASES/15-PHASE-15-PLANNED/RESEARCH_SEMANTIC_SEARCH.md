# Phase 15 Research: Semantic Search Models

**Date:** February 3, 2026
**Status:** ✅ Completed

## 1. Goal

Enable natural language search for audio files (e.g., "fast drum beat", "sad piano loop") using vector embeddings.

## 2. Model Candidates

### A. CLAP (Contrastive Language-Audio Pretraining)

- **Source**: Microsoft / LAION
- **Mechanism**: Jointly trained audio and text encoders. Maps audio and text to the same vector space.
- **Pros**:
  - State-of-the-art for zero-shot audio classification and retrieval.
  - Native support in Hugging Face `transformers` (`ClapModel`).
  - Directly optimized for the "text-to-audio" retrieval task.
- **Cons**:
  - Model can be large (~500MB+ for base).
  - Inference time might be slower on CPU.

### B. Audio Spectrogram Transformer (AST)

- **Source**: MIT
- **Mechanism**: Vision Transformer applied to spectrograms.
- **Pros**: Excellent classification.
- **Cons**: Not natively bi-modal (audio+text). Requires a separate text encoder mapping, which is harder to align for arbitrary queries.

### C. PANNs (Pretrained Audio Neural Networks)

- **Source**: ByteDance
- **Pros**: Lightweight, fast.
- **Cons**: Primarily for tagging (classification), not open-ended semantic search embedding.

## 3. Selected Strategy: CLAP (via Hugging Face)

We will use `laion/clap-htsat-unfused` or a similar variant available in `transformers`.

**Workflow:**

1.  **Indexing**:
    - Load Audio -> Resample -> `ClapAudioModel` -> Audio Embedding (Vector).
    - Store Vector + Metadata in `ChromaDB`.
2.  **Searching**:
    - User Query (Text) -> `ClapTextModel` -> Text Embedding (Vector).
    - `ChromaDB.query()` -> Nearest Audio Neighbors.

## 4. Vector Database: ChromaDB

- **Status**: Already in `pyproject.toml`.
- **Usage**: Local file-based storage (persistent).
- **Collection**: `samplemind_audio_embeddings`.

## 5. Implementation Plan

1.  Create `src/samplemind/core/search/vector_engine.py`.
2.  Class `VectorSearchEngine`.
3.  Methods:
    - `initialize_model()`: Lazy load CLAP.
    - `generate_embedding(audio_path)`: Return numpy vector.
    - `index_file(path)`: Add to DB.
    - `search(text)`: Query DB.
