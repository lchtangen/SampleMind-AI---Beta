# 🎨 Design System Quick Reference - SampleMind AI 2025

**Purpose:** Fast lookup for AI assistants and developers
**Updated:** October 6, 2025
**Status:** ✅ Production Ready

---

## 🚀 Quick Start

### Import Design Tokens

```typescript
import { designTokens } from "@/design-system/tokens";
```

### Use Tailwind Utilities (Recommended)

```tsx
<div className="glass-card rounded-xl p-6 shadow-glow-purple">
  <button className="cyberpunk-button hover-glow-cyan">Click Me</button>
</div>
```

---

## 🎨 Color Palette

### Primary Colors

```typescript
primary: "#8B5CF6"; // Electric Purple
purpleDark: "#7C3AED"; // Darker Purple
purpleLight: "#A78BFA"; // Lighter Purple
```

### Accent Colors

```typescript
cyan: "#06B6D4"; // Electric Cyan
pink: "#EC4899"; // Neon Pink/Magenta
blue: "#3B82F6"; // Electric Blue
green: "#10B981"; // Neon Green
```

### Background Colors

```typescript
bg-primary: '#0A0A0F'    // Deep Space Black
bg-secondary: '#131318'  // Dark Charcoal
bg-tertiary: '#1A1A24'   // Elevated Surface
```

### Tailwind Classes

```tsx
// Backgrounds
className = "bg-bg-primary";
className = "bg-bg-secondary";
className = "bg-bg-tertiary";

// Text
className = "text-text-primary"; // White
className = "text-text-secondary"; // Gray
className = "text-text-muted"; // Darker Gray

// Gradients
className = "bg-gradient-purple"; // Purple gradient
className = "bg-gradient-cyan"; // Cyan gradient
className = "text-gradient"; // Gradient text
```

---

## ✨ Glassmorphism

### Glass Card Variants

```tsx
// Standard glass card
<div className="glass-card p-6">
  Content
</div>

// Heavy blur
<div className="glass-card-heavy p-8">
  More blur
</div>

// Subtle glass
<div className="glass-card-subtle p-4">
  Light effect
</div>
```

### Manual Glassmorphism

```tsx
<div className="bg-white/5 backdrop-blur-xl border border-white/10">
  Custom glass
</div>
```

---

## 🌟 Neon Glow Effects

### Shadow Glows

```tsx
// Purple glow (primary)
className = "shadow-glow-purple";

// Cyan glow
className = "shadow-glow-cyan";

// Pink glow
className = "shadow-glow-pink";

// Intense variants (stronger glow)
className = "shadow-glow-purple-intense";
className = "shadow-glow-cyan-intense";
className = "shadow-glow-pink-intense";
```

### Neon Glows (Alternative)

```tsx
className = "neon-glow-purple";
className = "neon-glow-cyan";
className = "neon-glow-pink";
```

### Hover Glows

```tsx
className = "hover-glow-purple";
className = "hover-glow-cyan";
className = "hover-glow-pink";
```

---

## 📝 Typography

### Font Families

```tsx
// Headings (Orbitron - futuristic)
className = "font-heading";

// Display text (Rajdhani - tech)
className = "font-display";

// Body text (Inter - clean)
className = "font-body";

// Code (JetBrains Mono)
className = "font-code";
```

### Text Sizes

```tsx
// Headings
className = "text-5xl font-heading"; // Hero
className = "text-3xl font-heading"; // Section
className = "text-2xl font-heading"; // Subsection
className = "text-xl font-semibold"; // Card title

// Body
className = "text-base"; // Standard
className = "text-sm"; // Small
className = "text-xs"; // Extra small
```

### Text Effects

```tsx
// Gradient text
className = "text-gradient";

// Glowing text
className = "text-glow-purple";
className = "text-glow-cyan";
className = "text-glow-pink";

// Holographic text
className = "holographic-text";
```

---

## 🎭 Component Presets

### Buttons

```tsx
// Cyberpunk button
<button className="cyberpunk-button hover-glow-purple">
  Action
</button>

// With gradient
<button className="bg-gradient-purple rounded-lg px-6 py-3 shadow-glow-purple hover:shadow-glow-cyan transition-normal">
  Gradient Button
</button>
```

### Inputs

```tsx
<input className="cyberpunk-input" />

// Custom
<input className="
  bg-bg-tertiary border border-primary/30
  rounded-lg px-4 py-3
  focus:border-primary focus:ring-2 focus:ring-primary/50
  transition-normal
" />
```

