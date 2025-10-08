import type { Config } from 'tailwindcss';
import plugin from 'tailwindcss/plugin';
import { designTokens } from './src/design-system/tokens';

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // ==================== COLORS ====================
      colors: {
        // Primary brand colors
        primary: {
          DEFAULT: designTokens.colors.primary.purple,
          dark: designTokens.colors.primary.purpleDark,
          light: designTokens.colors.primary.purpleLight,
          glow: designTokens.colors.primary.purpleGlow,
        },

        // Accent colors
        accent: {
          cyan: designTokens.colors.accent.cyan,
          'cyan-glow': designTokens.colors.accent.cyanGlow,
          pink: designTokens.colors.accent.pink,
          'pink-glow': designTokens.colors.accent.pinkGlow,
          magenta: designTokens.colors.accent.magenta,
          'magenta-glow': designTokens.colors.accent.magentaGlow,
          blue: designTokens.colors.accent.blue,
          'blue-glow': designTokens.colors.accent.blueGlow,
          green: designTokens.colors.accent.green,
          'green-glow': designTokens.colors.accent.greenGlow,
        },

        // Background colors
        bg: {
          primary: designTokens.colors.background.primary,
          secondary: designTokens.colors.background.secondary,
          tertiary: designTokens.colors.background.tertiary,
          overlay: designTokens.colors.background.overlay,
        },

        // Glass colors
        glass: {
          surface: designTokens.colors.glass.surface,
          border: designTokens.colors.glass.border,
          glow: designTokens.colors.glass.glow,
          subtle: designTokens.colors.glass.subtle,
        },

        // Cyberpunk effect colors
        cyberpunk: {
          scanline: designTokens.colors.cyberpunk.scanline,
          grid: designTokens.colors.cyberpunk.grid,
          'circuit-primary': designTokens.colors.cyberpunk.circuitPrimary,
          'circuit-secondary': designTokens.colors.cyberpunk.circuitSecondary,
          'holo-start': designTokens.colors.cyberpunk.holographicStart,
          'holo-mid': designTokens.colors.cyberpunk.holographicMid,
          'holo-end': designTokens.colors.cyberpunk.holographicEnd,
          'glitch-red': designTokens.colors.cyberpunk.glitchRed,
          'glitch-cyan': designTokens.colors.cyberpunk.glitchCyan,
          'glitch-green': designTokens.colors.cyberpunk.glitchGreen,
        },

        // Semantic colors
        success: designTokens.colors.semantic.success,
        warning: designTokens.colors.semantic.warning,
        error: designTokens.colors.semantic.error,
        info: designTokens.colors.semantic.info,
      },

      // ==================== TYPOGRAPHY ====================
      fontFamily: {
        display: designTokens.typography.fonts.display.split(','),
        body: designTokens.typography.fonts.body.split(','),
        code: designTokens.typography.fonts.code.split(','),
        heading: designTokens.typography.fonts.heading.split(','),
        cyber: designTokens.typography.fonts.cyber.split(','),
      },

      fontSize: designTokens.typography.sizes,
      fontWeight: designTokens.typography.weights,
      lineHeight: designTokens.typography.leading,
      letterSpacing: designTokens.typography.tracking,

      // ==================== SPACING ====================
      spacing: designTokens.spacing,

      // ==================== BORDER RADIUS ====================
      borderRadius: designTokens.radius,

      // ==================== SHADOWS ====================
      boxShadow: {
        ...designTokens.shadows,
        'glow-purple': designTokens.shadows.glow.purple,
        'glow-purple-intense': designTokens.shadows.glow.purpleIntense,
        'glow-cyan': designTokens.shadows.glow.cyan,
        'glow-cyan-intense': designTokens.shadows.glow.cyanIntense,
        'glow-pink': designTokens.shadows.glow.pink,
        'glow-pink-intense': designTokens.shadows.glow.pinkIntense,
        'glow-blue': designTokens.shadows.glow.blue,
        'glow-multi': designTokens.shadows.glow.multi,
        'glass': designTokens.shadows.glass,
        'glass-heavy': designTokens.shadows.glassHeavy,
      },

      // ==================== BACKGROUND ====================
      backgroundImage: {
        'gradient-purple': designTokens.gradients.purple,
        'gradient-cyber': designTokens.gradients.cyber,
        'gradient-neon': designTokens.gradients.neon,
        'gradient-dark': designTokens.gradients.dark,
        'gradient-glow': designTokens.gradients.glow,
        'gradient-holographic': designTokens.gradients.holographic,
        'gradient-circuit': designTokens.gradients.circuit,
        'gradient-scanline': designTokens.gradients.scanline,
      },

      // ==================== ANIMATION ====================
      transitionDuration: designTokens.animation.duration,
      transitionTimingFunction: designTokens.animation.easing,

      // Custom keyframes
      keyframes: {
        glow: {
          '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
          '50%': { opacity: '0.8', filter: 'brightness(1.2)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        holographic: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
        glitch: {
          '0%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
          '100%': { transform: 'translate(0)' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
      },

      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scanline': 'scanline 8s linear infinite',
        'holographic': 'holographic 3s ease-in-out infinite',
        'glitch': 'glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },

      // ==================== Z-INDEX ====================
      zIndex: designTokens.zIndex,

      // ==================== CUSTOM UTILITIES ====================
      // Glassmorphic backdrop blur
      backdropBlur: {
        glass: '8px',
        'glass-heavy': '12px',
      },

      // Blur utilities
      blur: designTokens.effects.blur,

      // Opacity
      opacity: designTokens.effects.opacity,
    },
  },
  plugins: [
    // Comprehensive Cyberpunk Effects Plugin
    plugin(({ addUtilities, addComponents, theme }) => {
      // ========== GLASSMORPHISM UTILITIES ==========
      addUtilities({
        '.glass-card': {
          background: designTokens.colors.glass.surface,
          backdropFilter: 'blur(8px)',
          border: `1px solid ${designTokens.colors.glass.border}`,
          boxShadow: designTokens.shadows.glass,
        },
        '.glass-card-heavy': {
          background: 'rgba(26, 26, 36, 0.7)',
          backdropFilter: 'blur(12px)',
          border: `1px solid ${designTokens.colors.glass.border}`,
          boxShadow: designTokens.shadows.glassHeavy,
        },
        '.glass-card-subtle': {
          background: designTokens.colors.glass.subtle,
          backdropFilter: 'blur(4px)',
          border: `1px solid rgba(255, 255, 255, 0.05)`,
        },

        // ========== NEON GLOW UTILITIES ==========
        '.neon-glow-purple': {
          boxShadow: designTokens.shadows.glow.purple,
        },
        '.neon-glow-purple-intense': {
          boxShadow: designTokens.shadows.glow.purpleIntense,
        },
        '.neon-glow-cyan': {
          boxShadow: designTokens.shadows.glow.cyan,
        },
        '.neon-glow-cyan-intense': {
          boxShadow: designTokens.shadows.glow.cyanIntense,
        },
        '.neon-glow-pink': {
          boxShadow: designTokens.shadows.glow.pink,
        },
        '.neon-glow-pink-intense': {
          boxShadow: designTokens.shadows.glow.pinkIntense,
        },
        '.neon-glow-multi': {
          boxShadow: designTokens.shadows.glow.multi,
        },

        // ========== TEXT EFFECTS ==========
        '.text-gradient': {
          backgroundClip: 'text',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
        },
        '.text-glow-purple': {
          textShadow: '0 0 10px rgba(139, 92, 246, 0.8), 0 0 20px rgba(139, 92, 246, 0.4)',
        },
        '.text-glow-cyan': {
          textShadow: '0 0 10px rgba(6, 182, 212, 0.8), 0 0 20px rgba(6, 182, 212, 0.4)',
        },
        '.text-glow-pink': {
          textShadow: '0 0 10px rgba(236, 72, 153, 0.8), 0 0 20px rgba(236, 72, 153, 0.4)',
        },

        // ========== BORDER EFFECTS ==========
        '.border-glow-purple': {
          border: `1px solid ${designTokens.colors.primary.purple}`,
          boxShadow: `0 0 10px ${designTokens.colors.primary.purpleGlow}`,
        },
        '.border-glow-cyan': {
          border: `1px solid ${designTokens.colors.accent.cyan}`,
          boxShadow: `0 0 10px ${designTokens.colors.accent.cyanGlow}`,
        },
        '.border-glow-animated': {
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: '-2px',
            background: designTokens.gradients.holographic,
            borderRadius: 'inherit',
            opacity: '0',
            transition: 'opacity 0.3s ease',
            zIndex: '-1',
          },
          '&:hover::before': {
            opacity: '0.6',
          },
        },

        // ========== BACKGROUND PATTERNS ==========
        '.bg-grid': {
          backgroundImage: `
            linear-gradient(${designTokens.colors.cyberpunk.grid} 1px, transparent 1px),
            linear-gradient(90deg, ${designTokens.colors.cyberpunk.grid} 1px, transparent 1px)
          `,
          backgroundSize: `${designTokens.patterns.grid.size} ${designTokens.patterns.grid.size}`,
        },
        '.bg-scanline': {
          backgroundImage: designTokens.gradients.scanline,
        },
        '.bg-circuit': {
          backgroundImage: `
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 10px,
              ${designTokens.colors.cyberpunk.circuitPrimary}20 10px,
              ${designTokens.colors.cyberpunk.circuitPrimary}20 11px
            ),
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent 10px,
              ${designTokens.colors.cyberpunk.circuitSecondary}20 10px,
              ${designTokens.colors.cyberpunk.circuitSecondary}20 11px
            )
          `,
        },

        // ========== HOVER EFFECTS ==========
        '.hover-glow-purple': {
          transition: 'box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: designTokens.shadows.glow.purpleIntense,
          },
        },
        '.hover-glow-cyan': {
          transition: 'box-shadow 0.3s ease',
          '&:hover': {
            boxShadow: designTokens.shadows.glow.cyanIntense,
          },
        },
        '.hover-scale': {
          transition: 'transform 0.3s ease',
          '&:hover': {
            transform: 'scale(1.05)',
          },
        },
        '.hover-lift': {
          transition: 'transform 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
          },
        },

        // ========== HOLOGRAPHIC EFFECTS ==========
        '.holographic': {
          background: designTokens.gradients.holographic,
          backgroundSize: '200% 200%',
          animation: 'holographic 3s ease-in-out infinite',
        },
        '.holographic-text': {
          background: designTokens.gradients.holographic,
          backgroundSize: '200% 200%',
          backgroundClip: 'text',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          animation: 'holographic 3s ease-in-out infinite',
        },
      });

      // ========== COMPONENT UTILITIES ==========
      addComponents({
        '.cyberpunk-button': {
          position: 'relative',
          padding: `${theme('spacing.3')} ${theme('spacing.6')}`,
          background: designTokens.colors.glass.surface,
          backdropFilter: 'blur(8px)',
          border: `1px solid ${designTokens.colors.primary.purple}`,
          borderRadius: theme('borderRadius.lg'),
          color: theme('colors.white'),
          fontWeight: theme('fontWeight.semibold'),
          transition: 'all 0.3s ease',
          cursor: 'pointer',
          '&:hover': {
            boxShadow: designTokens.shadows.glow.purpleIntense,
            transform: 'translateY(-2px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        '.cyberpunk-card': {
          background: designTokens.colors.glass.surface,
          backdropFilter: 'blur(8px)',
          border: `1px solid ${designTokens.colors.glass.border}`,
          borderRadius: theme('borderRadius.xl'),
          padding: theme('spacing.6'),
          boxShadow: designTokens.shadows.glass,
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: `${designTokens.shadows.glass}, ${designTokens.shadows.glow.purple}`,
            transform: 'translateY(-4px)',
          },
        },
        '.cyberpunk-input': {
          background: 'rgba(26, 26, 36, 0.5)',
          backdropFilter: 'blur(4px)',
          border: `1px solid ${designTokens.colors.glass.border}`,
          borderRadius: theme('borderRadius.lg'),
          padding: `${theme('spacing.3')} ${theme('spacing.4')}`,
          color: theme('colors.white'),
          transition: 'all 0.3s ease',
          '&:focus': {
            outline: 'none',
            borderColor: designTokens.colors.primary.purple,
            boxShadow: designTokens.shadows.glow.purple,
          },
        },
      });
    }),
  ],
};

export default config;
