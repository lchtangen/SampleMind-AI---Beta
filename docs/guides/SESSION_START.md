# SampleMind AI — Session Start Guide

> Read this at the start of every Claude Code / Copilot / Codex session.
> **Phase:** 15 — v3.0 Migration | **Last Updated:** 2026-03-17

---

## 3-Step Session Startup

```bash
cd SampleMind-AI---Beta
git pull
source .venv/bin/activate
```

Then check current state:

```bash
# Read in this order:
# 1. docs/v3/STATUS.md — current project state
# 2. docs/v3/CHECKLIST.md — what to work on next
# 3. docs/v3/ROADMAP.md — full alpha/beta release plan
```

---

## Current Project State (2026-03-07 — Session 3 complete)

| Area | Status | Notes |
|------|--------|-------|
| CLI (primary product) | ✅ Working | `python main.py` |
| TUI — 13 screens | ✅ Working | Needs Textual ^0.87 screen migration |
| FastAPI server | ✅ Working | `make dev` → localhost:8000 |
| FL Studio plugin | ✅ Working | C++ JUCE + Python wrapper |
| Ableton plugin | ✅ Working | REST backend + JS bridge |
| Anthropic Claude | ✅ Upgraded | `^0.40.0`, Claude 3.7 Sonnet, extended thinking |
| Google Gemini | ✅ Upgraded | `google-genai ^0.8.0`, Gemini 2.0 Flash |
| OpenAI | ✅ Upgraded | `^1.58.0`, GPT-4o default |
| Ollama (offline) | ✅ New | qwen2.5:7b, phi3:mini, gemma2:2b, <100ms |
| pyproject.toml | ✅ v3.0 | All dep targets applied — needs `poetry install` |
| Web UI | ❌ Not started | Phase 15 P2 — Next.js 15 |
| LangGraph agents | ⏳ Dep added | Integration pending |
| Test coverage | ⚠️ ~30% | 120+ tests, target 80% |

---

## Next Actions by Priority

### This Session First: Install the Updated Dependencies

```bash
source .venv/bin/activate
make upgrade-deps   # poetry update — install all v3.0 deps
make test           # verify nothing broke
```

### P0 Remaining (1 item)

- [ ] **P0-008** — Remove scipy monkey-patch from `src/samplemind/__init__.py`
  - Only do this AFTER `poetry install` completes and `librosa ^0.11.0` imports cleanly
  - Delete lines 24–33 in `__init__.py`

### P1 Next Priorities

- [ ] **P1-TUI** — Migrate 13 Textual screens to `^0.87.0` API
  - Guide: `docs/v3/TUI_NOTES.md`
  - Guide: `docs/guides/TUI_MIGRATION.md`
- [ ] **P1-011** — Integrate `demucs` into `audio_engine.py` (dep is installed, needs code)
- [ ] **P1-012** — Integrate `pedalboard` effects into CLI + API
- [ ] **P1-016** — Wire `faster-whisper` for local audio transcription

### P2 Next

- [ ] Scaffold `apps/web/` — `cd apps && npx create-next-app@latest web`
- [ ] Reference: `docs/v3/WEB_UI.md`

---

## Session Workflows

### Workflow A — Install & Verify Dependencies

```bash
source .venv/bin/activate
make upgrade-deps               # poetry update
python -c "import samplemind; print(samplemind.__version__)"
python -c "from anthropic import AsyncAnthropic; print('anthropic ok')"
python -c "from google import genai; print('google-genai ok')"
python -c "import librosa; print(librosa.__version__)"  # should be 0.11.x
make test-unit
```

### Workflow B — TUI Screen Migration (Textual ^0.87)

```bash
# 1. Read the migration guide
# See: docs/v3/TUI_NOTES.md
# See: docs/guides/TUI_MIGRATION.md

# 2. Read + update one screen at a time
/read src/samplemind/interfaces/tui/screens/main_screen.py

# 3. Test TUI launches without errors
python -m samplemind.interfaces.tui.main

# 4. Run TUI-specific tests
make test-unit -- tests/unit/tui/
```

### Workflow C — Demucs Integration

```bash
# 1. Read audio engine
/read src/samplemind/core/engine/audio_engine.py

# 2. Add StemSeparation class using demucs
# 3. Add API endpoint: POST /api/v1/audio/separate
# 4. Write tests in tests/unit/core/

make test-unit
```

