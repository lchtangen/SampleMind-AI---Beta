<div align="center">

```
 ╔═══════════════════════════════════════════════════════════════╗
 ║  ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗        ║
 ║  ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝        ║
 ║  ███████╗███████║██╔████╔██║██████╔╝██║     █████╗          ║
 ║  ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝          ║
 ║  ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗        ║
 ║  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝        ║
 ║  ███╗   ███╗██╗███╗   ██╗██████╗      █████╗ ██╗            ║
 ║  ████╗ ████║██║████╗  ██║██╔══██╗    ██╔══██╗██║            ║
 ║  ██╔████╔██║██║██╔██╗ ██║██║  ██║    ███████║██║            ║
 ║  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║    ██╔══██║██║            ║
 ║  ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝    ██║  ██║██║            ║
 ║  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝  ╚═╝╚═╝            ║
 ╚═══════════════════════════════════════════════════════════════╝
```

**`[ NEURAL AUDIO INTELLIGENCE — PHASE 16 ACTIVE ]`**

*The next-generation AI music production platform. Analyze. Create. Dominate.*

---

[![Python](https://img.shields.io/badge/PYTHON-3.12+-00d4ff?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a1a)](https://python.org)
[![Version](https://img.shields.io/badge/VERSION-3.0.0--BETA-ff00ff?style=for-the-badge&labelColor=0a0a1a)](CHANGELOG.md)
[![Phase](https://img.shields.io/badge/PHASE-16%20ACTIVE-00ff9f?style=for-the-badge&labelColor=0a0a1a)](docs/v3/CHECKLIST.md)
[![License](https://img.shields.io/badge/LICENSE-MIT-ff6b35?style=for-the-badge&labelColor=0a0a1a)](LICENSE)

[![Backend CI](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/lchtangen/SampleMind-AI---Beta/actions/workflows/frontend-ci.yml)
[![Tests](https://img.shields.io/badge/TESTS-120%2B%20PASSING-00ff9f?style=flat-square&labelColor=0a0a1a)](tests/)
[![Coverage](https://img.shields.io/codecov/c/github/lchtangen/SampleMind-AI---Beta?style=flat-square&label=COVERAGE&labelColor=0a0a1a)](https://codecov.io/gh/lchtangen/SampleMind-AI---Beta)
[![Code Style](https://img.shields.io/badge/CODE_STYLE-RUFF%20%2B%20BLACK-ff00ff?style=flat-square&labelColor=0a0a1a)](https://github.com/astral-sh/ruff)

</div>

---

<div align="center">

## `◈ NEURAL CORE SYSTEMS ◈`

</div>

```
┌─────────────────────────────────────────────────────────────────┐
│  AUDIO ENGINE          ████████████████████  ONLINE            │
│  AI PROVIDER MESH      ████████████████████  4 NODES ACTIVE    │
│  FAISS VECTOR INDEX    ████████████████████  512-DIM CLAP      │
│  LANGGRAPH PIPELINE    ████████████████████  7 NODES           │
│  REST API              ████████████████████  12 ROUTERS        │
│  NEXT.JS WEB UI        ███████████████░░░░░  PHASE 16          │
│  AGENT MEMORY          ████████████████████  FAISS-BACKED      │
└─────────────────────────────────────────────────────────────────┘
```

SampleMind AI is a **CLI-first, offline-capable music production intelligence platform** — combining neural audio analysis, multi-provider AI routing, semantic vector search, stem separation, MIDI transcription, smart playlist curation, and a sample pack marketplace into one unified system.

Built for **producers, beatmakers, audio engineers, and sound designers** who demand precision, speed, and creative intelligence.

---

## `◈ QUICK BOOT SEQUENCE ◈`

```bash
# ── CLONE ──────────────────────────────────────────────────────
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta

# ── INITIALIZE VIRTUAL ENVIRONMENT ────────────────────────────
python3 -m venv .venv && source .venv/bin/activate

# ── INSTALL NEURAL CORE ────────────────────────────────────────
pip install -e ".[dev]"

# ── INJECT API KEYS (choose one or all) ───────────────────────
export ANTHROPIC_API_KEY="sk-ant-..."   # Claude sonnet-4-6
export GOOGLE_API_KEY="AIza..."          # Gemini 2.5 Flash
export OPENAI_API_KEY="sk-..."           # GPT-4o
# Ollama runs locally — no key needed (localhost:11434)

# ── LAUNCH ─────────────────────────────────────────────────────
python main.py
```

> **Linux/macOS one-liner:** `./scripts/setup/quick_start.sh`
> **Windows:** `.\scripts\setup\windows_setup.ps1`

---

## `◈ INTERFACES ◈`

<div align="center">

| INTERFACE | STATUS | DESCRIPTION |
|:---------:|:------:|:------------|
| `CLI` | **◉ ONLINE** | 200+ commands · Rich/Typer · 12 themes · ~2255 lines |
| `TUI` | **◉ ONLINE** | Textual ^0.87 · 13 screens · 60 FPS · mouse support |
| `REST API` | **◉ ONLINE** | FastAPI ^0.115 · 12 routers · async · Swagger docs |
| `Web UI` | **◈ PHASE 16** | Next.js 15 · React 19 · Tailwind · Framer Motion |
| `Desktop` | **◈ SCAFFOLD** | Tauri v2 · Svelte 5 · native binary |

</div>

```bash
# ── CLI (primary interface) ────────────────────────────────────
python main.py

# ── TUI (terminal UI — 13 screens, mouse support) ─────────────
python -m samplemind.interfaces.tui.main

# ── REST API (FastAPI with Swagger at /docs) ──────────────────
uvicorn samplemind.interfaces.api.main:app --reload --port 8000

# ── WEB UI (Next.js 15 dev server) ────────────────────────────
cd apps/web && npm run dev
```

---

## `◈ AI PROVIDER MESH ◈`

```
 ┌──────────────────────────────────────────────────────────────┐
 │                    LiteLLM Router                            │
 │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────┐ │
 │  │  CLAUDE    │→ │  GEMINI    │→ │   GPT-4o   │→ │OLLAMA │ │
 │  │sonnet-4-6  │  │2.5-flash   │  │  agents    │  │ local │ │
 │  │ primary    │  │ fast/stream│  │  tool use  │  │<100ms │ │
 │  └────────────┘  └────────────┘  └────────────┘  └───────┘ │
 │         Primary ──────────────────────────────► Fallback    │
 └──────────────────────────────────────────────────────────────┘
```

| PROVIDER | MODEL | ROLE | LATENCY |
|----------|-------|------|---------|
| **Anthropic** | `claude-sonnet-4-6` | Primary analysis · tool_use | ~3–5s |
| **Google** | `gemini-2.5-flash` | Streaming · fast queries | ~1–2s |
| **OpenAI** | `gpt-4o` | Agent workflows · tool calls | ~2–4s |
| **Ollama** | `qwen2.5-coder:7b` | Offline · no key needed | **<100ms** |

```python
# ── LiteLLM Router Pattern ────────────────────────────────────
from samplemind.integrations.litellm_router import chat_completion

response = await chat_completion(
    messages=[{"role": "user", "content": "Analyze this 808 kick at 140 BPM"}],
    prefer_fast=True,   # → gemini-2.5-flash
)
# Auto-falls back: Claude → Gemini → GPT-4o → Ollama
```

---

## `◈ FEATURE MODULES ◈`

<details>
<summary><b>🔊 Audio Intelligence Engine</b></summary>

```
 ANALYSIS LEVELS:
 ┌─────────────┬────────────────────────────────────────┬──────────┐
 │ BASIC       │ BPM · Key · Duration                   │  <0.5s   │
 │ STANDARD    │ + MFCC · Chroma · Spectral             │  <1.0s   │
 │ DETAILED    │ + Harmonic/Percussive sep              │  <2.0s   │
 │ PROFESSIONAL│ + AI analysis · CLAP embeddings        │  <5.0s   │
 └─────────────┴────────────────────────────────────────┴──────────┘
```

- **BPM & Key Detection** — librosa-powered, sub-second analysis
- **6-Stem Source Separation** — Demucs `htdemucs_6s` (vocals, drums, bass, guitar, piano, other)
- **CLAP Embeddings** — `laion/clap-htsat-unfused` 512-dim semantic audio vectors
- **MIDI Transcription** — `basic-pitch` neural network, offline
- **Real-time Effects** — 10 professional pedalboard chains (Spotify SDK)
- **Audio Streaming** — chunk-based processing for large files

</details>

<details>
<summary><b>🧠 AI Agent Pipeline (LangGraph)</b></summary>

```
 AGENT GRAPH:
                    ┌──────────────┐
                    │  router_node │ ← AgentMemory (FAISS)
                    └──────┬───────┘
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │analysis_agent│ │tagging   │ │mixing_agent  │
    │(Claude tool  │ │_agent    │ │(suggestions) │
    │  use)        │ │(CLAP+ML) │ │              │
    └──────┬───────┘ └────┬─────┘ └──────┬───────┘
           └──────────────┼──────────────┘
                          ▼
                  ┌──────────────────┐
                  │ aggregator_node  │ → stores to AgentMemory
                  └──────────────────┘
```

- **7-node LangGraph StateGraph** — `build_graph()` in `ai/agents/graph.py`
- **Agent Memory** — FAISS-backed vector store for conversation persistence
- **Tool Use** — Claude native tool_use for FAISS search, playlist gen, library stats
- **Celery Tasks** — async agent execution via Redis broker

</details>

<details>
<summary><b>🔍 Semantic Search (FAISS + CLAP)</b></summary>

```python
from samplemind.core.search.faiss_index import get_index

index = get_index(auto_load=True)

# Search by text description
results = index.search_text("dark cinematic 808 sub bass", top_k=20)

# Search by audio file
results = index.search_audio("reference_kick.wav", top_k=10)
```

- **FAISS IndexFlatIP** — cosine similarity over 512-dim CLAP embeddings
- **Text + Audio query** — natural language or audio reference
- **Sub-millisecond search** — across 10,000+ samples

</details>

<details>
<summary><b>🎛️ New Phase 16 Feature Modules</b></summary>

| MODULE | ENDPOINT | DESCRIPTION |
|--------|----------|-------------|
| **Audio Copilot** | `POST /api/v1/copilot/chat` | SSE streaming chat with tool_use |
| **Remix Studio** | `POST /api/v1/remix/separate` | Demucs stems + AI mix suggestions |
| **Sonic Graph** | `GET /api/v1/graph/sonic-map` | FAISS pairwise similarity force graph |
| **Mix Reference** | `POST /api/v1/reference/compare` | LUFS + frequency comparison + AI recs |
| **Auto Packs** | `POST /api/v1/autopacks/generate` | AI-curated themed sample packs |
| **Trend Engine** | `GET /api/v1/trends/analysis` | BPM/key/genre forecasts + gap detection |

</details>

<details>
<summary><b>🎵 Sample Pack Marketplace</b></summary>

- **Stripe Connect** — Express marketplace for creators
- **Pack Builder** — `.smpack` ZIP format with manifest spec
- **R2 Storage** — Cloudflare R2 (S3-compatible) via boto3
- **Publish & Purchase** — Full billing flow at `/api/v1/marketplace/`

</details>

---

## `◈ ARCHITECTURE OVERVIEW ◈`

```
SampleMind-AI---Beta/
│
├── src/samplemind/
│   ├── interfaces/
│   │   ├── cli/menu.py              # 2255-line Typer/Rich CLI
│   │   ├── tui/                     # Textual ^0.87 — 13 screens
│   │   └── api/
│   │       ├── main.py              # FastAPI app factory (18 routers)
│   │       └── routes/              # ai · audio · analytics · search
│   │                                # copilot · remix · graph · reference
│   │                                # autopacks · trends · marketplace · auth
│   ├── core/
│   │   ├── engine/audio_engine.py   # LibROSA analysis engine
│   │   ├── search/faiss_index.py    # FAISS + CLAP semantic search
│   │   ├── database/                # Tortoise ORM models + ChromaDB
│   │   ├── packs/pack_builder.py    # .smpack builder
│   │   └── tasks/                   # Celery task queue
│   ├── ai/
│   │   ├── agents/graph.py          # LangGraph 7-node pipeline
│   │   ├── classification/          # Ensemble (SVM+XGBoost+KNN)
│   │   ├── curation/                # Playlist gen + gap analyzer
│   │   ├── generation/              # AudioCraft + style transfer
│   │   └── transcription/           # faster-whisper local STT
│   ├── integrations/
│   │   ├── litellm_router.py        # Claude→Gemini→GPT→Ollama
│   │   ├── supabase_client.py       # Auth + JWT
│   │   └── realtime_sync.py         # Multi-device library sync
│   └── services/
│       └── storage/r2_provider.py   # Cloudflare R2
│
├── apps/web/                         # Next.js 15 (108 TS files)
│   ├── src/app/                      # Pages: dashboard · library · upload
│   │                                 #        copilot · remix · sonic-graph
│   │                                 #        reference · autopacks · trends
│   ├── src/components/               # AIChatWindow · AdvancedWaveform
│   ├── src/hooks/                    # useCopilotChat · useWebSocket
│   └── src/lib/                      # api-client · feature-endpoints
│
├── app/                              # Tauri v2 + Svelte 5 desktop
├── plugins/                          # FL Studio (JUCE C++) + Ableton
└── tests/unit/                       # 120+ tests
```

---

## `◈ TECHNOLOGY STACK ◈`

<div align="center">

**BACKEND**

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Redis_broker-37814A?style=flat-square&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-cache+pubsub-DC382D?style=flat-square&logo=redis&logoColor=white)

**AI / ML**

![Claude](https://img.shields.io/badge/Claude-sonnet--4--6-CC785C?style=flat-square&logo=anthropic&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![GPT](https://img.shields.io/badge/GPT-4o-412991?style=flat-square&logo=openai&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-qwen2.5_7b-000000?style=flat-square&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent_pipeline-1C3C3C?style=flat-square&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-512dim_CLAP-0066CC?style=flat-square&logoColor=white)

**AUDIO**

![librosa](https://img.shields.io/badge/librosa-analysis-FF6B6B?style=flat-square&logoColor=white)
![Demucs](https://img.shields.io/badge/Demucs-6stem_sep-9B59B6?style=flat-square&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.5-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![pedalboard](https://img.shields.io/badge/pedalboard-Spotify_FX-1DB954?style=flat-square&logoColor=white)

**FRONTEND**

![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Tauri](https://img.shields.io/badge/Tauri-v2_desktop-FFC131?style=flat-square&logo=tauri&logoColor=black)

**STORAGE**

![SQLite](https://img.shields.io/badge/SQLite-Tortoise_ORM-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-auth+sync-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![R2](https://img.shields.io/badge/Cloudflare_R2-S3_storage-F38020?style=flat-square&logo=cloudflare&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Connect-635BFF?style=flat-square&logo=stripe&logoColor=white)

</div>

---

## `◈ DEVELOPMENT COMMANDS ◈`

```bash
# ── ENVIRONMENT ────────────────────────────────────────────────
make setup              # Full environment initialization
make setup-db           # Initialize SQLite + Redis
make install-models     # Pull Ollama models locally

# ── DEVELOPMENT ────────────────────────────────────────────────
make dev                # Start FastAPI + Celery + Redis
python main.py          # CLI interactive menu
python -m samplemind.interfaces.tui.main  # TUI (13 screens)
cd apps/web && npm run dev               # Next.js web UI

# ── QUALITY ────────────────────────────────────────────────────
make quality            # ruff + mypy + bandit (run before commit)
make test               # pytest tests/unit/ -v --tb=short
make format             # ruff format .
make lint               # ruff check .
make type-check         # mypy .

# ── API EXAMPLES ───────────────────────────────────────────────
# Analyze audio
curl -X POST http://localhost:8000/api/v1/audio/analyze \
  -F "file=@track.wav" -F "level=detailed"

# Semantic search
curl "http://localhost:8000/api/v1/ai/faiss?q=dark+808+trap&top_k=10"

# Stream AI copilot chat
curl -X POST http://localhost:8000/api/v1/copilot/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Find dark trap kicks above 140 BPM"}]}'
```

---

## `◈ USAGE PATTERNS ◈`

```python
# ── SEMANTIC AUDIO SEARCH ─────────────────────────────────────
from samplemind.core.search.faiss_index import get_index

index = get_index(auto_load=True)
results = index.search_text("aggressive 808 sub bass 140 BPM", top_k=20)
for r in results:
    print(f"{r.filename}  score={r.score:.3f}  BPM={r.metadata.get('bpm')}")


# ── AI STREAMING CHAT ─────────────────────────────────────────
from samplemind.integrations.litellm_router import chat_completion

response = await chat_completion(
    messages=[{"role": "user", "content": "What samples match a dark trap vibe?"}],
    prefer_fast=True,
)
print(response.choices[0].message.content)


# ── SAMPLE ANALYSIS (ORM) ─────────────────────────────────────
from samplemind.core.database.tortoise_models import TortoiseSample

heavy_kicks = await TortoiseSample.filter(
    bpm__gte=130, bpm__lte=160
).order_by("-bpm").limit(50).all()


# ── AGENT PIPELINE ────────────────────────────────────────────
from samplemind.ai.agents.graph import build_graph

graph = build_graph()
result = await graph.ainvoke({
    "file_path": "kick_808.wav",
    "analysis_level": "PROFESSIONAL",
    "user_request": "Analyze and tag this sample"
})
print(result["final_output"])
```

---

## `◈ BUILD STATUS ◈`

```
PHASE COMPLETION  ──────────────────────────────────────
  P0  Core Infrastructure    ████████████████████  90%
  P1  Audio Engine           ████████████████████ 100%
  P2  Web Frontend           ████████████████░░░░  79%
  P3  Agent Pipeline         ████████████████████ 100%
  P4  Advanced Features      ███████████████░░░░░  75%
  P5  Production             ██████░░░░░░░░░░░░░░  33%
─────────────────────────────────────────────────────────
  OVERALL                    ████████████████░░░░  82%
  94 / 115 checklist items complete
```

<div align="center">

| SYSTEM | STATUS | DETAIL |
|--------|:------:|--------|
| Audio Engine | `◉ STABLE` | librosa BPM/key/MFCC/chroma/spectral |
| LiteLLM Router | `◉ ACTIVE` | Claude→Gemini→GPT→Ollama fallback chain |
| FAISS Search | `◉ ACTIVE` | 512-dim CLAP, text+audio queries |
| LangGraph Agents | `◉ ACTIVE` | 7-node pipeline + FAISS memory |
| FastAPI (18 routers) | `◉ ACTIVE` | REST + WebSocket + SSE streaming |
| Celery Workers | `◉ ACTIVE` | Redis broker, audio + agent tasks |
| Ensemble Classifier | `◉ ACTIVE` | SVM+XGBoost+KNN soft-voting |
| Stem Separation | `◉ ACTIVE` | Demucs htdemucs_6s (6 stems) |
| MIDI Transcription | `◉ ACTIVE` | basic-pitch neural network |
| Stripe Marketplace | `◉ ACTIVE` | Connect Express publish+purchase |
| Next.js Web UI | `◈ PHASE 16` | 108 TS files, 8 pages live |
| Tauri Desktop | `◈ SCAFFOLD` | v2 + Svelte 5 |
| Rate Limiting | `◈ PENDING` | slowapi dep present, not wired |

</div>

---

## `◈ CONTRIBUTING ◈`

```bash
# ── SETUP ──────────────────────────────────────────────────────
git clone https://github.com/lchtangen/SampleMind-AI---Beta.git
cd SampleMind-AI---Beta
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# ── VALIDATE ───────────────────────────────────────────────────
make quality     # must pass before opening a PR
make test        # pytest tests/unit/ -v --tb=short

# ── SUBMIT ─────────────────────────────────────────────────────
git checkout -b feat/your-feature
git commit -m "feat: your change"
git push origin feat/your-feature
# → open Pull Request
```

**Rules:**
- Never re-implement existing modules — check `CLAUDE.md` first
- All new functions need type annotations (mypy strict)
- All async I/O must use `async def` or `ThreadPoolExecutor`
- Never call `SampleMindAIManager` — use `litellm_router.chat_completion()`

📋 [CONTRIBUTING.md](CONTRIBUTING.md) · [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) · [CLAUDE.md](CLAUDE.md)

---

## `◈ LINKS ◈`

<div align="center">

[![Changelog](https://img.shields.io/badge/CHANGELOG-view_history-00d4ff?style=for-the-badge&labelColor=0a0a1a)](CHANGELOG.md)
[![Checklist](https://img.shields.io/badge/CHECKLIST-phase_16-ff00ff?style=for-the-badge&labelColor=0a0a1a)](docs/v3/CHECKLIST.md)
[![Roadmap](https://img.shields.io/badge/ROADMAP-v3-00ff9f?style=for-the-badge&labelColor=0a0a1a)](docs/v3/ROADMAP.md)
[![License](https://img.shields.io/badge/MIT_LICENSE-read-ff6b35?style=for-the-badge&labelColor=0a0a1a)](LICENSE)

</div>

---

<div align="center">

```
╔═══════════════════════════════════════════════════════════════╗
║  SAMPLEMIND AI  //  BUILT FOR PRODUCERS  //  PHASE 16 ACTIVE  ║
║  Python 3.12  ·  FastAPI  ·  Next.js 15  ·  Claude sonnet-4-6 ║
║  "Where neural intelligence meets musical intuition"           ║
╚═══════════════════════════════════════════════════════════════╝
```

*MIT License · © 2026 lchtangen · [github.com/lchtangen/SampleMind-AI---Beta](https://github.com/lchtangen/SampleMind-AI---Beta)*

</div>