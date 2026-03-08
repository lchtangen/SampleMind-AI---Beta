# SampleMind AI — Active Workspace Index

> **AI Agent Entry Point** — Read this file first to orient yourself in the codebase.
> **Last Updated:** 2026-03-07 (Session 3 complete) | **Phase:** 15 — v3.0 Migration
> **Version:** 2.1.0-beta → 3.0.0 | **Branch:** `main`

---

## What Is This Project?

SampleMind AI is a **CLI-first, offline-capable music production AI** for audio analysis,
sample management, stem separation, MIDI transcription, and AI-powered production coaching.

**Primary interfaces:** CLI (main product), TUI (Textual ^0.87), FastAPI REST, Next.js 15 web UI (building)
**AI stack:** Claude 3.7 Sonnet (primary) · Gemini 2.0 Flash (fast) · GPT-4o (agents) · Ollama (offline <100ms)
**Audio stack:** librosa ^0.11, demucs ^4.0 (stems), basic-pitch ^0.4 (MIDI), pedalboard ^0.9 (effects), faster-whisper ^1.1

---

## Phase 15 Progress — What's Done vs. Next

### ✅ P0 + P1 Complete (Session 3 — 2026-03-07)

All AI provider SDKs migrated, pyproject.toml fully upgraded:

| Area | Done |
|------|------|
| `anthropic ^0.40.0` | Claude 3.7 Sonnet + extended thinking |
| `google-genai ^0.8.0` | Gemini 2.0 Flash, new Client API (full rewrite) |
| `openai ^1.58.0` | GPT-4o default, gpt-5 removed |
| `ollama ^0.3.0` | NEW offline provider (qwen2.5, phi3, gemma2) |
| AI routing | Anthropic=PRIMARY, Ollama=INSTANT, QUICK_ANALYSIS → Ollama |
| All dep upgrades | numpy >=2.0, scipy ^1.14, librosa ^0.11, torch ^2.5, textual ^0.87 |
| New deps added | demucs, pedalboard, basic-pitch, faster-whisper, langgraph, langchain-core, openai-agents |
| Tests | 120+ tests (added test_anthropic, test_ollama, rewrote test_google, updated test_ai_manager) |
| Docs cleanup | 73 files archived, docs/active/ created, 8 root docs updated |

### Current Active Priorities

| Priority | Task | Status |
|----------|------|--------|
| P0-008 | Remove scipy monkey-patch | ⏳ After `poetry install` + `librosa ^0.11` verified |
| P1-TUI | Migrate 13 TUI screens to Textual ^0.87 | ⏳ Next |
| P1-011 | Integrate `demucs` into audio_engine.py | ⏳ Next |
| P2 | Scaffold `apps/web/` — Next.js 15 | ⏳ Next |
| P3 | LangGraph multi-agent architecture | ⏳ Deps added, integration pending |
| P5-001 | Test coverage 30% → 50% → 80% | ⏳ Ongoing |

**First action this session:** `source .venv/bin/activate && make upgrade-deps`

---

## Key Source Files

```
src/samplemind/
├── __init__.py                        — lazy imports (scipy monkey-patch: remove after librosa ^0.11 install)
├── core/
│   ├── engine/audio_engine.py         — main audio processing (BPM, key, MFCC, stems)
│   ├── loader.py                      — AdvancedAudioLoader (multi-format)
│   ├── database/chroma.py             — ChromaDB vector search
│   └── library/pack_creator.py        — sample pack creation
├── integrations/
│   ├── ai_manager.py                  — multi-provider routing (UPDATED v3.0)
│   ├── anthropic_integration.py       — Claude 3.7 Sonnet + extended thinking (UPDATED)
│   ├── google_ai_integration.py       — Gemini 2.0 Flash / google-genai SDK (UPDATED)
│   ├── openai_integration.py          — GPT-4o (UPDATED)
│   ├── ollama_integration.py          — Offline Ollama provider (NEW)
│   └── daw/fl_studio_plugin.py        — FL Studio integration
├── interfaces/
│   ├── cli/menu.py                    — main CLI (~2255 lines, Rich + Typer)
│   ├── cli/commands/effects.py        — Effects chain CLI
│   ├── tui/app.py                     — Textual TUI app (needs ^0.87 migration)
│   ├── tui/screens/                   — 13 screens (needs ^0.87 migration)
│   ├── api/                           — FastAPI router layer
│   └── server/                        — FastAPI server entrypoint
├── ai/                                — AI utilities and helpers
└── services/                          — business logic services

main.py                                — CLI entry point
pyproject.toml                         — ALL deps now at v3.0 targets
```

> **Note:** API path is `src/samplemind/interfaces/api/` and `src/samplemind/server/` — NOT `src/samplemind/api/`

---

## Document Directory Map