### Workflow D — Web UI Scaffold

```bash
# Requires: Node.js 20+
# See: docs/v3/WEB_UI.md
cd apps
npx create-next-app@latest web --typescript --tailwind --app
cd web && npm install
npm run dev  # → localhost:3000
```

### Workflow E — Agent Architecture

```bash
# LangGraph + openai-agents are in pyproject.toml
# Target location:
mkdir -p src/samplemind/integrations/agents/
# See: docs/v3/ARCHITECTURE.md
```

---

## AI Tool Routing

| Task | Best Tool | Notes |
|------|-----------|-------|
| Refactor large files (2000+ lines) | Claude Code | Largest context window |
| Multi-file feature across 5+ files | Claude Code | Full codebase awareness |
| Quick function completion | Copilot (VSCode) | Fast in-editor suggestions |
| New React component boilerplate | Copilot | Strong on TypeScript/TSX |
| Write 20+ unit tests | Claude Code | Best test quality |
| Generate TypeScript types from API | Copilot | Strong on TS inference |
| Research PyPI versions | Any + web | `poetry search` or pypi.org |
| Create GitHub PRs from issues | Copilot (GitHub) | `@copilot` on issue |

---

## Architecture Quick Reference

```
src/samplemind/
├── __init__.py              lazy imports (scipy patch — REMOVE after librosa ^0.11 install)
├── core/
│   ├── engine/audio_engine.py   ← BPM, key, MFCC, stems, spectral
│   ├── loader.py                ← AdvancedAudioLoader (WAV/MP3/FLAC/OGG/AAC)
│   ├── database/chroma.py       ← ChromaDB vector similarity
│   └── library/pack_creator.py  ← sample pack creation
├── integrations/
│   ├── ai_manager.py            ← multi-provider routing (v3.0 routing table)
│   ├── anthropic_integration.py ← Claude 3.7 Sonnet + extended thinking
│   ├── google_ai_integration.py ← Gemini 2.0 Flash (google-genai SDK)
│   ├── openai_integration.py    ← GPT-4o
│   └── ollama_integration.py    ← Offline Ollama provider (NEW)
├── interfaces/
│   ├── cli/menu.py              ← main CLI, ~2255 lines
│   ├── tui/                     ← 13 screens (Textual migration needed)
│   ├── api/                     ← FastAPI router layer
│   └── server/                  ← FastAPI server entrypoint (NOT interfaces.api.main)
└── services/                    ← business logic

plugins/                         ← DAW plugins (FL Studio, Ableton)
apps/web/                        ← Next.js 15 (to be created)
```

---

## Session End Checklist

```bash
# 1. Quality checks
make quality          # ruff + mypy + bandit

# 2. Tests
make test-unit

# 3. Update status
# Edit: docs/v3/STATUS.md
# Edit: docs/v3/PHASE15.md
# Edit: docs/v3/CHECKLIST.md — tick off completed items

# 4. Commit and push
git add <changed files>
git commit -m "feat(phase15): <describe what you did>"
git push origin main
```

---

## Service Ports Reference

| Service | Port | Command |
|---------|------|---------|
| FastAPI | 8000 | `make dev` |
| Next.js | 3000 | `cd apps/web && npm run dev` |
| MongoDB | 27017 | `docker-compose up -d mongodb` |
| Redis | 6379 | `docker-compose up -d redis` |
| ChromaDB | 8002 | `docker-compose up -d chromadb` |
| Celery Flower | 5555 | `./scripts/start-flower.sh` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |

---

## Known Issues

| Issue | Status | Resolution |
|-------|--------|-----------|
| scipy monkey-patch in `__init__.py` | ⏳ Keep for now | Remove after `librosa ^0.11.0` installed |
| Textual screens not on ^0.87 API | ⏳ P1-TUI | Migrate screens — see TUI_V3_UPGRADE_NOTES.md |
| `demucs`/`pedalboard` in pyproject but not integrated | ⏳ P1 | Wire into audio_engine.py + API |
| CLI startup ~2s | ⏳ Medium | Further lazy import optimization |
| Test coverage 30% | ⏳ P5 | Target 80% — write tests alongside each feature |
| Web UI not built | ⏳ P2 | Scaffold Next.js 15 in apps/web/ |

---

*SESSION_START_GUIDE.md v3.0 — Updated 2026-03-17. Reflects documentation overhaul and new v3 doc structure.*
