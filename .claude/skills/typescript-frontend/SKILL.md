---
name: typescript-frontend
description: Next.js 15 App Router with React 19 and Tailwind CSS
---

## TypeScript Frontend Development

### Stack
- Next.js 15 (App Router) + React 19 + Tailwind CSS
- framer-motion for animations, wavesurfer.js v7 for audio
- next-auth v5 beta (Supabase provider)

### Project Structure
```
apps/web/src/
├── app/(app)/      # Authenticated routes with sidebar layout
├── components/     # AIChatWindow, AdvancedWaveform, BpmTapTempo
├── design-system/  # Container, GlassPanel, Grid, StatCard
└── lib/            # api-client.ts, utils.ts, analytics.ts
```

### Key Imports
```typescript
import { cn } from "@/lib/utils";           // Tailwind class merging
import { apiFetch } from "@/lib/api-client"; // Typed backend requests
import { Container, GlassPanel } from "@/design-system";
```

### Rules
- `"use client"` directive for components with hooks/interactivity
- Strict TypeScript — no `any` unless absolutely necessary
- Install: `npm install --legacy-peer-deps` (required for peer dep conflicts)
- `@/` alias maps to `apps/web/src/`
- Do NOT scaffold from scratch — 108+ files already exist
