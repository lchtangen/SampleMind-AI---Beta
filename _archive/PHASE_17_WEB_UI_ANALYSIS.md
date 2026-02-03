# Phase 17: Web UI Analysis Report

**Date:** 2025-05-20 (Simulated)
**Target:** `apps/web`
**Status:** Analysis Complete - CRITICAL GAPS FOUND

## 1. Executive Summary

The Web UI is a modern **Next.js 14** application using **App Router**, **TypeScript**, and **Tailwind CSS**. It includes advanced visualization components (Three.js/Fiber) for audio analysis. However, the connectivity layer to the Python backend is currently **broken** due to missing library files.

## 2. Technical Inventory

| Component      | Technology                                | Status                 |
| -------------- | ----------------------------------------- | ---------------------- |
| **Framework**  | Next.js 14.1.0                            | ✅ Up to date          |
| **Router**     | App Router (`app/`)                       | ✅ Modern standard     |
| **Styling**    | Tailwind CSS + Radix UI                   | ✅ Robust              |
| **State**      | React Query + Context                     | ✅ Good pattern        |
| **Audio Vis**  | primitives from `react-three-fiber`, `d3` | ✅ Advanced capability |
| **API Client** | Custom (`@/lib/api-client`)               | ❌ **MISSING**         |
| **Sockets**    | Custom (`WebSocketManager`)               | ❌ **MISSING**         |

## 3. Architecture Audit

### 3.1 Directory Structure Anomaly

The project has a split structure which may cause confusion:

- `apps/web/app/` (Next.js Routes) -> **At Root**
- `apps/web/src/` (Source Code) -> **Contains `components`, `lib`, but also `hooks`.**
- `apps/web/hooks/` (Hooks) -> **Also exists at Root.**

_Recommendation:_ Consolidate all source code into `src/` (move `app` to `src/app`, `hooks` to `src/hooks`) to match the `tsconfig` `@/*` alias mapping which points to `./src/*`.

### 3.2 The "Missing Link"

Multiple hooks (`useAudio`, `useWebSocket`) import from `@/lib/api-client`.
Analysis of `apps/web/src/lib` shows **this file does not exist**.

- Missing: `apps/web/src/lib/api-client.ts`
- Missing: `apps/web/src/lib/websocket-manager.ts` (or mapped inside api-client)

This renders the frontend incapable of communicating with the backend without immediate remediation.

## 4. Integration Status

- **Config**: `next.config.mjs` and `.env` are correctly set up to point to `localhost:8000`.
- **Endpoints Expected**:
  - `POST /api/audio/upload` (inferred from `useAudio`)
  - `GET /api/audio` (list)
  - `WS /ws/{user_id}` (WebSockets)

## 5. Phase 17 Action Plan

1.  **Restructure**: Move root-level `hooks/` and `app/` into `src/` to strictly follow the `@/` alias convention.
2.  **Restore**: Create `src/lib/api-client.ts` implementing `AudioAPI`, `TokenManager`, and `WebSocketManager`.
3.  **Connect**: Verify the connection to the Python backend (FastAPI).
4.  **Visualize**: Ensure `ThreeJSAudioVisualizer` receives data correctly from the now-working API.

## 6. Detailed File Listing (Key Files Only)

- `apps/web/app/page.tsx`: Landing page (Mockup ready).
- `apps/web/app/dashboard/page.tsx`: Main dashboard (Mockup ready).
- `apps/web/hooks/useAudio.ts`: Logic exists but imports are broken.
