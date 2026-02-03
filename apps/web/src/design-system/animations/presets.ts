/**
 * ANIMATION PRESETS
 * Production-ready Framer Motion animation configurations
 */

import { Variants, Transition } from 'framer-motion';

/**
 * TIMING & EASING
 */
export const timing = {
  instant: 0.1,
  fast: 0.2,
  normal: 0.3,
  slow: 0.5,
  verySlow: 0.8,
} as const;

export const easing = {
  smooth: [0.4, 0, 0.2, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
  elastic: [0.68, -0.6, 0.32, 1.6],
  easeIn: [0.4, 0, 1, 1],
  easeOut: [0, 0, 0.2, 1],
  easeInOut: [0.4, 0, 0.2, 1],
} as const;

/**
 * SPRING PHYSICS
 */
export const spring = {
  // Snappy interactions (buttons, clicks)
  snappy: {
    type: 'spring' as const,
    stiffness: 400,
    damping: 17,
  },
  
  // Bouncy animations (modals, tooltips)
  bouncy: {
    type: 'spring' as const,
    stiffness: 300,
    damping: 10,
  },
  
  // Smooth transitions (page transitions)
  smooth: {
    type: 'spring' as const,
    stiffness: 200,
    damping: 20,
  },
  
  // Floaty animations (hover effects)
  floaty: {
    type: 'spring' as const,
    stiffness: 100,
    damping: 8,
  },
  
  // Gentle animations (background elements)
  gentle: {
    type: 'spring' as const,
    stiffness: 150,
    damping: 25,
  },
} as const;

/**
 * FADE ANIMATIONS
 */
export const fade: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.smooth,
    },
  },
};

export const fadeOut: Variants = {
  initial: { opacity: 1 },
  animate: { 
    opacity: 0,
    transition: {
      duration: timing.fast,
      ease: easing.smooth,
    },
  },
};

/**
 * SLIDE ANIMATIONS
 */
