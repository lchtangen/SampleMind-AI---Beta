---
applyTo: "apps/web/**/*.ts,apps/web/**/*.tsx,apps/web/**/*.js"
---

# Next.js Web App Instructions

- Location: `apps/web/` (108+ files, do NOT scaffold from scratch)
- Framework: Next.js 15 with App Router, React 19
- Auth pages go in `apps/web/src/app/(app)/` route group with sidebar layout
- Public pages go in `apps/web/src/app/` root (login, landing, etc.)
- Layout: `(app)/layout.tsx` provides sidebar + topbar for authenticated pages
- API client: `src/lib/api-client.ts` — `apiFetch<T>()` wrapper for FastAPI backend
- Utils: `src/lib/utils.ts` — `cn()` for Tailwind class merging
- Analytics: `src/lib/analytics.ts` — `getAnalytics()` no-op facade
- Design system: `src/design-system/` — Container, GlassPanel, Grid, StatCard, GradientText, WaveformBars
- Components: `src/components/` — AIChatWindow, AdvancedWaveform, SampleCard, BpmTapTempo
- Install: `cd apps/web && npm install --legacy-peer-deps`
- Build: `cd apps/web && npm run build`
- Dev: `cd apps/web && npm run dev`
