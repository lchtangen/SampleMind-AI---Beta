/**
 * Animation System
 * Central export for all animation utilities, hooks, and configurations
 */

// Core configuration
export {
  animationTiming,
  animationEasing,
  springConfigs,
  defaultTransition,
  staggerConfig,
  animationPresets,
  fadeVariants,
  slideUpVariants,
  slideDownVariants,
  slideLeftVariants,
  slideRightVariants,
  scaleVariants,
  blurVariants,
  glowPulseVariants,
  hoverScaleVariants,
  staggerContainerVariants,
  staggerItemVariants,
  pageTransitionVariants,
  backdropVariants,
  modalVariants,
  shimmerVariants,
  neonGlowVariants,
} from './config';

export type { AnimationPreset } from './config';

// Animation hooks
export {
  useAnimation,
  useScrollAnimation,
  useStaggerAnimation,
  useHoverAnimation,
  usePageTransition,
  useModalAnimation,
  useGlowPulse,
  useNeonGlow,
  useSequenceAnimation,
  useReducedMotion,
  useAnimationControls,
  useFadeIn,
  useSlideIn,
  useScale,
  useBlur,
  useParallax,
} from './hooks';

export type { UseAnimationOptions } from './hooks';
