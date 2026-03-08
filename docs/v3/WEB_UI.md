# Web UI Specification — Phase 15

**Status:** Placeholder (not yet started)
**Tech Stack:** Next.js 15, React 19, Tailwind CSS v4, shadcn/ui
**Phase:** 15 — v3.0 Migration
**Last Updated:** 2026-03-07

---

## Overview

The Web UI (`apps/web/`) is a new Phase 15 deliverable — a browser-based interface for
SampleMind AI that complements the CLI and TUI. It targets music producers who prefer a
visual, drag-and-drop workflow.

---

## Planned Directory Structure

```
apps/web/
├── src/
│   ├── app/                  Next.js 15 App Router pages
│   │   ├── page.tsx          Landing / library view
│   │   ├── analyze/          Audio analysis page
│   │   ├── library/          Sample browser
│   │   └── settings/         User settings
│   ├── components/
│   │   ├── audio/
│   │   │   ├── AudioUpload.tsx
│   │   │   ├── WaveformViewer.tsx
│   │   │   └── AnalysisCard.tsx
│   │   ├── library/
│   │   │   ├── SampleBrowser.tsx
│   │   │   ├── TagFilter.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── effects/
│   │   │   ├── EffectsChain.tsx
│   │   │   └── EQVisualizer.tsx
│   │   └── ui/               shadcn/ui components
│   ├── hooks/
│   │   ├── useAudioAnalysis.ts
│   │   ├── useLibrary.ts
│   │   └── usePlayback.ts
│   ├── stores/               Zustand v5 state
│   └── lib/
│       └── api/              TypeScript API client (from OpenAPI spec)
├── package.json
└── tailwind.config.ts
```

---

## API Integration

The web UI communicates with the FastAPI backend (`localhost:8000`).

```typescript
import { samplemindApi } from '@/lib/api'

const result = await samplemindApi.audio.analyze({
  file: audioFile,
  level: 'PROFESSIONAL',
  model: 'claude-3-7-sonnet-20250219'
})
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| First Contentful Paint | <1s |
| Audio upload + analysis start | <200ms UI response |
| Waveform render (30s file) | <500ms |

---

## Dependencies

```json
{
  "next": "^15.0.0",
  "react": "^19.0.0",
  "tailwindcss": "^4.0.0",
  "zustand": "^5.0.0",
  "@shadcn/ui": "latest"
}
```

---

*This is a planning placeholder. Implementation begins after dependency upgrades are complete.*
