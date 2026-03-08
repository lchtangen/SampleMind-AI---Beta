# Dependency Upgrade Status

**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07 (Session 3 complete)

---

## Summary

| Priority | Total | Done | Pending |
|----------|-------|------|---------|
| P0 Critical | 12 | 11 | 1 |
| P1 High | 8 | 8 | 0 |
| P2 Medium | 6 | 6 | 0 |
| New (added) | 6 | 6 | 0 |
| **Total** | **32** | **31** | **1** |

---

## P0 Critical — AI Providers

| Package | Before | After | File Changed | Status |
|---------|--------|-------|--------------|--------|
| `anthropic` | `^0.7.0` | `^0.40.0` | `pyproject.toml` + `anthropic_integration.py` | ✅ Done |
| `openai` | `^1.3.0` | `^1.58.0` | `pyproject.toml` + `openai_integration.py` | ✅ Done |
| `google-generativeai` | `^0.3.0` | `google-genai ^0.8.0` | `pyproject.toml` + `google_ai_integration.py` | ✅ Done |
| `ollama` | `^0.1.7` | `^0.3.0` | `pyproject.toml` + new `ollama_integration.py` | ✅ Done |

## P0 Critical — Audio Stack

| Package | Before | After | Status |
|---------|--------|-------|--------|
| `librosa` | `0.10.1` (pinned) | `^0.11.0` | ✅ Done |
| `scipy` | `^1.11.4` | `^1.14.0` | ✅ Done |
| `numpy` | `>=1.26,<2.0.0` | `>=2.0.0,<3.0.0` | ✅ Done — `<2.0.0` cap removed |
| `torch` / `torchaudio` | `^2.1.0` | `^2.5.0` | ✅ Done |
| `transformers` | `^4.35.0` | `^4.47.0` | ✅ Done |
| `textual` | `^0.44.0` | `^0.87.0` | ✅ pyproject.toml updated — ⚠️ TUI screens not yet migrated |
| `basic-pitch` | commented out | `^0.4.0` | ✅ Done — re-enabled |
| scipy monkey-patch | `__init__.py` | remove after librosa verified | ⏳ Pending — needs install test |

## P1 High — New Dependencies Added

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| `demucs` | `^4.0.0` | 6-stem source separation (htdemucs_6s) | ✅ Added to pyproject.toml |
| `pedalboard` | `^0.9.0` | Spotify professional audio effects | ✅ Added to pyproject.toml |
| `faster-whisper` | `^1.1.0` | Fast local speech-to-text / transcription | ✅ Added to pyproject.toml |
| `openai-agents` | `^0.0.5` | OpenAI Agents SDK for agent workflows | ✅ Added to pyproject.toml |
| `langgraph` | `^0.2.0` | LangGraph multi-agent orchestration | ✅ Added to pyproject.toml |
| `langchain-core` | `^0.3.0` | LangChain core abstractions | ✅ Added to pyproject.toml |

## P2 Medium — Infra Upgrades

| Package | Before | After | Status |
|---------|--------|-------|--------|
| `fastapi` | `^0.104.1` | `^0.115.0` | ✅ Done |
| `uvicorn` | `^0.24.0` | `^0.32.0` | ✅ Done |
| `motor` | `^3.3.1` | `^3.6.0` | ✅ Done |
| `chromadb` | `>=0.5.0` | `^0.6.0` | ✅ Done |
| `ruff` (dev) | `^0.1.6` | `^0.4.0` | ✅ Done |
| `pytest` (dev) | `^7.4.3` | `^8.0.0` | ✅ Done |

---

## Remaining Work

### 1. scipy Monkey-Patch Removal (Medium priority)

**File:** `src/samplemind/__init__.py` lines 24–33

```python
# This patch is still needed until librosa ^0.11.0 is installed and verified:
try:
    import scipy.signal
    if not hasattr(scipy.signal, 'hann'):
        import scipy.signal.windows
        scipy.signal.hann = scipy.signal.windows.hann
except ImportError:
    pass
```

**When to remove:** After running `poetry install` and confirming `librosa ^0.11.0` imports cleanly.

### 2. TUI Screens Migration (High priority — Phase 15 P4)

`textual ^0.87.0` is in `pyproject.toml` but the 13 TUI screens have not been updated for the new API. Tracked in `docs/active/ui-ux/TUI_V3_UPGRADE_NOTES.md`.

### 3. Dependencies to Install

All pyproject.toml changes are code-only. The actual packages need to be installed:

```bash
source .venv/bin/activate
make upgrade-deps   # runs: poetry update
# or for fresh install:
make setup          # poetry install from scratch
```

---

## Installation Order (avoids conflicts)

```
1. scipy ^1.14.0         — unblocks monkey-patch removal
2. librosa ^0.11.0       — remove scipy monkey-patch after this
3. numpy >=2.0.0         — must be before torch
4. torch ^2.5.0 + torchaudio + transformers  — upgrade together
5. anthropic ^0.40.0
6. openai ^1.58.0
7. google-genai ^0.8.0
8. ollama ^0.3.0
9. textual ^0.87.0       — then audit all 13 TUI screens
10. demucs / pedalboard / basic-pitch / faster-whisper
11. langgraph / langchain-core / openai-agents
12. fastapi + uvicorn + motor + chromadb
```

---

*Updated: 2026-03-07 — Session 3 complete. All P0/P1 pyproject.toml changes applied.*
