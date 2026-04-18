/**
 * @fileoverview Barrel export for the SampleMind AI **Cyberpunk Glassmorphism**
 * design system.
 *
 * Re-exports all design tokens, visual effects, animation presets, and
 * primitive layout components so consumers can import from a single path:
 *
 * ```ts
 * import { spacing, glass, glowPresets, Container } from "@/design-system";
 * ```
 *
 * **Exported categories:**
 * - **Tokens** — `spacing`, `layout` (grid/breakpoint constants)
 * - **Effects** — `glass` (blur + opacity utilities), `glow` (neon shadow utilities)
 * - **Animations** — `presets` (keyframe configs), `config` (duration/easing tokens)
 * - **Components** — `Container` (max-width centred wrapper)
 *
 * @module design-system
 */

// Tokens
export * from './tokens/spacing';
export * from './tokens/layout';
export * from './tokens/colors';
export * from './tokens/typography';

// Effects
export * from './effects/glass';
export { glowEffects, textGlow, glassGlow } from './effects/glow';
export type { GlowColor, GlowSize } from './effects/glow';

// Animations (glowPulse comes from presets, not effects/glow)
export * from './animations/presets';
export * from './animations/config';

// Components
export { Container } from './components/Container';
export { GlassPanel } from './components/GlassPanel';
export { Grid, GridItem } from './components/Grid';
export { GradientText } from './components/GradientText';
export { StatCard } from './components/StatCard';
export { WaveformBars } from './components/WaveformBars';
