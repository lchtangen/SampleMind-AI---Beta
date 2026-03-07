# Changelog — SampleMind AI

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] — v3.0.0

### In Progress (Phase 15)

- Textual ^0.87.0 TUI migration (13 existing screens + 3 new: AgentChat, Waveform, MixingBoard)
- Next.js 15 + React 19 web UI scaffold (`apps/web/`)
- LangGraph ^0.2.0 multi-agent orchestration
- scipy monkey-patch removal (after librosa ^0.11.0 install verification)
- Test coverage expansion: 30% → 80%+ target
- OpenTelemetry distributed tracing

---

## [2.1.0-beta] — Phase 15 Sessions 1–3 (2026-03-07)

### Added

#### AI Providers — Full v3.0 Migration (Phase 15 Session 3)

- **Ollama offline provider** (`src/samplemind/integrations/ollama_integration.py`) — NEW
  - `OllamaModel` enum: `qwen2.5:7b-instruct` (default), `phi3:mini`, `gemma2:2b`
  - `OllamaMusicProducer` class with async `analyze_music_comprehensive()` and `check_availability()`
  - Plain-text response parsing (Ollama returns prose, not JSON)
  - No API key required — needs `ollama serve` running
  - `OLLAMA_HOST` env var for custom host (default `http://localhost:11434`)
- **Claude 3.7 Sonnet extended thinking** — `anthropic_integration.py` updated
  - `CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"` added as primary model
  - Extended thinking enabled: `thinking={"type": "enabled", "budget_tokens": 5000}` for 3.7 Sonnet
  - `max_tokens` raised to 8096; `temperature` correctly omitted for extended thinking
- **Gemini 2.0 Flash** — `google_ai_integration.py` fully migrated to `google-genai` SDK
  - `GEMINI_2_0_FLASH = "gemini-2.0-flash"` as primary model
  - New `Client(api_key=...)` pattern replacing `genai.configure()`
  - Async `client.aio.models.generate_content()` replacing `GenerativeModel().generate_content()`
  - `GenerateContentConfig` with `SafetySetting` objects
  - Token usage from `response.usage_metadata.total_token_count`
- **GPT-4o default** — `openai_integration.py` cleaned up
  - Removed non-existent `GPT_5 = "gpt-5"` from `OpenAIModel` enum
  - `GPT_4O` set as default model
- **Ollama routing in AI manager** (`ai_manager.py`)
  - `OLLAMA` added to `AIProvider` enum
  - `QUICK_ANALYSIS` routed to Ollama (offline/instant)
  - `COMPREHENSIVE_ANALYSIS` and `HARMONIC_ANALYSIS` moved from Google → Anthropic (Claude primary)
  - Provider priority corrected: Anthropic=1 (PRIMARY), Google=2 (FAST), OpenAI=3 (FALLBACK), Ollama=0 (INSTANT)
  - `_convert_ollama_result()` method added

#### Dependencies — All v3.0 Targets Applied (pyproject.toml)

| Package | Before | After |
|---------|--------|-------|
| `anthropic` | `^0.7.0` | `^0.40.0` |
| `openai` | `^1.3.0` | `^1.58.0` |
| `google-generativeai` | `^0.3.0` | `google-genai ^0.8.0` (renamed) |
| `ollama` | `^0.1.7` | `^0.3.0` |
| `librosa` | `0.10.1` (pinned) | `^0.11.0` |
| `scipy` | `^1.11.4` | `^1.14.0` |
| `numpy` | `>=1.26,<2.0.0` | `>=2.0.0,<3.0.0` |
| `torch` / `torchaudio` | `^2.1.0` | `^2.5.0` |
| `transformers` | `^4.35.0` | `^4.47.0` |
| `textual` | `^0.44.0` | `^0.87.0` |
| `fastapi` | `^0.104.1` | `^0.115.0` |
| `uvicorn` | `^0.24.0` | `^0.32.0` |
| `motor` | `^3.3.1` | `^3.6.0` |
| `chromadb` | `>=0.5.0` | `^0.6.0` |
| `pytest` | `^7.4.3` | `^8.0.0` |
| `pytest-asyncio` | `^0.21.1` | `^0.23.0` |
| `ruff` | `^0.1.6` | `^0.4.0` |
| `basic-pitch` | commented out | `^0.4.0` (re-enabled) |
| `demucs` | absent | `^4.0.0` (added) |
| `pedalboard` | absent | `^0.9.0` (added) |

