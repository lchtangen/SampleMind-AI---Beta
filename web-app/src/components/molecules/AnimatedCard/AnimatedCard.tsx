/**
 * AnimatedCard Component
 *
 * Extends the GlassmorphicCard component with Framer Motion entry animations.
 * Provides fade-in, slide-up, and stagger effects for card lists.
 *
 * @module AnimatedCard
 */

import React from 'react';
import { motion } from 'framer-motion';
import { GlassmorphicCard, type GlassmorphicCardProps } from '../GlassmorphicCard';

/**
 * Animation preset types
 */
export type AnimationPreset = 'fadeIn' | 'slideUp' | 'slideRight' | 'scale' | 'blur';

/**
 * Props extending GlassmorphicCardProps with animation options
 */
export interface AnimatedCardProps extends GlassmorphicCardProps {
  /**
   * Animation preset to use on entry.
   *
   * @optional
   * @default 'fadeIn'
   */
  animationPreset?: AnimationPreset;

  /**
   * Delay before animation starts (in seconds).
   *
   * @optional
   * @default 0
   */
  delay?: number;

  /**
   * Duration of the animation (in seconds).
   *
   * @optional
   * @default 0.5
   */
  duration?: number;

  /**
   * Index for stagger animations in lists.
   *
   * @optional
   */
  index?: number;

  /**
   * Disable animations.
   *
   * @optional
   * @default false
   */
  disableAnimation?: boolean;
}

/**
 * Animation variant configurations
 */
const animationVariants = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
  },
  slideUp: {
    initial: { opacity: 0, y: 30 },
    animate: { opacity: 1, y: 0 },
  },
  slideRight: {
    initial: { opacity: 0, x: -30 },
    animate: { opacity: 1, x: 0 },
  },
  scale: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
  },
  blur: {
    initial: { opacity: 0, filter: 'blur(10px)' },
    animate: { opacity: 1, filter: 'blur(0px)' },
  },
};

/**
 * AnimatedCard - Glassmorphic card with entry animations.
 *
 * @example
 * ```tsx
 * <AnimatedCard
 *   title="Audio File"
 *   description="Analyzed audio"
 *   animationPreset="slideUp"
 *   delay={0.2}
 * />
 * ```
 *
 * @example
 * ```tsx
 * // In a list with stagger effect
 * {items.map((item, index) => (
 *   <AnimatedCard
 *     key={item.id}
 *     title={item.title}
 *     description={item.description}
 *     animationPreset="slideUp"
 *     index={index}
 *   />
 * ))}
 * ```
 */
export const AnimatedCard: React.FC<AnimatedCardProps> = ({
  animationPreset = 'fadeIn',
  delay = 0,
  duration = 0.5,
  index,
  disableAnimation = false,
  ...glassmorphicCardProps
}) => {
  /**
   * Calculate stagger delay if index is provided
   */
  const staggerDelay = index !== undefined ? index * 0.1 : 0;
  const totalDelay = delay + staggerDelay;

  /**
   * Get animation config for preset
   */
  const animationConfig = animationVariants[animationPreset];

  if (disableAnimation) {
    return <GlassmorphicCard {...glassmorphicCardProps} />;
  }

  return (
    <motion.div
      initial={animationConfig.initial}
      animate={animationConfig.animate}
      transition={{
        duration,
        delay: totalDelay,
        ease: [0.4, 0, 0.2, 1], // Custom easing
      }}
      style={{ width: '100%' }}
    >
      <GlassmorphicCard {...glassmorphicCardProps} />
    </motion.div>
  );
};

AnimatedCard.displayName = 'AnimatedCard';

export default AnimatedCard;
