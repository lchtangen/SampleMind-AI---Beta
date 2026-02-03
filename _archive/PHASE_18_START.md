# Phase 18: Web UI Build & Integration

**Date:** 2025-05-20 (Simulated)
**Status:** In Progress
**Goal:** Verify the restructured Web UI builds correctly and integrates with the backend.

## 1. Objectives

- [ ] **Build Validation**: Ensure `apps/web` compiles with `next build` after the file restructuring.
- [ ] **Dependency Management**: Ensure all packages are installed and linked (pnpm workspace).
- [ ] **Integration Test**: Verify the "Upload" flow works against the local Python backend.
- [ ] **UI Integration**: Ensure `ThreeJSAudioVisualizer` and other components are correctly rendered.

## 2. Plan

1. Install dependencies.
2. Run `tsc` (via `typecheck` script) or `next build` to find broken imports.
3. Fix import errors resulting from the `app/` -> `src/app/` move.
4. Launch Backend + Frontend.
5. Perform End-to-End Check.
