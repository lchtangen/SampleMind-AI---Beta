/**
 * STAGGER ANIMATION UTILITIES
 * Helper functions for staggered animations
 */

import { Variants } from 'framer-motion';

/**
 * Create stagger container variant
 */
export const createStaggerContainer = (
  staggerDelay: number = 0.1,
  delayChildren: number = 0
): Variants => ({
  initial: {},
  animate: {
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
  exit: {
    transition: {
      staggerChildren: staggerDelay / 2,
      staggerDirection: -1,
    },
  },
});

/**
 * Create stagger item variant
 */
export const createStaggerItem = (
  direction: 'up' | 'down' | 'left' | 'right' = 'up',
  distance: number = 10
): Variants => {
  const directions = {
    up: { y: distance, x: 0 },
    down: { y: -distance, x: 0 },
    left: { x: distance, y: 0 },
    right: { x: -distance, y: 0 },
  };

  return {
    initial: {
      ...directions[direction],
      opacity: 0,
    },
    animate: {
      x: 0,
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 200,
        damping: 20,
      },
    },
    exit: {
      ...directions[direction],
      opacity: 0,
      transition: {
        duration: 0.2,
      },
    },
  };
};

/**
 * Get stagger delay for individual items
 */
export const getStaggerDelay = (index: number, baseDelay: number = 0.05) => index * baseDelay;
