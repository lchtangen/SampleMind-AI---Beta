# SampleMind AI — Docs

> **AI agent entry point.** Read this file first.
> **Phase:** 15 — v3.0 Migration | **Version:** 3.0.0-alpha | **Updated:** 2026-03-17

---

## Structure

```
docs/
├── README.md          ← you are here
├── v3/                ← active working docs (update every session)
├── guides/            ← reference docs (stable)
└── archive/
    ├── phases/        ← completed phase history (1–14)
    └── legacy/        ← old notes, business docs
```

---

## v3/ — Active Working Documents

> These are the files you open and update every session.

| File | Purpose |
|------|---------|
| `v3/STATUS.md` | Current project state — update at session end |
| `v3/CHECKLIST.md` | P0/P1/P2 migration tasks — tick items as done |
| `v3/PHASE15.md` | Session-by-session progress log |
| `v3/ROADMAP.md` | **Alpha/Beta release roadmap** — 132 tasks, 4 milestones, 10 follow-up questions |
| `v3/ARCHITECTURE.md` | ADRs and v3.0 architecture decisions |
| `v3/DEPENDENCIES.md` | Dep upgrade tracking (all P0/P1/P2 done) |
| `v3/AI_PROVIDERS.md` | Claude 3.7 / Gemini 2.0 / GPT-4o / Ollama upgrade log |
| `v3/TUI_NOTES.md` | Textual ^0.87 migration notes |
| `v3/WEB_UI.md` | Next.js 15 web UI spec |

---

## guides/ — Reference Docs

| File | Purpose |
|------|---------|
| `guides/QUICKSTART.md` | 60-second startup (v3.0 — updated 2026-03-17) |
| `guides/INSTALLATION.md` | Full install guide (v3.0 — updated 2026-03-17) |
| `guides/DEVELOPMENT.md` | Dev workflow, commands, Makefile |
| `guides/CLI.md` | Full CLI command reference (200+ commands) |
| `guides/API.md` | FastAPI endpoint reference |
| `guides/AI_SETUP.md` | AI provider setup (keys, models) |
| `guides/PLUGINS.md` | FL Studio / Ableton plugin install |
| `guides/TUI_MIGRATION.md` | Textual ^0.87 migration guide |
| `guides/AUDIO.md` | Audio processing pipeline deep dive |
| `guides/PERFORMANCE.md` | Performance targets and profiling |
| `guides/ARCHITECTURE.md` | System architecture overview |
| `guides/SESSION_START.md` | Session startup checklist |

---

## Quick Reference

### Session Checklist
```bash
git pull
source .venv/bin/activate
# Read: docs/v3/STATUS.md + docs/v3/CHECKLIST.md
python main.py
# At end: update docs/v3/STATUS.md + docs/v3/PHASE15.md → commit
```

### Key Source Paths
| What | Where |
|------|-------|
| CLI entry | `main.py` |
| CLI menu | `src/samplemind/interfaces/cli/menu.py` |
| Audio engine | `src/samplemind/core/engine/audio_engine.py` |
| AI manager | `src/samplemind/integrations/ai_manager.py` |
| TUI app | `src/samplemind/interfaces/tui/app.py` |
| TUI screens | `src/samplemind/interfaces/tui/screens/` |
| FastAPI | `src/samplemind/interfaces/api/` + `src/samplemind/server/` |
| Config | `pyproject.toml` |

### AI SDK Patterns (v3.0)
```python
# Anthropic — PRIMARY (no temperature with extended thinking)
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=key)
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=8096,
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[{"role": "user", "content": prompt}],
)

# Google — package is google-genai, NOT google-generativeai
from google import genai
client = genai.Client(api_key=key)

# OpenAI — gpt-4o only (gpt-5 does not exist)
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=key)

# Ollama — offline, no API key
import ollama
client = ollama.AsyncClient(host="http://localhost:11434")
```

### Service Ports
| Service | Port | Command |
|---------|------|---------|
| CLI | — | `python main.py` |
| FastAPI | 8000 | `make dev` |
| Next.js | 3000 | `cd apps/web && npm run dev` |
| MongoDB | 27017 | `docker-compose up -d` |
| Redis | 6379 | `docker-compose up -d` |
| ChromaDB | 8002 | `docker-compose up -d` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |

### Task Routing
| Task | Read |
|------|------|
| Audio analysis | `guides/AUDIO.md` + `core/engine/audio_engine.py` |
| AI integration | `v3/AI_PROVIDERS.md` + `integrations/ai_manager.py` |
| CLI work | `guides/CLI.md` + `interfaces/cli/menu.py` |
| TUI work | `v3/TUI_NOTES.md` + `guides/TUI_MIGRATION.md` |
| API work | `guides/API.md` + `interfaces/api/` |
| Dependency upgrade | `v3/DEPENDENCIES.md` + `pyproject.toml` |
| Next task to work on | `v3/CHECKLIST.md` + `v3/STATUS.md` |
