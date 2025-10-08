/**
 * GlowingBadge Component
 *
 * A cyberpunk-themed badge component for status indicators
 * with neon glow effects and smooth animations.
 *
 * @module GlowingBadge
 */

import React from 'react';
import { motion } from 'framer-motion';

/**
 * Badge variant types
 */
export type BadgeVariant = 'primary' | 'success' | 'warning' | 'error' | 'info' | 'cyan' | 'pink';

/**
 * Badge size types
 */
export type BadgeSize = 'sm' | 'md' | 'lg';

/**
 * Props for the GlowingBadge component
 */
export interface GlowingBadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  glow?: boolean;
  pulse?: boolean;
  dot?: boolean;
  className?: string;
  testId?: string;
}

/**
 * Get variant-specific styles with neon colors
 */
const getVariantStyles = (variant: BadgeVariant): string => {
  const styles = {
    primary: 'bg-primary/20 text-primary border-primary/50 shadow-[0_0_15px_rgba(139,92,246,0.4)]',
    success: 'bg-success/20 text-success border-success/50 shadow-[0_0_15px_rgba(16,185,129,0.4)]',
    warning: 'bg-warning/20 text-warning border-warning/50 shadow-[0_0_15px_rgba(245,158,11,0.4)]',
    error: 'bg-error/20 text-error border-error/50 shadow-[0_0_15px_rgba(239,68,68,0.4)]',
    info: 'bg-info/20 text-info border-info/50 shadow-[0_0_15px_rgba(59,130,246,0.4)]',
    cyan: 'bg-accent-cyan/20 text-accent-cyan border-accent-cyan/50 shadow-[0_0_15px_rgba(6,182,212,0.4)]',
    pink: 'bg-accent-pink/20 text-accent-pink border-accent-pink/50 shadow-[0_0_15px_rgba(236,72,153,0.4)]',
  };

  return styles[variant];
};

/**
 * Get size-specific styles
 */
const getSizeStyles = (size: BadgeSize): string => {
  const styles = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  return styles[size];
};

/**
 * GlowingBadge - Atom-level status indicator with neon glow effects.
 *
 * @example
 * ```tsx
 * <GlowingBadge variant="success" pulse>
 *   Active
 * </GlowingBadge>
 * ```
 */
export const GlowingBadge: React.FC<GlowingBadgeProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  glow = true,
  pulse = false,
  dot = false,
  className = '',
  testId,
}) => {
  const baseStyles = `
    inline-flex
    items-center
    gap-1.5
    font-semibold
    rounded-full
    border
    backdrop-blur-sm
    transition-all
    duration-normal
  `.trim().replace(/\s+/g, ' ');

  const combinedClassName = `
    ${baseStyles}
    ${getVariantStyles(variant)}
    ${getSizeStyles(size)}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  return (
    <motion.span
      className={combinedClassName}
      data-testid={testId}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{
        opacity: 1,
        scale: 1,
        ...(pulse && {
          boxShadow: [
            '0 0 15px currentColor',
            '0 0 25px currentColor',
            '0 0 15px currentColor',
          ],
        }),
      }}
      transition={{
        opacity: { duration: 0.2 },
        scale: { duration: 0.2 },
        ...(pulse && {
          boxShadow: {
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          },
        }),
      }}
    >
      {/* Status Dot */}
      {dot && (
        <span
          className="w-2 h-2 rounded-full bg-current"
          aria-hidden="true"
        />
      )}

      {/* Badge Content */}
      {children}
    </motion.span>
  );
};

GlowingBadge.displayName = 'GlowingBadge';

export default GlowingBadge;
