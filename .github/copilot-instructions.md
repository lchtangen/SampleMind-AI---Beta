# GitHub Copilot Instructions — SampleMind AI

> Codebase context for GitHub Copilot. Read alongside any file you're working in.
> Full project instructions: `.claude/CLAUDE.md` | Active workspace index: `docs/active/INDEX.md`

---

## Project Summary

SampleMind AI is a **CLI-first, offline-capable music production AI** for audio analysis,
sample management, stem separation, MIDI transcription, and AI-powered recommendations.
Active phase: **Phase 15 — v3.0 Migration** (upgrading all AI providers, audio libs, and adding Web UI).

**Language:** Python 3.11+ | **Package manager:** Poetry | **Primary interface:** CLI + Textual TUI

---

## Tech Stack

### AI Providers
| Provider | SDK | Model | Use |
|----------|-----|-------|-----|
| Anthropic | `anthropic ^0.40.0` (target) | `claude-3-7-sonnet-20250219` | Primary analysis |
| OpenAI | `openai ^1.58.0` (target) | `gpt-4o` | Agent workflows |
| Google | `google-genai ^0.8.0` (target) | `gemini-2.0-flash` | Fast streaming |
| Ollama | `ollama ^0.3.0` | `qwen2.5:7b-instruct` | Offline inference |

### Audio
- `librosa ^0.11.0` — BPM, key, MFCC, chroma, spectral features
- `demucs ^4.0.0` — 6-stem source separation (htdemucs_6s model)
- `basic-pitch ^0.4.0` — MIDI transcription from audio
- `pedalboard ^0.9.0` — Professional audio effects (Spotify)
- `soundfile ^0.12.1` — Audio I/O (WAV, FLAC, OGG)
- `torch ^2.5.0` + `transformers ^4.47.0` — ML models

### UI / API
- `textual ^0.87.0` — Terminal UI framework (11 screens)
- `fastapi ^0.115.0` + `uvicorn` — REST API
- `next.js 15` + `react 19` + `tailwind v4` — Web UI (in progress)

### Database
- `motor ^3.6.0` — MongoDB async driver
- `redis ^5.0.1` — Session cache
- `chromadb ^0.5.0` — Vector similarity search

---

## Key File Locations

```
main.py                                        # CLI entry point (⚠️ still has "v6" in --version — legacy artifact)
pyproject.toml                                 # All dependencies (needs major v3.0 upgrade)

src/samplemind/
├── interfaces/
│   ├── cli/menu.py                            # Main CLI (~2255 lines)
│   ├── cli/commands/effects.py                # Effects chain CLI
│   ├── tui/app.py                             # Textual TUI app
│   ├── tui/screens/                           # 13 TUI screens (verified on disk)
│   │   # Screens: main, analyze, batch, results, favorites, settings,
│   │   # comparison, search, tagging, performance, library, chain, classification
│   └── api/                                   # FastAPI router layer
├── server/                                    # FastAPI server entrypoint
├── core/
│   ├── engine/audio_engine.py                 # Audio analysis engine
│   ├── loader.py                              # AdvancedAudioLoader
│   ├── database/chroma.py                     # ChromaDB vector search
│   └── library/pack_creator.py                # Sample pack creation
├── integrations/
│   ├── ai_manager.py                          # Multi-provider AI routing (CRITICAL)
│   └── daw/fl_studio_plugin.py                # FL Studio integration
├── ai/                                        # AI utilities
├── services/                                  # Business logic services
└── utils/                                     # Cross-cutting utilities

plugins/
├── fl_studio_plugin.py                        # FL Studio Python wrapper
├── fl_studio/cpp/samplemind_wrapper.cpp       # C++ native plugin (486 lines)
├── ableton/python_backend.py                  # Ableton REST backend
└── installer.py                               # Cross-DAW installer

tests/unit/                                    # 81 tests, 13 subdirectories, ~30% coverage
tests/fixtures/                                # Test audio files (integration_test.wav, neural_test.wav)
scripts/                                       # Setup + utility scripts
docs/active/INDEX.md                           # Active workspace index — read this first
docs/02-ROADMAPS/CURRENT_STATUS.md             # Current project status
docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md     # Phase 15 task checklist
```

