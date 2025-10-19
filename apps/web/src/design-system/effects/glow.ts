/**
 * GLOW EFFECT SYSTEM
 * Neon glow effects for cyberpunk aesthetic
 */

/**
 * Box shadow glow effects
 */
export const glowEffects = {
  // Blue glow (primary)
  blue: {
    sm: '0 0 10px hsl(220, 90%, 60%, 0.3)',
    md: '0 0 20px hsl(220, 90%, 60%, 0.5), 0 0 40px hsl(220, 90%, 60%, 0.3)',
    lg: '0 0 30px hsl(220, 90%, 60%, 0.6), 0 0 60px hsl(220, 90%, 60%, 0.4)',
  },

  // Purple glow (special)
  purple: {
    sm: '0 0 10px hsl(270, 85%, 65%, 0.3)',
    md: '0 0 20px hsl(270, 85%, 65%, 0.5), 0 0 40px hsl(270, 85%, 65%, 0.3)',
    lg: '0 0 30px hsl(270, 85%, 65%, 0.6), 0 0 60px hsl(270, 85%, 65%, 0.4)',
  },

  // Cyan glow (success)
  cyan: {
    sm: '0 0 10px hsl(180, 95%, 55%, 0.3)',
    md: '0 0 20px hsl(180, 95%, 55%, 0.5), 0 0 40px hsl(180, 95%, 55%, 0.3)',
    lg: '0 0 30px hsl(180, 95%, 55%, 0.6), 0 0 60px hsl(180, 95%, 55%, 0.4)',
  },

  // Magenta glow (warning)
  magenta: {
    sm: '0 0 10px hsl(320, 90%, 60%, 0.3)',
    md: '0 0 20px hsl(320, 90%, 60%, 0.5), 0 0 40px hsl(320, 90%, 60%, 0.3)',
    lg: '0 0 30px hsl(320, 90%, 60%, 0.6), 0 0 60px hsl(320, 90%, 60%, 0.4)',
  },

  // White glow (neutral)
  white: {
    sm: '0 0 10px rgba(255, 255, 255, 0.3)',
    md: '0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(255, 255, 255, 0.3)',
    lg: '0 0 30px rgba(255, 255, 255, 0.6), 0 0 60px rgba(255, 255, 255, 0.4)',
  },
} as const;

/**
 * Text shadow glow effects
 */
export const textGlow = {
  blue: '0 0 10px hsl(220, 90%, 60%, 0.8), 0 0 20px hsl(220, 90%, 60%, 0.5), 0 0 30px hsl(220, 90%, 60%, 0.3)',
  purple: '0 0 10px hsl(270, 85%, 65%, 0.8), 0 0 20px hsl(270, 85%, 65%, 0.5), 0 0 30px hsl(270, 85%, 65%, 0.3)',
  cyan: '0 0 10px hsl(180, 95%, 55%, 0.8), 0 0 20px hsl(180, 95%, 55%, 0.5), 0 0 30px hsl(180, 95%, 55%, 0.3)',
  magenta: '0 0 10px hsl(320, 90%, 60%, 0.8), 0 0 20px hsl(320, 90%, 60%, 0.5), 0 0 30px hsl(320, 90%, 60%, 0.3)',
  white: '0 0 10px rgba(255, 255, 255, 0.8), 0 0 20px rgba(255, 255, 255, 0.5)',
} as const;

/**
 * Combined glass + glow effects
 */
export const glassGlow = {
  blue: {
    ...glowEffects.blue.md,
    glass: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(220, 90%, 60%, 0.3)',
  },
  purple: {
    ...glowEffects.purple.md,
    glass: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(270, 85%, 65%, 0.3)',
  },
  cyan: {
    ...glowEffects.cyan.md,
    glass: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(180, 95%, 55%, 0.3)',
  },
  magenta: {
    ...glowEffects.magenta.md,
    glass: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(320, 90%, 60%, 0.3)',
  },
} as const;

/**
 * Pulsing glow animation
 */
export const glowPulse = {
  keyframes: {
    '0%, 100%': {
      filter: 'brightness(1)',
      opacity: 1,
    },
    '50%': {
      filter: 'brightness(1.2)',
      opacity: 0.8,
    },
  },
  animation: 'glowPulse 2s ease-in-out infinite',
} as const;

export type GlowColor = keyof typeof glowEffects;
export type GlowSize = 'sm' | 'md' | 'lg';
