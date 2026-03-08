# SampleMind AI — Developer Quick Reference

> **For:** Claude Code, GitHub Copilot, and human developers
> **Version:** v3.0 (migration in progress) | **Last Updated:** 2026-03-07

---

## 30-Second Setup

```bash
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
make setup                   # creates .venv + poetry install
source .venv/bin/activate
make install-models          # downloads Ollama models (optional, for offline AI)
python main.py               # run CLI
```

If `.venv` exists already:

```bash
source .venv/bin/activate
make upgrade-deps            # poetry update to v3.0 targets
python main.py
```

---

## Common Commands

### Development

```bash
# Run CLI (primary interface)
python main.py

# Run TUI (Textual-based)
python -m samplemind.interfaces.tui.main

# Run FastAPI server
make dev                     # → localhost:8000
make dev-full                # full stack with Docker

# Start databases
docker-compose up -d         # MongoDB:27017, Redis:6379, ChromaDB:8002
make setup-db                # same thing

# Start Ollama offline AI
scripts/launch-ollama-api.sh  # → localhost:11434
```

### Testing

```bash
make test                    # all tests with coverage
make test-unit               # unit tests only (no integration)
make test-unit -- tests/unit/integrations/   # specific directory
pytest tests/unit/core/test_audio_engine.py  # specific file
pytest -k "test_bpm"         # by name pattern
```

### Code Quality (run before every commit)

```bash
make quality                 # ruff + mypy + bandit (all must pass)
make lint                    # ruff check + mypy
make format                  # black + isort
make security                # bandit + safety
```

### Dependency Management

```bash
make upgrade-deps            # poetry update
make setup                   # fresh install from scratch
poetry add some-package      # add new dependency
poetry add some-package --group dev  # add dev dependency
```

---

## Project Structure (condensed)

```
src/samplemind/
├── core/engine/audio_engine.py    — BPM, key, MFCC, stems, spectral
├── core/loader.py                 — AdvancedAudioLoader (multi-format)
├── core/database/chroma.py        — ChromaDB vector search
├── integrations/ai_manager.py     — multi-provider AI routing
├── integrations/anthropic_*.py    — Claude 3.7 Sonnet (PRIMARY)
├── integrations/google_ai_*.py    — Gemini 2.0 Flash (FAST)
├── integrations/openai_*.py       — GPT-4o (AGENTS)
├── integrations/ollama_*.py       — Ollama offline (INSTANT)
├── interfaces/cli/menu.py         — main CLI (~2255 lines)
├── interfaces/tui/                — 13 Textual screens
├── interfaces/api/                — FastAPI routers
└── server/                        — FastAPI entrypoint

main.py                            — CLI entry point
pyproject.toml                     — all dependencies (Poetry)
Makefile                           — all dev commands
```

> **API path:** `src/samplemind/interfaces/api/` + `src/samplemind/server/`
> There is NO `src/samplemind/api/` — that path does not exist.

---

## AI SDK Patterns (v3.0)

Always use these patterns. Never use old/deprecated patterns.

### Anthropic (Claude 3.7 Sonnet)

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Standard call
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=8096,
    messages=[{"role": "user", "content": prompt}],
)

# With extended thinking (do NOT pass temperature)
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=8096,
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[{"role": "user", "content": prompt}],
)
text = response.content[-1].text
```

### Google Gemini 2.0 Flash

```python
from google import genai                           # NOT google.generativeai
from google.genai import types as genai_types

client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))
# NEVER use: genai.configure(api_key=...)

response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=genai_types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=4096,
    ),
)
text = response.text
tokens = response.usage_metadata.total_token_count
```

### OpenAI GPT-4o

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# gpt-5 does NOT exist — use gpt-4o

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
)
text = response.choices[0].message.content
```

### Ollama (offline)

```python
import ollama

client = ollama.AsyncClient(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
response = await client.chat(
    model="qwen2.5:7b-instruct",
    messages=[{"role": "user", "content": prompt}],
    options={"temperature": 0.7},
)
text = response["message"]["content"]
```

