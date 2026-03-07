# Phase 15: v3.0 Migration — IN PROGRESS

**Status:** IN PROGRESS
**Started:** 2026-03-07
**Target Completion:** TBD

---

## Overview

Phase 15 is the major v3.0 upgrade and migration cycle for SampleMind AI. This phase upgrades
all core AI provider SDKs, audio libraries, and the TUI framework to their 2025/2026 target
versions, and introduces the Next.js 15 web UI.

> Note: The directory `15-OLD-SEMANTIC-SEARCH-COMPLETED/` contains documentation for a
> previously completed Semantic Search sub-feature that was mislabeled as Phase 15. That work
> is complete. This directory represents the current active Phase 15 (v3.0 Migration).

---

## P0 Priorities

| Priority | Task | Status |
|----------|------|--------|
| P0 | Upgrade `anthropic` ^0.7.0 → ^0.40.0 | Pending |
| P0 | Upgrade `openai` ^1.3.0 → ^1.58.0 | Pending |
| P0 | Upgrade `google-generativeai` ^0.3.0 → ^0.8.0 (now `google-genai`) | Pending |
| P0 | Upgrade `textual` ^0.44.0 → ^0.87.0 | Pending |
| P1 | Upgrade `torch` ^2.1.0 → ^2.5.0 | Pending |
| P1 | Upgrade `transformers` ^4.35.0 → ^4.47.0 | Pending |
| P1 | Remove `numpy <2.0.0` cap | Pending |
| P1 | Re-enable `basic-pitch` in pyproject.toml | Pending |
| P2 | Build Next.js 15 web UI (apps/web/) | Pending |

---

## Working Documents

- [PHASE_15_PROGRESS.md](../../active/roadmap/PHASE_15_PROGRESS.md) — session-by-session log
- [V3_MIGRATION_CHECKLIST.md](../../02-ROADMAPS/V3_MIGRATION_CHECKLIST.md) — 100-item checklist
- [CURRENT_STATUS.md](../../02-ROADMAPS/CURRENT_STATUS.md) — real-time status

---

## Key Files for This Phase

| File | Purpose |
|------|---------|
| `pyproject.toml` | Dependency version changes |
| `src/samplemind/integrations/ai_manager.py` | AI provider SDK updates |
| `src/samplemind/interfaces/tui/app.py` | Textual v0.87 migration |
| `apps/web/` | Next.js 15 web UI (to be created) |

---

**Last Updated:** 2026-03-07
