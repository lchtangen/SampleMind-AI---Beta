/**
 * GLASS EFFECT SYSTEM
 * Glassmorphism utilities with intensity variants
 */

export const glassEffects = {
  /**
   * Base glass effect
   * Standard frosted glass with 5% opacity
   */
  base: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(10px) saturate(180%)',
    WebkitBackdropFilter: 'blur(10px) saturate(180%)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
  },

  /**
   * Light glass effect
   * More visible with 8% opacity
   */
  light: {
    background: 'rgba(255, 255, 255, 0.08)',
    backdropFilter: 'blur(10px) saturate(180%)',
    WebkitBackdropFilter: 'blur(10px) saturate(180%)',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
  },

  /**
   * Strong glass effect
   * Highly visible with 12% opacity and stronger blur
   */
  strong: {
    background: 'rgba(255, 255, 255, 0.12)',
    backdropFilter: 'blur(12px) saturate(180%)',
    WebkitBackdropFilter: 'blur(12px) saturate(180%)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    boxShadow: '0 12px 48px rgba(0, 0, 0, 0.5)',
  },

  /**
   * Subtle glass effect
   * Barely visible, for subtle layers
   */
  subtle: {
    background: 'rgba(255, 255, 255, 0.03)',
    backdropFilter: 'blur(8px) saturate(150%)',
    WebkitBackdropFilter: 'blur(8px) saturate(150%)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
  },

  /**
   * Hover state glass
   * Enhanced for interactive elements
   */
  hover: {
    background: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px) saturate(180%)',
    WebkitBackdropFilter: 'blur(10px) saturate(180%)',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(66, 153, 225, 0.3)',
  },
} as const;

/**
 * Glass CSS class names for Tailwind
 */
export const glassClasses = {
  base: 'glass',
  light: 'glass-light',
  strong: 'glass-strong',
  subtle: 'backdrop-blur-sm bg-white/[0.03] border border-white/5',
  hover: 'glass-hover',
} as const;

/**
 * Gradient border effect for glass panels
 */
export const gradientBorder = {
  blue: {
    borderImage: 'linear-gradient(135deg, hsl(220, 90%, 60%), hsl(270, 85%, 65%)) 1',
  },
  purple: {
    borderImage: 'linear-gradient(135deg, hsl(270, 85%, 65%), hsl(320, 90%, 60%)) 1',
  },
  cyan: {
    borderImage: 'linear-gradient(135deg, hsl(180, 95%, 55%), hsl(220, 90%, 60%)) 1',
  },
  rainbow: {
    borderImage: 'linear-gradient(135deg, hsl(220, 90%, 60%), hsl(270, 85%, 65%), hsl(320, 90%, 60%)) 1',
  },
} as const;

/**
 * Performance-optimized glass effect
 * For mobile devices and lower-end hardware
 */
export const glassOptimized = {
  base: {
    background: 'rgba(255, 255, 255, 0.05)',
    backdropFilter: 'blur(8px)',
    WebkitBackdropFilter: 'blur(8px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.3)',
  },
} as const;

export type GlassEffect = keyof typeof glassEffects;
export type GlassClass = keyof typeof glassClasses;
export type GradientBorder = keyof typeof gradientBorder;
