# SampleMind AI — v3.0 Migration Checklist

> **Started:** 2026-03-07 | **Target Completion:** 2026-Q2
> **Tracking:** Check off items as you complete them. Update progress % at top.
> **Overall Progress:** ~68% complete (~76/112 items) — Updated 2026-04-09
> **Active Phase:** Phase 16 — Web UI completions + Agent pipeline + Production hardening

---

## P0 — Critical Blockers

*All dependency upgrades in pyproject.toml applied. Integration code migrated. Tests written.*

### Dependency Upgrades

- [x] **P0-001** — Upgrade `anthropic` to `^0.40.0` in pyproject.toml
- [x] **P0-002** — Migrate `anthropic_integration.py` — Claude 3.7 Sonnet + extended thinking
- [x] **P0-003** — Upgrade `openai` to `^1.58.0` in pyproject.toml
- [x] **P0-004** — Migrate `openai_integration.py` — GPT-4o default, removed gpt-5
- [x] **P0-005** — Rename `google-generativeai` → `google-genai ^0.8.0` in pyproject.toml
- [x] **P0-006** — Migrate `google_ai_integration.py` — new Client API, Gemini 2.0 Flash
- [x] **P0-007** — Remove `numpy<2.0.0` version cap; upgrade to `>=2.0.0,<3.0.0`
- [x] **P0-008** — Remove scipy monkey-patch from `src/samplemind/__init__.py` *(no monkey-patch found in current codebase — resolved)*
- [x] **P0-009** — Re-enable `basic-pitch ^0.4.0` in pyproject.toml
- [x] **P0-010** — Upgrade `textual ^0.87.0` in pyproject.toml *(screens not yet migrated — see P1-TUI)*

### New Core Audio Libraries

- [x] **P0-011** — Add `demucs ^4.0.0` for 6-stem source separation (htdemucs_6s)
- [x] **P0-012** — Add `pedalboard ^0.9.0` by Spotify for audio effects/processing
- [ ] **P0-013** — Add `audioflux ^0.1.8` for fast FFT/spectrogram/MFCC *(optional — evaluate vs librosa)*
- [x] **P0-014** — Upgrade `torch ^2.5.0` + `torchaudio ^2.5.0` (CUDA 12.x compatible)
- [x] **P0-015** — Upgrade `transformers ^4.47.0` for HuggingFace model loading

### Environment & Build

- [x] **P0-016** — Update `.env.example` with all v3.0 keys (Claude, Gemini 2.0, Ollama)
- [ ] **P0-017** — Upgrade `python-dotenv` to `^1.0.1` *(currently ^1.0.0 — low priority)*
- [x] **P0-018** — Pin Python to `>=3.11,<3.13` in pyproject.toml
- [ ] **P0-019** — Create `docker-compose.v3.yml` with updated service versions *(optional)*
- [x] **P0-020** — Update `Makefile` with v3.0 targets (upgrade-deps, install-dev, install-models)

**P0 Progress: 17/20 done (85%)** *(P0-013 optional, P0-017 low-priority, P0-019 optional)*

---

## P1 — Core Engine Upgrades

### AI Models & Routing

- [x] **P1-001** — `claude-3-7-sonnet-20250219` as primary analysis model
- [x] **P1-002** — `claude-3-5-haiku-20241022` as fast/cheap secondary
- [x] **P1-003** — `gemini-2.0-flash` as primary Gemini model
- [ ] **P1-004** — `gemini-2.0-flash-thinking` for complex reasoning tasks
- [x] **P1-005** — `gpt-4o` as primary OpenAI model
- [x] **P1-006** — `gpt-4o-mini` available for high-volume tasks
- [x] **P1-007** — Ollama offline provider: `qwen2.5:7b-instruct`, `phi3:mini`, `gemma2:2b`
- [x] **P1-008** — AI model auto-selection via `ANALYSIS_ROUTING` dict in `ai_manager.py`
- [x] **P1-009** — AI response caching via Redis (avoid re-querying same analysis)
- [x] **P1-010** — AI fallback chain: Claude → Gemini → GPT → Ollama (priority system)

### Audio Engine

- [x] **P1-011** — Integrate `demucs` stem separation into `audio_engine.py`
- [x] **P1-012** — Integrate `pedalboard` effects chain into CLI + API
- [x] **P1-013** — Stem separation REST endpoint (`POST /api/v1/audio/separate`)
- [ ] **P1-014** — Real-time audio effects chain using pedalboard
- [x] **P1-015** — Upgrade MIDI transcription with `basic-pitch ^0.4.0` model
- [x] **P1-016** — Add `faster-whisper ^1.1.0` for local audio transcription — `ai/transcription/whisper_transcriber.py` implemented
- [ ] **P1-017** — Audio streaming: chunk-based processing for files >30s
- [ ] **P1-018** — Parallel audio processing with `joblib` for batch jobs

### TUI — Textual ^0.87.0 Migration

