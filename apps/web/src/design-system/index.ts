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

// Effects
export * from './effects/glass';
export * from './effects/glow';

// Animations
export * from './animations/presets';
export * from './animations/config';

// Components
export { Container } from './components/Container';
