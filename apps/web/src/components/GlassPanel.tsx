/**
 * @fileoverview Glassmorphism panel component from the SampleMind design system.
 *
 * Renders a `<div>` with a frosted-glass backdrop, rounded corners, and a
 * subtle border. Supports three visual intensity variants and four padding
 * sizes, applied via the project's Tailwind CSS utility classes.
 *
 * @module components/GlassPanel
 */

import React from 'react'
import clsx from 'clsx'

/**
 * Props accepted by {@link GlassPanel}.
 *
 * Extends all standard `<div>` HTML attributes so callers can pass
 * `onClick`, `style`, `aria-*`, etc.
 *
 * @property variant  - Visual intensity: `"default"` (standard blur),
 *                      `"light"` (reduced opacity), or `"strong"` (heavier frost).
 * @property padding  - Inner spacing: `"none"`, `"sm"` (12 px), `"md"` (20 px),
 *                      or `"lg"` (32 px).
 */
type Props = React.HTMLAttributes<HTMLDivElement> & {
  variant?: 'default' | 'light' | 'strong'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const variantMap: Record<NonNullable<Props['variant']>, string> = {
  default: 'glass',
  light: 'glass-light',
  strong: 'glass-strong',
}

const padMap: Record<NonNullable<Props['padding']>, string> = {
  none: 'p-0',
  sm: 'p-3',
  md: 'p-5',
  lg: 'p-8',
}

/**
 * A general-purpose glassmorphism container panel.
 *
 * @example
 * ```tsx
 * <GlassPanel variant="strong" padding="lg">
 *   <h2>Section Title</h2>
 * </GlassPanel>
 * ```
 */
export default function GlassPanel({ variant = 'default', padding = 'md', className, children, ...rest }: Props) {
  return (
    <div className={clsx('rounded-glass border border-glass-border', variantMap[variant], padMap[padding], className)} {...rest}>
      {children}
    </div>
  )
}
