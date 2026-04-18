---
name: faiss-search
description: FAISS IndexFlatIP semantic search with 512-dim CLAP embeddings
---

## FAISS Semantic Search

### Index
- Type: `IndexFlatIP` (inner product on normalized vectors = cosine similarity)
- Dimensions: 512 (CLAP embeddings from `laion/clap-htsat-unfused`)
- Location: `src/samplemind/core/search/faiss_index.py`

### Usage
```python
from samplemind.core.search.faiss_index import get_index

index = get_index(auto_load=True)

# Text search
results = index.search_text("dark trap kick", top_k=20)

# Audio search
results = index.search_audio("/path/to/sample.wav", top_k=10)

# Add vectors (must normalize first)
import numpy as np
vec = vec / np.linalg.norm(vec)
index.add(vec, metadata={"filename": "kick.wav"})
```

### CLI
- `interfaces/cli/commands/search.py` — `index_app` and `search_app`

### API
- `GET /api/v1/ai/faiss` — registered in main.py

### Rules
- Always normalize vectors before adding to index
- Lazy-import faiss — it has a heavy load time
- Batch vector operations for performance
- Agent memory (`ai/agents/memory.py`) uses same FAISS backend