export const slideUp: Variants = {
  initial: { 
    y: 10,
    opacity: 0,
  },
  animate: { 
    y: 0,
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
  exit: {
    y: -10,
    opacity: 0,
    transition: {
      duration: timing.fast,
      ease: easing.easeIn,
    },
  },
};

export const slideDown: Variants = {
  initial: { 
    y: -10,
    opacity: 0,
  },
  animate: { 
    y: 0,
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
  exit: {
    y: 10,
    opacity: 0,
    transition: {
      duration: timing.fast,
      ease: easing.easeIn,
    },
  },
};

export const slideLeft: Variants = {
  initial: { 
    x: 10,
    opacity: 0,
  },
  animate: { 
    x: 0,
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
};

export const slideRight: Variants = {
  initial: { 
    x: -10,
    opacity: 0,
  },
  animate: { 
    x: 0,
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
};

/**
 * SCALE ANIMATIONS
 */
export const scaleIn: Variants = {
  initial: { 
    scale: 0.95,
    opacity: 0,
  },
  animate: { 
    scale: 1,
    opacity: 1,
    transition: spring.snappy,
  },
  exit: {
    scale: 0.95,
    opacity: 0,
    transition: {
      duration: timing.fast,
    },
  },
};

export const scaleOut: Variants = {
  initial: { 
    scale: 1,
    opacity: 1,
  },
  animate: { 
    scale: 0.95,
    opacity: 0,
    transition: {
      duration: timing.fast,
    },
  },
};

export const popIn: Variants = {
  initial: { 
    scale: 0,
    opacity: 0,
  },
  animate: { 
    scale: 1,
    opacity: 1,
    transition: spring.bouncy,
  },
  exit: {
    scale: 0,
    opacity: 0,
    transition: {
      duration: timing.fast,
    },
  },
};

/**
 * ROTATION ANIMATIONS
 */
export const rotate: Variants = {
  initial: { rotate: 0 },
  animate: { 
    rotate: 360,
    transition: {
      duration: 1,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

export const rotateSlow: Variants = {
  initial: { rotate: 0 },
  animate: { 
    rotate: 360,
    transition: {
      duration: 3,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

/**
 * FLOAT ANIMATION
 */
export const float: Variants = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 3,
      ease: 'easeInOut',
      repeat: Infinity,
    },
  },
};

/**
 * GLOW PULSE ANIMATION
 */
export const glowPulse: Variants = {
  animate: {
    filter: ['brightness(1)', 'brightness(1.2)', 'brightness(1)'],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 2,
      ease: 'easeInOut',
      repeat: Infinity,
    },
  },
};

/**
 * STAGGER CHILDREN
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const staggerItem: Variants = {
  initial: { 
    y: 10,
    opacity: 0,
  },
  animate: { 
    y: 0,
    opacity: 1,
    transition: spring.smooth,
  },
};

/**
 * PAGE TRANSITIONS
 */
export const pageTransition: Variants = {
  initial: { 
    opacity: 0,
    y: 20,
  },
  animate: { 
    opacity: 1,
    y: 0,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: timing.fast,
      ease: easing.easeIn,
    },
  },
};

/**
 * MODAL ANIMATIONS
 */
export const modalBackdrop: Variants = {
  initial: { opacity: 0 },
  animate: { 
    opacity: 1,
    transition: {
      duration: timing.fast,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: timing.fast,
      delay: 0.1,
    },
  },
};

export const modalContent: Variants = {
  initial: { 
    scale: 0.95,
    opacity: 0,
    y: 20,
  },
  animate: { 
    scale: 1,
    opacity: 1,
    y: 0,
    transition: spring.bouncy,
  },
  exit: {
    scale: 0.95,
    opacity: 0,
    y: 20,
    transition: {
      duration: timing.fast,
    },
  },
};

/**
 * INTERACTION ANIMATIONS
 */
export const hoverScale = {
  whileHover: { 
    scale: 1.02,
    transition: spring.snappy,
  },
  whileTap: { 
    scale: 0.98,
  },
};

export const hoverLift = {
  whileHover: { 
    y: -2,
    transition: spring.snappy,
  },
  whileTap: { 
    y: 0,
  },
};

export const hoverGlow = {
  whileHover: { 
    boxShadow: '0 0 20px hsl(220, 90%, 60%, 0.5), 0 0 40px hsl(220, 90%, 60%, 0.3)',
    transition: {
      duration: timing.fast,
    },
  },
};

/**
 * AUDIO-REACTIVE ANIMATIONS
 * Designed to respond to real-time audio data (amplitude, frequency)
 */
export const audioReactiveBounce: Variants = {
  animate: (amplitudeValue: number = 0) => ({
    scale: [1, 1 + amplitudeValue * 0.1, 1],
    transition: {
      duration: 0.05,
      ease: 'linear',
    },
  }),
};

export const audioReactiveGlow: Variants = {
  animate: (amplitudeValue: number = 0) => ({
    boxShadow: [
      `0 0 10px hsl(180, 95%, 55%, ${0.3 + amplitudeValue * 0.4})`,
      `0 0 30px hsl(180, 95%, 55%, ${0.5 + amplitudeValue * 0.5})`,
      `0 0 10px hsl(180, 95%, 55%, ${0.3 + amplitudeValue * 0.4})`,
    ],
    transition: {
      duration: 0.1,
      ease: 'linear',
    },
  }),
};

export const audioReactivePulse: Variants = {
  animate: (frequencyValue: number = 0) => ({
    opacity: [1, 0.8 + frequencyValue * 0.2, 1],
    transition: {
      duration: 0.15,
      ease: 'easeInOut',
    },
  }),
};

/**
 * PARTICLE ANIMATION PATTERNS
 * For GPU-accelerated particle systems
 */
export const particleFloat: Variants = {
  animate: {
    y: [0, -20, 0],
    x: [-5, 5, -5],
    transition: {
      duration: 4,
      ease: 'easeInOut',
      repeat: Infinity,
    },
  },
};

export const particleSwoosh: Variants = {
  animate: {
    x: [0, 30, 0],
    y: [0, -30, 0],
    opacity: [1, 0.6, 0],
    transition: {
      duration: 2,
      ease: 'easeOut',
      repeat: Infinity,
    },
  },
};

export const particleExplode: Variants = {
  initial: {
    scale: 1,
    opacity: 1,
  },
  animate: {
    scale: [1, 2, 0],
    opacity: [1, 0.6, 0],
    transition: {
      duration: 1.5,
      ease: 'easeOut',
    },
  },
};

/**
 * 3D TRANSFORMATION ANIMATIONS
 * For Three.js visualizer and 3D components
 */
export const rotateX: Variants = {
  animate: {
    rotateX: 360,
    transition: {
      duration: 8,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

export const rotateY: Variants = {
  animate: {
    rotateY: 360,
    transition: {
      duration: 6,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

export const rotateZ: Variants = {
  animate: {
    rotateZ: 360,
    transition: {
      duration: 10,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

export const perspective3D: Variants = {
  initial: {
    rotateY: 45,
    rotateX: 10,
    scale: 0.8,
    opacity: 0,
  },
  animate: {
    rotateY: 0,
    rotateX: 0,
    scale: 1,
    opacity: 1,
    transition: {
      duration: timing.slow,
      ease: easing.smooth,
    },
  },
};

/**
 * ADVANCED INTERACTION PATTERNS
 * For sophisticated user interactions
 */
export const hoverTilt = {
  whileHover: {
    rotateY: 2,
    rotateX: -2,
    transition: spring.snappy,
  },
  whileTap: {
    scale: 0.95,
  },
};

export const hoverBridge = {
  whileHover: {
    y: -8,
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
    transition: spring.bouncy,
  },
  whileTap: {
    y: -2,
    boxShadow: '0 5px 15px rgba(0, 0, 0, 0.2)',
  },
};

export const dragTension = {
  whileDrag: {
    scale: 1.05,
    opacity: 0.8,
  },
  dragElastic: 0.2,
};

export const tapSucceed: Variants = {
  tap: {
    scale: 0.95,
  },
};

/**
 * WAVEFORM ANIMATIONS
 * For audio waveform visualizations
 */
export const waveformBars: Variants = {
  animate: (index: number) => ({
    height: ['20%', '80%', '20%'],
    transition: {
      duration: 0.5,
      ease: 'easeInOut',
      repeat: Infinity,
      delay: index * 0.05,
    },
  }),
};

export const waveformFrequency: Variants = {
  animate: {
    y: [0, -5, 0],
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 0.2,
      ease: 'linear',
    },
  },
};

/**
 * PROGRESS & STATUS ANIMATIONS
 */
export const progressFill: Variants = {
  initial: { scaleX: 0 },
  animate: {
    scaleX: 1,
    transition: {
      duration: timing.slow,
      ease: easing.easeOut,
    },
  },
};

export const progressPulse: Variants = {
  animate: {
    opacity: [0.6, 1, 0.6],
    transition: {
      duration: 1.5,
      ease: 'easeInOut',
      repeat: Infinity,
    },
  },
};

export const statusIndicator: Variants = {
  animate: {
    boxShadow: [
      '0 0 0 0 rgba(52, 211, 153, 0.7)',
      '0 0 0 10px rgba(52, 211, 153, 0)',
    ],
    transition: {
      duration: 2,
      ease: 'easeOut',
      repeat: Infinity,
    },
  },
};

/**
 * COMMAND PALETTE ANIMATIONS
 */
export const commandPaletteBackdrop: Variants = {
  initial: { opacity: 0, backdropFilter: 'blur(0px)' },
  animate: {
    opacity: 1,
    backdropFilter: 'blur(4px)',
    transition: {
      duration: timing.fast,
    },
  },
  exit: {
    opacity: 0,
    backdropFilter: 'blur(0px)',
    transition: {
      duration: timing.fast,
    },
  },
};

export const commandPaletteContent: Variants = {
  initial: {
    y: -10,
    opacity: 0,
  },
  animate: {
    y: 0,
    opacity: 1,
    transition: spring.snappy,
  },
  exit: {
    y: -10,
    opacity: 0,
    transition: {
      duration: timing.fast,
    },
  },
};

/**
 * BENTO GRID ANIMATIONS
 */
export const bentoItemEnter: Variants = {
  initial: {
    scale: 0.8,
    opacity: 0,
  },
  animate: {
    scale: 1,
    opacity: 1,
    transition: {
      duration: timing.normal,
      ease: easing.easeOut,
    },
  },
};

export const bentoItemHover = {
  whileHover: {
    scale: 1.03,
    y: -4,
    transition: spring.snappy,
  },
};

/**
 * SKELETON LOADING ANIMATIONS
 */
export const skeletonShimmer: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      ease: 'linear',
      repeat: Infinity,
    },
  },
};

/**
 * UTILITY FUNCTIONS
 */
export const getStaggerDelay = (index: number, baseDelay: number = 0.1) => ({
  delay: index * baseDelay,
});

export const getSlideDirection = (direction: 'up' | 'down' | 'left' | 'right') => {
  const directions = {
    up: slideUp,
    down: slideDown,
    left: slideLeft,
    right: slideRight,
  };
  return directions[direction];
};

/**
 * AUDIO-REACTIVE VALUE GENERATOR
 * Converts normalized audio data (0-1) to animation values
 */
export const getAudioValue = (
  amplitude: number,
  minValue: number,
  maxValue: number
): number => {
  return minValue + amplitude * (maxValue - minValue);
};

/**
 * STAGGER ANIMATION BUILDER
 * Creates coordinated stagger animations for sequences
 */
export const createStaggerAnimation = (
  itemVariants: Variants,
  staggerDelay: number = 0.05,
  delayChildren: number = 0.1
): { container: Variants; item: Variants } => ({
  container: {
    initial: 'initial',
    animate: 'animate',
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
  item: itemVariants,
});

export type AnimationPreset = keyof typeof spring;
export type SlideDirection = 'up' | 'down' | 'left' | 'right';
