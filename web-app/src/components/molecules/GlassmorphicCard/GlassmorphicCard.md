# GlassmorphicCard Component

A production-ready glassmorphic card component with animated neon glow effects for the SampleMind AI application.

## Features

✨ **Glassmorphism Effects**
- Backdrop blur with semi-transparent background
- Subtle border with controlled opacity
- Multi-layer shadow system for depth

🌟 **Neon Glow Animation**
- Multi-layer box-shadow combining primary (purple) and accent (cyan) colors
- Smooth 0.5s transition duration
- Intensified glow on hover state

🎯 **Interactive States**
- Hover: Intensified glow + 5% scale transform
- Focus: Custom focus ring with purple glow
- Active: Subtle scale reduction for tactile feedback
- Non-interactive: Display-only mode

🌓 **Light/Dark Mode Support**
- Automatic color adaptation
- `bg-white/5` for dark backgrounds
- `bg-black/5` for light backgrounds

♿ **Full Accessibility**
- ARIA labels and semantic HTML
- Keyboard navigation (Tab, Enter, Space)
- Proper roles and attributes
- Screen reader optimized

📱 **Responsive Design**
- Mobile: `p-6` (24px padding)
- Desktop: `md:p-8` (32px padding)
- Fluid typography scaling
- Tested across viewports

🎨 **Design System Integration**
- Uses design tokens from [`tokens.ts`](../../design-system/tokens.ts)
- Follows 8pt grid spacing system
- Adheres to typography scale
- Integrates with Tailwind config

## Installation

The component is part of the SampleMind AI design system and doesn't require separate installation.

```bash
# Dependencies are already installed in the project
cd web-app
npm install
```

## Import

```typescript
// Named import (recommended for tree-shaking)
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

// With types
import { GlassmorphicCard, type GlassmorphicCardProps } from '@/components/molecules/GlassmorphicCard';
```

## Basic Usage

### Simple Display Card

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function MyComponent() {
  return (
    <GlassmorphicCard
      title="Audio Waveform"
      description="View detailed spectral analysis of your audio files"
    />
  );
}
```

### Interactive Card

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function MyComponent() {
  const handleCardClick = () => {
    console.log('Card clicked!');
    // Navigate or perform action
  };

  return (
    <GlassmorphicCard
      title="Open Audio Analysis"
      description="Click to view detailed waveform breakdown"
      onClick={handleCardClick}
      ariaLabel="Open audio analysis panel"
    />
  );
}
```

### Card with Icon

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';
import { MusicIcon } from '@/components/icons';

function MyComponent() {
  return (
    <GlassmorphicCard
      title="Music Library"
      description="Browse your audio collection"
      icon={<MusicIcon className="w-8 h-8" />}
      onClick={() => navigate('/library')}
    />
  );
}
```

## Props API

### GlassmorphicCardProps

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | `string` | ✅ Yes | - | Main heading text displayed in the card |
| `description` | `string` | ✅ Yes | - | Description or content text below the title |
| `icon` | `ReactNode` | ❌ No | `undefined` | Optional icon component or element |
| `onClick` | `() => void` | ❌ No | `undefined` | Click handler making the card interactive |
| `className` | `string` | ❌ No | `''` | Additional CSS classes for customization |
| `ariaLabel` | `string` | ❌ No | `title` | ARIA label for accessibility |
| `testId` | `string` | ❌ No | `undefined` | Test ID for component testing |

### Type Definitions

```typescript
interface GlassmorphicCardProps {
  title: string;
  description: string;
  icon?: ReactNode;
  onClick?: () => void;
  className?: string;
  ariaLabel?: string;
  testId?: string;
}
```

## Advanced Examples

### Grid Layout

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function Dashboard() {
  const features = [
    { id: 1, title: 'Audio Analysis', description: 'Analyze audio files', icon: <AudioIcon /> },
    { id: 2, title: 'Waveform View', description: 'Visualize waveforms', icon: <WaveIcon /> },
    { id: 3, title: 'Export', description: 'Export processed audio', icon: <ExportIcon /> },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {features.map((feature) => (
        <GlassmorphicCard
          key={feature.id}
          title={feature.title}
          description={feature.description}
          icon={feature.icon}
          onClick={() => handleFeatureClick(feature.id)}
        />
      ))}
    </div>
  );
}
```

### Custom Styling

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function CustomCard() {
  return (
    <GlassmorphicCard
      title="Custom Styled Card"
      description="With additional classes"
      className="max-w-md mx-auto mt-8"
      onClick={() => console.log('clicked')}
    />
  );
}
```

### Conditional Interactivity

```tsx
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function ConditionalCard({ isClickable }: { isClickable: boolean }) {
  return (
    <GlassmorphicCard
      title="Conditional Card"
      description={isClickable ? 'Click me!' : 'Display only'}
      onClick={isClickable ? () => handleClick() : undefined}
    />
  );
}
```

### With State Management

```tsx
import { useState } from 'react';
import { GlassmorphicCard } from '@/components/molecules/GlassmorphicCard';

function StatefulCard() {
  const [isSelected, setIsSelected] = useState(false);

  return (
    <GlassmorphicCard
      title="Selectable Card"
      description={isSelected ? 'Selected ✓' : 'Click to select'}
      onClick={() => setIsSelected(!isSelected)}
      className={isSelected ? 'ring-2 ring-primary' : ''}
      ariaLabel={`Selectable card, currently ${isSelected ? 'selected' : 'not selected'}`}
    />
  );
}
```

## Accessibility

### Keyboard Navigation

The component fully supports keyboard navigation:

- **Tab**: Focus the card (when interactive)
- **Enter**: Activate the card
- **Space**: Activate the card
- **Shift+Tab**: Focus previous element

### Screen Reader Support

```tsx
<GlassmorphicCard
  title="Audio File"
  description="file.mp3"
  ariaLabel="Open audio file file.mp3 for editing"
  onClick={handleOpen}