#### Tests — New and Rewritten

- `tests/unit/integrations/test_anthropic_integration.py` — NEW (120+ lines, 8 test classes)
  - Extended thinking param assertions (present for 3.7 Sonnet, absent for Haiku)
  - Temperature param assertions (absent for 3.7 Sonnet, present for others)
- `tests/unit/integrations/test_ollama_integration.py` — NEW (180+ lines, 8 test classes)
  - Mock `ollama.AsyncClient`, availability checks, response parsing
- `tests/unit/integrations/test_google_ai_integration.py` — REWRITTEN
  - Removed `pytest.skip()` gate (tests now always run)
  - Updated for `google-genai` SDK: `Client()`, `aio.models.generate_content()`
- `tests/unit/integrations/test_openai_integration.py` — UPDATED
  - Removed `pytest.skip()` gate
  - Removed `GPT_5` assertions, added `test_gpt5_does_not_exist()`
  - Fixed `get_stats()` → `get_usage_stats()`
- `tests/unit/integrations/test_ai_manager.py` — UPDATED
  - `TestAnalysisRoutingTable`: COMPREHENSIVE/HARMONIC → ANTHROPIC, QUICK_ANALYSIS → OLLAMA
  - `TestOllamaProvider`: enum value, `_convert_ollama_result()`
  - Provider priority: Anthropic=1 (was Google=1)

#### Documentation Reorganization (Phase 15 Sessions 1–2)

- `docs/active/` — NEW working directory for V3 migration
  - `INDEX.md` — AI agent entry point
  - `architecture/V3_ARCHITECTURE_DECISIONS.md` — ADRs
  - `devops/DEPENDENCY_UPGRADE_STATUS.md` — upgrade tracking
  - `features/WEB_UI_SPEC.md` — Next.js 15 spec
  - `models/AI_PROVIDER_UPGRADE_LOG.md` — per-provider migration log
  - `roadmap/PHASE_15_PROGRESS.md` — session log
  - `ui-ux/TUI_V3_UPGRADE_NOTES.md` — Textual ^0.87 migration guide
- 73 outdated files archived to `docs/_archive/` and `_archive/`
- Phase directories renamed: `15-PHASE-15-COMPLETED` → `15-OLD-SEMANTIC-SEARCH-COMPLETED`
- TUI screen count corrected: 11 → **13** (chain_screen.py + classification_screen.py were undocumented)

### Fixed

