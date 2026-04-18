/**
 * @fileoverview Animated gradient text component for headings and labels.
 *
 * Renders text with a CSS gradient fill that optionally animates across the
 * color spectrum. Supports all cyberpunk color presets.
 *
 * @example
 * ```tsx
 * <GradientText preset="cyan-purple" as="h1" animated>
 *   Welcome to SampleMind
 * </GradientText>
 * ```
 *
 * @module design-system/components/GradientText
 */

'use client';

import React from 'react';
import { cn } from '@/lib/utils';

/** Available gradient color presets */
type GradientPreset =
  | 'cyan-purple'
  | 'purple-magenta'
  | 'blue-cyan'
  | 'magenta-blue'
  | 'rainbow';

interface GradientTextProps {
  children: React.ReactNode;
  /** Gradient color preset */
  preset?: GradientPreset;
  /** Whether the gradient animates (shifts position over time) */
  animated?: boolean;
  /** HTML tag to render */
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'p' | 'span';
  className?: string;
}

const GRADIENT_MAP: Record<GradientPreset, string> = {
  'cyan-purple':
    'from-cyber-cyan via-cyber-blue to-cyber-purple',
  'purple-magenta':
    'from-cyber-purple via-cyber-magenta to-neon-pink',
  'blue-cyan':
    'from-cyber-blue via-cyber-cyan to-emerald-400',
  'magenta-blue':
    'from-cyber-magenta via-cyber-purple to-cyber-blue',
  rainbow:
    'from-cyber-cyan via-cyber-purple to-cyber-magenta',
};

export const GradientText: React.FC<GradientTextProps> = ({
  children,
  preset = 'cyan-purple',
  animated = false,
  as: Component = 'span',
  className,
}) => (
  <Component
    className={cn(
      'bg-gradient-to-r bg-clip-text text-transparent',
      GRADIENT_MAP[preset],
      animated && 'bg-[length:200%_auto] animate-spark-flow',
      className,
    )}
  >
    {children}
  </Component>
);

GradientText.displayName = 'GradientText';
