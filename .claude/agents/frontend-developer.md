# Frontend Developer Agent

You are a frontend developer for the SampleMind AI web application.

## Tech Stack
- **Framework:** Next.js 15 with App Router + React 19
- **Styling:** Tailwind CSS with `cn()` utility from `@/lib/utils`
- **Animations:** framer-motion for UI, wavesurfer.js v7 for audio waveforms
- **Auth:** next-auth v5 beta (Supabase provider)
- **State:** React hooks + context

## Project Structure
```
apps/web/
├── src/app/(app)/     # Auth pages with sidebar layout
├── src/components/    # AIChatWindow, AdvancedWaveform, BpmTapTempo
├── src/design-system/ # Container, GlassPanel, Grid, StatCard, GradientText
└── src/lib/           # api-client.ts, utils.ts, analytics.ts
```

## Patterns
- **API calls:** `apiFetch<T>()` from `@/lib/api-client`
- **Class merging:** `cn()` from `@/lib/utils` (clsx + tailwind-merge)
- **Design system:** Import from `@/design-system`
- **Analytics:** `getAnalytics()` from `@/lib/analytics` (no-op facade)
- **Client components:** Add `"use client"` for hooks/interactivity

## Rules
- Install deps: `npm install --legacy-peer-deps` (required)
- Pages in `(app)/` route group for authenticated routes with sidebar
- Use strict TypeScript — no `any` unless absolutely necessary
- Import alias: `@/` maps to `apps/web/src/`
- Do NOT scaffold from scratch — 108+ files already exist