- [x] **P1-TUI-001** — Audit all 13 screens for Textual ^0.87 breaking changes (all screens already ^0.87 compatible)
- [x] **P1-TUI-002** — Migrate `main_screen.py`
- [x] **P1-TUI-003** — Migrate `analyze_screen.py`
- [x] **P1-TUI-004** — Migrate `batch_screen.py`
- [x] **P1-TUI-005** — Migrate `results_screen.py`
- [x] **P1-TUI-006** — Migrate `library_screen.py`
- [x] **P1-TUI-007** — Migrate remaining 8 screens
- [x] **P1-TUI-008** — `AIChatScreen` exists (agent chat UI with multi-provider support)
- [x] **P1-TUI-009** — `VisualizerScreen` exists (waveform + spectrum + mel + chroma)
- [x] **P1-TUI-010** — `ChainScreen` exists (effects chain builder with pedalboard)

### Database & Storage

- [x] **P1-021** — Upgrade `chromadb ^0.6.0`
- [x] **P1-022** — Upgrade `motor ^3.6.0` for async MongoDB
- [x] **P1-023** — Vector similarity search: FAISS IndexFlatIP + CLAPEmbedder in `core/search/faiss_index.py`
- [x] **P1-024** — Redis response caching layer for AI analyses
- [x] **P1-025** — v3.0 schema via Tortoise ORM: `TortoiseUser/Sample/Library/Pack/Playlist` in `core/database/tortoise_models.py`

**P1 Progress: 24/25 done (96%)** *(P1-017 and P1-018 deferred; P1-004 optional)*

---

## P2 — Web Platform (Next.js 15)

### Setup

- [x] **P2-001** — Initialize `apps/web/` with Next.js 15 + App Router (108 TS/TSX files present)
- [x] **P2-002** — Install Tailwind CSS v4 + shadcn/ui
- [x] **P2-003** — Install Framer Motion for animations
- [ ] **P2-004** — Install Zustand v5 for state management
- [x] **P2-005** — TypeScript strict mode
- [ ] **P2-006** — ESLint + Prettier + Husky pre-commit hooks
- [ ] **P2-007** — `@tanstack/react-query v5` for server state
- [ ] **P2-008** — `next-auth v5` for authentication
- [x] **P2-009** — Audio file upload — upload page exists (`src/app/upload/page.tsx`)
- [ ] **P2-010** — `vitest` + React Testing Library

### Core Pages

- [x] **P2-011** — Landing page with animated waveform hero (`src/app/page.tsx`)
- [x] **P2-012** — Dashboard (library overview + recent activity) (`src/app/dashboard/page.tsx`)
- [x] **P2-013** — Library browser (`src/app/library/page.tsx`)
- [x] **P2-014** — Sample analyzer upload + analysis (`src/app/upload/page.tsx`, `analysis/[id]/page.tsx`)
- [x] **P2-015** — Waveform visualizer — `AdvancedWaveform.tsx` uses wavesurfer.js v7
- [x] **P2-016** — AI chat interface — `AIChatWindow.tsx` component built
- [ ] **P2-017** — Effects chain builder (drag-drop pedalboard UI)
- [x] **P2-018** — Sample pack creator / collections (`src/app/collections/page.tsx`)
- [ ] **P2-019** — Genre classification dashboard with confidence scores
- [x] **P2-020** — Settings page (`src/app/settings/page.tsx` + profile/api-keys/cloud sub-pages)

### Audio Web Components

- [x] **P2-021** — Web Audio API integration — `AudioControls.tsx` + `AudioAnalysisVisualizer.tsx`
- [x] **P2-022** — Spectrogram visualizer — `AudioAnalysisVisualizer.tsx` (WebGL canvas via Three.js)
- [x] **P2-023** — Real-time waveform component — `AdvancedWaveform.tsx`
- [ ] **P2-024** — BPM tap tempo tool
- [ ] **P2-025** — API client module (`apps/web/src/lib/`) — **MISSING, next to implement**

**P2 Progress: ~16/25 done (64%)** *(P2-025 is next priority: Step 3 of active plan)*

---

## P3 — Multi-Agent System

*(Dependencies now in pyproject.toml: `langgraph ^0.2.0`, `langchain-core ^0.3.0`, `openai-agents ^0.0.5`)*

### Agent Architecture

- [x] **P3-001** — `AgentOrchestrator` via LangGraph `build_graph()` in `ai/agents/graph.py` (210 lines)
- [x] **P3-002** — `AnalysisAgent` — `analysis_agent.py` (Claude tool_use + AudioEngine)
- [x] **P3-003** — `TaggingAgent` — `tagging_agent.py` (CLAP + ensemble, 147 lines)
- [x] **P3-004** — `RecommendationAgent` — `recommendation_agent.py` (FAISS similarity)
- [x] **P3-005** — `PackBuilderAgent` — `pack_builder_agent.py`
- [ ] **P3-006** — `QualityAgent` — detects clipping, noise, silence issues
- [ ] **P3-007** — Celery task queue for async agent jobs — **MISSING `agent_tasks.py`** (Step 6)
- [ ] **P3-008** — Agent WebSocket for real-time progress — **MISSING `/ws/agent/{task_id}`** (Step 7)
- [ ] **P3-009** — Agent run history + logs to MongoDB
- [x] **P3-010** — LangGraph `StateGraph` with 6 nodes (router→analysis→tagging→mixing→recommend→aggregator)

