# GitHub Copilot Instructions — SampleMind AI

> Codebase context for GitHub Copilot. Read alongside any file you are working in.
> Full project instructions: `CLAUDE.md` | Active checklist: `docs/v3/CHECKLIST.md`

---

## Project Summary

SampleMind AI is a **CLI-first, offline-capable music production AI** for audio analysis,
sample management, stem separation, MIDI transcription, AI-powered recommendations,
semantic search, smart playlist curation, and sample pack marketplace.

Active phase: **Phase 16 — Web UI completions + Agent pipeline + Production hardening**

**Language:** Python 3.12 | **Package manager:** pip/uv | **Primary interfaces:** CLI + Textual TUI + Next.js 15 Web + Tauri v2 Desktop

---

## Tech Stack (2026-04 — ACTUAL INSTALLED VERSIONS)

### AI Providers
| Provider | SDK | Model | Use |
|----------|-----|-------|-----|
| Anthropic | `anthropic` | `claude-sonnet-4-6` | Primary analysis + curation |
| OpenAI | `openai` | `gpt-4o` | Agent workflows |
| Google | `google-genai` | `gemini-2.5-flash` | Fast streaming |
| Ollama | `ollama` | `qwen2.5-coder:7b` at `localhost:11434` | Offline inference |
| LiteLLM | `litellm` | Router: Claude -> Gemini -> GPT -> Ollama | Unified fallback chain |

### Audio
- `librosa` — BPM, key, MFCC, chroma, spectral features
- `demucs ^4.0.0` — 6-stem source separation (htdemucs_6s model)
- `basic-pitch ^0.4.0` — MIDI transcription from audio
- `pedalboard ^0.9.0` — Professional audio effects (Spotify)
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
- `fastapi ^0.115.0` + `uvicorn` — REST API (12 routers registered)
- `next.js 15` + React 19 + Tailwind + framer-motion + wavesurfer.js v7 — Web UI (apps/web/, 108 TS files)
- Tauri v2 + Svelte 5 — Desktop app scaffold (app/)
- `plotly` — Analytics charts (BPM histogram, key heatmap, genre breakdown, energy pie)

### Billing & Platform
- `stripe` — Stripe Connect marketplace (pack publishing + purchase)
- `slowapi` — Redis-backed rate limiting (dep present, not yet wired)

---

## Key File Locations (ACCURATE as of 2026-04-09)

```
CLAUDE.md                                      # AI assistant instructions
pyproject.toml                                 # All dependencies (v0.3.0, Python >=3.12)

src/samplemind/
├── interfaces/
│   ├── cli/menu.py                            # Main CLI (~2255 lines, Typer/Rich)
│   ├── cli/commands/search.py                 # FAISS semantic search CLI (index_app, search_app)
│   ├── tui/app.py                             # Textual TUI app
│   ├── tui/screens/                           # 13 TUI screens (Textual ^0.87)
│   └── api/
│       ├── main.py                            # App factory, lifespan, 12 include_router calls
│       └── routes/                            # ai.py, search.py, analytics.py, marketplace.py,
│                                              # billing.py, audio.py, auth.py, tasks.py, websocket.py
├── core/
│   ├── engine/audio_engine.py                 # Audio analysis engine (LibROSA-based)
│   ├── loader.py                              # AdvancedAudioLoader
│   ├── database/
│   │   ├── chroma.py                          # ChromaDB manager
│   │   └── tortoise_models.py                 # Tortoise ORM models (TortoiseUser/Sample/Library)
│   ├── search/faiss_index.py                  # FAISS IndexFlatIP + CLAPEmbedder (512-dim)
│   ├── packs/pack_builder.py                  # .smpack ZIP builder + manifest spec
│   ├── services/stripe_connect.py             # Stripe Connect Express marketplace
│   └── tasks/
│       ├── celery_app.py                      # Celery app instance
│       └── audio_tasks.py                     # Audio processing Celery tasks
│       # MISSING: agent_tasks.py              # Needs to be created (Step 6)
├── integrations/
│   ├── litellm_router.py                      # LiteLLM Router: Claude->Gemini->GPT->Ollama
│   ├── supabase_client.py                     # Supabase Auth + user sync
│   └── realtime_sync.py                       # Supabase Realtime multi-device library sync
├── ai/
│   ├── agents/
│   │   ├── graph.py                           # LangGraph StateGraph (210 lines, build_graph())
│   │   ├── state.py                           # AudioAnalysisState TypedDict
│   │   ├── analysis_agent.py                  # Claude tool_use audio analysis node
│   │   ├── tagging_agent.py                   # CLAP + ensemble tagging node
│   │   ├── mixing_agent.py                    # Mixing recommendations node
│   │   ├── recommendation_agent.py            # FAISS similarity search node
│   │   └── pack_builder_agent.py              # Auto pack creation node
│   ├── classification/
│   │   ├── ensemble.py                        # SVM + XGBoost + KNN soft-voting ensemble
│   │   ├── multi_label_genre.py               # 400+ genre taxonomy classifier
│   │   ├── mood_detector.py                   # Russell circumplex mood classifier
│   │   └── instrument_detector.py             # 128-class GM instrument detector
│   ├── curation/
│   │   ├── playlist_generator.py              # Energy arc playlists + Camelot Wheel scoring
│   │   └── gap_analyzer.py                    # Library coverage analysis + LiteLLM suggestions
│   ├── generation/
│   │   ├── musicgen.py                        # Meta AudioCraft text-to-audio (GPU optional)
│   │   └── style_transfer.py                  # demucs stem sep + librosa time-stretch/pitch-shift
│   └── transcription/
│       └── whisper_transcriber.py             # faster-whisper local transcription (IMPLEMENTED)
├── services/
│   └── storage/r2_provider.py                 # Cloudflare R2 (boto3 S3-compatible)

apps/web/                                      # Next.js 15 Web UI (108 TS/TSX files)
├── src/app/                                   # Pages: dashboard, library, upload, login,
│                                              # settings, gallery, analysis, collections
│                                              # MISSING: search/, analytics/ (Steps 4-5)
├── src/components/                            # AIChatWindow, AdvancedWaveform, SampleCard etc.
└── src/lib/                                   # MISSING: API client (Step 3)

app/                                           # Tauri v2 + Svelte 5 desktop scaffold
tests/unit/                                    # 120+ tests, ~30% coverage (target: 50%)
docs/v3/                                       # CHECKLIST.md, STATUS.md, ROADMAP.md
```

