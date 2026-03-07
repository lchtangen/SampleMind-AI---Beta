# SampleMind AI — Active Workspace Index

> **AI Agent Entry Point** — Read this file first to orient yourself in the codebase.
> Last Updated: 2026-03-07 | Active Phase: 15 — v3.0 Migration | Version: 2.1.0-beta → 3.0.0

---

## What Is This Project?

SampleMind AI is a CLI-first, offline-capable music production AI tool for audio analysis,
sample management, stem separation, MIDI transcription, and AI-powered recommendations.

**Primary interfaces:** CLI (main product), TUI (Textual), FastAPI REST, Next.js 15 web UI (Phase 15)
**AI providers:** Claude 3.7 Sonnet (primary), Gemini 2.0 Flash, GPT-4o, Ollama (offline)
**Audio stack:** librosa, demucs v4, basic-pitch, pedalboard (Spotify), Microsoft BEATs

---

## Active Phase 15 — Where To Start

| Task | Read This First |
|------|----------------|
| What is the current state? | [CURRENT_STATUS.md](../../docs/02-ROADMAPS/CURRENT_STATUS.md) |
| What needs to be done next? | [V3_MIGRATION_CHECKLIST.md](../../docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md) |
| Session-by-session progress log | [roadmap/PHASE_15_PROGRESS.md](roadmap/PHASE_15_PROGRESS.md) |
| Full 100-point upgrade roadmap | [roadmap/V3_100_KEYPOINTS.md](roadmap/V3_100_KEYPOINTS.md) |
| Architecture decisions (ADRs) | [architecture/V3_ARCHITECTURE_DECISIONS.md](architecture/V3_ARCHITECTURE_DECISIONS.md) |
| Dependency upgrade status | [devops/DEPENDENCY_UPGRADE_STATUS.md](devops/DEPENDENCY_UPGRADE_STATUS.md) |
| AI provider upgrade log | [models/AI_PROVIDER_UPGRADE_LOG.md](models/AI_PROVIDER_UPGRADE_LOG.md) |
| TUI v3 upgrade notes | [ui-ux/TUI_V3_UPGRADE_NOTES.md](ui-ux/TUI_V3_UPGRADE_NOTES.md) |
| Web UI spec (Phase 15) | [features/WEB_UI_SPEC.md](features/WEB_UI_SPEC.md) |

---

## Key Source Files

```
src/samplemind/
├── interfaces/
│   ├── cli/menu.py                    # Main CLI (~2255 lines) — primary product
│   ├── cli/commands/effects.py        # Effects chain CLI
│   ├── tui/app.py                     # Textual TUI app
│   ├── tui/screens/                   # 13 TUI screens (verified on disk):
│   │   # main, analyze, batch, results, favorites, settings, comparison,
│   │   # search, tagging, performance, library, chain, classification
│   └── api/                           # FastAPI router layer
├── server/                            # FastAPI server entrypoint
├── core/
│   ├── engine/audio_engine.py         # Audio analysis (BPM, key, MFCC, stems)
│   ├── loader.py                      # AdvancedAudioLoader
│   ├── database/chroma.py             # ChromaDB vector search
│   └── library/pack_creator.py        # Sample pack creation
├── integrations/
│   ├── ai_manager.py                  # Multi-provider AI routing (CRITICAL)
│   └── daw/fl_studio_plugin.py        # FL Studio integration
├── ai/                                # AI utilities
└── services/                          # Business logic services

plugins/
├── fl_studio_plugin.py                # FL Studio Python wrapper
├── fl_studio/cpp/                     # C++ native plugin (JUCE)
├── ableton/                           # Ableton REST backend + JS bridge
└── installer.py                       # Cross-DAW installer

main.py                                # CLI entry point
pyproject.toml                         # Dependencies (NEEDS v3.0 upgrade)
```

---

## Document Directory Map

```
docs/
├── active/                            # <-- YOU ARE HERE: V3 working documents
│   ├── INDEX.md                       # This file — master AI navigation hub
│   ├── architecture/
│   │   └── V3_ARCHITECTURE_DECISIONS.md   # ADRs for v3.0 decisions
│   ├── devops/
│   │   └── DEPENDENCY_UPGRADE_STATUS.md   # Tracks all dep upgrades
│   ├── features/
│   │   └── WEB_UI_SPEC.md                 # Next.js 15 web UI specification
│   ├── models/
│   │   └── AI_PROVIDER_UPGRADE_LOG.md     # Claude/OpenAI/Gemini upgrade log
│   ├── roadmap/
│   │   ├── PHASE_15_PROGRESS.md           # Session-by-session log (update each session)
│   │   └── V3_100_KEYPOINTS.md            # Full 100-point v3.0 upgrade plan
│   └── ui-ux/
│       └── TUI_V3_UPGRADE_NOTES.md        # Textual ^0.87 migration notes
│
├── 02-ROADMAPS/                       # Authoritative status + checklist
│   ├── CURRENT_STATUS.md              # Real-time project status (update every session)
│   ├── V3_MIGRATION_CHECKLIST.md      # 100-item P0/P1/P2 checklist (tick off as done)
│   └── README.md                      # Roadmap navigation
│
├── 04-TECHNICAL-IMPLEMENTATION/       # User guides + reference + technical docs
│   ├── guides/                        # Installation, platform, AI setup guides
│   │   ├── AI_INTEGRATION_SETUP.md    # AI provider configuration (v3.0 updated)
│   │   ├── TEXTUAL_MIGRATION.md       # TUI v0.87 migration guide
│   │   ├── INSTALLATION_GUIDE.md      # Main install guide
│   │   └── PLUGIN_INSTALLATION_GUIDE.md  # DAW plugin install
│   ├── reference/
│   │   └── DEVELOPMENT.md             # Development reference
│   └── technical/
│       ├── audio_processing.md        # Audio pipeline deep dive
│       └── OPTIMIZATION_GUIDE.md      # Performance optimization
│
├── 00-INDEX/                          # Phase index and status dashboard
│   ├── MASTER_PHASE_INDEX.md          # All phases 1-15 documented
│   └── PHASE_STATUS_DASHBOARD.md      # Phase completion status
│
├── 01-PHASES/15-PHASE-15-IN-PROGRESS/ # Active phase directory
│   └── README.md                      # Phase 15 entry point
│
├── API_DOCUMENTATION.md               # Full FastAPI reference (24K)
├── CLI_REFERENCE.md                   # Full CLI command reference (62K)
├── SESSION_START_GUIDE.md             # Session startup checklist
└── README.md                          # Docs home page
```

