---
name: tailwind-styling
description: Tailwind CSS styling with cn() utility and design system tokens
---

## Tailwind Styling

### Utility
```typescript
import { cn } from "@/lib/utils"; // clsx + tailwind-merge

<div className={cn(
  "rounded-lg border p-4",
  isActive && "border-purple-500 bg-purple-500/10",
  className
)} />
```

### Design System Components
```typescript
import { Container, GlassPanel, Grid, StatCard, GradientText, WaveformBars } from "@/design-system";

<Container>
  <GlassPanel>
    <GradientText>SampleMind</GradientText>
    <Grid cols={3}>
      <StatCard label="BPM" value="140" />
    </Grid>
  </GlassPanel>
</Container>
```

### Theme
- Dark-first design with purple/blue accent colors
- Glass morphism panels with backdrop blur
- Consistent spacing using Tailwind's scale
- Responsive: mobile-first with `sm:`, `md:`, `lg:` breakpoints

### Rules
- Always use `cn()` for conditional/merged classes
- Import design system components — don't recreate
- Use Tailwind utilities, not custom CSS
- Config: `tailwind.config.js` at project root
