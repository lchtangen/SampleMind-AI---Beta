/**
 * @fileoverview Cyberpunk color token definitions.
 *
 * Centralises all color constants used across the SampleMind AI design system.
 * Values match the Tailwind `theme.extend.colors` in `tailwind.config.js`,
 * making them available for programmatic use in JS/TS (e.g. canvas drawing,
 * Three.js materials, or dynamic style generation).
 *
 * @module design-system/tokens/colors
 */

// ─── Primary Cyberpunk Palette ───────────────────────────────────────────────

export const cyber = {
  blue:    { DEFAULT: 'hsl(220, 90%, 60%)', light: 'hsl(220, 90%, 70%)', dark: 'hsl(220, 90%, 50%)' },
  purple:  { DEFAULT: 'hsl(270, 85%, 65%)', light: 'hsl(270, 85%, 75%)', dark: 'hsl(270, 85%, 55%)' },
  cyan:    { DEFAULT: 'hsl(180, 95%, 55%)', light: 'hsl(180, 95%, 65%)', dark: 'hsl(180, 95%, 45%)' },
  magenta: { DEFAULT: 'hsl(320, 90%, 60%)', light: 'hsl(320, 90%, 70%)', dark: 'hsl(320, 90%, 50%)' },
} as const;

// ─── Neon Accent Palette ─────────────────────────────────────────────────────

export const neon = {
  pink:   '#ff2a6d',
  blue:   '#05d9e8',
  purple: '#d300c5',
  cyan:   '#00f1ff',
} as const;

// ─── Neutral Dark Theme ──────────────────────────────────────────────────────

export const dark = {
  100: 'hsl(220, 15%, 18%)',
  200: 'hsl(220, 15%, 15%)',
  300: 'hsl(220, 15%, 12%)',
  400: 'hsl(220, 15%, 10%)',
  500: 'hsl(220, 15%, 8%)',   // Main background
  600: 'hsl(220, 15%, 6%)',
  700: 'hsl(220, 15%, 4%)',
  800: 'hsl(220, 15%, 2%)',
} as const;

// ─── Glass Surface Colors ────────────────────────────────────────────────────

export const glass = {
  light:  'rgba(255, 255, 255, 0.05)',
  DEFAULT: 'rgba(255, 255, 255, 0.08)',
  strong: 'rgba(255, 255, 255, 0.12)',
  border: 'rgba(255, 255, 255, 0.1)',
} as const;

// ─── Text Colors ─────────────────────────────────────────────────────────────

export const text = {
  primary:   'hsl(0, 0%, 98%)',
  secondary: 'hsl(220, 10%, 65%)',
  tertiary:  'hsl(220, 10%, 45%)',
  muted:     'hsl(220, 10%, 35%)',
} as const;

// ─── Semantic Colors ─────────────────────────────────────────────────────────

export const semantic = {
  success: 'hsl(145, 85%, 55%)',
  warning: 'hsl(45, 95%, 60%)',
  error:   'hsl(0, 90%, 60%)',
  info:    'hsl(210, 90%, 60%)',
} as const;

// ─── Gradient Presets (CSS strings) ──────────────────────────────────────────

export const gradients = {
  spark1:  'linear-gradient(135deg, hsl(220,90%,60%) 0%, hsl(250,85%,65%) 50%, hsl(320,90%,60%) 100%)',
  spark2:  'linear-gradient(90deg, hsl(180,95%,55%) 0%, hsl(220,90%,60%) 50%, hsl(270,85%,65%) 100%)',
  cyanPurple: 'linear-gradient(135deg, hsl(180,95%,55%), hsl(270,85%,65%))',
  purpleMagenta: 'linear-gradient(135deg, hsl(270,85%,65%), hsl(320,90%,60%))',
} as const;

export type CyberColor = keyof typeof cyber;
export type NeonColor = keyof typeof neon;
export type SemanticColor = keyof typeof semantic;
