# ✅ SampleMind AI v3.0 Migration Checklist

> **Started:** 2026-03-07 | **Target Completion:** 2026-Q2  
> **Tracking:** Tick off items as you complete them. Update the progress % at top.  
> **Overall Progress:** 0% complete (0/100 items)

---

## 🔴 P0 — Critical Blockers (Week 1: Mar 7–14)
*Must complete before any new features work*

### Dependency Upgrades
- [ ] **P0-001** — Upgrade `anthropic` to `^0.40.0` in pyproject.toml
- [ ] **P0-002** — Migrate `ai_manager.py` to new anthropic SDK (streaming, tool_use, claude-3-7-sonnet)
- [ ] **P0-003** — Upgrade `openai` to `^1.58.0` in pyproject.toml
- [ ] **P0-004** — Migrate `ai_manager.py` to new openai SDK (gpt-4o, gpt-4o-mini)
- [ ] **P0-005** — Upgrade `google-generativeai` to `google-genai ^0.8.0` (new package name)
- [ ] **P0-006** — Migrate AI manager to `gemini-2.0-flash` model
- [ ] **P0-007** — Remove `numpy<2.0.0` version cap; upgrade to `numpy^2.2.0`
- [ ] **P0-008** — Fix scipy monkey-patch in `src/samplemind/__init__.py` — move to proper import
- [ ] **P0-009** — Re-enable `basic-pitch` in pyproject.toml + test MIDI transcription
- [ ] **P0-010** — Upgrade `textual` to `^0.87.0` and fix all breaking TUI changes

### New Core Audio Libraries
- [ ] **P0-011** — Add `demucs^4.0.0` for stem separation (vocals/drums/bass/other)
- [ ] **P0-012** — Add `pedalboard^0.9.0` by Spotify for audio effects/processing
- [ ] **P0-013** — Add `audioflux^0.1.8` for fast FFT, spectrogram, MFCC
- [ ] **P0-014** — Add `torch^2.5.0` + `torchaudio^2.5.0` (CUDA 12.x compatible)
- [ ] **P0-015** — Add `transformers^4.47.0` for HuggingFace model loading

### Environment
- [ ] **P0-016** — Update `.env.example` with all new v3.0 keys (Claude, Gemini 2.0, Suno, Udio)
- [ ] **P0-017** — Upgrade `python-dotenv` to `^1.0.1`
- [ ] **P0-018** — Pin Python to `>=3.11,<3.13` in pyproject.toml (3.12 recommended)
- [ ] **P0-019** — Create `docker-compose.v3.yml` with updated services
- [ ] **P0-020** — Update `Makefile` with new v3.0 commands

---

## 🟡 P1 — Core Engine Upgrades (Week 2: Mar 14–21)
*Foundation of all new features*

### AI Models
- [ ] **P1-001** — Add `claude-3-7-sonnet-20250219` as primary analysis model
- [ ] **P1-002** — Add `claude-3-5-haiku-20241022` as fast/cheap secondary model
- [ ] **P1-003** — Add `gemini-2.0-flash` for multimodal audio+text
- [ ] **P1-004** — Add `gemini-2.0-flash-thinking` for complex reasoning tasks
- [ ] **P1-005** — Add `gpt-4o` as GPT fallback
- [ ] **P1-006** — Add `gpt-4o-mini` for high-volume, cheap tasks
- [ ] **P1-007** — Add Ollama provider for `llama3.2`, `mistral`, `deepseek-coder-v2` (offline)
- [ ] **P1-008** — Implement AI model auto-selection based on task type + cost
- [ ] **P1-009** — Add AI response caching (Redis) to avoid re-querying same analysis
- [ ] **P1-010** — Add AI fallback chain: Claude → Gemini → GPT → Ollama (offline)

### Audio Engine
- [ ] **P1-011** — Migrate audio analysis to use `audioflux` (3-5x faster than librosa for spectrograms)
- [ ] **P1-012** — Keep `librosa` for compatibility but make it optional fallback
- [ ] **P1-013** — Implement stem separation endpoint using `demucs` (REST API)
- [ ] **P1-014** — Add real-time audio effects chain using `pedalboard`
- [ ] **P1-015** — Implement BPM detection using `madmom` (more accurate than librosa)
- [ ] **P1-016** — Upgrade MIDI transcription with latest `basic-pitch` model
- [ ] **P1-017** — Add `essentia` for advanced music information retrieval
- [ ] **P1-018** — Add `pyworld` for pitch/voice analysis
- [ ] **P1-019** — Implement parallel audio processing with `joblib`
- [ ] **P1-020** — Add audio streaming support (chunk-based processing for large files)

### Database & Storage
- [ ] **P1-021** — Upgrade `chromadb` to `^0.6.0` with new embedding models
- [ ] **P1-022** — Add `motor` for async MongoDB operations
- [ ] **P1-023** — Implement vector similarity search with `chromadb` collections per genre
- [ ] **P1-024** — Add `redis-py` with async support for caching + job queues
- [ ] **P1-025** — Design v3.0 MongoDB schema for samples, packs, users, projects

---

## 🟢 P2 — Web Platform (Phase 15: Mar 21 – Apr 11)
*New web UI — the biggest new surface*

