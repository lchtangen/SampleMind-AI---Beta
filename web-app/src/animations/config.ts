/**
 * Global Animation Configuration
 * Framer Motion-based animation system for SampleMind AI
 * Provides consistent timing, easing, and variant configurations
 */

import { Transition, Variants } from 'framer-motion';

/**
 * Animation Timing Configuration
 */
export const animationTiming = {
  /** Ultra-fast animations (micro-interactions) */
  instant: 0.1,
  /** Fast animations (button hovers, small elements) */
  fast: 0.2,
  /** Normal animations (most UI transitions) */
  normal: 0.3,
  /** Moderate animations (cards, modals) */
  moderate: 0.4,
  /** Slow animations (page transitions, large elements) */
  slow: 0.6,
  /** Very slow animations (special effects) */
  verySlow: 0.8,
} as const;

/**
 * Animation Easing Functions
 * Cyberpunk-themed easing curves for smooth, futuristic motion
 */
export const animationEasing = {
  /** Smooth acceleration and deceleration */
  smooth: [0.4, 0, 0.2, 1],
  /** Sharp entry, smooth exit (cyberpunk feel) */
  sharp: [0.4, 0, 0.6, 1],
  /** Bouncy effect for playful interactions */
  bouncy: [0.68, -0.55, 0.265, 1.55],
  /** Linear motion for mechanical effects */
  linear: [0, 0, 1, 1],
  /** Ease in for subtle entries */
  easeIn: [0.4, 0, 1, 1],
  /** Ease out for natural exits */
  easeOut: [0, 0, 0.2, 1],
  /** Spring-like motion */
  spring: [0.175, 0.885, 0.32, 1.275],
} as const;

/**
 * Spring Animation Configurations
 */
export const springConfigs = {
  /** Gentle spring for subtle movements */
  gentle: {
    type: 'spring' as const,
    stiffness: 120,
    damping: 14,
  },
  /** Bouncy spring for playful elements */
  bouncy: {
    type: 'spring' as const,
    stiffness: 260,
    damping: 20,
  },
  /** Stiff spring for quick snappy movements */
  stiff: {
    type: 'spring' as const,
    stiffness: 400,
    damping: 30,
  },
  /** Slow spring for smooth, fluid motion */
  slow: {
    type: 'spring' as const,
    stiffness: 80,
    damping: 12,
  },
} as const;

/**
 * Default Transition Configuration
 */
export const defaultTransition: Transition = {
  duration: animationTiming.normal,
  ease: animationEasing.smooth,
};

/**
 * Stagger Configuration for List Animations
 */
export const staggerConfig = {
  /** Minimal stagger for subtle effect */
  minimal: 0.05,
  /** Small stagger for quick succession */
  small: 0.1,
  /** Medium stagger for balanced timing */
  medium: 0.15,
  /** Large stagger for dramatic effect */
  large: 0.2,
} as const;

/**
 * Common Animation Variants
 */

/** Fade In/Out Variants */
export const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: animationTiming.normal,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.easeIn,
    },
  },
};

/** Slide Up Variants */
export const slideUpVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Slide Down Variants */
export const slideDownVariants: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Slide Left Variants */
export const slideLeftVariants: Variants = {
  hidden: { opacity: 0, x: 20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Slide Right Variants */
export const slideRightVariants: Variants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Scale Variants */
export const scaleVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Blur Variants (Glassmorphic Effect) */
export const blurVariants: Variants = {
  hidden: { opacity: 0, filter: 'blur(10px)' },
  visible: {
    opacity: 1,
    filter: 'blur(0px)',
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    filter: 'blur(10px)',
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/** Glow Pulse Variants (Cyberpunk Effect) */
export const glowPulseVariants: Variants = {
  initial: {
    boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
  },
  pulse: {
    boxShadow: [
      '0 0 20px rgba(139, 92, 246, 0.3)',
      '0 0 40px rgba(139, 92, 246, 0.6)',
      '0 0 20px rgba(139, 92, 246, 0.3)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: animationEasing.smooth,
    },
  },
};

/** Hover Scale Variants */
export const hoverScaleVariants: Variants = {
  initial: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.smooth,
    },
  },
  tap: {
    scale: 0.95,
    transition: {
      duration: animationTiming.instant,
      ease: animationEasing.sharp,
    },
  },
};

/** Stagger Container Variants */
export const staggerContainerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerConfig.medium,
      delayChildren: 0.1,
    },
  },
};

/** Stagger Item Variants */
export const staggerItemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
};

/**
 * Page Transition Variants
 */
export const pageTransitionVariants: Variants = {
  initial: { opacity: 0, x: -20 },
  enter: {
    opacity: 1,
    x: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/**
 * Modal Backdrop Variants
 */
export const backdropVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.easeOut,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.easeIn,
    },
  },
};

/**
 * Modal Content Variants
 */
export const modalVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: animationTiming.moderate,
      ease: animationEasing.smooth,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.8,
    y: 20,
    transition: {
      duration: animationTiming.fast,
      ease: animationEasing.sharp,
    },
  },
};

/**
 * Shimmer Loading Variants
 */
export const shimmerVariants: Variants = {
  initial: {
    backgroundPosition: '-200% 0',
  },
  animate: {
    backgroundPosition: '200% 0',
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: animationEasing.linear,
    },
  },
};

/**
 * Neon Glow Animation Variants
 */
export const neonGlowVariants: Variants = {
  initial: {
    textShadow: '0 0 10px rgba(139, 92, 246, 0.5)',
  },
  glow: {
    textShadow: [
      '0 0 10px rgba(139, 92, 246, 0.5)',
      '0 0 20px rgba(139, 92, 246, 0.8), 0 0 30px rgba(6, 182, 212, 0.6)',
      '0 0 10px rgba(139, 92, 246, 0.5)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: animationEasing.smooth,
    },
  },
};

/**
 * Export all variant presets
 */
export const animationPresets = {
  fade: fadeVariants,
  slideUp: slideUpVariants,
  slideDown: slideDownVariants,
  slideLeft: slideLeftVariants,
  slideRight: slideRightVariants,
  scale: scaleVariants,
  blur: blurVariants,
  glowPulse: glowPulseVariants,
  hoverScale: hoverScaleVariants,
  staggerContainer: staggerContainerVariants,
  staggerItem: staggerItemVariants,
  pageTransition: pageTransitionVariants,
  backdrop: backdropVariants,
  modal: modalVariants,
  shimmer: shimmerVariants,
  neonGlow: neonGlowVariants,
} as const;

/**
 * Animation Preset Type
 */
export type AnimationPreset = keyof typeof animationPresets;
