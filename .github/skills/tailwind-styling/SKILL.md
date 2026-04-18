---
name: tailwind-styling
description: Guide for Tailwind CSS styling patterns used in the SampleMind web app. Use when styling components.
---

## Tailwind CSS Styling

### Class Merging
Always use `cn()` from `@/lib/utils` for conditional classes:
```typescript
import { cn } from "@/lib/utils"

<div className={cn(
  "rounded-xl p-4",
  isActive && "bg-purple-500/20 border-purple-500",
  !isActive && "bg-gray-800/50 border-gray-700"
)} />
```

### Design Tokens (from design-system)
- **Colors:** Purple/violet primary, gray neutrals, glass effects
- **Spacing:** Consistent padding/margin scale
- **Typography:** JetBrains Mono for code, system fonts for UI
- **Effects:** Glass morphism (`backdrop-blur`), glow effects

### Common Patterns
```tsx
// Glass card
<div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6">

// Gradient text
<span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">

// Hover effect
<button className="transition-all duration-200 hover:bg-white/10 hover:scale-105">
```
