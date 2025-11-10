/** @type {import('tailwindcss').Config} */
const plugin = require('tailwindcss/plugin')

module.exports = {
  darkMode: 'class',
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      // ============================================================================
      // CYBERPUNK COLOR SYSTEM (HSL-based for easy manipulation)
      // ============================================================================
      colors: {
        // Primary Cyberpunk Colors
        cyber: {
          blue: {
            DEFAULT: 'hsl(220, 90%, 60%)',
            light: 'hsl(220, 90%, 70%)',
            dark: 'hsl(220, 90%, 50%)',
            glow: 'hsl(220, 90%, 60%, 0.5)',
          },
          purple: {
            DEFAULT: 'hsl(270, 85%, 65%)',
            light: 'hsl(270, 85%, 75%)',
            dark: 'hsl(270, 85%, 55%)',
            glow: 'hsl(270, 85%, 65%, 0.5)',
          },
          cyan: {
            DEFAULT: 'hsl(180, 95%, 55%)',
            light: 'hsl(180, 95%, 65%)',
            dark: 'hsl(180, 95%, 45%)',
            glow: 'hsl(180, 95%, 55%, 0.5)',
          },
          magenta: {
            DEFAULT: 'hsl(320, 90%, 60%)',
            light: 'hsl(320, 90%, 70%)',
            dark: 'hsl(320, 90%, 50%)',
            glow: 'hsl(320, 90%, 60%, 0.5)',
          },
        },
        neon: {
          pink: '#ff2a6d',
          blue: '#05d9e8',
          purple: '#d300c5',
          cyan: '#00f1ff',
        },
        
        // Neutral Dark Theme
        dark: {
          100: 'hsl(220, 15%, 18%)',
          200: 'hsl(220, 15%, 15%)',
          300: 'hsl(220, 15%, 12%)',
          400: 'hsl(220, 15%, 10%)',
          500: 'hsl(220, 15%, 8%)',  // Main background
          600: 'hsl(220, 15%, 6%)',
          700: 'hsl(220, 15%, 4%)',
          800: 'hsl(220, 15%, 2%)',
          900: 'hsl(220, 15%, 0%)',
        },
        
        // Glass Surface Colors
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          DEFAULT: 'rgba(255, 255, 255, 0.08)',
          strong: 'rgba(255, 255, 255, 0.12)',
          border: 'rgba(255, 255, 255, 0.1)',
        },
        
        // Text Colors
        text: {
          primary: 'hsl(0, 0%, 98%)',
          secondary: 'hsl(220, 10%, 65%)',
          tertiary: 'hsl(220, 10%, 45%)',
          muted: 'hsl(220, 10%, 35%)',
        },
        
        // Semantic Colors (with cyberpunk twist)
        success: 'hsl(145, 85%, 55%)',
        warning: 'hsl(45, 95%, 60%)',
        error: 'hsl(0, 90%, 60%)',
        info: 'hsl(210, 90%, 60%)',
        
        // macOS system colors (kept for compatibility)
        system: {
          blue: '#007AFF',
          green: '#34C759',
          indigo: '#5856D6',
          orange: '#FF9500',
          pink: '#FF2D55',
          purple: '#AF52DE',
          red: '#FF3B30',
          teal: '#5AC8FA',
          yellow: '#FFCC00',
        },
      },
      
      // ============================================================================
      // GRADIENT PRESETS (Sparking Effects)
      // ============================================================================
      backgroundImage: {
        // Electric Storm Gradients
        'spark-1': 'linear-gradient(135deg, hsl(220, 90%, 60%) 0%, hsl(250, 85%, 65%) 50%, hsl(320, 90%, 60%) 100%)',
        'spark-2': 'linear-gradient(90deg, hsl(180, 95%, 55%) 0%, hsl(220, 90%, 60%) 50%, hsl(270, 85%, 65%) 100%)',
        'spark-3': 'linear-gradient(180deg, hsl(270, 85%, 65%) 0%, hsl(320, 90%, 60%) 100%)',
        'spark-4': 'linear-gradient(45deg, hsl(220, 90%, 60%) 0%, hsl(180, 95%, 55%) 100%)',
        
        // Animated Spark (for keyframe animations)
        'spark-animated': 'linear-gradient(90deg, hsl(180, 95%, 55%), hsl(220, 90%, 60%), hsl(270, 85%, 65%), hsl(320, 90%, 60%), hsl(180, 95%, 55%))',
        
        // Subtle Background Gradients
        'bg-cyber': 'linear-gradient(135deg, hsl(220, 15%, 8%) 0%, hsl(270, 20%, 10%) 100%)',
        'bg-panel': 'linear-gradient(135deg, rgba(255, 255, 255, 0.07) 0%, rgba(255, 255, 255, 0.03) 100%)',
        
        // Mesh Gradients (multi-stop)
        'mesh-1': 'radial-gradient(at 0% 0%, hsl(220, 90%, 30%) 0%, transparent 50%), radial-gradient(at 100% 100%, hsl(270, 85%, 30%) 0%, transparent 50%)',
        'mesh-2': 'radial-gradient(at 0% 100%, hsl(180, 95%, 30%) 0%, transparent 50%), radial-gradient(at 100% 0%, hsl(320, 90%, 30%) 0%, transparent 50%)',
      },
      
      // ============================================================================
      // BOX SHADOWS (Glass & Glow Effects)
      // ============================================================================
      boxShadow: {
        // Glass Shadows
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
        'glass-lg': '0 12px 48px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
        'glass-sm': '0 4px 16px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05)',
        
        // Neon Glow Effects
        'glow-blue': '0 0 20px hsl(220, 90%, 60%, 0.5), 0 0 40px hsl(220, 90%, 60%, 0.3)',
        'glow-purple': '0 0 20px hsl(270, 85%, 65%, 0.5), 0 0 40px hsl(270, 85%, 65%, 0.3)',
        'glow-cyan': '0 0 20px hsl(180, 95%, 55%, 0.5), 0 0 40px hsl(180, 95%, 55%, 0.3)',
        'glow-magenta': '0 0 20px hsl(320, 90%, 60%, 0.5), 0 0 40px hsl(320, 90%, 60%, 0.3)',
        
        // Combined Glass + Glow
        'glass-glow-blue': '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(220, 90%, 60%, 0.3)',
        'glass-glow-purple': '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px hsl(270, 85%, 65%, 0.3)',
        
        // macOS compatibility
        'macos': '0 4px 20px rgba(0, 0, 0, 0.1), 0 0 0 0.5px rgba(0, 0, 0, 0.05)',
        'macos-dark': '0 4px 20px rgba(0, 0, 0, 0.3), 0 0 0 0.5px rgba(255, 255, 255, 0.1)',
      },
      
      // ============================================================================
      // BORDER RADIUS (Modern, smooth corners)
      // ============================================================================
      borderRadius: {
        'glass': '12px',
        'glass-sm': '8px',
        'glass-lg': '16px',
        'glass-xl': '20px',
        'macos': '10px',
        'macos-sm': '6px',
        'macos-lg': '14px',
      },
      
      // ============================================================================
      // TYPOGRAPHY
      // ============================================================================
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['JetBrains Mono', 'Monaco', 'Cascadia Code', 'Courier New', 'monospace'],
        display: ['Inter', '-apple-system', 'sans-serif'],
        orbitron: ['"Orbitron"', 'Inter', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      
      // ============================================================================
      // ANIMATIONS & TRANSITIONS
      // ============================================================================
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'elastic': 'cubic-bezier(0.68, -0.6, 0.32, 1.6)',
        'macos': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      transitionDuration: {
        'instant': '100ms',
        'fast': '200ms',
        'normal': '300ms',
        'slow': '500ms',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'spark-flow': 'sparkFlow 3s ease infinite',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },
      keyframes: {
        sparkFlow: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        glowPulse: {
          '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
          '50%': { opacity: '0.8', filter: 'brightness(1.2)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      
      // ============================================================================
      // BACKDROP FILTERS (Glass Effects)
      // ============================================================================
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'DEFAULT': '10px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '40px',
        '3xl': '64px',
      },
      backdropSaturate: {
        0: '0',
        50: '.5',
        100: '1',
        150: '1.5',
        180: '1.8',
        200: '2',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    
    // Custom Glass Plugin
    plugin(function({ addUtilities, theme }) {
      const glassUtilities = {
        '.glass': {
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px) saturate(180%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        },
        '.glass-light': {
          background: 'rgba(255, 255, 255, 0.08)',
          backdropFilter: 'blur(10px) saturate(180%)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        },
        '.glass-strong': {
          background: 'rgba(255, 255, 255, 0.12)',
          backdropFilter: 'blur(12px) saturate(180%)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          boxShadow: '0 12px 48px rgba(0, 0, 0, 0.5)',
        },
        '.glass-hover': {
          background: 'rgba(255, 255, 255, 0.1)',
          borderColor: 'rgba(255, 255, 255, 0.3)',
        },
      }
      addUtilities(glassUtilities)
    }),
    
    // Custom Glow Plugin
    plugin(function({ addUtilities }) {
      const glowUtilities = {
        '.glow-text-blue': {
          textShadow: '0 0 10px hsl(220, 90%, 60%, 0.8), 0 0 20px hsl(220, 90%, 60%, 0.5)',
        },
        '.glow-text-purple': {
          textShadow: '0 0 10px hsl(270, 85%, 65%, 0.8), 0 0 20px hsl(270, 85%, 65%, 0.5)',
        },
        '.glow-text-cyan': {
          textShadow: '0 0 10px hsl(180, 95%, 55%, 0.8), 0 0 20px hsl(180, 95%, 55%, 0.5)',
        },
      }
      addUtilities(glowUtilities)
    }),
  ],
}
