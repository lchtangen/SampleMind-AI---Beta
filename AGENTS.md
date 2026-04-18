# AGENTS.md — SampleMind AI

> Agent instructions for AI coding assistants (Copilot, Claude, Gemini, etc.)
> For full project context see: `CLAUDE.md` | Checklist: `docs/v3/CHECKLIST.md`

---

## Project Overview

**SampleMind AI** is a CLI-first, offline-capable music production AI platform for audio analysis,
sample management, stem separation, MIDI transcription, AI-powered recommendations,
semantic search, smart playlist curation, and a sample pack marketplace.

**Language:** Python 3.12 | **Frontend:** Next.js 15 + React 19 | **Desktop:** Tauri v2 + Svelte 5

---

## Dev Environment Setup

```bash
# Python backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'

# Frontend
cd apps/web && npm install --legacy-peer-deps
```

## Key Commands

| Task | Command |
|------|---------|
| Start backend | `python main.py` |
| Start frontend | `cd apps/web && npm run dev` |
| Run tests | `pytest tests/unit/ -v --tb=short` |
| Lint Python | `ruff check src/ && mypy src/` |
| Format Python | `ruff format src/` |
| Lint frontend | `cd apps/web && npm run lint` |
| Build frontend | `cd apps/web && npm run build` |
| Full quality | `make quality` |

## Testing

- Framework: **pytest** with fixtures in `tests/fixtures/`
- Always mock AI providers, FAISS, torch, transformers, librosa, demucs
- Test files: `tests/unit/test_<module>.py`
- Run: `pytest tests/unit/ -v --tb=short`

## Architecture

```
src/samplemind/
├── interfaces/          # CLI (Typer), TUI (Textual), API (FastAPI)
│   ├── cli/             # Main CLI menu + search commands
│   ├── tui/             # 13 Textual screens
│   └── api/             # FastAPI app + 12 route modules
├── core/                # Engine, database, search, tasks, processing
│   ├── engine/          # LibROSA-based audio analysis
│   ├── database/        # Tortoise ORM + ChromaDB
│   ├── search/          # FAISS IndexFlatIP + CLAP embeddings
│   ├── tasks/           # Celery task definitions
│   └── processing/      # Realtime effects, audio DNA, etc.
├── ai/                  # AI agents, classification, curation, generation
│   ├── agents/          # LangGraph 9-node pipeline + memory
│   ├── classification/  # Ensemble, genre, mood, instrument
│   ├── curation/        # Playlist generator + gap analyzer
│   └── generation/      # MusicGen, style transfer, similar sample
├── integrations/        # LiteLLM router, Supabase, realtime sync
└── services/            # Cloudflare R2 storage

apps/web/                # Next.js 15 (108+ TS files)
app/                     # Tauri v2 + Svelte 5 desktop scaffold
tests/unit/              # 120+ pytest tests
docs/v3/                 # Active roadmap + checklist
```

## Critical Rules

1. **No `time.sleep()`** — use `asyncio.sleep()` or `self.set_timer()`
2. **No `asyncio.run()` in Textual** — Textual has its own event loop
3. **No blocking I/O in `compose()`** — use `on_mount()`
4. **Lazy imports** for torch, librosa, faiss, demucs, transformers
5. **Use `litellm_router.chat_completion()`** — not direct SDK calls
6. **AI models:** claude-sonnet-4-6, gpt-4o, gemini-2.5-flash, qwen2.5-coder:7b
7. **API code** is at `interfaces/api/` — NOT `src/samplemind/api/`
8. **Active docs** are in `docs/v3/` — NOT `docs/02-ROADMAPS/`
9. **Type annotations required** on all new functions (mypy strict)
10. **Always run tests** before committing: `pytest tests/unit/ -v --tb=short`

## PR Conventions

- Title: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:` prefix
- Always run `ruff check src/ && mypy src/` before committing
- Update `docs/v3/CHECKLIST.md` when completing checklist items
- Do not remove or modify unrelated tests
