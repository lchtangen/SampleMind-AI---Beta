/**
 * @fileoverview Typography token definitions.
 *
 * Centralises font families, sizes, weights, and line-heights used
 * throughout the SampleMind AI UI. Values align with tailwind.config.js
 * but are available for programmatic use.
 *
 * @module design-system/tokens/typography
 */

// ─── Font Families ───────────────────────────────────────────────────────────

export const fontFamily = {
  /** Primary body / UI font */
  sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
  /** Code / technical readouts */
  mono: ['JetBrains Mono', 'Monaco', 'Cascadia Code', 'Courier New', 'monospace'],
  /** Display / marketing headings */
  display: ['Orbitron', 'Inter', '-apple-system', 'sans-serif'],
} as const;

// ─── Font Size Scale ─────────────────────────────────────────────────────────

export const fontSize = {
  xs:   { size: '0.75rem',  lineHeight: '1rem' },
  sm:   { size: '0.875rem', lineHeight: '1.25rem' },
  base: { size: '1rem',     lineHeight: '1.5rem' },
  lg:   { size: '1.125rem', lineHeight: '1.75rem' },
  xl:   { size: '1.25rem',  lineHeight: '1.75rem' },
  '2xl': { size: '1.5rem',  lineHeight: '2rem' },
  '3xl': { size: '1.875rem', lineHeight: '2.25rem' },
  '4xl': { size: '2.25rem', lineHeight: '2.5rem' },
  '5xl': { size: '3rem',    lineHeight: '1' },
} as const;

// ─── Font Weights ────────────────────────────────────────────────────────────

export const fontWeight = {
  normal:   400,
  medium:   500,
  semibold: 600,
  bold:     700,
  extrabold: 800,
} as const;

// ─── Letter Spacing ──────────────────────────────────────────────────────────

export const letterSpacing = {
  tighter: '-0.05em',
  tight:   '-0.025em',
  normal:  '0',
  wide:    '0.025em',
  wider:   '0.05em',
  widest:  '0.1em',
} as const;

export type FontSize = keyof typeof fontSize;
export type FontWeight = keyof typeof fontWeight;
