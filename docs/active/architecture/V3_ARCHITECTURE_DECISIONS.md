# v3.0 Architecture Decisions (ADR Log)

**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07

---

## ADR-001: Upgrade Anthropic SDK to ^0.40.0

**Date:** 2026-03-07
**Status:** Proposed

**Context:** The current `anthropic ^0.7.0` uses a deprecated API surface. Claude 3.7 Sonnet
with extended thinking requires `^0.40.0`.

**Decision:** Upgrade to `anthropic ^0.40.0`. Migrate all `Anthropic()` calls to use the new
client pattern. Add extended thinking support for PROFESSIONAL analysis level.

**Consequences:**
- Breaking: client instantiation changes
- Gain: extended thinking, streaming improvements, claude-3-7-sonnet-20250219 support

---

## ADR-002: Rename google-generativeai → google-genai

**Date:** 2026-03-07
**Status:** Proposed

**Context:** Google deprecated `google-generativeai` in favor of `google-genai ^0.8.0`.
The import path also changes (`from google import genai`).

**Decision:** Replace `google-generativeai` with `google-genai` in `pyproject.toml`.
Update all imports in `ai_manager.py`.

**Consequences:**
- Breaking: import path change
- Gain: Gemini 2.0 Flash support, lower latency

---

## ADR-003: Remove numpy <2.0.0 cap

**Date:** 2026-03-07
**Status:** Proposed

**Context:** numpy <2.0.0 cap was added to avoid scipy/torch incompatibilities that are now
resolved in scipy ^1.14.0 and torch ^2.5.0.

**Decision:** Remove the cap. Upgrade numpy, scipy, and torch together to avoid conflicts.

**Consequences:** Must upgrade scipy and torch in the same session as numpy.

---

## ADR-004: Adopt Next.js 15 App Router for Web UI

**Date:** 2026-03-07
**Status:** Proposed

**Context:** Phase 15 introduces a browser UI. Next.js 15 with App Router, React 19, and
Tailwind v4 is the current best-in-class stack.

**Decision:** Scaffold `apps/web/` with Next.js 15. Use shadcn/ui for components, Zustand v5
for state, TypeScript API client generated from FastAPI OpenAPI spec.

**Consequences:** New `apps/web/` directory. Node.js + pnpm added to dev requirements.

---

## ADR-005: Textual ^0.87 — No Rust Rewrite

**Date:** 2026-03-07 (reconfirmed from original Phase 13 decision)
**Status:** Active

**Context:** The TUI upgrade from ^0.44 to ^0.87 was evaluated alongside a Rust rewrite.

**Decision:** Stay with Textual (Python). Upgrade to ^0.87 for Phase 15 new screens
(AgentChatScreen, WaveformScreen, MixingBoardScreen).

**Consequences:** ~2-3 week migration effort vs. 6-12 months for Rust. Python audio stack
(librosa, demucs, pedalboard) preserved.
