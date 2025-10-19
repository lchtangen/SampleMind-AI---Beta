/**
 * FRAMER MOTION GLOBAL CONFIGURATION
 */

import { MotionConfig } from 'framer-motion';

export const motionConfig = {
  // Reduced motion for accessibility
  reducedMotion: 'user',
  
  // Global transition defaults
  transition: {
    duration: 0.3,
    ease: [0.4, 0, 0.2, 1],
  },
} as const;

export const animationFeatures = {
  // Enable/disable features globally
  layout: true,
  animation: true,
  exit: true,
  drag: false, // Enable when needed
  whileInView: true,
} as const;
