---
applyTo: "**/*.ts,**/*.tsx"
---

# TypeScript/React Instructions

- Target: TypeScript 5.x with strict mode enabled
- Framework: Next.js 15 (App Router) + React 19
- Styling: Tailwind CSS with `cn()` utility from `@/lib/utils` (clsx + tailwind-merge)
- Animations: framer-motion for UI animations, wavesurfer.js v7 for audio
- State: React hooks + context (Zustand planned but not yet installed)
- API calls: Use `apiFetch<T>()` from `@/lib/api-client` for typed backend requests
- Analytics: Use `getAnalytics()` from `@/lib/analytics` (no-op facade)
- Components: Use design system from `@/design-system` (Container, GlassPanel, Grid, StatCard, GradientText, WaveformBars)
- Pages go in `apps/web/src/app/(app)/` for authenticated routes with sidebar layout
- Auth: next-auth v5 beta (Supabase provider)
- Import style: `@/` alias maps to `apps/web/src/`
- Install deps with `npm install --legacy-peer-deps` (peer dep conflicts)
- Use `"use client"` directive for components with hooks/interactivity
