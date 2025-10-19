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

export type AnimationPreset = keyof typeof spring;
export type SlideDirection = 'up' | 'down' | 'left' | 'right';