### Cards

```tsx
<div className="cyberpunk-card">
  Card content
</div>

// Or use glass-card
<div className="glass-card rounded-xl p-6 shadow-glow-purple">
  Glassmorphic card
</div>
```

---

## 🎬 Animations

### Animation Classes

```tsx
// Glow pulse
className = "animate-glow";

// Scanline effect
className = "animate-scanline";

// Holographic shift
className = "animate-holographic";

// Glitch effect
className = "animate-glitch";

// Float up and down
className = "animate-float";

// Spin
className = "animate-spin-slow"; // Slow spin
```

### Transition Utilities

```tsx
// Standard transition (300ms)
className = "transition-normal";

// Fast transition (150ms)
className = "transition-fast";

// Slow transition (500ms)
className = "transition-slow";

// Easing
className = "ease-out";
className = "ease-in-out";
```

### Hover Effects

```tsx
// Scale up
className = "hover:scale-105 transition-normal";

// Lift up
className = "hover-lift";

// Glow
className = "hover-glow-purple";

// Combined
className = "hover:scale-105 hover-glow-cyan transition-normal";
```

---

## 🌈 Background Patterns

### Grid Patterns

```tsx
// Cyberpunk grid
className = "bg-cyberpunk-grid";

// Scanline
className = "bg-scanline";

// Circuit pattern
className = "bg-circuit";

// Hexagon pattern
className = "hex-pattern";
```

### Usage

```tsx
<div className="min-h-screen bg-bg-primary bg-cyberpunk-grid">
  <div className="relative z-10">Content above pattern</div>
</div>
```

---

## 📏 Spacing (8pt Grid)

### Padding/Margin Scale

```tsx
p - 1; // 4px
p - 2; // 8px
p - 3; // 12px
p - 4; // 16px  ⭐ Most common
p - 6; // 24px  ⭐ Cards
p - 8; // 32px  ⭐ Sections
p - 12; // 48px
p - 16; // 64px
p - 24; // 96px
p - 32; // 128px
```

### Common Patterns

```tsx
// Card
className = "p-6 md:p-8";

// Section
className = "py-16 md:py-24";

// Button
className = "px-6 py-3";

// Gap in grid
className = "gap-4 md:gap-6 lg:gap-8";
```

---

## 📐 Responsive Design

### Breakpoints

```tsx
// Mobile-first approach
className = "grid-cols-1"; // 320px+ (mobile)
className = "md:grid-cols-2"; // 768px+ (tablet)
className = "lg:grid-cols-3"; // 1024px+ (desktop)
className = "xl:grid-cols-4"; // 1440px+ (wide)
className = "2xl:grid-cols-5"; // 1920px+ (ultra)
```

### Responsive Utilities

```tsx
// Hide on mobile
className = "hidden md:block";

// Show only on mobile
className = "md:hidden";

// Responsive padding
className = "p-4 md:p-6 lg:p-8";

// Responsive text
className = "text-2xl md:text-4xl lg:text-6xl";
```

---

## ♿ Accessibility

### Focus States

```tsx
className="
  focus:ring-2 focus:ring-primary
  focus:ring-offset-2 focus:ring-offset-bg-primary
  focus:outline-none
"
```

### ARIA Labels

```tsx
<button aria-label="Play audio track">
  <PlayIcon />
</button>

<div role="button" tabIndex={0} aria-pressed={isActive}>
  Interactive div
</div>
```

### Keyboard Navigation

```tsx
<div
  role="button"
  tabIndex={0}
  onKeyPress={(e) => e.key === "Enter" && handleClick()}
  onClick={handleClick}
>
  Keyboard accessible
</div>
```

---

## 🎨 Component Templates

### Glassmorphic Card

```tsx
<div
  className="
  glass-card rounded-xl p-6
  shadow-glow-purple
  hover:shadow-glow-cyan
  transition-normal
  hover:scale-105
"
>
  <h3 className="text-xl font-semibold text-text-primary mb-4">Card Title</h3>
  <p className="text-text-secondary">Card content</p>
</div>
```

### Cyberpunk Button

```tsx
<button
  className="
  bg-gradient-purple
  rounded-lg px-6 py-3
  font-semibold text-text-primary
  shadow-glow-purple
  hover:shadow-glow-cyan hover:scale-105
  active:scale-95
  transition-normal ease-out
"
>
  Click Me
</button>
```

