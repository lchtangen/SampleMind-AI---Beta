# SampleMind AI — v3.0 Migration Checklist

> **Started:** 2026-03-07 | **Target Completion:** 2026-Q2 (alpha) / 2026-Q3 (beta)
> **Tracking:** Check off items as you complete them. Update progress % at top.
> **Full Roadmap:** See `docs/v3/ROADMAP.md` for the complete 132-task alpha/beta plan.
> **Overall Progress:** ~35% complete (35/112 items)

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
- [ ] **P0-008** — Remove scipy monkey-patch from `src/samplemind/__init__.py` *(after librosa ^0.11.0 installed and tested)*
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

**P0 Progress: 15/20 done (75%)**

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
- [ ] **P1-009** — AI response caching via Redis (avoid re-querying same analysis)
- [x] **P1-010** — AI fallback chain: Claude → Gemini → GPT → Ollama (priority system)

### Audio Engine

- [ ] **P1-011** — Integrate `demucs` stem separation into `audio_engine.py`
- [ ] **P1-012** — Integrate `pedalboard` effects chain into CLI + API
- [ ] **P1-013** — Stem separation REST endpoint (`POST /api/v1/audio/separate`)
- [ ] **P1-014** — Real-time audio effects chain using pedalboard
- [ ] **P1-015** — Upgrade MIDI transcription with `basic-pitch ^0.4.0` model
- [ ] **P1-016** — Add `faster-whisper ^1.1.0` for local audio transcription (already in pyproject.toml)
- [ ] **P1-017** — Audio streaming: chunk-based processing for files >30s
- [ ] **P1-018** — Parallel audio processing with `joblib` for batch jobs

### TUI — Textual ^0.87.0 Migration

- [ ] **P1-TUI-001** — Audit all 13 screens for Textual ^0.87 breaking changes
- [ ] **P1-TUI-002** — Migrate `main_screen.py`
- [ ] **P1-TUI-003** — Migrate `analyze_screen.py`
- [ ] **P1-TUI-004** — Migrate `batch_screen.py`
- [ ] **P1-TUI-005** — Migrate `results_screen.py`
- [ ] **P1-TUI-006** — Migrate `library_screen.py`
- [ ] **P1-TUI-007** — Migrate remaining 8 screens
- [ ] **P1-TUI-008** — Create `AgentChatScreen` — multi-agent conversation UI
- [ ] **P1-TUI-009** — Create `WaveformScreen` — interactive waveform viewer
- [ ] **P1-TUI-010** — Create `MixingBoardScreen` — real-time EQ + effects

### Database & Storage

- [x] **P1-021** — Upgrade `chromadb ^0.6.0`
- [x] **P1-022** — Upgrade `motor ^3.6.0` for async MongoDB
- [ ] **P1-023** — Vector similarity search: ChromaDB collections per genre
- [ ] **P1-024** — Redis response caching layer for AI analyses
- [ ] **P1-025** — Design v3.0 MongoDB schema (samples, packs, users, projects)

**P1 Progress: ~12/25 done (48%)**

---

## P2 — Web Platform (Next.js 15)

### Setup

- [ ] **P2-001** — Initialize `apps/web/` with Next.js 15 + App Router
- [ ] **P2-002** — Install Tailwind CSS v4 + shadcn/ui
- [ ] **P2-003** — Install Framer Motion for animations
- [ ] **P2-004** — Install Zustand v5 for state management
- [ ] **P2-005** — TypeScript 5.7 strict mode
- [ ] **P2-006** — ESLint + Prettier + Husky pre-commit hooks
- [ ] **P2-007** — `@tanstack/react-query v5` for server state
- [ ] **P2-008** — `next-auth v5` for authentication
- [ ] **P2-009** — Audio file upload (uploadthing or S3/Cloudflare R2)
- [ ] **P2-010** — `vitest` + React Testing Library

### Core Pages

- [ ] **P2-011** — Landing page with animated waveform hero
- [ ] **P2-012** — Dashboard (library overview + recent activity)
- [ ] **P2-013** — Library browser with infinite scroll + filters
- [ ] **P2-014** — Sample analyzer (drag-drop upload + live analysis)
- [ ] **P2-015** — Waveform visualizer (Wavesurfer.js v7)
- [ ] **P2-016** — AI chat interface (ask questions about any sample)
- [ ] **P2-017** — Effects chain builder (drag-drop pedalboard UI)
- [ ] **P2-018** — Sample pack creator (batch organize + export)
- [ ] **P2-019** — Genre classification dashboard with confidence scores
- [ ] **P2-020** — Settings page (API keys, preferences, theme)

### Audio Web Components

