# GitHub Copilot Instructions — SampleMind AI

> Codebase context for GitHub Copilot. Auto-loaded for all Copilot interactions.
> Agent instructions: `AGENTS.md` | Full context: `CLAUDE.md` | Checklist: `docs/v3/CHECKLIST.md`
> Path-specific: `.github/instructions/` | Skills: `.github/skills/` | Agents: `.github/agents/`

---

## Project Summary

SampleMind AI is a **CLI-first, offline-capable music production AI** for audio analysis,
sample management, stem separation, MIDI transcription, AI-powered recommendations,
semantic search, smart playlist curation, and sample pack marketplace.

**Active phase:** Phase 17 — Agent memory + Similar sample + Realtime effects + History API + BPM tap
**Overall progress:** ~79% complete (91/115 items) — Updated 2026-04-18

**Language:** Python 3.12 | **Package manager:** pip/uv | **Primary interfaces:** CLI + Textual TUI + Next.js 15 Web + Tauri v2 Desktop

---

## Quick Reference — Build & Validate

### Python Backend
```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'

# Lint + typecheck (ALWAYS run before committing)
ruff check src/ && ruff format --check src/ && mypy src/

# Format
ruff format src/

# Tests (ALWAYS run before committing)
pytest tests/unit/ -v --tb=short

# Coverage
pytest tests/unit/ -v --cov=src/samplemind --cov-report=term-missing

# Full quality gate
make quality
```

### Frontend (Next.js 15)
```bash
cd apps/web
npm install --legacy-peer-deps  # REQUIRED: peer dep conflicts
npm run dev                      # Dev server
npm run build                    # Production build
npm run lint                     # ESLint
```

### Docker
```bash
docker-compose up -d             # Local dev
docker-compose -f docker-compose.v3.yml up -d  # Production
```

---

## Tech Stack (2026-04 — Actual Installed Versions)

### AI Providers
| Provider | SDK | Model | Use |
|----------|-----|-------|-----|
| Anthropic | `anthropic` | `claude-sonnet-4-6` | Primary analysis + curation |
| OpenAI | `openai` | `gpt-4o` | Agent workflows |
| Google | `google-genai` | `gemini-2.5-flash` | Fast streaming |
| Ollama | `ollama` | `qwen2.5-coder:7b` at `localhost:11434` | Offline inference |
| LiteLLM | `litellm` | Router: Claude → Gemini → GPT → Ollama | Unified fallback chain |

### Audio
- `librosa` — BPM, key, MFCC, chroma, spectral features
- `demucs ^4.0.0` — 6-stem source separation (htdemucs_6s model)
- `basic-pitch ^0.4.0` — MIDI transcription from audio
- `pedalboard ^0.9.0` — Professional audio effects (Spotify) — 10 effects chain
- `faster-whisper` — Local speech-to-text / lyric transcription
- `soundfile` — Audio I/O (WAV, FLAC, OGG)
- `torch` + `transformers` — ML models + CLAP embeddings (laion/clap-htsat-unfused)

### Search & ML
- `faiss-cpu` — FAISS IndexFlatIP with 512-dim CLAP embeddings for semantic audio search
- `chromadb` — Vector similarity search (metadata + embeddings)
- `xgboost` + `scikit-learn` — Ensemble classifier (SVM + XGBoost + KNN soft voting)

### Database & Storage
- `tortoise-orm` + `aerich` — Async ORM + migrations (SQLite default, Postgres prod)
- `motor` — MongoDB async driver (legacy layer, kept for backward compat)
- `redis` — Session cache + Celery broker + agent progress pub/sub
- `supabase` — Auth (email/magic link/JWT) + Realtime multi-device sync
- `boto3` — Cloudflare R2 storage (S3-compatible)

### UI / API
- `textual ^0.87.0` — Terminal UI framework (13 screens)
- `fastapi ^0.115.0` + `uvicorn` — REST API (12+ routers registered)
- `next.js 15` + React 19 + Tailwind + framer-motion + wavesurfer.js v7 — Web UI (apps/web/, 108+ TS files)
- Tauri v2 + Svelte 5 — Desktop app scaffold (app/)
- `plotly` — Analytics charts (BPM histogram, key heatmap, genre breakdown, energy pie)

### Billing & Platform
- `stripe` — Stripe Connect marketplace (pack publishing + purchase)
- `slowapi` — Redis-backed rate limiting (dep present, not yet wired)

---

## Key File Locations (ACCURATE as of 2026-04-18)