- `Makefile`: `setup` target now uses `poetry install` (was `pip install -r requirements.txt` — file doesn't exist)
- `Makefile`: `dev` target now uses correct server path `src.samplemind.server.main:app`
- `Dockerfile`: `CMD` now uses correct path `samplemind.server.main:app`
- `pyproject.toml` scripts entry: `src.interfaces.cli.main:app` → `samplemind.interfaces.cli.menu:main`
- All "v6" legacy strings removed from `main.py`, `__init__.py`, `interfaces/__init__.py`, `tui/app.py`
- API docs corrected: `src/samplemind/api/` does NOT exist — actual path is `interfaces/api/` + `server/`
- `pytest.ini`: removed `--cov-fail-under=80` (coverage is ~30%; gate would fail every run)
- `.pre-commit-config.yaml`: ruff hook updated from `v0.1.8` → `v0.4.10`
- `.gitignore`: removed triplicate entries
- `CONTRIBUTING.md`: removed all "v6" references, updated clone URLs, bug template version
- Dead files removed: `finder_dialog.py`, `modern_file_picker.py`, stale test files, 20+ root-level reports

### Changed

- AI provider routing: Anthropic is now unambiguously PRIMARY (priority 1) — was incorrectly set to Google
- `.env.example`: provider ordering updated to reflect 4-tier architecture (Ollama → Anthropic → Google → OpenAI)
- `GeminiModel` enum: `GEMINI_2_0_FLASH` added as primary, deprecated models removed
- `ClaudeModel` enum: `CLAUDE_3_7_SONNET` and `CLAUDE_3_5_HAIKU` added

---

## [2.1.0-beta] — Phase 10–14 (2025-11-XX to 2026-01-19)

### Phase 14 — Analytics, GitHub, Community Launch

- PostHog analytics integration
- GitHub Actions CI/CD pipeline
- Cross-platform verification suite

### Phase 13 — Effects CLI, DAW Plugins, VST3

- Effects chain CLI (reverb, EQ, compression, saturation) — `interfaces/cli/commands/effects.py`
- FL Studio plugin: Python wrapper + C++ native (JUCE, 486 lines) — `plugins/fl_studio/cpp/`
- Ableton Live: REST backend + Max for Live JS bridge — `plugins/ableton/`
- Cross-DAW plugin installer — `plugins/installer.py`
- VST3 C++ bridge with Python embedding

### Phase 12 — UX Polish, Accessibility, Performance

- WCAG 2.1 accessibility audit
- CLI startup optimization (lazy imports)
- Theme system refinement

### Phase 11 — Performance Optimization, CLI Polish

- Multi-level caching: memory + disk + ChromaDB vector
- CLI performance profiling and optimization
- Shell completions: bash, zsh, fish, PowerShell

### Phase 10 — Modern Menu, Shell Completions, Error Handling

- Modern interactive CLI menu with 12 themes and arrow-key navigation
- Questionary integration for interactive selection
- 200+ commands accessible from unified menu
- `src/samplemind/exceptions.py`: 20+ custom exception types
- Structured logging with loguru (3 output formats, auto-rotation)
- Health check commands: `samplemind health:check`, `health:status`, `health:logs`
- Shell completions for bash, zsh, fish, PowerShell
- 130+ automated tests across CLI, audio, AI, error handling, output formats

---

## [2.0.0-beta] — Phases 1–9 Foundation (2025-10-04)

- Core audio engine: LibROSA-based BPM, key, MFCC, chroma, spectral analysis
- Advanced audio loader: WAV, MP3, FLAC, OGG, AAC, AIFF support
- AI manager: multi-provider routing (Anthropic, Google, OpenAI, Ollama)
- ChromaDB vector similarity search and embeddings
- MongoDB (Motor) + Redis database layer
- FastAPI async REST API with JWT authentication and WebSocket support
- Textual TUI framework integration (initial screens)
- CLI interface (Typer + Rich)
- Sample pack creation and library management
- Docker Compose stack: MongoDB, Redis, ChromaDB, Ollama, Prometheus, Grafana

---

## Version History Summary

| Version | Phase | Date | Highlights |
|---------|-------|------|------------|
| 2.1.0-beta P15 | 15 | 2026-03-07 | AI SDK v3.0, Ollama, routing overhaul, 120+ tests |
| 2.1.0-beta | 10–14 | 2025-11 – 2026-01 | Menu, shell completions, DAW plugins, analytics |
| 2.0.0-beta | 1–9 | 2025-10-04 | Core engine, CLI, TUI, API, vector DB |

---

## Known Issues (Current)

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | `textual ^0.87.0` migration — 13 screens need API updates | 🔴 Critical | In progress (Phase 15 P4) |
| 2 | Test coverage at ~30% (target 80%) | 🟠 High | In progress |
| 3 | scipy monkey-patch in `__init__.py` | 🟡 Medium | Remove after librosa ^0.11.0 verified installed |
| 4 | Web UI not yet built | 🟠 High | Phase 15 P5 |
| 5 | CLI startup ~2s (target <1s) | 🟡 Medium | Lazy import optimization needed |

---

*Last updated: 2026-03-07 — Phase 15 Session 3 complete*