### Neon Input

```tsx
<div className="space-y-2">
  <label className="text-sm font-medium text-text-secondary">Label</label>
  <input
    className="
      w-full bg-bg-tertiary
      border border-primary/30
      rounded-lg px-4 py-3
      text-text-primary
      focus:border-primary focus:ring-2 focus:ring-primary/50
      transition-normal
    "
    placeholder="Enter value..."
  />
</div>
```

### Hero Section

```tsx
<section
  className="
  min-h-screen
  bg-bg-primary bg-cyberpunk-grid
  flex items-center justify-center
  relative overflow-hidden
"
>
  {/* Background effects */}
  <ScanlineOverlay enabled={true} />

  {/* Content */}
  <div className="relative z-10 text-center space-y-8">
    <HolographicText as="h1" className="text-8xl">
      SampleMind AI
    </HolographicText>

    <p className="text-2xl text-text-secondary max-w-2xl">
      AI-Powered Music Production Platform
    </p>

    <button className="cyberpunk-button hover-glow-purple">Get Started</button>
  </div>
</section>
```

---

## 🎯 Framer Motion Patterns

### Basic Animation

```tsx
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  Animated content
</motion.div>;
```

### Stagger Children

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

<motion.div variants={container} initial="hidden" animate="show">
  {items.map((item, i) => (
    <motion.div key={i} variants={item}>
      {item}
    </motion.div>
  ))}
</motion.div>;
```

### Gesture Animations

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  whileFocus={{ outline: "2px solid #8B5CF6" }}
>
  Interactive Button
</motion.button>
```

### Scroll Animations

```tsx
import { useScroll, useTransform } from "framer-motion";

const { scrollYProgress } = useScroll();
const y = useTransform(scrollYProgress, [0, 1], [0, -200]);
const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [1, 0.5, 0]);

<motion.div style={{ y, opacity }}>Parallax content</motion.div>;
```

---

## 🚫 Common Mistakes (Avoid)

### ❌ DON'T:

```tsx
// Hardcoded colors
<div style={{ backgroundColor: '#8B5CF6' }}>

// Inline styles for spacing
<div style={{ padding: '16px', margin: '8px' }}>

// Missing aria labels
<button><PlayIcon /></button>

// Non-semantic HTML
<div onClick={handleClick}>Click me</div>

// Mixing design systems
<div className="text-blue-500">  // Not our blue!
```

### ✅ DO:

```tsx
// Use Tailwind utilities
<div className="bg-primary p-4 m-2">

// Add aria labels
<button aria-label="Play audio track">
  <PlayIcon />
</button>

// Use semantic HTML
<button onClick={handleClick}>Click me</button>

// Use design tokens
<div className="text-accent-cyan">
```

---

## 🔍 Debugging Tips

### Check Applied Styles

```tsx
// Add borders to see layout
className = "border border-red-500";

// View glassmorphism
// Ensure parent has bg-bg-primary or solid background
```

### Animation Issues

```tsx
// Disable animations for testing
<motion.div animate={false}>

// Reduce motion for accessibility
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

### Performance

```tsx
// Use will-change for animated properties
className="will-change-transform"

// Avoid animating width/height (use scale instead)
<motion.div style={{ scale: 1.1 }} />  // ✅
<motion.div style={{ width: '110%' }} />  // ❌
```

---

## 📚 Quick Links

- **Design Tokens:** `/web-app/src/design-system/tokens.ts`
- **Tailwind Config:** `/web-app/tailwind.config.ts`
- **Global Styles:** `/web-app/src/index.css`
- **Components:** `/web-app/src/components/`

---

## 🎯 Usage Checklist

- [ ] Import design tokens or use Tailwind classes
- [ ] Use semantic HTML (`<button>` not `<div>`)
- [ ] Add ARIA labels to interactive elements
- [ ] Include focus states for keyboard navigation
- [ ] Use 8pt spacing grid (p-4, p-6, p-8)
- [ ] Add responsive breakpoints (md:, lg:, xl:)
- [ ] Test with `prefers-reduced-motion`
- [ ] Use design system colors (no hardcoded hex)
- [ ] Add transition-normal for smooth animations
- [ ] Include alt text for images

---

**Status:** ✅ Production Ready
**Last Updated:** October 6, 2025
**Version:** 1.0.0 Phoenix Beta
