# SampleMind AI — Beta (Phase 17 Active)

AI-powered music production platform. Python 3.12. Multi-provider AI.

## Current Phase
Phase 17 — Agent memory + Similar sample + Realtime effects + History API + BPM tap.
Track: `docs/v3/CHECKLIST.md` | Overall: ~82% (94/115 items)

## Key Commands
| Task | Command |
|------|---------|
| Start backend | `python main.py` |
| Start frontend | `cd apps/web && npm run dev` |
| Run tests | `pytest tests/unit/ -v --tb=short` |
| Lint + typecheck | `ruff check src/ && mypy src/` |
| Format | `ruff format src/` |
| Full quality | `make quality` |
| Frontend build | `cd apps/web && npm install --legacy-peer-deps && npm run build` |

## AI Providers (2026-04)
| Provider | Model | Use |
|----------|-------|-----|
| Anthropic | claude-sonnet-4-6 | Primary analysis + curation |
| Google | gemini-2.5-flash | Fast streaming |
| OpenAI | gpt-4o | Agent workflows |
| Ollama | qwen2.5-coder:7b @ localhost:11434 | Offline inference |
| LiteLLM | Router: Claude→Gemini→GPT→Ollama | Unified fallback chain |

## Critical Files
- `src/samplemind/` — main package (interfaces, core, ai, integrations, services)
- `src/samplemind/interfaces/api/` — FastAPI backend (NOT `src/samplemind/api/`)
- `src/samplemind/ai/agents/` — LangGraph 9-node pipeline + memory
- `docs/v3/` — active roadmaps (NOT `docs/02-ROADMAPS/`)
- `tests/unit/` — 120+ unit tests
- `apps/web/` — Next.js 15 web UI (108+ TS files)
- `app/` — Tauri v2 + Svelte 5 desktop scaffold

## Copilot Customization
- `.github/copilot-instructions.md` — repository-wide Copilot instructions
- `.github/instructions/` — 21 path-specific instruction files
- `.github/agents/` — 12 custom agent profiles (`.agent.md` format)
- `.github/skills/` — 25 agent skills with SKILL.md files
- `.github/hooks/` — agent lifecycle hooks (session start, pre/post tool use)
- `AGENTS.md` — standard agent instructions (root)

## Claude Code
- `.claude/settings.json` — permissions, sandbox, hooks, env
- `.claude/commands/` — 8 slash commands (quality, test, lint, analyze, status, security, dev, build)
- `.claude/skills/` — 26 Claude-specific skills with SKILL.md files
- `.claude/agents/` — 12 subagent profiles

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'
```

## Rules
- Use `litellm_router.chat_completion()` — NOT direct provider SDKs
- No `time.sleep()` — use `asyncio.sleep()`
- No `asyncio.run()` inside Textual
- Lazy imports for torch, librosa, faiss, demucs, transformers
- Type annotations required on all new functions
- Always run `pytest tests/unit/ -v --tb=short` before committing
