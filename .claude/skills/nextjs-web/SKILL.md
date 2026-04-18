---
name: nextjs-web
description: Next.js 15 web app with 108+ files in apps/web/
---

## Next.js Web Application

### Location
`apps/web/` — do NOT scaffold from scratch, 108+ files exist.

### Structure
```
apps/web/src/
├── app/(app)/      # Authenticated pages with sidebar layout
├── app/            # Public pages (login, landing)
├── components/     # AIChatWindow, AdvancedWaveform, SampleCard, BpmTapTempo
├── design-system/  # Container, GlassPanel, Grid, StatCard, GradientText
└── lib/            # api-client.ts, utils.ts, analytics.ts
```

### Layout
- `(app)/layout.tsx` provides sidebar + topbar for authenticated pages
- Public pages go in `apps/web/src/app/` root

### Commands
```bash
cd apps/web
npm install --legacy-peer-deps    # REQUIRED for peer deps
npm run dev                        # Development
npm run build                      # Production build
npm run lint                       # ESLint
```

### Rules
- Auth pages in `(app)/` route group
- Use design system components from `@/design-system`
- API calls via `apiFetch<T>()` from `@/lib/api-client`
- Class merging via `cn()` from `@/lib/utils`
