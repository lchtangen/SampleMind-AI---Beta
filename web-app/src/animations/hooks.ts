/**
 * Animation Hooks
 * React hooks for easy integration of Framer Motion animations
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useInView } from 'framer-motion';
import {
  animationPresets,
  AnimationPreset,
  staggerConfig,
  animationTiming,
} from './config';
import type { Variants, Transition } from 'framer-motion';

/**
 * Hook Options
 */
export interface UseAnimationOptions {
  /** Animation preset to use */
  preset?: AnimationPreset;
  /** Custom delay before animation starts */
  delay?: number;
  /** Custom duration for animation */
  duration?: number;
  /** Index for stagger effects */
  index?: number;
  /** Stagger delay multiplier */
  stagger?: number;
  /** Whether to disable the animation */
  disabled?: boolean;
  /** Whether to trigger animation only once */
  once?: boolean;
  /** Amount of element that needs to be visible (0-1) */
  amount?: number;
}

/**
 * useAnimation Hook
 * Returns configured animation variants based on preset
 */
export function useAnimation(options: UseAnimationOptions = {}) {
  const {
    preset = 'fade',
    delay = 0,
    duration,
    index = 0,
    stagger = staggerConfig.medium,
    disabled = false,
  } = options;

  const variants = animationPresets[preset];

  // Calculate stagger delay if index is provided
  const totalDelay = delay + (index * stagger);

  // Create modified variants with custom timing
  const customVariants: Variants = {
    ...variants,
    visible: {
      ...variants.visible,
      transition: {
        ...(variants.visible as any).transition,
        delay: totalDelay,
        ...(duration && { duration }),
      },
    },
  };

  return disabled ? {} : customVariants;
}

/**
 * useScrollAnimation Hook
 * Triggers animation when element scrolls into view
 */
export function useScrollAnimation(options: UseAnimationOptions = {}) {
  const {
    preset = 'slideUp',
    once = true,
    amount = 0.3,
    ...restOptions
  } = options;

  const ref = useRef<HTMLElement>(null);
  const isInView = useInView(ref, { once, amount });
  const variants = useAnimation({ preset, ...restOptions });

  return {
    ref,
    variants,
    initial: 'hidden',
    animate: isInView ? 'visible' : 'hidden',
  };
}

/**
 * useStaggerAnimation Hook
 * For animating lists with stagger effect
 */
export function useStaggerAnimation(options: UseAnimationOptions = {}) {
  const { preset = 'slideUp', stagger = staggerConfig.medium } = options;

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

  return {
    container: containerVariants,
    item: itemVariants,
  };
}

/**
 * useHoverAnimation Hook
 * Returns hover and tap animation states
 */
export function useHoverAnimation(options: { disabled?: boolean } = {}) {
  const { disabled = false } = options;

  if (disabled) {
    return {};
  }

  return {
    whileHover: { scale: 1.05 },
    whileTap: { scale: 0.95 },
    transition: { duration: animationTiming.fast },
  };
}

/**
 * usePageTransition Hook
 * For page/route transitions
 */
export function usePageTransition() {
  return {
    variants: animationPresets.pageTransition,
    initial: 'initial',
    animate: 'enter',
    exit: 'exit',
  };
}

/**
 * useModalAnimation Hook
 * For modal/dialog animations
 */
export function useModalAnimation() {
  return {
    backdrop: {
      variants: animationPresets.backdrop,
      initial: 'hidden',
      animate: 'visible',
      exit: 'exit',
    },
    content: {
      variants: animationPresets.modal,
      initial: 'hidden',
      animate: 'visible',
      exit: 'exit',
    },
  };
}

/**
 * useGlowPulse Hook
 * For cyberpunk glow pulse effects
 */
export function useGlowPulse(options: { disabled?: boolean } = {}) {
  const { disabled = false } = options;

  if (disabled) {
    return {};
  }

  return {
    variants: animationPresets.glowPulse,
    initial: 'initial',
    animate: 'pulse',
  };
}