### Claude Tool Use

- [x] **P3-011** — Claude tool_use for analysis in `analysis_agent.py`
- [x] **P3-012** — File system path handling in `router_node`
- [x] **P3-013** — Multi-step pipeline via LangGraph edges
- [ ] **P3-014** — Agent conversation memory (vector search of past analysis)
- [x] **P3-015** — `AIChatScreen` TUI integration (already exists in tui/screens/)

**P3 Progress: ~9/15 done (60%)** *(agent_tasks.py + WebSocket + QualityAgent + memory still needed)*

---

## P4 — Advanced Music AI

- [x] **P4-001** — Multi-label genre classifier — `ai/classification/multi_label_genre.py` (400+ taxonomy)
- [x] **P4-002** — Mood detection — `ai/classification/mood_detector.py` (Russell circumplex)
- [x] **P4-003** — Instrument detection — `ai/classification/instrument_detector.py` (128-class GM)
- [ ] **P4-004** — Audio fingerprinting (detect duplicates/near-duplicates)
- [x] **P4-005** — Harmonic key detection with Camelot Wheel — in `ai/curation/playlist_generator.py`
- [ ] **P4-006** — Micro-timing analysis (groove feel, humanization)
- [x] **P4-007** — Meta MusicGen — `ai/generation/musicgen.py` (AudioCraft + mock WAV fallback)
- [ ] **P4-008** — "Generate similar sample" from existing file
- [x] **P4-009** — Style transfer — `ai/generation/style_transfer.py` (demucs + librosa)
- [ ] **P4-010** — Loop extension via AI continuation
- [ ] **P4-011** — Microsoft BEATs audio classifier integration
- [x] **P4-012** — `whisper-large-v3` transcription — `ai/transcription/whisper_transcriber.py` (fully implemented)

**P4 Progress: 6/12 done (50%)**

---

## P5 — Production & Platform

### Testing

- [ ] **P5-001** — Reach 50% test coverage (current: ~30%, 120+ tests)
- [ ] **P5-002** — Reach 80% test coverage (target)
- [ ] **P5-003** — Integration tests for all API endpoints
- [ ] **P5-004** — E2E tests with Playwright for web UI
- [ ] **P5-005** — Performance benchmarks (audio analysis latency targets)

### DevOps

- [ ] **P5-006** — Vercel deployment for Next.js
- [ ] **P5-007** — Render/Railway for FastAPI backend
- [x] **P5-008** — Cloudflare R2 — `services/storage/r2_provider.py` (boto3 S3-compatible)
- [ ] **P5-009** — GitHub Actions CI: coverage gate + apps/web build *(Step 10 of active plan)*
- [ ] **P5-010** — Sentry error monitoring (Python + Next.js)
- [ ] **P5-011** — OpenTelemetry distributed tracing
- [ ] **P5-012** — Rate limiting (Redis) — `slowapi` in deps, not yet wired *(Step 9 of active plan)*
- [x] **P5-013** — JWT auth + Supabase session — `integrations/supabase_client.py`
- [x] **P5-014** — Stripe Connect marketplace — `core/services/stripe_connect.py` + `routes/marketplace.py`
- [ ] **P5-015** — Staging environment

**P5 Progress: 3/15 done (20%)**

---

## Progress Summary

| Phase | Items | Done | Progress |
|-------|-------|------|----------|
| P0 — Critical Blockers | 20 | 17 | 85% |
| P1 — Core Engine | 25 | 24 | 96% |
| P2 — Web Platform | 25 | ~16 | 64% |
| P3 — Multi-Agent | 15 | ~9 | 60% |
| P4 — Advanced AI | 12 | 6 | 50% |
| P5 — Production | 15 | 3 | 20% |
| **TOTAL** | **112** | **~75** | **~67%** |

---

## Active Phase 16 — Next Priorities

1. `apps/web/src/lib/` — TypeScript API client + `endpoints.ts` (Step 3)
2. `apps/web/src/app/search/` — Semantic search page (Step 4)
3. `apps/web/src/app/analytics/` — Plotly analytics page (Step 5)
4. `core/tasks/agent_tasks.py` + `POST /tasks/analyze-agent` (Step 6)
5. `/ws/agent/{task_id}` WebSocket progress endpoint (Step 7)
6. 5 new unit test files → 50% coverage (Step 8)
7. `slowapi` rate limiting wired into `main.py` (Step 9)
8. GitHub Actions CI coverage gate + `apps/web` build (Step 10)

---

*Updated: 2026-04-09 — Phase 16 active. Reflects actual completed work from all prior sessions.*
