---
name: typescript-frontend
description: Guide for building Next.js 15 frontend features. Use when asked to create or modify web UI components and pages.
---

## TypeScript Frontend Development

When building frontend features for the SampleMind web app:

1. **Check `apps/web/src/`** — 108+ existing files, do NOT scaffold from scratch
2. **Auth pages** go in `apps/web/src/app/(app)/` route group
3. **Public pages** go in `apps/web/src/app/` root
4. **Use design system** — import from `@/design-system` before creating new components

### Setup
```bash
cd apps/web
npm install --legacy-peer-deps
npm run dev
```

### Build & Validate
```bash
cd apps/web
npm run build
npm run lint
```

### Key Imports
```typescript
import { cn } from "@/lib/utils"           // Tailwind class merging
import { apiFetch } from "@/lib/api-client" // Typed API client
import { Container, GlassPanel } from "@/design-system"
```

### Component Patterns
- Use `"use client"` for components with hooks/interactivity
- Use `cn()` for conditional Tailwind classes
- Use framer-motion for animations
- Use wavesurfer.js v7 for audio waveforms
