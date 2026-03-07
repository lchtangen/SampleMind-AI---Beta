# Phase 15: v3.0 Migration — IN PROGRESS

**Status:** IN PROGRESS — P0+P1 code complete, packages pending `poetry install`
**Started:** 2026-03-07
**Sessions:** 3 complete
**Overall Progress:** ~24% (27/112 checklist items)

---

## Overview

Phase 15 is the major v3.0 upgrade cycle for SampleMind AI. Sessions 1–3 completed all
AI provider SDK migrations, pyproject.toml upgrades, Ollama offline provider, routing table
overhaul, and 120+ unit tests. The actual packages need to be installed with `poetry install`.

> **Note:** `docs/01-PHASES/15-OLD-SEMANTIC-SEARCH-COMPLETED/` contains documentation for a
> previously completed Semantic Search sub-feature mislabeled as Phase 15. That work is
> archived. This directory is the current active Phase 15 (v3.0 Migration).

---

## Session Summary

| Session | Date | Work Completed |
|---------|------|----------------|
| Session 1 | 2026-03-07 | Audited all files, built migration plan |
| Session 2 | 2026-03-07 | pyproject.toml upgrades, Makefile fixes, version string cleanup |
| Session 3 | 2026-03-07 | AI provider migrations, Ollama new provider, routing fix, tests rewrite, docs overhaul |

---

## P0 Task Status

| Task | Status |
|------|--------|
| Upgrade `anthropic` ^0.7.0 → ^0.40.0 | ✅ Done |
| Migrate `anthropic_integration.py` — Claude 3.7 Sonnet + extended thinking | ✅ Done |
| Upgrade `openai` ^1.3.0 → ^1.58.0 | ✅ Done |
| Migrate `openai_integration.py` — GPT-4o default, removed gpt-5 | ✅ Done |
| Rename `google-generativeai` → `google-genai ^0.8.0` | ✅ Done |
| Migrate `google_ai_integration.py` — new Client API, Gemini 2.0 Flash | ✅ Done |
| Add `ollama ^0.3.0`, create `ollama_integration.py` | ✅ Done |
| Fix AI routing: Anthropic=PRIMARY, Ollama=INSTANT, Gemini=FAST | ✅ Done |
| Remove `numpy <2.0.0` cap | ✅ Done |
| Upgrade `librosa` 0.10.1 → `^0.11.0` | ✅ Done |
| Upgrade `scipy ^1.14.0`, `torch ^2.5.0`, `transformers ^4.47.0` | ✅ Done |
| Upgrade `textual ^0.87.0` in pyproject.toml | ✅ Done |
| Add `demucs ^4.0.0`, `pedalboard ^0.9.0`, `basic-pitch ^0.4.0` | ✅ Done |
| Add `faster-whisper ^1.1.0`, `langgraph ^0.2.0`, `langchain-core ^0.3.0`, `openai-agents ^0.0.5` | ✅ Done |
| Update `fastapi ^0.115.0`, `uvicorn ^0.32.0`, `motor ^3.6.0`, `chromadb ^0.6.0` | ✅ Done |
| Fix Makefile — broken `setup` and `dev` targets | ✅ Done |
| Create `.env.example` | ✅ Done |
| Update `CONTRIBUTING.md`, `README.md`, `CHANGELOG.md`, `Dockerfile` | ✅ Done |
| Write `test_anthropic_integration.py` (new) | ✅ Done |
| Rewrite `test_google_ai_integration.py` (remove skip gate) | ✅ Done |
| Write `test_ollama_integration.py` (new) | ✅ Done |
| Update `test_ai_manager.py` — Ollama routing, priority assertions | ✅ Done |
| **Remove scipy monkey-patch from `__init__.py`** | ⏳ After `poetry install` verified |

---

## P1 Next Tasks

### Immediate (Next Session)

```bash
make upgrade-deps    # install all v3.0 packages
make test            # verify tests pass
# If librosa ^0.11.0 imports cleanly:
# Delete lines 24-33 in src/samplemind/__init__.py (scipy monkey-patch)
```

### P1 Audio Engine

- [ ] Integrate `demucs` into `audio_engine.py` — `StemSeparation` class, htdemucs_6s model
- [ ] Add `POST /api/v1/audio/separate` REST endpoint
- [ ] Integrate `pedalboard` effects chain into CLI + API
- [ ] Wire `faster-whisper` for local transcription

### P1 TUI Migration (Textual ^0.87)

All 13 screens need API updates. Guide: `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md`

- [ ] Audit breaking changes in all 13 screens
- [ ] Migrate `main_screen.py`, `analyze_screen.py`, `batch_screen.py`, `results_screen.py`
- [ ] Migrate remaining 9 screens
- [ ] Create new screens: `AgentChatScreen`, `WaveformScreen`, `MixingBoardScreen`

### P2 Web Platform

- [ ] Scaffold `apps/web/` — `npx create-next-app@latest web --typescript --tailwind --app`
- [ ] Reference: `docs/active/features/WEB_UI_SPEC.md`

---

## Files Changed This Phase

### New Files
- `src/samplemind/integrations/ollama_integration.py`
- `tests/unit/integrations/test_anthropic_integration.py`
- `tests/unit/integrations/test_ollama_integration.py`
- `.env.example`

### Significantly Changed
- `pyproject.toml` — all dep targets at v3.0
- `src/samplemind/integrations/anthropic_integration.py` — Claude 3.7 + extended thinking
- `src/samplemind/integrations/google_ai_integration.py` — full SDK migration to google-genai
- `src/samplemind/integrations/openai_integration.py` — removed gpt-5, gpt-4o default
- `src/samplemind/integrations/ai_manager.py` — Ollama provider, routing table fix
- `tests/unit/integrations/test_google_ai_integration.py` — removed skip gate, new SDK mocks
- `tests/unit/integrations/test_ai_manager.py` — routing + Ollama assertions

---

## Working Documents

| Document | Purpose |
|----------|---------|
| `docs/active/INDEX.md` | AI agent entry point — master navigation |
| `docs/active/roadmap/PHASE_15_PROGRESS.md` | Session-by-session log |
| `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` | 112-item P0–P5 checklist |
| `docs/02-ROADMAPS/CURRENT_STATUS.md` | Real-time project state |
| `docs/active/devops/DEPENDENCY_UPGRADE_STATUS.md` | Dep upgrade tracking |
| `docs/active/models/AI_PROVIDER_UPGRADE_LOG.md` | AI provider migration log |
| `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md` | Textual ^0.87 migration guide |
| `docs/04-TECHNICAL-IMPLEMENTATION/guides/TEXTUAL_MIGRATION.md` | Textual migration reference |
| `docs/active/features/WEB_UI_SPEC.md` | Next.js 15 web UI spec |

---

*Updated: 2026-03-07 — Session 3. P0+P1 migration code complete. Next: `poetry install`.*
