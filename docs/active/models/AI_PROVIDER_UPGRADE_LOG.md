# AI Provider SDK Migration Log

**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07

---

## Provider Status

| Provider | Package (old) | Package (new) | Version (old) | Version (new) | Status |
|----------|--------------|--------------|--------------|--------------|--------|
| Anthropic | `anthropic` | `anthropic` | ^0.7.0 | ^0.40.0 | Pending |
| OpenAI | `openai` | `openai` | ^1.3.0 | ^1.58.0 | Pending |
| Google | `google-generativeai` | `google-genai` | ^0.3.0 | ^0.8.0 | Pending |
| Ollama | `ollama` | `ollama` | ^0.1.0 | ^0.3.0 | Pending |

---

## Anthropic — anthropic ^0.7.0 → ^0.40.0

**Key breaking changes:**
- `Anthropic()` client (sync) replaces `anthropic.Anthropic()`
- `AsyncAnthropic()` for async usage
- Model IDs updated: `claude-3-7-sonnet-20250219` (was `claude-3-sonnet-20240229`)
- Extended thinking: `thinking={"type": "enabled", "budget_tokens": 10000}`
- Streaming via `.stream()` context manager

**Files to update:**
- `src/samplemind/integrations/ai_manager.py`

---

## OpenAI — openai ^1.3.0 → ^1.58.0

**Key breaking changes:**
- Agents SDK now stable: `from openai import agents`
- Responses API: `client.responses.create()` for stateful multi-turn
- New model IDs: `gpt-4o`, `gpt-4o-mini`

**Files to update:**
- `src/samplemind/integrations/ai_manager.py`

---

## Google — google-generativeai ^0.3.0 → google-genai ^0.8.0

**Key breaking changes:**
- Package renamed: `google-generativeai` → `google-genai`
- Import: `from google import genai` (was `import google.generativeai as genai`)
- Client-based API: `client = genai.Client(api_key=...)`
- Model: `gemini-2.0-flash` (was `gemini-pro`)

**Files to update:**
- `src/samplemind/integrations/ai_manager.py`
- `pyproject.toml` (package name change)

---

## Migration Notes

When upgrading, update `pyproject.toml` version constraints first, then run:
```bash
source .venv/bin/activate
pip install --upgrade anthropic openai google-genai ollama
make quality  # verify no regressions
```