---

## Phase 15 — Priority Queue

### P0 — Critical (unblocks everything)
- [ ] Upgrade `anthropic ^0.7.0` → `^0.40.0` (Claude 3.7 Sonnet + extended thinking)
- [ ] Upgrade `openai ^1.3.0` → `^1.58.0` (GPT-4o + Agents SDK)
- [ ] Rename `google-generativeai` → `google-genai ^0.8.0` (Gemini 2.0 Flash)
- [ ] Remove `numpy <2.0.0` cap; upgrade numpy, scipy, torch together
- [ ] Re-enable `basic-pitch = "^0.4.0"` in pyproject.toml
- [ ] Upgrade `textual ^0.44.0` → `^0.87.0` + fix breaking TUI changes

### P1 — Core upgrades (Week 2)
- [ ] Add `demucs ^4.0.0` — 6-stem source separation (htdemucs_6s)
- [ ] Add `pedalboard ^0.9.0` — Spotify professional audio effects
- [ ] Implement multi-agent architecture with LangGraph
- [ ] Build 3 new TUI screens: AgentChatScreen, WaveformScreen, MixingBoardScreen

### P2 — New features (Week 3-4)
- [ ] Scaffold `apps/web/` — Next.js 15 + React 19 + Tailwind v4
- [ ] FastAPI → TypeScript client generation from OpenAPI spec
- [ ] Upgrade test coverage 30% → 80%+

---

## Common Tasks — What To Read

| Scenario | Files to read |
|----------|--------------|
| Working on audio analysis | `src/samplemind/core/engine/audio_engine.py` + `docs/04-TECHNICAL-IMPLEMENTATION/technical/audio_processing.md` |
| Working on AI integration | `src/samplemind/integrations/ai_manager.py` + `docs/active/models/AI_PROVIDER_UPGRADE_LOG.md` |
| Working on CLI | `src/samplemind/interfaces/cli/menu.py` + `docs/CLI_REFERENCE.md` |
| Working on TUI | `src/samplemind/interfaces/tui/app.py` + `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md` |
| Working on API | `src/samplemind/api/` + `docs/API_DOCUMENTATION.md` |
| Working on DAW plugins | `plugins/` + `docs/04-TECHNICAL-IMPLEMENTATION/guides/PLUGIN_INSTALLATION_GUIDE.md` |
| Upgrading dependencies | `pyproject.toml` + `docs/active/devops/DEPENDENCY_UPGRADE_STATUS.md` |
| Understanding architecture | `docs/active/architecture/V3_ARCHITECTURE_DECISIONS.md` + `docs/04-TECHNICAL-IMPLEMENTATION/technical/` |
| Starting a new session | `docs/SESSION_START_GUIDE.md` + `docs/02-ROADMAPS/CURRENT_STATUS.md` |
| Planning next task | `docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md` + `docs/active/roadmap/PHASE_15_PROGRESS.md` |

---

## Critical Rules (Do Not Violate)

1. Never call `scipy` functions at module import time (`src/samplemind/__init__.py` monkey-patch)
2. Never use `asyncio.run()` inside Textual event handlers — use `async def`
3. Never block `main.py` event loop — audio I/O must be in `ThreadPoolExecutor`
4. Run `make quality` before every commit (`ruff + mypy + bandit`)
5. Update `docs/02-ROADMAPS/CURRENT_STATUS.md` and `docs/active/roadmap/PHASE_15_PROGRESS.md` at session end

---

## Service Ports

| Service | Port | Run Command |
|---------|------|-------------|
| CLI | — | `python main.py` |
| FastAPI | 8000 | `make dev` |
| MongoDB | 27017 | `docker-compose up -d` |
| Redis | 6379 | `docker-compose up -d` |
| ChromaDB | 8002 | `docker-compose up -d` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |

---

*This file is the master navigation hub for Claude Code, GitHub Copilot, and all AI agents.*
*Update when adding new active working documents or changing the directory structure.*