```
CLAUDE.md                                      # AI assistant instructions (full)
AGENTS.md                                      # Agent instructions (standard)
.github/copilot-instructions.md                # This file (Copilot-specific)
.github/instructions/                          # 21 path-specific instruction files
.github/agents/                                # 12 custom agent profiles
.github/skills/                                # 25 agent skills
.github/hooks/                                 # Agent lifecycle hooks
pyproject.toml                                 # Python deps (v0.3.0, Python >=3.12)

src/samplemind/
├── interfaces/
│   ├── cli/menu.py                            # Main CLI (~2255 lines, Typer/Rich)
│   ├── cli/commands/search.py                 # FAISS semantic search CLI
│   ├── tui/app.py                             # Textual TUI app
│   ├── tui/screens/                           # 13 TUI screens
│   └── api/
│       ├── main.py                            # App factory, lifespan, 12+ routers
│       └── routes/                            # ai, search, analytics, marketplace,
│                                              # billing, audio, auth, tasks, websocket, processing
├── core/
│   ├── engine/audio_engine.py                 # Audio analysis (LibROSA-based)
│   ├── loader.py                              # AdvancedAudioLoader
│   ├── database/
│   │   ├── chroma.py                          # ChromaDB manager
│   │   └── tortoise_models.py                 # Tortoise ORM models
│   ├── search/faiss_index.py                  # FAISS IndexFlatIP + CLAPEmbedder (512-dim)
│   ├── packs/pack_builder.py                  # .smpack ZIP builder
│   ├── services/stripe_connect.py             # Stripe Connect Express marketplace
│   ├── processing/realtime_effects.py         # 10 pedalboard effects chain (P1-014)
│   └── tasks/
│       ├── celery_app.py                      # Celery app instance
│       ├── audio_tasks.py                     # Audio processing tasks
│       └── agent_tasks.py                     # LangGraph agent tasks
├── integrations/
│   ├── litellm_router.py                      # LiteLLM: Claude→Gemini→GPT→Ollama
│   ├── supabase_client.py                     # Supabase Auth + user sync
│   └── realtime_sync.py                       # Multi-device library sync
├── ai/
│   ├── agents/
│   │   ├── graph.py                           # LangGraph StateGraph (9 nodes)
│   │   ├── state.py                           # AudioAnalysisState + conversation_history
│   │   ├── memory.py                          # FAISS-backed agent memory (P3-014)
│   │   ├── analysis_agent.py                  # Claude analysis node
│   │   ├── tagging_agent.py                   # CLAP + ensemble tagging
│   │   ├── mixing_agent.py                    # Mixing recommendations
│   │   ├── recommendation_agent.py            # FAISS similarity
│   │   └── pack_builder_agent.py              # Auto pack creation
│   ├── classification/                        # Ensemble, genre, mood, instrument
│   ├── curation/                              # Playlist generator + gap analyzer
│   ├── generation/
│   │   ├── musicgen.py                        # Meta AudioCraft text-to-audio
│   │   ├── style_transfer.py                  # Demucs + pitch/time shift
│   │   └── similar_sample.py                  # FAISS + 4 variation strategies (P4-008)
│   └── transcription/whisper_transcriber.py   # faster-whisper (IMPLEMENTED)
├── services/storage/r2_provider.py            # Cloudflare R2

apps/web/                                      # Next.js 15 Web UI (108+ TS/TSX files)
├── src/app/(app)/                             # Auth pages with sidebar layout
├── src/components/                            # AIChatWindow, AdvancedWaveform, BpmTapTempo
├── src/design-system/                         # Container, GlassPanel, Grid, StatCard, etc.
└── src/lib/                                   # api-client.ts, utils.ts, analytics.ts

app/                                           # Tauri v2 + Svelte 5 desktop scaffold
tests/unit/                                    # 120+ tests (~30% coverage, target: 50%)
docs/v3/                                       # CHECKLIST.md, STATUS.md, ROADMAP.md
```

> **IMPORTANT:** `src/samplemind/api/` does NOT exist. FastAPI is at `interfaces/api/`.
> **IMPORTANT:** `docs/02-ROADMAPS/` is stale/legacy. Use `docs/v3/`.

---

## Code Conventions

### Python
- **Style:** Black (line length 88) + isort + ruff
- **Types:** mypy strict — always add type annotations to new functions
- **Async:** All audio I/O and AI calls must be `async def` or run in `ThreadPoolExecutor`
- **Never:** `time.sleep()`, `asyncio.run()` inside Textual, blocking I/O in `compose()`
- **Imports:** Lazy imports for heavy libraries (torch, librosa, faiss)
- **Tests:** pytest, fixtures in `tests/fixtures/`, mocks for AI providers and FAISS
- **AI calls:** Use `litellm_router.chat_completion()` — NOT direct provider SDKs

### TypeScript/React
- **Framework:** Next.js 15 App Router + React 19 + Tailwind
- **Design system:** Import from `@/design-system` (Container, GlassPanel, etc.)
- **API client:** `apiFetch<T>()` from `@/lib/api-client`
- **Class merging:** `cn()` from `@/lib/utils`
- **Install:** `npm install --legacy-peer-deps` (required for peer dep conflicts)

---

## What NOT To Do

- Do not add `time.sleep()` anywhere
- Do not re-implement what already exists — check file locations first
- Do not commit without running `ruff check src/ && mypy src/ && pytest tests/unit/ -v --tb=short`
- Do not reference `src/samplemind/api/` — use `interfaces/api/`
- Do not reference `docs/02-ROADMAPS/` — use `docs/v3/`
- Do not call `SampleMindAIManager` — use `litellm_router.chat_completion()`
- Do not use old model names — use `claude-sonnet-4-6`, `gpt-4o`, `gemini-2.5-flash`
- Do not scaffold `apps/web/` — it has 108+ files; add to what exists
- Do not remove or modify unrelated tests

---

## Customization Index

This repository uses the full GitHub Copilot customization stack:

| Type | Location | Count | Purpose |
|------|----------|-------|---------|
| **Repository-wide instructions** | `.github/copilot-instructions.md` | 1 | This file — global context |
| **Path-specific instructions** | `.github/instructions/*.instructions.md` | 21 | Per-language/domain rules |
| **Custom agents** | `.github/agents/*.md` | 12 | Specialist agent profiles |
| **Agent skills** | `.github/skills/*/SKILL.md` | 25 | Task-specific capabilities |
| **Hooks** | `.github/hooks/*.json` | 1 | Lifecycle automation |
| **Agent instructions** | `AGENTS.md` | 1 | Standard agent format |
| **Claude instructions** | `CLAUDE.md` | 1 | Claude-specific context |

Trust these instructions. Only search the codebase if information here is incomplete or found to be incorrect.