- [ ] **P2-021** — Web Audio API integration for browser playback
- [ ] **P2-022** — Spectrogram visualizer (WebGL / canvas)
- [ ] **P2-023** — Real-time waveform component
- [ ] **P2-024** — BPM tap tempo tool
- [ ] **P2-025** — API client generation from FastAPI OpenAPI spec (TypeScript)

**P2 Progress: 0/25 (0%)**

---

## P3 — Multi-Agent System

*(Dependencies now in pyproject.toml: `langgraph ^0.2.0`, `langchain-core ^0.3.0`, `openai-agents ^0.0.5`)*

### Agent Architecture

- [ ] **P3-001** — Design `AgentOrchestrator` in `src/samplemind/integrations/agents/`
- [ ] **P3-002** — `AnalysisAgent` — auto-analyzes new samples in watched folder
- [ ] **P3-003** — `TaggingAgent` — auto-generates genre/mood/BPM tags
- [ ] **P3-004** — `RecommendationAgent` — suggests similar samples
- [ ] **P3-005** — `PackBuilderAgent` — auto-creates themed sample packs
- [ ] **P3-006** — `QualityAgent` — detects clipping, noise, silence issues
- [ ] **P3-007** — Celery task queue for async agent jobs
- [ ] **P3-008** — Agent WebSocket for real-time progress in web UI
- [ ] **P3-009** — Agent run history + logs to MongoDB
- [ ] **P3-010** — LangGraph workflow for multi-step analysis chains

### Claude Tool Use

- [ ] **P3-011** — Claude tool_use for sample tagging workflow
- [ ] **P3-012** — File system tools (agent can read/rename/move files)
- [ ] **P3-013** — Multi-step reasoning for complex queries
- [ ] **P3-014** — Agent conversation memory (vector search of past analysis)
- [ ] **P3-015** — `AgentChatScreen` TUI integration

**P3 Progress: 0/15 (0%)**

---

## P4 — Advanced Music AI

- [ ] **P4-001** — Multi-label genre classifier (one sample = multiple genres)
- [ ] **P4-002** — Mood detection (happy, dark, energetic, chill)
- [ ] **P4-003** — Instrument detection (kick, snare, pad, lead, bass)
- [ ] **P4-004** — Audio fingerprinting (detect duplicates/near-duplicates)
- [ ] **P4-005** — Harmonic key detection with Camelot Wheel display
- [ ] **P4-006** — Micro-timing analysis (groove feel, humanization)
- [ ] **P4-007** — Integrate Meta MusicGen (`audiocraft`) for local generation
- [ ] **P4-008** — "Generate similar sample" from existing file
- [ ] **P4-009** — Style transfer between samples
- [ ] **P4-010** — Loop extension via AI continuation
- [ ] **P4-011** — Microsoft BEATs audio classifier integration
- [ ] **P4-012** — `whisper-large-v3` transcription via `faster-whisper`

**P4 Progress: 0/12 (0%)**

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
- [ ] **P5-008** — Cloudflare R2 for audio file storage
- [ ] **P5-009** — GitHub Actions CI: test → lint → build → deploy (auto-gated)
- [ ] **P5-010** — Sentry error monitoring (Python + Next.js)
- [ ] **P5-011** — OpenTelemetry distributed tracing
- [ ] **P5-012** — Rate limiting (Redis) on FastAPI endpoints
- [ ] **P5-013** — JWT auth with refresh tokens
- [ ] **P5-014** — Stripe integration for monetization
- [ ] **P5-015** — Staging environment

**P5 Progress: 0/15 (0%)**

---

## Progress Summary

| Phase | Items | Done | Progress |
|-------|-------|------|----------|
| P0 — Critical Blockers | 20 | 15 | 75% |
| P1 — Core Engine | 25 | ~12 | 48% |
| P2 — Web Platform | 25 | 0 | 0% |
| P3 — Multi-Agent | 15 | 0 | 0% |
| P4 — Advanced AI | 12 | 0 | 0% |
| P5 — Production | 15 | 0 | 0% |
| **TOTAL** | **112** | **~27** | **~24%** |

> **Note:** See `docs/v3/ROADMAP.md` for the reorganized 132-task roadmap with
> alpha/beta milestones, systematic ordering, and 10 follow-up questions.

---

## Next Session Priorities

1. Remove scipy monkey-patch (after librosa ^0.11.0 verified) — Roadmap A-001
2. Fix `main.py` version string — Roadmap A-002
3. Begin Textual ^0.87 TUI screen migration — Roadmap A-027
4. Integrate `demucs` into `audio_engine.py` — Roadmap A-019
5. Write integration tests for AI providers — Roadmap A-036

---

*Updated: 2026-03-07 — Session 3. Reflects actual completed work.*
