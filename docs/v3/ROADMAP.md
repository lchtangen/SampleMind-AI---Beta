# 🚀 SampleMind AI — v3.0 Release Roadmap

> **Alpha & Beta Release Plan with Systematic Task Ordering**

**Last Updated:** 2026-03-17 (Session 4 — Full review & modernization)
**Version:** `2.1.0-beta` → `3.0.0-alpha` → `3.0.0-beta` → `3.0.0`
**Repository:** [lchtangen/SampleMind-AI---Beta](https://github.com/lchtangen/SampleMind-AI---Beta)

---

## 📋 Executive Summary

SampleMind AI is a **CLI-first, offline-capable music production AI** platform. This roadmap defines every task needed to reach **alpha** (core feature-complete, developer-ready) and **beta** (user-ready, polished, production-stable) releases.

**Current State (2026-03-17):**
- ✅ Foundation complete (Phases 1–14)
- ✅ All dependency upgrades applied (P0/P1/P2 in pyproject.toml)
- ✅ All 4 AI providers migrated (Claude 3.7, Gemini 2.0, GPT-4o, Ollama)
- ⚠️ TUI screens need Textual ^0.87 migration
- ⚠️ Web UI not scaffolded
- ⚠️ Test coverage at ~30% (target 80%)
- ⚠️ Agent framework packages installed but not integrated

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    SampleMind AI v3.0                     │
├──────────┬──────────┬──────────┬────────────────────────┤
│   CLI    │   TUI    │ REST API │       Web UI           │
│  (Rich)  │(Textual) │(FastAPI) │   (Next.js 15)         │
├──────────┴──────────┴──────────┴────────────────────────┤
│                  Service Layer                           │
│  AudioEngine │ AIManager │ PackCreator │ VectorSearch    │
├─────────────────────────────────────────────────────────┤
│               AI Provider Router                         │
│  Claude 3.7 │ Gemini 2.0 │ GPT-4o │ Ollama (offline)   │
├─────────────────────────────────────────────────────────┤
│              Agent Orchestration                         │
│  LangGraph │ OpenAI Agents │ Custom Agents              │
├─────────────────────────────────────────────────────────┤
│                Audio Processing                          │
│  librosa │ demucs │ pedalboard │ basic-pitch │ torch    │
├─────────────────────────────────────────────────────────┤
│                  Data Layer                               │
│  MongoDB (motor) │ Redis │ ChromaDB │ SQLAlchemy         │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack (v3.0)

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.11–3.12 |
| **Package Manager** | Poetry | 1.8+ |
| **AI — Primary** | Anthropic (Claude 3.7 Sonnet) | `anthropic ^0.84.0` |
| **AI — Fast** | Google (Gemini 2.0 Flash) | `google-genai ^1.56.0` |
| **AI — Agents** | OpenAI (GPT-4o) | `openai ^2.0.0` |
| **AI — Offline** | Ollama (qwen2.5:7b) | `ollama ^0.4.0` |
| **Audio Analysis** | librosa | `^0.11.0` |
| **Stem Separation** | demucs (Meta) | `^4.0.0` |
| **Audio Effects** | pedalboard (Spotify) | `^0.9.0` |
| **MIDI** | basic-pitch | `^0.4.0` |
| **ML** | PyTorch + transformers | `^2.8.0` / `^4.47.0` |
| **Web Framework** | FastAPI | `^0.135.0` |
| **CLI** | Rich + Typer + Click | Latest |
| **TUI** | Textual | `^0.87.0` |
| **Web UI** | Next.js 15 + React 19 | Latest |
| **Database** | MongoDB (Motor) + Redis + ChromaDB | Latest |
| **Orchestration** | LangGraph + LangChain Core | `^1.0.0` |

---

## 🎯 RELEASE MILESTONES

### v3.0.0-alpha (Target: 2026-Q2)
> Core feature-complete. All systems functional. Developer-ready for testing.

**Gate Criteria:**
- [ ] All AI providers working with new SDKs (verified with integration tests)
- [ ] Audio engine: analysis + stem separation + effects chain functional
- [ ] CLI + TUI fully working on Textual ^0.87
- [ ] REST API endpoints functional with auth
- [ ] Test coverage ≥ 50%
- [ ] Documentation current and accurate

### v3.0.0-beta (Target: 2026-Q3)
> User-ready. Polished UI. Production-stable. Community feedback period.

**Gate Criteria:**
- [ ] Web UI (Next.js 15) live with core pages
- [ ] Multi-agent system functional (LangGraph workflows)
- [ ] Test coverage ≥ 80%
- [ ] Performance benchmarks met (BPM < 2s, search < 100ms)
- [ ] CI/CD pipeline: test → lint → build → deploy (auto-gated)
- [ ] Security audit passed (bandit + safety + secret scanning)
- [ ] User onboarding flow complete

### v3.0.0 (Target: 2026-Q4)
> Production release. Marketplace-ready. Cloud deployment.

**Gate Criteria:**
- [ ] Cloud deployment (Vercel + Railway/Render)
- [ ] User accounts + cloud sync
- [ ] DAW plugins v2 (VST3/AU native)
- [ ] Sample marketplace MVP
- [ ] E2E test suite passing
- [ ] Performance regression tests in CI

---

## 📋 SYSTEMATIC TASK LIST

> Tasks ordered by dependency chain. Complete top-to-bottom within each milestone.
> Each task has a unique ID for tracking in issues/PRs.

---

## 🔴 MILESTONE 1: ALPHA FOUNDATION (Weeks 1–4)
> *Stabilize the core, fix what exists, make everything work*

### M1.1 — Code Cleanup & Foundation

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-001 | Remove scipy monkey-patch from `__init__.py` (verify librosa ^0.11.0 works) | P0 | ⏳ | 1h |
| A-002 | Fix `main.py` version string — replace "v6" with "3.0.0-alpha" | P0 | ⏳ | 30m |
| A-003 | Fix `interfaces/__init__.py` — remove "v6" references | P0 | ⏳ | 30m |
| A-004 | Consolidate duplicate cache dirs (`core/cache/` + `core/caching/` → `CacheManager`) | P1 | ⏳ | 3h |
| A-005 | Refactor `core/loader.py` (28 KB monolith) into `core/loading/` submodules | P1 | ⏳ | 4h |
| A-006 | Fix hardcoded absolute paths in scripts (replace with `$(git rev-parse --show-toplevel)`) | P1 | ⏳ | 2h |
| A-007 | Clean `.gitignore` — exclude `*.wav` test files, debug scripts | P2 | ⏳ | 1h |
| A-008 | Implement stub `__init__.py` files (`ai/classification/`, `ai/mastering/`, `core/generation/`) | P2 | ⏳ | 2h |
| A-009 | Verify Python 3.12 full compatibility (`match/case`, `tomllib`, `typing.override`) | P2 | ⏳ | 2h |
| A-010 | Run `poetry install` end-to-end — resolve all dependency conflicts | P0 | ⏳ | 2h |

### M1.2 — AI Engine Integration

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-011 | Verify Anthropic integration — Claude 3.7 Sonnet + extended thinking works end-to-end | P0 | ⏳ | 2h |
| A-012 | Verify Google integration — Gemini 2.0 Flash via `google-genai` works end-to-end | P0 | ⏳ | 2h |
| A-013 | Verify OpenAI integration — GPT-4o via `openai ^2.0.0` works end-to-end | P0 | ⏳ | 2h |
| A-014 | Verify Ollama integration — offline inference with qwen2.5:7b works | P0 | ⏳ | 1h |
| A-015 | Test AI fallback chain: Claude → Gemini → GPT-4o → Ollama | P0 | ⏳ | 2h |
| A-016 | Implement AI response caching via Redis (avoid re-querying same analysis) | P1 | ⏳ | 4h |
| A-017 | Add `gemini-2.0-flash-thinking` for complex reasoning tasks | P2 | ⏳ | 2h |
| A-018 | Add GPT-4o audio modality (`gpt-4o-audio-preview`) for direct audio understanding | P2 | ⏳ | 3h |

### M1.3 — Audio Engine Upgrades

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-019 | Integrate demucs stem separation into `audio_engine.py` | P0 | ⏳ | 4h |
| A-020 | Add stem separation REST endpoint (`POST /api/v1/audio/separate`) | P0 | ⏳ | 3h |
| A-021 | Integrate pedalboard effects chain into CLI + API | P0 | ⏳ | 4h |
| A-022 | Verify basic-pitch MIDI transcription works with ^0.4.0 | P1 | ⏳ | 2h |
| A-023 | Add `faster-whisper ^1.1.0` transcription pipeline | P1 | ⏳ | 3h |
| A-024 | Audio streaming — chunk-based processing for files > 30s | P2 | ⏳ | 4h |
| A-025 | Parallel audio processing with `joblib` for batch jobs | P2 | ⏳ | 3h |
| A-026 | Audio format conversion engine (WAV ↔ FLAC ↔ MP3 ↔ OGG) | P2 | ⏳ | 3h |

### M1.4 — TUI Migration (Textual ^0.87)

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-027 | Audit all 15 TUI screens for Textual ^0.87 breaking changes | P0 | ⏳ | 3h |
| A-028 | Migrate `main_screen.py` | P0 | ⏳ | 2h |
| A-029 | Migrate `analyze_screen.py` | P0 | ⏳ | 2h |
| A-030 | Migrate `batch_screen.py` | P0 | ⏳ | 2h |
| A-031 | Migrate `results_screen.py` | P0 | ⏳ | 2h |
| A-032 | Migrate `library_screen.py` | P0 | ⏳ | 2h |
| A-033 | Migrate remaining 10 screens (search, favorites, settings, comparison, tagging, performance, chain, classification, ai_chat, visualizer) | P1 | ⏳ | 8h |
| A-034 | Verify all 6 custom themes work on ^0.87 | P1 | ⏳ | 2h |
| A-035 | Fix command palette (`/` key) on new Textual version | P2 | ⏳ | 1h |

### M1.5 — Testing & Quality (Alpha Gate)

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-036 | Write integration tests for all 4 AI providers (mock API responses) | P0 | ⏳ | 4h |
| A-037 | Write unit tests for audio engine (BPM, key, spectral, stem separation) | P0 | ⏳ | 4h |
| A-038 | Write API endpoint tests (auth, upload, analyze, search) | P1 | ⏳ | 4h |
| A-039 | Write CLI tests (menu navigation, analyze command, batch) | P1 | ⏳ | 3h |
| A-040 | Reach 50% test coverage | P0 | ⏳ | 8h |
| A-041 | Run `make validate` — fix all lint, type, and security issues | P0 | ⏳ | 4h |
| A-042 | Update GitHub Actions CI — matrix: Python 3.11 + 3.12, Ubuntu + macOS | P1 | ⏳ | 3h |

**M1 Total: 42 tasks | Est. ~120 hours**

---

## 🟠 MILESTONE 2: ALPHA POLISH (Weeks 5–8)
> *Advanced features, agent system, deeper audio intelligence*

### M2.1 — Multi-Agent System

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-043 | Design `AgentOrchestrator` in `src/samplemind/integrations/agents/` | P0 | ⏳ | 4h |
| A-044 | Build `AnalysisAgent` — auto-analyzes new samples in watched folder | P0 | ⏳ | 4h |
| A-045 | Build `TaggingAgent` — auto-generates genre/mood/BPM tags | P1 | ⏳ | 4h |
| A-046 | Build `RecommendationAgent` — suggests similar samples | P1 | ⏳ | 4h |
| A-047 | Build `PackBuilderAgent` — auto-creates themed sample packs | P2 | ⏳ | 4h |
| A-048 | Build `QualityAgent` — detects clipping, noise, silence issues | P2 | ⏳ | 3h |
| A-049 | LangGraph workflow for multi-step analysis chains | P1 | ⏳ | 4h |
| A-050 | Claude tool_use for sample tagging workflow | P1 | ⏳ | 3h |
| A-051 | Agent WebSocket for real-time progress in TUI/web | P2 | ⏳ | 3h |
| A-052 | Agent run history + logs to MongoDB | P2 | ⏳ | 3h |

### M2.2 — Advanced Audio Intelligence

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-053 | Add CLAP audio embeddings (zero-shot classification) → ChromaDB | P1 | ⏳ | 4h |
| A-054 | Add BEATs audio foundation model (527 AudioSet categories) | P1 | ⏳ | 4h |
| A-055 | Add Audio Spectrogram Transformer (AST) for genre/instrument classification | P2 | ⏳ | 4h |
| A-056 | Multi-label genre classifier (400+ genre taxonomy) | P1 | ⏳ | 4h |
| A-057 | Mood/emotion detection (valence + arousal, Russell circumplex) | P1 | ⏳ | 3h |
| A-058 | Instrument detection (128 MIDI GM classes, OpenMIC-2018) | P2 | ⏳ | 4h |
| A-059 | Audio fingerprinting (Chromaprint-style duplicate detection) | P2 | ⏳ | 4h |
| A-060 | Harmonic key detection with Camelot Wheel display | P1 | ⏳ | 3h |

### M2.3 — Database & Storage

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-061 | Implement full `core/database/` module (mongo_client, redis_client, chroma_client) | P0 | ⏳ | 4h |
| A-062 | Build Beanie ODM models (`AudioSample(Document)` with all analysis fields) | P0 | ⏳ | 4h |
| A-063 | Vector similarity search — ChromaDB collections per genre | P1 | ⏳ | 3h |
| A-064 | Redis response caching layer for AI analyses (TTL: analysis=30d, AI=7d) | P1 | ⏳ | 3h |
| A-065 | Design v3.0 MongoDB schema (samples, packs, users, projects) | P1 | ⏳ | 3h |

### M2.4 — New TUI Screens & Widgets

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| A-066 | Create `AgentChatScreen` — multi-agent conversation UI | P1 | ⏳ | 4h |
| A-067 | Create `WaveformScreen` — interactive waveform viewer (textual-plotext) | P1 | ⏳ | 4h |
| A-068 | Create `MixingBoardScreen` — real-time EQ + effects | P2 | ⏳ | 4h |
| A-069 | Build widget library: waveform, spectrum, sample_card, bpm_wheel, ai_chat_panel | P1 | ⏳ | 6h |
| A-070 | TUI Status bar (always-visible): active model, library size, API status | P2 | ⏳ | 2h |

**M2 Total: 28 tasks | Est. ~100 hours**

---

## 🟢 MILESTONE 3: BETA FOUNDATION (Weeks 9–14)
> *Web UI, production hardening, user-facing quality*

### M3.1 — Web UI (Next.js 15 + React 19)

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-001 | Initialize `apps/web/` with Next.js 15 + App Router + Turbopack | P0 | ⏳ | 3h |
| B-002 | Install Tailwind CSS v4 + shadcn/ui component library | P0 | ⏳ | 2h |
| B-003 | Install TypeScript 5.7 strict + ESLint + Prettier | P0 | ⏳ | 1h |
| B-004 | Install Zustand v5 (state) + TanStack Query v5 (server state) | P0 | ⏳ | 2h |
| B-005 | Build landing page with animated waveform hero | P0 | ⏳ | 4h |
| B-006 | Build dashboard (library overview + recent activity) | P0 | ⏳ | 4h |
| B-007 | Build library browser with infinite scroll + filters | P1 | ⏳ | 4h |
| B-008 | Build sample analyzer (drag-drop upload + live analysis) | P1 | ⏳ | 4h |
| B-009 | Build waveform visualizer (WaveSurfer.js v7) | P1 | ⏳ | 4h |
| B-010 | Build AI chat interface (model selector, attach audio) | P1 | ⏳ | 4h |
| B-011 | Build effects chain builder (drag-drop pedalboard UI) | P2 | ⏳ | 4h |
| B-012 | Build sample pack creator (batch organize + export) | P2 | ⏳ | 4h |
| B-013 | Build genre classification dashboard | P2 | ⏳ | 3h |
| B-014 | Build settings page (API keys, preferences, theme) | P1 | ⏳ | 3h |
| B-015 | API client generation from FastAPI OpenAPI spec (TypeScript) | P0 | ⏳ | 3h |
| B-016 | Web Audio API integration for browser playback | P1 | ⏳ | 3h |
| B-017 | Real-time analysis progress via WebSocket | P1 | ⏳ | 3h |
| B-018 | Mobile-responsive layout + PWA support | P2 | ⏳ | 4h |
| B-019 | vitest + React Testing Library setup | P1 | ⏳ | 2h |
| B-020 | Dark/light theme with SampleMind design tokens | P1 | ⏳ | 3h |

### M3.2 — Backend Hardening

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-021 | FastAPI full router implementation (analyze, library, search, CRUD, WebSocket) | P0 | ⏳ | 6h |
| B-022 | Rate limiting (slowapi) — per-user limits | P1 | ⏳ | 2h |
| B-023 | Add Redis Pub/Sub for real-time events (analysis complete → UI update) | P1 | ⏳ | 3h |
| B-024 | Add Celery Beat scheduler (nightly re-scan, weekly re-index) | P2 | ⏳ | 3h |
| B-025 | Add OpenTelemetry distributed tracing | P2 | ⏳ | 3h |
| B-026 | JWT auth with refresh tokens | P1 | ⏳ | 3h |
| B-027 | File upload validation (magic bytes, size limits, ClamAV hook) | P1 | ⏳ | 3h |

### M3.3 — Testing & CI/CD (Beta Gate)

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-028 | Reach 80% test coverage | P0 | ⏳ | 16h |
| B-029 | E2E tests with Playwright for web UI | P1 | ⏳ | 6h |
| B-030 | Performance benchmarks in CI (BPM < 2s, search < 100ms, embedding < 5s) | P1 | ⏳ | 4h |
| B-031 | GitHub Actions CI: test → lint → type-check → security → build → deploy | P0 | ⏳ | 4h |
| B-032 | Security audit: bandit + safety + detect-secrets pre-commit | P0 | ⏳ | 3h |
| B-033 | Load testing with Locust (API endpoints, concurrent analysis) | P2 | ⏳ | 3h |

### M3.4 — DAW Plugins v2

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-034 | Improved FL Studio real-time sync | P1 | ⏳ | 4h |
| B-035 | Ableton MIDI clip generation from analysis | P1 | ⏳ | 4h |
| B-036 | Logic Pro integration planning + prototype | P2 | ⏳ | 4h |
| B-037 | JUCE-based VST3 native plugin scaffold | P2 | ⏳ | 6h |

### M3.5 — UX & Design System

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-038 | Create SampleMind design tokens (colors, typography, spacing) | P1 | ⏳ | 3h |
| B-039 | Onboarding flow (first run: library folder → AI mode → API keys → scan) | P1 | ⏳ | 4h |
| B-040 | Animated splash screen for TUI | P2 | ⏳ | 2h |
| B-041 | Responsive TUI for different terminal sizes (80×24, 120×40, 200×60) | P2 | ⏳ | 3h |
| B-042 | WCAG 2.1 AA compliance audit | P2 | ⏳ | 3h |

**M3 Total: 42 tasks | Est. ~160 hours**

---

## 🟣 MILESTONE 4: BETA POLISH (Weeks 15–20)
> *Platform features, marketplace, cloud deployment*

### M4.1 — Platform & Cloud

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-043 | User accounts + authentication (OAuth2: GitHub, Google + magic link) | P0 | ⏳ | 6h |
| B-044 | Cloud storage integration (S3 / Cloudflare R2) with delta sync | P1 | ⏳ | 4h |
| B-045 | Vercel deployment for Next.js frontend | P0 | ⏳ | 3h |
| B-046 | Railway/Render deployment for FastAPI backend | P0 | ⏳ | 3h |
| B-047 | Docker multi-stage build optimization | P1 | ⏳ | 3h |
| B-048 | Staging environment with preview deployments | P1 | ⏳ | 3h |
| B-049 | Sentry error monitoring (Python + Next.js) | P1 | ⏳ | 2h |

### M4.2 — Advanced Features

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-050 | Collaborative collections (share with producers, ratings, stars) | P2 | ⏳ | 6h |
| B-051 | Sample marketplace MVP (browse, upload, download) | P2 | ⏳ | 8h |
| B-052 | Rekordbox / Serato / Traktor cue point export | P2 | ⏳ | 4h |
| B-053 | MCP Server integration (expose as tool for Claude Desktop) | P2 | ⏳ | 4h |
| B-054 | OSC protocol bridge for real-time DAW communication | P2 | ⏳ | 4h |
| B-055 | Numba JIT compilation for DSP hot paths (10x speedup) | P2 | ⏳ | 4h |
| B-056 | Auto-organize: genre/key/BPM/date sorting (move/copy/symlink modes) | P1 | ⏳ | 4h |

### M4.3 — Documentation & Community

| ID | Task | Priority | Status | Est. |
|----|------|----------|--------|------|
| B-057 | Create TESTING.md guide (test structure, coverage goals, mock patterns) | P0 | ⏳ | 3h |
| B-058 | Create TROUBLESHOOTING.md (common errors, solutions, FAQ) | P0 | ⏳ | 3h |
| B-059 | Create MIGRATION_GUIDE.md (v2.0 → v3.0 upgrade path) | P1 | ⏳ | 3h |
| B-060 | Create SECURITY.md (API key best practices, threat model) | P1 | ⏳ | 2h |
| B-061 | Create ENVIRONMENT_SETUP.md (.env variable reference) | P1 | ⏳ | 2h |
| B-062 | OpenAPI spec export + Swagger branding | P2 | ⏳ | 2h |

**M4 Total: 20 tasks | Est. ~80 hours**

---

## 📊 Progress Summary

| Milestone | Tasks | Done | Progress | Target |
|-----------|-------|------|----------|--------|
| M1 — Alpha Foundation | 42 | 0 | 0% | 2026-Q2 Week 4 |
| M2 — Alpha Polish | 28 | 0 | 0% | 2026-Q2 Week 8 |
| M3 — Beta Foundation | 42 | 0 | 0% | 2026-Q3 Week 14 |
| M4 — Beta Polish | 20 | 0 | 0% | 2026-Q3 Week 20 |
| **TOTAL** | **132** | **0** | **0%** | |

> **Note:** Many P0 dependency tasks are already done in pyproject.toml — the tasks above track *integration and verification* of those dependencies.

---

## ⚡ Priority Execution Order (Critical Path)

```
WEEK 1-2:   M1.1 (Code cleanup) + M1.2 (AI verification)
WEEK 3-4:   M1.3 (Audio engine) + M1.4 (TUI migration)
WEEK 5:     M1.5 (Testing to 50%) → ★ ALPHA GATE CHECK
WEEK 6-7:   M2.1 (Agent system) + M2.2 (Audio intelligence)
WEEK 8:     M2.3 (Database) + M2.4 (New TUI screens)
WEEK 9-11:  M3.1 (Web UI scaffold + core pages)
WEEK 12:    M3.2 (Backend hardening)
WEEK 13-14: M3.3 (Testing to 80%) + M3.4 (DAW v2) → ★ BETA GATE CHECK
WEEK 15-17: M4.1 (Platform & cloud deployment)
WEEK 18-20: M4.2 (Advanced features) + M4.3 (Docs) → ★ RELEASE
```

---

## 🛠️ Development Workflow

### Session Checklist

```bash
git pull
source .venv/bin/activate
# Read: docs/v3/STATUS.md + docs/v3/CHECKLIST.md
# Pick next task from this roadmap
# Code → Test → Lint → Commit
make pre-commit   # format + lint + test-fast
# Update: docs/v3/STATUS.md + docs/v3/PHASE15.md → commit
```

### Recommended AI Tool Setup

| Tool | Use Case |
|------|----------|
| **Claude Code (Pro)** | Architecture, complex refactors, multi-file migrations |
| **GitHub Copilot (Pro)** | Inline completions, PR descriptions, quick Q&A |
| **Codex (Plus)** | Bulk code generation, scaffolding, test generation |

### Key Make Targets

```bash
make test           # pytest with coverage
make lint           # ruff + mypy
make format         # black + isort + ruff --fix
make security       # bandit + safety
make validate       # full validation (lint + test + typecheck + security)
make dev            # start FastAPI dev server
make install-models # pull Ollama models
make upgrade-deps   # poetry update
```

---

## 🔗 Quick Links

- **Repository:** https://github.com/lchtangen/SampleMind-AI---Beta
- **Status:** [docs/v3/STATUS.md](STATUS.md)
- **Checklist:** [docs/v3/CHECKLIST.md](CHECKLIST.md)
- **Dependencies:** [docs/v3/DEPENDENCIES.md](DEPENDENCIES.md)
- **AI Providers:** [docs/v3/AI_PROVIDERS.md](AI_PROVIDERS.md)

---

## ❓ 10 Follow-Up Questions for Project Planning

After reviewing the entire codebase, architecture, and roadmap, here are 10 strategic questions to guide the next phase of development:

### Architecture & Design
1. **Agent Orchestration Strategy:** Should the multi-agent system (M2.1) use LangGraph's built-in state management or a custom Redis-backed state store? LangGraph provides graph-based orchestration out of the box, but a custom solution offers more control over audio-specific workflow patterns like `analyze → separate → classify → tag → embed`.

2. **Web UI vs TUI Priority:** Given limited development resources, should the Web UI (M3.1) be prioritized over completing the TUI migration (M1.4)? The TUI serves power users and developers, while the Web UI opens the platform to a broader audience. Which user persona should be targeted first for the alpha release?

3. **Offline-First Architecture:** How important is full offline functionality for the beta release? Currently, Ollama provides offline inference, but the Web UI, cloud sync, and marketplace features all require internet. Should there be an explicit "offline mode" with graceful degradation?

### AI & Audio
4. **Model Selection Strategy:** With 4 AI providers now integrated, what's the ideal routing policy for production? Should users be able to override the automatic routing (e.g., force Claude for genre classification), or should the `ANALYSIS_ROUTING` table in `ai_manager.py` be the single source of truth?

5. **Audio Embedding Choice:** For vector similarity search, should the project use CLAP embeddings (text-to-audio zero-shot), BEATs (AudioSet categories), or sentence-transformers (current)? Each has different strengths: CLAP enables natural language queries ("find dark trap beats"), BEATs gives fine-grained audio classification, and sentence-transformers are lightweight.

6. **Stem Separation Workflow:** When demucs separates a file into 6 stems, should each stem be automatically added to the library as a separate entry (with parent reference), or should stems be stored as ephemeral outputs that the user explicitly saves? This affects the MongoDB schema design (A-062) and storage costs.

### Platform & Business
7. **Monetization Model:** For the sample marketplace (B-051), what's the preferred business model? Options include: (a) free + open-source with optional cloud hosting, (b) freemium with local-only free tier and cloud/marketplace paid, (c) subscription-based with usage limits. This decision impacts the auth system (B-043) and Stripe integration architecture.

8. **DAW Plugin Distribution:** The current FL Studio and Ableton plugins use Python backends. For the VST3 native plugin (B-037), should the project invest in JUCE (C++ framework) for cross-DAW compatibility, or use a lighter approach like Python-embedded VST via `pedalboard`? JUCE is industry-standard but adds significant C++ complexity.

### Operations & Quality
9. **Test Coverage Strategy:** The gap from 30% → 80% coverage is significant (~50% increase). Should the focus be on unit tests for core modules (audio engine, AI manager) or integration/E2E tests that validate real workflows? Unit tests catch regressions faster, but integration tests prove the system works end-to-end.

10. **CI/CD & Deployment Pipeline:** For the beta release, what's the minimum viable CI/CD pipeline? Should the project use GitHub Actions → Vercel (frontend) + Railway (backend), or invest in a more robust setup with staging environments, preview deployments, and automated rollbacks? The simpler approach ships faster, but the robust approach prevents production incidents.

---

*SampleMind AI v3.0 — The Future of Intelligent Music Production*
*Last updated: 2026-03-17 — Full roadmap review & modernization*

