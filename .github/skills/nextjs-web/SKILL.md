---
name: nextjs-web
description: Guide for Next.js 15 App Router pages and layouts. Use when creating new pages or modifying the web app structure.
---

## Next.js 15 Web App Development

### Page Structure
- **Auth pages:** `apps/web/src/app/(app)/` — sidebar + topbar layout
- **Public pages:** `apps/web/src/app/` — no sidebar
- **Layout:** `(app)/layout.tsx` — shared authenticated layout

### New Page Template
```typescript
// apps/web/src/app/(app)/new-feature/page.tsx
"use client"

import { Container, GlassPanel } from "@/design-system"
import { apiFetch } from "@/lib/api-client"

export default function NewFeaturePage() {
  return (
    <Container>
      <GlassPanel>
        <h1>New Feature</h1>
      </GlassPanel>
    </Container>
  )
}
```

### Existing Pages
- `/dashboard` — Main dashboard
- `/library` — Sample library browser
- `/upload` — File upload
- `/settings` — User settings
- `/gallery` — Sample gallery
- `/collections` — Sample collections
- `/analysis/[id]` — Individual analysis view

### Design System Components
Container, GlassPanel, Grid, GridItem, GradientText, StatCard, WaveformBars
