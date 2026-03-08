# Phase 15 Execution Plan: Semantic Audio Search

**Phase:** 15
**Status:** 📋 Planned
**Focus:** Vector Embeddings, Natural Language Search, CLAP Models
**Start Date:** February 3, 2026

## 1. Objective

Implement **Semantic Audio Search** (Roadmap Item #6). This feature moves beyond simple metadata tagging (BPM, Key) to allow users to search for sounds using natural language descriptions (e.g., "give me something that sounds like underwater bubbles" or "aggressive industrial percussion").

## 2. Key Features

### 2.1 Vector Embedding Engine

- **Model Integration**: Use a lightweight pre-trained audio-text model (like CLAP or a distilled version) to generate vector embeddings for audio files.
- **Database**: Integrate with a vector store (ChromaDB or FAISS) to index the sample library.

### 2.2 Search Interface

- **Natural Language Query**: "Find a sad piano loop" -> Converts text to vector -> Finds nearest audio vectors.
- **Audio-to-Audio Search**: "Find samples that sound like _this_ file".

### 2.3 CLI Integration

- New command: `sm search "query string"`
- New menu option within the CLI tool.

## 3. Implementation Steps

1. **Research & Select Model**: Evaluate `laion/clap-htsat-unfused` vs. other Hugging Face models for local performance (must run on CPU/standard GPU).
2. **Create `VectorSearchEngine`**:
   - `index_directory(path)`: Scans audio, generates embeddings, saves to DB.
   - `search(text_query)`: Returns list of file paths sorted by similarity.
3. **Optimize Performance**: Ensure indexing doesn't take forever for large libraries (use batching).

## 4. Risks & Mitigations

- **Model Size**: Some CLAP models are large. Need to ensure we pick a version suitable for local deployment.
- **Dependency Hell**: Adding `torch` or `transformers` can bloat the environment. Will segregate if necessary or use ONNX.

## 5. Success Criteria

- [ ] User can type "808 bass" and get 808s even if filenames don't say "808".
- [ ] Search returns results in < 2 seconds for a library of 10,000 samples.