### Next.js Setup
- [ ] **P2-001** — Initialize `apps/web/` with Next.js 15 + App Router
- [ ] **P2-002** — Install Tailwind CSS v4 + shadcn/ui component library
- [ ] **P2-003** — Install Framer Motion for animations
- [ ] **P2-004** — Install Zustand for state management
- [ ] **P2-005** — Set up TypeScript 5.7 strict mode
- [ ] **P2-006** — Configure ESLint + Prettier + Husky pre-commit hooks
- [ ] **P2-007** — Add `@tanstack/react-query` for server state/caching
- [ ] **P2-008** — Set up `next-auth v5` for authentication
- [ ] **P2-009** — Configure `uploadthing` or S3 for audio file uploads
- [ ] **P2-010** — Set up `vitest` + React Testing Library for frontend tests

### Core Web UI Pages
- [ ] **P2-011** — Landing page with animated waveform hero
- [ ] **P2-012** — Dashboard page (overview of library + recent activity)
- [ ] **P2-013** — Library browser with infinite scroll + filters
- [ ] **P2-014** — Sample analyzer page (drag-drop upload + live analysis)
- [ ] **P2-015** — Waveform visualizer component (Wavesurfer.js v7)
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
- [ ] **P2-025** — Pitch detection visualizer

---

## 🔵 P3 — Multi-Agent System (Phase 15b: Apr 11–25)
*Autonomous AI that does things for you*

### Agent Architecture
- [ ] **P3-001** — Design `AgentOrchestrator` class in `src/samplemind/agents/`
- [ ] **P3-002** — Implement `AnalysisAgent` — auto-analyzes all new samples in watched folder
- [ ] **P3-003** — Implement `TaggingAgent` — auto-generates genre/mood/BPM tags
- [ ] **P3-004** — Implement `RecommendationAgent` — suggests similar samples
- [ ] **P3-005** — Implement `PackBuilderAgent` — auto-creates themed sample packs
- [ ] **P3-006** — Implement `QualityAgent` — detects clipping, noise, silence issues
- [ ] **P3-007** — Add `celery^5.4.0` + Redis for async agent task queue
- [ ] **P3-008** — Add `celery beat` for scheduled agent runs (e.g., nightly analysis)
- [ ] **P3-009** — Implement agent status websocket (real-time progress in web UI)
- [ ] **P3-010** — Add agent run history and logs to MongoDB

### Claude Computer Use Integration
- [ ] **P3-011** — Implement Claude tool_use for sample tagging workflow
- [ ] **P3-012** — Add web search tool to AI agent (find sample info online)
- [ ] **P3-013** — Add file system tools (agent can read/rename/move files)
- [ ] **P3-014** — Implement multi-step reasoning for complex queries
- [ ] **P3-015** — Add agent conversation memory (vector search of past analysis)

---

## 🟣 P4 — Advanced Music AI (Apr 25 – May 23)
*Next-generation audio intelligence*

### Music Generation
- [ ] **P4-001** — Integrate Suno AI API for AI music generation from text prompts
- [ ] **P4-002** — Integrate Udio API as Suno alternative
- [ ] **P4-003** — Add `audiocraft` (Meta MusicGen) for local generation
- [ ] **P4-004** — Implement "generate similar sample" from existing file
- [ ] **P4-005** — Add style transfer between samples
- [ ] **P4-006** — Implement loop extension using AI continuation

### Advanced Audio Analysis
- [ ] **P4-007** — Upgrade genre classifier to multi-label (one sample = multiple genres)
- [ ] **P4-008** — Add mood detection (happy, dark, energetic, chill, etc.)
- [ ] **P4-009** — Add instrument detection (kick, snare, pad, lead, bass)
- [ ] **P4-010** — Implement audio fingerprinting (detect duplicates/near-duplicates)
- [ ] **P4-011** — Add harmonic key detection with camelot wheel display
- [ ] **P4-012** — Add micro-timing analysis (groove feel, humanization detection)

---

## ⚫ P5 — Production & Platform (May 23+)
*Shipping to real users*

### DevOps & Infrastructure
- [ ] **P5-001** — Set up Vercel deployment for Next.js web app
- [ ] **P5-002** — Set up Render/Railway for FastAPI backend
- [ ] **P5-003** — Configure Cloudflare R2 for audio file storage
- [ ] **P5-004** — Set up GitHub Actions CI: test → lint → build → deploy
- [ ] **P5-005** — Add Sentry for error monitoring (Python + Next.js)
- [ ] **P5-006** — Upgrade PostHog integration for product analytics
- [ ] **P5-007** — Set up Stripe integration for future monetization
- [ ] **P5-008** — Add rate limiting (Redis) to FastAPI endpoints
- [ ] **P5-009** — Implement JWT auth with refresh tokens
- [ ] **P5-010** — Set up staging environment

### Testing & Quality
- [ ] **P5-011** — Reach 50% test coverage (from current ~30%)
- [ ] **P5-012** — Reach 80% test coverage (target)
- [ ] **P5-013** — Add integration tests for all API endpoints
- [ ] **P5-014** — Add E2E tests with Playwright for web UI
- [ ] **P5-015** — Set up performance benchmarking (audio analysis latency)

---

## 📊 Progress Tracking

| Phase | Items | Done | Progress |
|-------|-------|------|----------|
| P0 Critical Blockers | 20 | 0 | 0% |
| P1 Core Engine | 25 | 0 | 0% |
| P2 Web Platform | 25 | 0 | 0% |
| P3 Multi-Agent | 15 | 0 | 0% |
| P4 Advanced Music AI | 12 | 0 | 0% |
| P5 Production | 15 | 0 | 0% |
| **TOTAL** | **112** | **0** | **0%** |

---

*V3_MIGRATION_CHECKLIST.md v1.0 — Created 2026-03-07. Check off items as you complete them.*