> **Important:** `src/samplemind/api/` does **NOT** exist. The FastAPI code is at `interfaces/api/` and `server/`.

---

## Code Conventions

### Python
- **Style:** Black (line length 88) + isort + ruff
- **Types:** mypy strict — always add type annotations to new functions
- **Async:** All audio I/O and AI calls must be async (`async def`) or run in `ThreadPoolExecutor`
- **Never:** `time.sleep()` in Textual handlers, `asyncio.run()` inside Textual, blocking I/O in `compose()`
- **Imports:** Lazy imports at module level for heavy libraries (torch, librosa) — check existing patterns
- **Tests:** pytest, fixtures in `tests/fixtures/`, mocks for AI providers

### Textual TUI Patterns
```python
# Always extend Screen, bind keys, use async handlers
class MyScreen(Screen):
    BINDINGS = [("escape", "pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        result = await self.app.some_async_method()
        self.notify(f"Done: {result}")
```

### AI Manager Pattern
```python
from src.samplemind.integrations.ai_manager import SampleMindAIManager

manager = SampleMindAIManager()
result = await manager.analyze_audio(
    audio_path="sample.wav",
    model="claude-3-7-sonnet-20250219",   # or "auto"
    analysis_level="PROFESSIONAL"
)
```

### FastAPI Pattern
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/audio", tags=["audio"])

@router.post("/analyze")
async def analyze_audio(file: UploadFile) -> AnalysisResult:
    ...
```

---

## Analysis Levels

```python
# Used in audio_engine.py — match to AnalysisLevel enum
BASIC        # BPM, key, duration — <0.5s
STANDARD     # + MFCC, chroma, spectral — <1s
DETAILED     # + harmonic/percussive separation — <2s
PROFESSIONAL # + AI analysis, BEATs classification, embeddings — <5s
```

---

## Phase 15 — Active Work (P0 blockers first)

### What Has NOT been done yet (0% complete as of 2026-03-07)
1. `pyproject.toml` — upgrade `anthropic ^0.7.0→^0.40.0`, `openai ^1.3.0→^1.58.0`, rename `google-genai`, `textual ^0.44.0→^0.87.0`, `numpy`, `torch`, `scipy`, `librosa`
2. **ADD** `demucs ^4.0.0` and `pedalboard ^0.9.0` (not in pyproject at all yet)
3. Re-enable `basic-pitch = "^0.4.0"` (commented out)
4. `src/samplemind/integrations/ai_manager.py` — migrate to new SDK APIs
5. `src/samplemind/interfaces/tui/` — upgrade 13 screens for Textual ^0.87
6. `apps/web/` — scaffold Next.js 15 web UI (directory exists but empty)
7. `tests/` — raise coverage from 30% → 80%+
8. Fix `main.py` legacy "v6" references in docstring and `--version`
9. Fix `pyproject.toml` scripts entry path (`src.interfaces.cli.main:app` is wrong)

Full checklist: `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md`
Dependency upgrade order: `docs/active/devops/DEPENDENCY_UPGRADE_STATUS.md`

---

## What NOT To Do

- Do not add `time.sleep()` anywhere in the codebase
- Do not cap numpy `<2.0.0` — remove this cap in Phase 15
- Do not remove the scipy monkey-patch in `__init__.py` until librosa is upgraded to ^0.11.0
- Do not commit without running `make quality` (ruff + mypy + bandit)
- Do not create files unless necessary — prefer editing existing ones
- Do not add backwards-compatibility shims for code that is being migrated
- Do not reference `src/samplemind/api/` — that path does not exist; use `interfaces/api/` + `server/`
- Do not assume `demucs` or `pedalboard` are installed — they are not in pyproject.toml yet
