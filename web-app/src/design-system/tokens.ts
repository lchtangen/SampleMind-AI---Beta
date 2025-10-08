/**
 * SampleMind AI Design System - Design Tokens
 * Modern Tech Cyberpunk Aesthetic
 *
 * These tokens are the single source of truth for all styling.
 * AI coding assistants should reference these values.
 */

export const designTokens = {
  // ==================== COLORS ====================
  colors: {
    // Primary Brand Colors
    primary: {
      purple: '#8B5CF6',      // Primary brand color
      purpleDark: '#7C3AED',  // Darker variant
      purpleLight: '#A78BFA', // Lighter variant
      purpleGlow: '#8B5CF6CC', // With opacity for glow
    },

    // Accent Colors
    accent: {
      cyan: '#06B6D4',      // Electric cyan
      cyanGlow: '#06B6D4DD',
      pink: '#EC4899',      // Neon pink/magenta
      pinkGlow: '#EC4899DD',
      magenta: '#EC4899',   // Alias for pink (explicit magenta)
      magentaGlow: '#EC4899DD',
      blue: '#3B82F6',      // Electric blue
      blueGlow: '#3B82F6DD',
      green: '#10B981',     // Neon green
      greenGlow: '#10B981DD',
    },

    // Background Colors (Dark Mode Primary)
    background: {
      primary: '#0A0A0F',    // Deep space black
      secondary: '#131318',  // Dark charcoal
      tertiary: '#1A1A24',   // Elevated surface
      overlay: '#0A0A0FE6',  // Dark overlay with transparency
    },

    // Glassmorphism
    glass: {
      surface: 'rgba(26, 26, 36, 0.5)',
      border: 'rgba(139, 92, 246, 0.2)',
      glow: 'rgba(139, 92, 246, 0.1)',
      subtle: 'rgba(255, 255, 255, 0.05)',
    },

    // Text Colors
    text: {
      primary: '#FFFFFF',     // Pure white
      secondary: '#94A3B8',   // Cool gray
      tertiary: '#64748B',    // Medium gray
      muted: '#475569',       // Dark gray
      glow: '#E0E7FF',        // Light glow text
    },

    // Semantic Colors
    semantic: {
      success: '#10B981',
      warning: '#F59E0B',
      error: '#EF4444',
      info: '#3B82F6',
    },

    // Audio/Music Themed
    audio: {
      waveformPrimary: '#8B5CF6',
      waveformAccent: '#06B6D4',
      spectrum: ['#8B5CF6', '#A78BFA', '#06B6D4', '#3B82F6', '#EC4899'],
    },

    // Cyberpunk Effects
    cyberpunk: {
      scanline: 'rgba(139, 92, 246, 0.05)',
      grid: 'rgba(6, 182, 212, 0.15)',
      circuitPrimary: '#8B5CF6',
      circuitSecondary: '#06B6D4',
      holographicStart: '#EC4899',
      holographicMid: '#8B5CF6',
      holographicEnd: '#06B6D4',
      glitchRed: '#FF0055',
      glitchCyan: '#00FFFF',
      glitchGreen: '#00FF00',
    },
  },

  // ==================== TYPOGRAPHY ====================
  typography: {
    fonts: {
      display: "'Orbitron', 'Inter', -apple-system, system-ui, sans-serif",
      body: "'Inter', -apple-system, system-ui, sans-serif",
      code: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
      heading: "'Rajdhani', 'Inter', -apple-system, system-ui, sans-serif",
      cyber: "'Orbitron', sans-serif",  // Explicit cyberpunk font
    },

    // Font Sizes (8pt Grid)
    sizes: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
      '5xl': '3rem',     // 48px
      '6xl': '3.75rem',  // 60px
      '7xl': '4.5rem',   // 72px
      '8xl': '6rem',     // 96px
    },

    // Font Weights
    weights: {
      light: 300,
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
      black: 900,
    },

    // Line Heights
    leading: {
      tight: 1.25,
      snug: 1.375,
      normal: 1.5,
      relaxed: 1.625,
      loose: 2,
    },

    // Letter Spacing
    tracking: {
      tighter: '-0.05em',
      tight: '-0.025em',
      normal: '0em',
      wide: '0.025em',
      wider: '0.05em',
      widest: '0.1em',
    },
  },

  // ==================== SPACING (8pt Grid) ====================
  spacing: {
    0: '0',
    1: '0.25rem',  // 4px
    2: '0.5rem',   // 8px
    3: '0.75rem',  // 12px
    4: '1rem',     // 16px
    5: '1.25rem',  // 20px
    6: '1.5rem',   // 24px
    8: '2rem',     // 32px
    10: '2.5rem',  // 40px
    12: '3rem',    // 48px
    16: '4rem',    // 64px
    20: '5rem',    // 80px
    24: '6rem',    // 96px
    32: '8rem',    // 128px
    40: '10rem',   // 160px
    48: '12rem',   // 192px
    56: '14rem',   // 224px
    64: '16rem',   // 256px
  },

  // ==================== BORDER RADIUS ====================
  radius: {
    none: '0',
    sm: '0.375rem',   // 6px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
    xl: '1rem',       // 16px
    '2xl': '1.5rem',  // 24px
    '3xl': '2rem',    // 32px
    full: '9999px',   // Fully rounded
  },

  // ==================== SHADOWS & GLOWS ====================
  shadows: {
    // Standard Shadows
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',

    // Neon Glows
    glow: {
      purple: '0 0 20px rgba(139, 92, 246, 0.5)',
      purpleIntense: '0 0 30px rgba(139, 92, 246, 0.8), 0 0 60px rgba(139, 92, 246, 0.4)',
      cyan: '0 0 20px rgba(6, 182, 212, 0.5)',
      cyanIntense: '0 0 30px rgba(6, 182, 212, 0.8), 0 0 60px rgba(6, 182, 212, 0.4)',
      pink: '0 0 20px rgba(236, 72, 153, 0.5)',
      pinkIntense: '0 0 30px rgba(236, 72, 153, 0.8), 0 0 60px rgba(236, 72, 153, 0.4)',
      blue: '0 0 20px rgba(59, 130, 246, 0.5)',
      multi: '0 0 20px rgba(139, 92, 246, 0.4), 0 0 40px rgba(6, 182, 212, 0.3)',
    },

    // Glassmorphic
    glass: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
    glassHeavy: '0 8px 32px 0 rgba(0, 0, 0, 0.5)',
  },

  // ==================== GRADIENTS ====================
  gradients: {
    purple: 'linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)',
    cyber: 'linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%)',
    neon: 'linear-gradient(135deg, #EC4899 0%, #8B5CF6 50%, #06B6D4 100%)',
    dark: 'linear-gradient(180deg, #0A0A0F 0%, #131318 100%)',
    glow: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.3) 0%, transparent 70%)',
    holographic: 'linear-gradient(45deg, #EC4899 0%, #8B5CF6 33%, #06B6D4 66%, #EC4899 100%)',
    circuit: 'linear-gradient(90deg, transparent 0%, #8B5CF6 50%, transparent 100%)',
    scanline: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(139, 92, 246, 0.03) 2px, rgba(139, 92, 246, 0.03) 4px)',
  },

  // ==================== ANIMATION ====================
  animation: {
    // Durations
    duration: {
      instant: '100ms',
      fast: '200ms',
      normal: '300ms',
      slow: '500ms',
      slower: '700ms',
      slowest: '1000ms',
    },

    // Timing Functions
    easing: {
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      smooth: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    },

    // Keyframe Definitions
    keyframes: {
      pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      glow: 'glow 2s ease-in-out infinite alternate',
      scanline: 'scanline 8s linear infinite',
      holographic: 'holographic 3s ease-in-out infinite',
      glitch: 'glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both',
    },
  },

  // ==================== PATTERNS & TEXTURES ====================
  patterns: {
    grid: {
      size: '40px',
      color: 'rgba(6, 182, 212, 0.1)',
      strokeWidth: '1px',
    },
    hexagon: {
      size: '60px',
      strokeColor: 'rgba(139, 92, 246, 0.15)',
      fillColor: 'rgba(139, 92, 246, 0.05)',
    },
    circuit: {
      lineColor: 'rgba(139, 92, 246, 0.2)',
      nodeColor: 'rgba(6, 182, 212, 0.5)',
      glowColor: 'rgba(139, 92, 246, 0.4)',
    },
    scanline: {
      spacing: '4px',
      opacity: 0.05,
      animationSpeed: '8s',
    },
  },

  // ==================== EFFECTS ====================
  effects: {
    blur: {
      none: '0',
      sm: '4px',
      md: '8px',
      lg: '12px',
      xl: '16px',
      '2xl': '24px',
    },
    opacity: {
      0: '0',
      5: '0.05',
      10: '0.1',
      20: '0.2',
      40: '0.4',
      60: '0.6',
      80: '0.8',
      90: '0.9',
      100: '1',
    },
  },

  // ==================== BREAKPOINTS ====================
  breakpoints: {
    mobile: '320px',
    mobileLg: '480px',
    tablet: '768px',
    desktop: '1024px',
    wide: '1440px',
    ultra: '1920px',
  },

  // ==================== Z-INDEX LAYERS ====================
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
    notification: 1080,
  },
} as const;

// Type exports for TypeScript
export type DesignTokens = typeof designTokens;
export type ColorToken = keyof typeof designTokens.colors;
export type SpacingToken = keyof typeof designTokens.spacing;
export type RadiusToken = keyof typeof designTokens.radius;

// CSS Variable Generator (for runtime usage)
export const generateCSSVariables = (): string => {
  return `
    :root {
      /* Colors */
      --color-primary-purple: ${designTokens.colors.primary.purple};
      --color-accent-cyan: ${designTokens.colors.accent.cyan};
      --color-accent-pink: ${designTokens.colors.accent.pink};
      --color-bg-primary: ${designTokens.colors.background.primary};
      --color-bg-secondary: ${designTokens.colors.background.secondary};
      --color-text-primary: ${designTokens.colors.text.primary};

      /* Spacing */
      --space-4: ${designTokens.spacing[4]};
      --space-8: ${designTokens.spacing[8]};

      /* Shadows */
      --shadow-glass: ${designTokens.shadows.glass};
      --shadow-glow-purple: ${designTokens.shadows.glow.purple};

      /* Animation */
      --duration-normal: ${designTokens.animation.duration.normal};
      --easing-out: ${designTokens.animation.easing.out};
    }
  `;
};

export default designTokens;
