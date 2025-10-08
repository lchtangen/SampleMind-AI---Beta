/**
 * ScrollReveal Component
 * Triggers animations when elements scroll into view
 * Uses Framer Motion's useInView (wraps Intersection Observer)
 */

import React, { useRef } from 'react';
import { motion, useInView, type Variants } from 'framer-motion';
import { animationPresets, type AnimationPreset, useAnimation } from '@/animations';

export interface ScrollRevealProps {
  /** Child elements to animate */
  children: React.ReactNode;
  /** Animation preset to use */
  preset?: AnimationPreset;
  /** Custom delay before animation starts */
  delay?: number;
  /** Custom duration for animation */
  duration?: number;
  /** Trigger animation only once (default: true) */
  once?: boolean;
  /** Amount of element that needs to be visible (0-1, default: 0.3) */
  amount?: number;
  /** Custom margin for triggering animation */
  margin?: string;
  /** Custom className */
  className?: string;
  /** Custom variants (overrides preset) */
  variants?: Variants;
  /** Whether to disable the animation */
  disabled?: boolean;
}

/**
 * ScrollReveal Component
 * Animates children when they scroll into view
 *
 * @example
 * ```tsx
 * <ScrollReveal preset="slideUp">
 *   <h1>This will slide up when scrolled into view</h1>
 * </ScrollReveal>
 * ```
 */
export const ScrollReveal: React.FC<ScrollRevealProps> = ({
  children,
  preset = 'slideUp',
  delay = 0,
  duration,
  once = true,
  amount = 0.3,
  className = '',
  variants: customVariants,
  disabled = false,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, amount });

  // Get animation variants
  const defaultVariants = useAnimation({ preset, delay, duration, disabled });
  const variants = customVariants || defaultVariants;

  if (disabled) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div
      ref={ref}
      variants={variants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
    >
      {children}
    </motion.div>
  );
};

ScrollReveal.displayName = 'ScrollReveal';

/**
 * ScrollRevealList Component
 * Reveals list items with stagger effect as they scroll into view
 */
export interface ScrollRevealListProps {
  /** Child elements (array of items) */
  children: React.ReactNode;
  /** Animation preset for items */
  preset?: AnimationPreset;
  /** Stagger delay between items */
  stagger?: number;
  /** Trigger animation only once */
  once?: boolean;
  /** Amount visible to trigger */
  amount?: number;
  /** Custom className for container */
  className?: string;
  /** Custom className for items */
  itemClassName?: string;
}

export const ScrollRevealList: React.FC<ScrollRevealListProps> = ({
  children,
  preset = 'slideUp',
  stagger = 0.1,
  once = true,
  amount = 0.2,
  className = '',
  itemClassName = '',
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, amount });

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: stagger,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = animationPresets[preset];

  return (
    <motion.div
      ref={ref}
      variants={containerVariants}
      initial="hidden"
      animate={isInView ? 'visible' : 'hidden'}
      className={className}
    >
      {React.Children.map(children, (child, index) => (
        <motion.div key={index} variants={itemVariants} className={itemClassName}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};

ScrollRevealList.displayName = 'ScrollRevealList';
