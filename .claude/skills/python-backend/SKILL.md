---
name: python-backend
description: Python 3.12 async-first backend development for SampleMind
---

## Python Backend Development

### Core Patterns
- Python 3.12+ features: `X | Y` union types, `match` statements, `Self` type
- Type annotations required on all function signatures and return types
- `async def` for all I/O operations (audio, AI, database, network)
- `ThreadPoolExecutor` for blocking ops without async support
- `pathlib.Path` over `os.path` for file operations
- `logging` module — never `print()` in library code

### Lazy Imports
```python
def _load_model():
    import torch
    from transformers import AutoModel
    return AutoModel.from_pretrained("laion/clap-htsat-unfused")
```
Libraries to lazy-import: torch, transformers, librosa, faiss, demucs, basic_pitch

### AI Calls
```python
from samplemind.integrations.litellm_router import chat_completion
response = await chat_completion(messages=[...], prefer_fast=True)
```
Never use direct SDK calls (anthropic, openai, google-genai).

### Style
- Black (line length 88) + isort + ruff
- Google-style docstrings with Args/Returns/Raises
- Lint: `ruff check src/ && mypy src/`
- Format: `ruff format src/`
