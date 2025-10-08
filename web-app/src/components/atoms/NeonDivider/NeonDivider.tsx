/**
 * NeonDivider Component
 *
 * A cyberpunk-themed divider with animated neon gradient line.
 * Uses Framer Motion for smooth glow transitions.
 *
 * @module NeonDivider
 */

import React from 'react';
import { motion } from 'framer-motion';

/**
 * Divider orientation types
 */
export type DividerOrientation = 'horizontal' | 'vertical';

/**
 * Gradient color preset types
 */
export type GradientPreset = 'purple' | 'cyber' | 'neon' | 'pink' | 'cyan';

/**
 * Props for the NeonDivider component
 */
export interface NeonDividerProps {
  /**
   * Orientation of the divider.
   *
   * @optional
   * @default 'horizontal'
   */
  orientation?: DividerOrientation;

  /**
   * Gradient color preset.
   *
   * @optional
   * @default 'cyber'
   */
  gradient?: GradientPreset;

  /**
   * Enable animated gradient flow.
   *
   * @optional
   * @default true
   */
  animated?: boolean;

  /**
   * Thickness of the divider line (in pixels).
   *
   * @optional
   * @default 2
   */
  thickness?: number;

  /**
   * Glow intensity.
   *
   * @optional
   * @default 'medium'
   */
  glowIntensity?: 'low' | 'medium' | 'high';

  /**
   * Additional CSS classes.
   *
   * @optional
   */
  className?: string;

  /**
   * Test ID.
   *
   * @optional
   */
  testId?: string;
}

/**
 * Gradient configurations
 */
const gradients = {
  purple: 'linear-gradient(90deg, transparent 0%, #8B5CF6 50%, transparent 100%)',
  cyber: 'linear-gradient(90deg, transparent 0%, #8B5CF6 30%, #06B6D4 70%, transparent 100%)',
  neon: 'linear-gradient(90deg, transparent 0%, #EC4899 25%, #8B5CF6 50%, #06B6D4 75%, transparent 100%)',
  pink: 'linear-gradient(90deg, transparent 0%, #EC4899 50%, transparent 100%)',
  cyan: 'linear-gradient(90deg, transparent 0%, #06B6D4 50%, transparent 100%)',
};

/**
 * Glow shadow configurations
 */
const glowShadows = {
  low: '0 0 5px currentColor',
  medium: '0 0 10px currentColor',
  high: '0 0 20px currentColor',
};

/**
 * NeonDivider - Atom-level divider with animated neon gradient.
 *
 * @example
 * ```tsx
 * <NeonDivider gradient="cyber" animated />
 * ```
 */
export const NeonDivider: React.FC<NeonDividerProps> = ({
  orientation = 'horizontal',
  gradient = 'cyber',
  animated = true,
  thickness = 2,
  glowIntensity = 'medium',
  className = '',
  testId,
}) => {
  const isHorizontal = orientation === 'horizontal';

  const containerStyles = isHorizontal
    ? `w-full h-[${thickness}px] ${className}`
    : `h-full w-[${thickness}px] ${className}`;

  return (
    <div
      className={`relative overflow-hidden ${containerStyles}`.trim()}
      role="separator"
      aria-orientation={orientation}
      data-testid={testId}
    >
      <motion.div
        className="absolute inset-0"
        style={{
          background: gradients[gradient],
          boxShadow: glowShadows[glowIntensity],
        }}
        initial={{ opacity: 0 }}
        animate={{
          opacity: 1,
          ...(animated && {
            backgroundPosition: isHorizontal
              ? ['0% 50%', '100% 50%', '0% 50%']
              : ['50% 0%', '50% 100%', '50% 0%'],
          }),
        }}
        transition={{
          opacity: { duration: 0.5 },
          ...(animated && {
            backgroundPosition: {
              duration: 3,
              repeat: Infinity,
              ease: 'linear',
            },
          }),
        }}
      />

      {/* Glow overlay */}
      <motion.div
        className="absolute inset-0"
        style={{
          background: gradients[gradient],
          filter: 'blur(8px)',
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: [0.3, 0.6, 0.3] }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        aria-hidden="true"
      />
    </div>
  );
};

NeonDivider.displayName = 'NeonDivider';

export default NeonDivider;