```
docs/
├── active/                            ← V3 WORKING WORKSPACE (you are here)
│   ├── INDEX.md                       ← This file — master AI navigation hub
│   ├── architecture/
│   │   └── V3_ARCHITECTURE_DECISIONS.md
│   ├── devops/
│   │   └── DEPENDENCY_UPGRADE_STATUS.md  ← Updated: all P0/P1 done
│   ├── features/
│   │   └── WEB_UI_SPEC.md             ← Next.js 15 spec
│   ├── models/
│   │   └── AI_PROVIDER_UPGRADE_LOG.md ← Updated: all 4 providers done
│   ├── roadmap/
│   │   ├── PHASE_15_PROGRESS.md       ← Session-by-session log (update each session)
│   │   └── V3_100_KEYPOINTS.md
│   └── ui-ux/
│       └── TUI_V3_UPGRADE_NOTES.md    ← Textual ^0.87 migration guide
│
├── ARCHITECTURE.md                    ← V3 architecture reference (new)
├── DEVELOPMENT.md                     ← Developer quick reference (new)
│
├── 02-ROADMAPS/
│   ├── CURRENT_STATUS.md              ← Real-time project status (update every session)
│   ├── V3_MIGRATION_CHECKLIST.md      ← Updated: P0 75% done, P1 48% done
│   └── README.md
│
├── 04-TECHNICAL-IMPLEMENTATION/
│   ├── guides/                        ← Installation, platform, AI, DAW guides
│   │   ├── INSTALLATION_GUIDE.md
│   │   ├── AI_INTEGRATION_SETUP.md
│   │   ├── TEXTUAL_MIGRATION.md       ← Textual ^0.87 migration guide
│   │   └── PLUGIN_INSTALLATION_GUIDE.md
│   └── technical/
│       └── audio_processing.md
│
├── 00-INDEX/
│   ├── MASTER_PHASE_INDEX.md
│   └── PHASE_STATUS_DASHBOARD.md      ← Updated: Phase 15 P0/P1 done
│
├── 01-PHASES/15-PHASE-15-IN-PROGRESS/ ← Active phase directory
│
├── CLI_REFERENCE.md                   ← Full CLI reference (62K)
├── API_DOCUMENTATION.md               ← Full API reference (24K)
├── SESSION_START_GUIDE.md             ← Updated session startup guide
└── _archive/                          ← Read-only: 73+ archived docs
```

---

## Task Routing — What to Read

| Scenario | Read These |
|----------|-----------|
| Working on audio analysis | `core/engine/audio_engine.py` + `technical/audio_processing.md` |
| Working on AI integration | `integrations/ai_manager.py` + `active/models/AI_PROVIDER_UPGRADE_LOG.md` |
| Working on CLI | `interfaces/cli/menu.py` + `CLI_REFERENCE.md` |
| Working on TUI | `interfaces/tui/` + `active/ui-ux/TUI_V3_UPGRADE_NOTES.md` + `guides/TEXTUAL_MIGRATION.md` |
| Working on API | `interfaces/api/` + `server/` + `API_DOCUMENTATION.md` |
| Working on agents | `integrations/` + `active/architecture/V3_ARCHITECTURE_DECISIONS.md` |
| Working on DAW plugins | `plugins/` + `guides/PLUGIN_INSTALLATION_GUIDE.md` |
| Upgrading dependencies | `pyproject.toml` + `active/devops/DEPENDENCY_UPGRADE_STATUS.md` |
| Planning next work | `02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` + `active/roadmap/PHASE_15_PROGRESS.md` |
| Starting a new session | `SESSION_START_GUIDE.md` + `02-ROADMAPS/CURRENT_STATUS.md` |

---

## AI SDK Patterns (v3.0 — use these, never the old patterns)

```python
# Anthropic ^0.40.0 — extended thinking for claude-3-7-sonnet
from anthropic import AsyncAnthropic
client = AsyncAnthropic(api_key=key)
response = await client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=8096,
    thinking={"type": "enabled", "budget_tokens": 5000},
    messages=[{"role": "user", "content": prompt}],
    # NOTE: DO NOT include temperature with extended thinking
)

# Google google-genai ^0.8.0 — NEVER use google-generativeai
from google import genai
from google.genai import types as genai_types
client = genai.Client(api_key=key)
response = await client.aio.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=genai_types.GenerateContentConfig(temperature=0.7),
)

# OpenAI ^1.58.0 — gpt-4o only (gpt-5 does NOT exist)
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=key)

# Ollama ^0.3.0 — offline, no API key
import ollama
client = ollama.AsyncClient(host="http://localhost:11434")
response = await client.chat(model="qwen2.5:7b-instruct", messages=[...])
text = response["message"]["content"]
```

---

## Critical Rules

1. **Never** use `google-generativeai` — package is `google-genai`, import is `from google import genai`
2. **Never** reference `gpt-5` — it does not exist
3. **Never** set `temperature` when using extended thinking (claude-3-7-sonnet)
4. **Never** call `genai.configure(api_key=...)` — use `genai.Client(api_key=...)` instead
5. **Never** use `asyncio.run()` inside Textual event handlers
6. **Always** run `make quality` before committing (`ruff + mypy + bandit`)
7. **Always** update `CURRENT_STATUS.md` and `PHASE_15_PROGRESS.md` at session end
8. **Keep** the scipy monkey-patch in `__init__.py` until librosa ^0.11.0 is installed and tested

---

## Service Ports

| Service | Port | Command |
|---------|------|---------|
| CLI | — | `python main.py` |
| TUI | — | `python -m samplemind.interfaces.tui.main` |
| FastAPI | 8000 | `make dev` |
| Next.js web | 3000 | `cd apps/web && npm run dev` |
| MongoDB | 27017 | `docker-compose up -d mongodb` |
| Redis | 6379 | `docker-compose up -d redis` |
| ChromaDB | 8002 | `docker-compose up -d chromadb` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |

---

*Master navigation hub for Claude Code, GitHub Copilot, and all AI agents.*
*Update at the end of each session when adding new documents or completing major milestones.*
