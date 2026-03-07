# 🚀 SampleMind AI — Session Start Guide

> Read this at the start of every Claude Code / Copilot / Codex session.  
> **Phase:** 15 — v3.0 Migration | **Date started:** 2026-03-07

---

## ⚡ 3-Step Session Startup

```bash
# 1. Go to project
cd ~/Projects/SampleMind-AI---Beta   # adjust path if needed

# 2. Pull latest
git pull

# 3. Activate environment
source .venv/bin/activate
```

Then check what's next:
```bash
# In Claude Code:
/read CLAUDE.md
/read docs/02-ROADMAPS/CURRENT_STATUS.md
/read docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md
```

---

## 🎯 What We're Building

**SampleMind AI** is a music production AI platform with:
- 🖥️ **CLI** (primary product) — Terminal interface for sample analysis, effects, library management
- 🎨 **TUI** — Beautiful terminal UI built with Textual framework
- 🌐 **Web UI** (Phase 15) — Next.js 15 + React 19 web platform
- 🤖 **Multi-Agent AI** — Claude 3.7, Gemini 2.0, GPT-4o, Ollama (offline)
- 🎵 **DAW Plugins** — FL Studio, Ableton, VST3 (JUCE)

**Current focus:** Upgrading from v2.0-beta to v3.0 — modern AI models, new audio tools, web UI, multi-agent architecture.

---

## 🗂️ Project State (2026-03-07)

| Area | Status | Notes |
|------|--------|-------|
| CLI | ✅ Working | `python main.py` |
| TUI (11 screens) | ✅ Working | Needs Textual upgrade |
| FastAPI server | ✅ Working | localhost:8000 |
| FL Studio plugin | ✅ Working | C++ + Python |
| Ableton plugin | ✅ Working | REST + JS |
| AI providers | ⚠️ Outdated | Deps 2+ years old |
| Web UI | ❌ Not started | Phase 15 priority |
| Multi-agent | ❌ Not started | Phase 15 priority |
| Test coverage | ⚠️ 30% | Target: 80% |

---

## 🔴 Current P0 Tasks (Week 1: Mar 7–14)

These are the most urgent items. Pick one and complete it:

1. **Upgrade `anthropic` → `^0.40.0`** — update pyproject.toml + ai_manager.py
2. **Upgrade `openai` → `^1.58.0`** — update pyproject.toml + ai_manager.py  
3. **Upgrade `google-generativeai` → `^0.8.0`** — migrate to new google.genai SDK
4. **Upgrade `textual` → `^0.87.0`** — fix all breaking API changes in TUI
5. **Remove `numpy <2.0.0` cap** — needed for torch 2.5+ and transformers 4.47+
6. **Fix scipy monkey-patch** in `src/samplemind/__init__.py`
7. **Re-enable `basic-pitch`** in pyproject.toml (currently commented out)
8. **Add `demucs ^4.0.0`** for source separation
9. **Add `pedalboard ^0.9.0`** for Spotify audio effects

---

## 🛠️ Recommended Session Workflows

### Workflow A — Dependency Upgrade Session
```bash
# 1. Read current pyproject.toml
cat pyproject.toml

# 2. Upgrade one dependency at a time
poetry add anthropic@^0.40.0

# 3. Run tests to check nothing broke
make test

# 4. Fix any import/API changes in source files
# 5. Commit: git commit -m "feat(phase15): upgrade anthropic to ^0.40.0"
```

### Workflow B — Feature Implementation Session
```bash
# 1. Read the target file
cat src/samplemind/integrations/ai_manager.py

# 2. Implement the feature (Claude Code is best for large files)
# 3. Write tests in tests/unit/
# 4. make quality && make test
# 5. Commit
```

### Workflow C — TUI Development Session
```bash
# 1. Launch TUI to see current state
python -m src.samplemind.interfaces.tui.main

# 2. Read the screen you're working on
cat src/samplemind/interfaces/tui/screens/analyze_screen.py

# 3. Make changes, preview with Ctrl+C to restart
# 4. Test with make test -- tests/unit/tui/
```

### Workflow D — Web UI Session (Phase 15)
```bash
# Only after apps/web/ is initialized:
cd apps/web
npm install
npm run dev   # Next.js dev server → localhost:3000
```

---

## 🤖 AI Tool Routing Guide

| What you're doing | Best tool | Why |
|-------------------|-----------|-----|
| Refactor a 2000+ line file | Claude Code | Largest context window |
| Implement new feature across 5+ files | Claude Code | Full codebase awareness |
| Quick function completion | Copilot (VSCode) | In-editor, fast |
| Write boilerplate (new component) | Codex (terminal) | `codex "create a Textual Screen"` |
| Research dependency versions | Any + web | `poetry search` or PyPI |
| Write 20+ unit tests | Claude Code | Best test quality |
| Generate TypeScript types | Copilot | In VSCode TS files |
| Create a GitHub PR | Copilot (GitHub) | `@copilot` on issues |

---

## 🏗️ Architecture Quick Reference

```
src/samplemind/
├── __init__.py           ← lazy imports (has scipy workaround — fix in Phase 15)
├── core/
│   ├── engine/
│   │   └── audio_engine.py   ← THE main audio analysis file
│   ├── loader.py             ← AdvancedAudioLoader (multi-format)
│   ├── library/
│   │   └── pack_creator.py   ← sample pack creation
│   └── database/
│       └── chroma.py         ← ChromaDB vector search
├── integrations/
│   ├── ai_manager.py         ← multi-provider AI (NEEDS UPGRADE)
│   └── daw/
│       └── fl_studio_plugin.py
├── interfaces/
│   ├── cli/
│   │   ├── menu.py           ← main CLI (~2255 lines, Rich + Typer)
│   │   └── commands/
│   │       └── effects.py    ← Effects CLI (Phase 13)
│   └── tui/
│       ├── app.py            ← Textual app root
│       ├── main.py           ← entry point
│       └── screens/          ← 11 screens (all working)
```

---

## ✅ Session End Checklist

Before you stop working, do this:

```bash
# 1. Run quality checks
make quality

# 2. Run tests
make test

# 3. Update status doc
# Edit docs/02-ROADMAPS/CURRENT_STATUS.md
# Add what you completed, update progress table

# 4. Update checklist
# Edit docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md
# Tick off completed items, update progress %

# 5. Commit everything
git add -A
git commit -m "feat(phase15): <describe what you did>"
git push origin main
```

---

## 📞 Ports & Services Reference

| Service | Port | Start command |
|---------|------|---------------|
| FastAPI | 8000 | `make dev` |
| Next.js | 3000 | `cd apps/web && npm run dev` |
| MongoDB | 27017 | `docker-compose up -d mongodb` |
| Redis | 6379 | `docker-compose up -d redis` |
| ChromaDB | 8002 | `docker-compose up -d chromadb` |
| Celery Flower | 5555 | `./start_flower.sh` |
| Ollama | 11434 | `scripts/launch-ollama-api.sh` |

---

## 🐛 Known Issues Quick Reference

| Issue | Workaround | Fix in |
|-------|------------|--------|
| `anthropic` SDK outdated | Don't use streaming | P0 upgrade |
| `scipy` import at top-level | Existing monkey-patch | P0 fix |
| `basic-pitch` commented out | Can't do MIDI transcription | P0 re-enable |
| CLI startup ~2s | Use `--no-banner` flag | P1 lazy imports |
| TUI Textual v0.44 | Some CSS broken | P1 upgrade |
| No web UI | Use CLI/TUI | Phase 15 |

---

*SESSION_START_GUIDE.md v1.0 — Created 2026-03-07. Update as the project evolves.*