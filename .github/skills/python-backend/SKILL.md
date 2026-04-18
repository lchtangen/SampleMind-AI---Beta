---
name: python-backend
description: Guide for implementing Python backend features in SampleMind. Use when asked to create or modify Python backend code.
---

## Python Backend Development

When implementing Python backend features for SampleMind:

1. **Check existing code first** — search `src/samplemind/` for similar implementations
2. **Follow the async pattern** — all I/O must be `async def` or wrapped in `ThreadPoolExecutor`
3. **Use type annotations** — mypy strict mode is enabled
4. **Prefer LiteLLM** — use `litellm_router.chat_completion()` over direct provider SDKs
5. **Lazy imports** — heavy libraries (torch, librosa, faiss) must be imported inside functions

### Setup
```bash
source .venv/bin/activate
pip install -e '.[dev]'
```

### Validate
```bash
ruff check src/
ruff format --check src/
mypy src/
pytest tests/unit/ -v --tb=short
```

### Key Directories
- `src/samplemind/core/` — engine, database, search, tasks, processing
- `src/samplemind/ai/` — agents, classification, curation, generation, transcription
- `src/samplemind/interfaces/` — CLI (Typer), TUI (Textual), API (FastAPI)
- `src/samplemind/integrations/` — LiteLLM, Supabase, realtime sync
