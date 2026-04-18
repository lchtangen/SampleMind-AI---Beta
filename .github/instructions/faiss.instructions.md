---
applyTo: "src/samplemind/core/search/**/*.py"
---

# FAISS Semantic Search Instructions

- Index: `core/search/faiss_index.py` — FAISS IndexFlatIP with 512-dim CLAP embeddings
- Embedder: CLAPEmbedder using `laion/clap-htsat-unfused` model
- Pattern:
  ```python
  from samplemind.core.search.faiss_index import get_index
  index = get_index(auto_load=True)
  results = index.search_text("dark trap kick", top_k=20)
  ```
- CLI: `interfaces/cli/commands/search.py` — `index_app` and `search_app`
- API: `GET /api/v1/ai/faiss` — registered in main.py
- Embeddings are cosine similarity (inner product on normalized vectors)
- Always normalize vectors before adding to index
- Agent memory uses same FAISS backend: `ai/agents/memory.py`
