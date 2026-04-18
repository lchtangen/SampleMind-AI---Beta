---
name: performance-optimization
description: Lazy imports, ThreadPoolExecutor, batch FAISS, Redis caching
---

## Performance Optimization

### Lazy Imports
```python
def _get_torch():
    import torch  # ~2s load time
    return torch
```
Must lazy-import: torch, transformers, librosa, faiss, demucs, basic_pitch

### Async & Threading
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)

async def analyze_audio(path: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _sync_analyze, path)
```

### FAISS Batch Operations
```python
# Batch add — much faster than one-by-one
vectors = np.stack(all_vectors)
vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
index.add(vectors)
```

### Redis Caching
- Cache repeated AI queries and analysis results
- Session cache for user preferences
- Pub/sub for agent progress updates

### Audio Processing
- Numpy vectorized ops over Python loops
- Process in chunks for large files
- Preserve sample rate — avoid unnecessary resampling
- Release tensors with `del` + `gc.collect()`
