# SampleMind AI — Beta (Phase 16 Active)
AI-powered music production platform. Python 3.12. FastMCP. Multi-provider AI.

## Current Phase
Phase 16 — Web UI completions + Agent pipeline + Production hardening.
Track: docs/v3/CHECKLIST.md

## Key Commands
- Start:   python main.py
- Tests:   pytest tests/ -v --cov
- Lint:    ruff check . && mypy .
- Format:  ruff format .

## AI Providers (2026-04)
- Claude:  claude-sonnet-4-6
- Gemini:  gemini-2.5-flash
- GPT:     gpt-4o
- Local:   ollama/qwen2.5-coder:7b at http://localhost:11434

## Critical Files
- src/samplemind/       — main package
- docs/v3/              — current roadmaps and status (CHECKLIST.md, STATUS.md)
- tests/unit/           — 120+ unit tests
- apps/web/             — Next.js 15 web UI (108 TS files, largely built)
- app/                  — Tauri v2 + Svelte 5 desktop scaffold

## Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e .[dev]