/**
 * useNeonGlow Hook
 * For neon text glow effects
 */
export function useNeonGlow(options: { disabled?: boolean } = {}) {
  const { disabled = false } = options;

  if (disabled) {
    return {};
  }

  return {
    variants: animationPresets.neonGlow,
    initial: 'initial',
    animate: 'glow',
  };
}

/**
 * useSequenceAnimation Hook
 * For orchestrating multiple animations in sequence
 */
export function useSequenceAnimation(
  steps: Array<{
    preset: AnimationPreset;
    delay: number;
  }>
) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (currentStep >= steps.length) {
      setIsComplete(true);
      return;
    }

    const timer = setTimeout(() => {
      setCurrentStep((prev) => prev + 1);
    }, steps[currentStep].delay * 1000);

    return () => clearTimeout(timer);
  }, [currentStep, steps]);

  const getCurrentVariants = useCallback(() => {
    if (isComplete || currentStep >= steps.length) {
      return animationPresets[steps[steps.length - 1].preset];
    }
    return animationPresets[steps[currentStep].preset];
  }, [currentStep, isComplete, steps]);

  return {
    variants: getCurrentVariants(),
    isComplete,
    currentStep,
  };
}

/**
 * useReducedMotion Hook
 * Detects user's motion preference
 */
export function useReducedMotion() {
  const [shouldReduceMotion, setShouldReduceMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setShouldReduceMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setShouldReduceMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return shouldReduceMotion;
}

/**
 * useAnimationControls Hook
 * Manual control over animations
 */
export function useAnimationControls() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const play = useCallback(() => {
    setIsPlaying(true);
    setIsPaused(false);
  }, []);

  const pause = useCallback(() => {
    setIsPaused(true);
  }, []);

  const resume = useCallback(() => {
    setIsPaused(false);
  }, []);

  const reset = useCallback(() => {
    setIsPlaying(false);
    setIsPaused(false);
  }, []);

  return {
    isPlaying,
    isPaused,
    play,
    pause,
    resume,
    reset,
  };
}

/**
 * useFadeIn Hook
 * Simple fade in animation
 */
export function useFadeIn(options: UseAnimationOptions = {}) {
  return useAnimation({ preset: 'fade', ...options });
}

/**
 * useSlideIn Hook
 * Slide in animation with configurable direction
 */
export function useSlideIn(
  direction: 'up' | 'down' | 'left' | 'right' = 'up',
  options: UseAnimationOptions = {}
) {
  const presetMap: Record<typeof direction, AnimationPreset> = {
    up: 'slideUp',
    down: 'slideDown',
    left: 'slideLeft',
    right: 'slideRight',
  };

  return useAnimation({ preset: presetMap[direction], ...options });
}

/**
 * useScale Hook
 * Scale animation
 */
export function useScale(options: UseAnimationOptions = {}) {
  return useAnimation({ preset: 'scale', ...options });
}

/**
 * useBlur Hook
 * Blur animation (glassmorphic effect)
 */
export function useBlur(options: UseAnimationOptions = {}) {
  return useAnimation({ preset: 'blur', ...options });
}

/**
 * useParallax Hook
 * Simple parallax scrolling effect
 */
export function useParallax(speed: number = 0.5) {
  const [offset, setOffset] = useState(0);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      const scrolled = window.scrollY;
      const elementTop = rect.top + scrolled;
      const parallaxOffset = (scrolled - elementTop) * speed;
      setOffset(parallaxOffset);
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial calculation

    return () => window.removeEventListener('scroll', handleScroll);
  }, [speed]);

  return {
    ref,
    style: {
      transform: `translateY(${offset}px)`,
    },
  };
}

/**
 * Export animation configuration utilities
 */
export { animationPresets, animationTiming, staggerConfig } from './config';
export type { AnimationPreset } from './config';
