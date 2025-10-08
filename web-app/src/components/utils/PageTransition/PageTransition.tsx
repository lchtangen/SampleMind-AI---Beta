/**
 * PageTransition Component
 * Animated page transitions for route changes
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { pageTransitionVariants, animationTiming, animationEasing } from '@/animations';

export interface PageTransitionProps {
  /** Child elements to animate */
  children: React.ReactNode;
  /** Unique key for AnimatePresence (typically route path) */
  routeKey: string;
  /** Transition mode */
  mode?: 'fade' | 'slide' | 'scale' | 'slideUp' | 'slideDown';
  /** Custom duration override */
  duration?: number;
  /** Custom className */
  className?: string;
}

/**
 * PageTransition Component
 * Wraps page content with smooth transition animations
 */
export const PageTransition: React.FC<PageTransitionProps> = ({
  children,
  routeKey,
  mode = 'slide',
  duration = animationTiming.moderate,
  className = '',
}) => {
  // Define variants based on mode
  const getVariants = () => {
    switch (mode) {
      case 'fade':
        return {
          initial: { opacity: 0 },
          enter: { opacity: 1 },
          exit: { opacity: 0 },
        };
      case 'slide':
        return {
          initial: { opacity: 0, x: -20 },
          enter: { opacity: 1, x: 0 },
          exit: { opacity: 0, x: 20 },
        };
      case 'slideUp':
        return {
          initial: { opacity: 0, y: 20 },
          enter: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: -20 },
        };
      case 'slideDown':
        return {
          initial: { opacity: 0, y: -20 },
          enter: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: 20 },
        };
      case 'scale':
        return {
          initial: { opacity: 0, scale: 0.95 },
          enter: { opacity: 1, scale: 1 },
          exit: { opacity: 0, scale: 1.05 },
        };
      default:
        return pageTransitionVariants;
    }
  };

  const variants = getVariants();

  return (
    <AnimatePresence mode="wait" initial={true}>
      <motion.div
        key={routeKey}
        variants={variants}
        initial="initial"
        animate="enter"
        exit="exit"
        transition={{
          duration,
          ease: animationEasing.smooth,
        }}
        className={className}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

PageTransition.displayName = 'PageTransition';