> **Important:** `src/samplemind/api/` does NOT exist. FastAPI code is at `interfaces/api/` and `server/`.
> **Important:** `docs/02-ROADMAPS/` is stale/legacy. Use `docs/v3/` instead.

---

## Code Conventions

### Python
- **Style:** Black (line length 88) + isort + ruff
- **Types:** mypy strict — always add type annotations to new functions
- **Async:** All audio I/O and AI calls must be `async def` or run in `ThreadPoolExecutor`
- **Never:** `time.sleep()` in Textual handlers, `asyncio.run()` inside Textual, blocking I/O in `compose()`
- **Imports:** Lazy imports at module level for heavy libraries (torch, librosa, faiss)
- **Tests:** pytest, fixtures in `tests/fixtures/`, mocks for AI providers and FAISS

### LiteLLM Router Pattern (prefer over ai_manager)
```python
from samplemind.integrations.litellm_router import chat_completion

response = await chat_completion(
    messages=[{"role": "user", "content": "Analyze this BPM: 140"}],
    prefer_fast=True,   # uses gemini-2.5-flash
)
```

### FAISS Search Pattern
```python
from samplemind.core.search.faiss_index import get_index

index = get_index(auto_load=True)
results = index.search_text("dark trap kick", top_k=20)
```

### Tortoise ORM Pattern
```python
from samplemind.core.database.tortoise_models import TortoiseSample

sample = await TortoiseSample.create(filename="kick.wav", bpm=140.0, key="A minor")
samples = await TortoiseSample.filter(bpm__gte=120).all()
```

### Celery Task Pattern
```python
from samplemind.core.tasks.celery_app import celery_app

@celery_app.task(bind=True, name="samplemind.tasks.my_task")
def my_task(self, file_path: str) -> dict:
    self.update_state(state="PROGRESS", meta={"pct": 50})
    return {"result": "done"}
```

### FastAPI Pattern
```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/audio", tags=["audio"])

@router.post("/analyze")
async def analyze_audio(file: UploadFile) -> AnalysisResult:
    ...
```

### Next.js API fetch pattern (apps/web)
```typescript
import { apiFetch } from "@/lib/api-client"

const data = await apiFetch<LibrarySummary>("/api/v1/analytics/summary")
```

---

## Analysis Levels

```python
BASIC        # BPM, key, duration — <0.5s
STANDARD     # + MFCC, chroma, spectral — <1s
DETAILED     # + harmonic/percussive separation — <2s
PROFESSIONAL # + AI analysis, CLAP classification, embeddings — <5s
```

---

## Phase 16 — Active Work Gaps (as of 2026-04-09)

### MISSING — needs implementation
1. `apps/web/src/lib/` — TypeScript API client module (does not exist)
2. `apps/web/src/app/search/` — Semantic search page
3. `apps/web/src/app/analytics/` — Plotly analytics page
4. `src/samplemind/core/tasks/agent_tasks.py` — Celery task wrapping LangGraph
5. `/ws/agent/{task_id}` — WebSocket endpoint for agent progress streaming
6. Unit tests for FAISS, LiteLLM router, playlist generator, pack builder, ensemble
7. Rate limiting via `slowapi` (dep exists, not wired in main.py)
8. CI coverage gate in `.github/workflows/backend-ci.yml`

### DONE — do NOT re-implement
- FastAPI backend with all 12 routers registered
- Next.js 15 `apps/web/` with 108 TS files and core pages
- LangGraph agent graph (`build_graph()`, 210 lines, 6 real nodes)
- faster-whisper `WhisperTranscriber` (fully implemented)
- FAISS semantic search (built + registered at `GET /api/v1/ai/faiss`)
- Curation: playlist generator + gap analyzer
- Analytics: 5 Plotly endpoints (bpm-histogram, key-heatmap, genre-breakdown, energy-breakdown, summary)
- Marketplace: Stripe Connect publish + purchase
- Tortoise ORM models, LiteLLM router, Ensemble classifier
- Tauri v2 + Svelte 5 desktop scaffold in `app/`

Full checklist: `docs/v3/CHECKLIST.md`

---

## What NOT To Do

- Do not add `time.sleep()` anywhere
- Do not re-implement what is already built — check the file locations table first
- Do not commit without running `make quality` (ruff + mypy + bandit)
- Do not reference `src/samplemind/api/` — use `interfaces/api/` + `server/`
- Do not reference `docs/02-ROADMAPS/` — stale; use `docs/v3/`
- Do not call `SampleMindAIManager` for new features — use `litellm_router.chat_completion()` instead
- Do not use old model names (`claude-3-7-sonnet-20250219`) — use `claude-sonnet-4-6`
- Do not scaffold `apps/web/` — it already has 108 files; add to what exists
