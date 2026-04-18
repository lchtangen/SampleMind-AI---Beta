---
name: performance-optimization
description: Guide for optimizing performance across the SampleMind platform. Use when profiling or improving speed/memory usage.
---

## Performance Optimization

### Audio Processing Targets
| Level | Target | Key Ops |
|-------|--------|---------|
| BASIC | <0.5s | BPM, key, duration |
| STANDARD | <1s | + MFCC, chroma, spectral |
| DETAILED | <2s | + harmonic/percussive sep |
| PROFESSIONAL | <5s | + AI, CLAP, embeddings |

### Python Backend
```python
# Lazy model loading
_model = None
def get_model():
    global _model
    if _model is None:
        _model = load_heavy_model()
    return _model

# ThreadPoolExecutor for CPU-bound work
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)
result = await loop.run_in_executor(executor, cpu_bound_function, args)

# Batch DB queries
samples = await TortoiseSample.filter(library=lib).prefetch_related("tags").all()
```

### Frontend
```typescript
// Dynamic imports for heavy components
const Waveform = dynamic(() => import("@/components/Waveform"), { ssr: false })

// Memoize expensive computations
const sorted = useMemo(() => items.sort((a, b) => a.bpm - b.bpm), [items])
```

### Profiling
```bash
# Python
python -m cProfile -o profile.prof script.py
python -m snakeviz profile.prof

# Memory
python -m memory_profiler script.py
```
