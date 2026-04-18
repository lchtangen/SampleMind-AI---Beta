---
name: faiss-search
description: Guide for semantic audio search with FAISS and CLAP embeddings. Use when implementing or modifying search functionality.
---

## FAISS Semantic Search

### Architecture
- **Index:** `src/samplemind/core/search/faiss_index.py` — IndexFlatIP (512-dim)
- **Embedder:** CLAPEmbedder using `laion/clap-htsat-unfused`
- **Memory:** `src/samplemind/ai/agents/memory.py` — FAISS-backed agent memory

### Usage Patterns
```python
# Get or create index
from samplemind.core.search.faiss_index import get_index
index = get_index(auto_load=True)

# Text search
results = index.search_text("dark trap kick", top_k=20)

# Audio search
results = index.search_audio("/path/to/sample.wav", top_k=10)

# Add to index
index.add_sample("/path/to/sample.wav", metadata={"bpm": 140})
```

### CLI Commands
```bash
# Build index
python -m samplemind.interfaces.cli.commands.search index --path /samples/

# Search
python -m samplemind.interfaces.cli.commands.search search "dark ambient pad"
```

### Key Facts
- Inner product similarity on L2-normalized vectors = cosine similarity
- 512-dimensional CLAP embeddings
- Always normalize before adding to index