---

## Rules — Never Break These

1. **Never** use `google-generativeai` — package is `google-genai`, import is `from google import genai`
2. **Never** reference `gpt-5` — it does not exist. Use `gpt-4o` or `gpt-4o-mini`
3. **Never** set `temperature` when using extended thinking (claude-3-7-sonnet)
4. **Never** call `genai.configure(api_key=...)` — use `genai.Client(api_key=...)` instead
5. **Never** use `asyncio.run()` inside Textual event handlers — use `async def`
6. **Never** block `main.py`'s event loop — audio I/O in `ThreadPoolExecutor`
7. **Keep** the scipy monkey-patch in `__init__.py` until `librosa ^0.11.0` is installed
8. **Always** run `make quality` before committing (ruff + mypy + bandit)
9. **Always** update `docs/02-ROADMAPS/CURRENT_STATUS.md` at session end
10. **Always** mock AI clients in tests — never make real API calls in unit tests

---

## Writing Tests

```python
# Pattern for async AI provider tests
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_analyze_music(producer, mock_response):
    producer.async_client.messages.create = AsyncMock(return_value=mock_response)
    result = await producer.analyze_music_comprehensive({"tempo": 120, "key": "C"})
    assert result.summary != ""
    producer.async_client.messages.create.assert_called_once()

# Mock Anthropic client
@pytest.fixture
def producer():
    with patch("anthropic.AsyncAnthropic"):
        p = AnthropicMusicProducer(api_key="test-key")
        p.async_client = MagicMock()
        p.async_client.messages.create = AsyncMock()
        yield p
```

Test files live in:
```
tests/
├── unit/
│   ├── core/           — audio engine, loader, database
│   ├── integrations/   — AI provider tests
│   ├── interfaces/     — CLI, TUI, API tests
│   └── services/       — business logic tests
└── fixtures/           — test audio files
```

Coverage target: 80% (current: ~30%). Run `make test` to see current coverage report.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# AI Providers
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
OPENAI_API_KEY=sk-...
OLLAMA_HOST=http://localhost:11434    # no key needed

# Databases
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=samplemind
REDIS_URL=redis://localhost:6379
CHROMADB_HOST=localhost
CHROMADB_PORT=8002

# Testing
RUN_AI_INTEGRATION_TESTS=0    # set to 1 to run live AI tests (costs tokens)
```

---

## Session Start Checklist

1. `git pull`
2. `source .venv/bin/activate`
3. Read `docs/active/INDEX.md` — master navigation
4. Check `docs/02-ROADMAPS/CURRENT_STATUS.md` — current state
5. Check `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` — next tasks

## Session End Checklist

1. `make quality` — ruff + mypy + bandit (must pass)
2. `make test-unit`
3. Update `docs/02-ROADMAPS/CURRENT_STATUS.md`
4. Update `docs/active/roadmap/PHASE_15_PROGRESS.md`
5. Tick completed items in `V3_MIGRATION_CHECKLIST.md`
6. `git add <files> && git commit -m "feat(phase15): ..."`
7. `git push origin main`

---

## Key Documentation Links

| Resource | Path |
|----------|------|
| AI agent entry point | `docs/active/INDEX.md` |
| Session startup guide | `docs/SESSION_START_GUIDE.md` |
| Migration checklist | `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` |
| Current status | `docs/02-ROADMAPS/CURRENT_STATUS.md` |
| Architecture reference | `docs/ARCHITECTURE.md` |
| API documentation | `docs/API_DOCUMENTATION.md` |
| CLI reference | `docs/CLI_REFERENCE.md` |
| TUI migration guide | `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md` |
| Dep upgrade status | `docs/active/devops/DEPENDENCY_UPGRADE_STATUS.md` |
| AI provider log | `docs/active/models/AI_PROVIDER_UPGRADE_LOG.md` |
| Web UI spec | `docs/active/features/WEB_UI_SPEC.md` |

---

*Developer reference for SampleMind AI v3.0. Updated: 2026-03-07.*
