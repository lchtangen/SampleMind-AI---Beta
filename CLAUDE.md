# SampleMind AI — Beta (Phase 15 Active)
AI-powered music production platform. Python 3.12. FastMCP. Multi-provider AI.

## Current Phase
Phase 15 — v3.0 Migration: Textual TUI ^0.87 + Next.js 15 web UI.
Track: docs/02-ROADMAPS/V3_MIGRATION_CHECKLIST.md

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
- docs/02-ROADMAPS/     — current roadmaps and status
- tests/unit/           — 120+ unit tests
- plugins/ableton/      — Ableton Live plugin

## Setup
python3 -m venv .venv && source .venv/bin/activate && pip install -e .[dev]