/>
```

### Non-Interactive Cards

Non-interactive cards use semantic `<article>` elements:

```tsx
<GlassmorphicCard
  title="Information"
  description="Display-only content"
  // No onClick = <article> element
/>
```

### Testing Accessibility

```bash
# Run accessibility tests
npm run test

# The component includes automated axe tests
# See GlassmorphicCard.test.tsx for details
```

## Styling & Customization

### Design Tokens

The component uses these design tokens:

```typescript
// From tokens.ts
colors.primary.purple      // #8B5CF6 - Primary glow
colors.accent.cyan         // #06B6D4 - Accent glow
colors.text.primary        // #FFFFFF - Title text
colors.text.secondary      // #94A3B8 - Description text
spacing[6]                 // 24px - Default padding
spacing[8]                 // 32px - Desktop padding
animation.duration.slow    // 500ms - Transition duration
```

### Multi-Layer Glow Effect

```css
/* Default glow */
box-shadow:
  0 0 20px rgba(139, 92, 246, 0.5),    /* Purple layer 1 */
  0 0 40px rgba(139, 92, 246, 0.3),    /* Purple layer 2 */
  0 0 60px rgba(6, 182, 212, 0.2),     /* Cyan accent */
  0 8px 32px rgba(0, 0, 0, 0.37);      /* Base shadow */

/* Hover glow (intensified) */
box-shadow:
  0 0 30px rgba(139, 92, 246, 0.75),   /* +50% opacity */
  0 0 60px rgba(139, 92, 246, 0.45),   /* +50% opacity */
  0 0 90px rgba(6, 182, 212, 0.3),     /* +50% opacity */
  0 8px 32px rgba(0, 0, 0, 0.37);      /* Unchanged */
```

### Custom Tailwind Classes

```tsx
<GlassmorphicCard
  title="Custom"
  description="Card"
  className="
    hover:border-cyan-500/50
    active:scale-[0.98]
    focus:ring-cyan-500
  "
/>
```

## Testing

### Unit Tests

```bash
# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

The component includes comprehensive tests for:
- Rendering with various props
- Accessibility compliance
- User interactions (mouse & keyboard)
- Edge cases

### Visual Regression Tests

```bash
# Run visual tests
npm run test:visual

# Update snapshots
npm run test:visual -- --update-snapshots

# View report
npm run test:visual:report
```

Visual tests cover:
- Glassmorphism effects
- Hover states
- Focus states
- Responsive viewports (mobile/tablet/desktop)
- Light/dark mode

## Best Practices

### ✅ DO

```tsx
// Use meaningful titles and descriptions
<GlassmorphicCard
  title="Audio Analysis Complete"
  description="Your file has been processed successfully"
/>

// Provide clear ARIA labels for interactive cards
<GlassmorphicCard
  title="Export"
  description="Download your file"
  onClick={handleExport}
  ariaLabel="Export processed audio file to downloads folder"
/>

// Use icons consistently
<GlassmorphicCard
  icon={<CheckIcon />}
  title="Success"
  description="Operation completed"
/>
```

### ❌ DON'T

```tsx
// Avoid vague descriptions
<GlassmorphicCard
  title="Click Here"
  description="Do something"
/>

// Don't use without onClick for actions
<GlassmorphicCard
  title="Delete File"  // Misleading - looks interactive
  description="Remove this item"
  // Missing onClick!
/>

// Don't override core glassmorphism styles
<GlassmorphicCard
  className="bg-black border-solid"  // Breaks glass effect
  title="Bad"
  description="Styling"
/>
```

## Performance

- **Tree-shakeable**: Uses named exports
- **Zero runtime overhead**: CSS-based animations
- **Optimized rendering**: React.memo not needed (stateless)
- **Small bundle**: ~2KB gzipped

## Browser Support

✅ **Chromium-Based Browsers**
- Chrome/Edge 91+
- **Brave 1.26+** (Chromium 91+)
- Opera 77+
- Vivaldi 4.0+
- Arc Browser
- Any Chromium-based browser

✅ **Other Browsers**
- Firefox 90+
- Safari 14.1+
- iOS Safari 14.5+
- Samsung Internet 14+

**Note on `backdrop-filter`**: This CSS property is widely supported across all modern browsers. Older browsers will gracefully degrade, showing the component without the blur effect but maintaining full functionality.

### Brave Browser Specifics

Brave browser has **full support** for all component features:
- ✅ Glassmorphism effects (`backdrop-filter`)
- ✅ Multi-layer box shadows
- ✅ CSS transitions and transforms
- ✅ All interactive states
- ✅ Responsive design

Since Brave uses Chromium's rendering engine, it provides identical support to Chrome/Edge.

## Related Components

- **Button**: For primary actions
- **Card**: For standard content containers
- **Modal**: For overlay content

## Changelog

### v1.0.0 (Current)
- ✨ Initial release
- ✨ Glassmorphism effects
- ✨ Neon glow animations
- ✨ Full accessibility support
- ✨ Comprehensive test coverage
- ✨ Confirmed Brave browser support

## Support

For issues or questions:
- 📖 [Design System Guide](../../../docs/AI_DESIGN_SYSTEM_INTEGRATION_GUIDE.md)
- 🎨 [Visual Design System](../../../docs/VISUAL_DESIGN_SYSTEM.md)
- 🐛 [Report an Issue](https://github.com/your-repo/issues)

---

**Component Status**: ✅ Production Ready
**Design System**: v1.0.0
**Browser Support**: All modern browsers including Brave
**Last Updated**: January 2025
