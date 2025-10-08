/**
 * NeonButton Component
 *
 * A cyberpunk-themed button with neon glow effects and smooth animations
 * using Framer Motion. Supports multiple variants, sizes, and states.
 *
 * @module NeonButton
 */

import React from 'react';
import { motion, type Variants } from 'framer-motion';
import type { NeonButtonProps, ButtonVariant, ButtonSize } from './NeonButton.types';

/**
 * Framer Motion animation variants for button interactions
 */
const buttonVariants: Variants = {
  idle: {
    scale: 1,
    transition: { duration: 0.2 },
  },
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
  tap: {
    scale: 0.95,
    transition: { duration: 0.1 },
  },
  underline: {
    width: '100%',
    transition: { duration: 0.3, ease: 'easeOut' },
  },
  pulse: {
    boxShadow: [
      '0 0 20px rgba(139, 92, 246, 0.5)',
      '0 0 40px rgba(139, 92, 246, 0.8)',
      '0 0 20px rgba(139, 92, 246, 0.5)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

/**
 * Loading spinner animation
 */
const spinnerVariants: Variants = {
  spin: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

/**
 * Get variant-specific styles
 */
const getVariantStyles = (variant: ButtonVariant): string => {
  const styles = {
    primary: `
      bg-gradient-purple
      text-text-primary
      shadow-glow-purple
      hover:shadow-[0_0_30px_rgba(139,92,246,0.75),0_0_60px_rgba(139,92,246,0.45)]
      border border-primary/30
      hover:border-primary/50
    `,
    secondary: `
      bg-gradient-cyber
      text-text-primary
      shadow-glow-cyan
      hover:shadow-[0_0_30px_rgba(6,182,212,0.75),0_0_60px_rgba(6,182,212,0.45)]
      border border-accent-cyan/30
      hover:border-accent-cyan/50
    `,
    ghost: `
      bg-transparent
      text-primary
      border border-primary/30
      hover:bg-primary/10
      hover:border-primary/50
      shadow-none
      hover:shadow-glow-purple
    `,
    danger: `
      bg-gradient-to-r from-error to-accent-pink
      text-text-primary
      shadow-[0_0_20px_rgba(239,68,68,0.5)]
      hover:shadow-[0_0_30px_rgba(239,68,68,0.75),0_0_60px_rgba(236,72,153,0.45)]
      border border-error/30
      hover:border-error/50
    `,
  };

  return styles[variant].trim().replace(/\s+/g, ' ');
};

/**
 * Get size-specific styles
 */
const getSizeStyles = (size: ButtonSize): string => {
  const styles = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return styles[size];
};

/**
 * NeonButton - An atom-level component with cyberpunk styling and neon effects.
 *
 * @example
 * ```tsx
 * <NeonButton
 *   variant="primary"
 *   onClick={() => console.log('clicked')}
 *   pulse
 * >
 *   Start Analysis
 * </NeonButton>
 * ```
 */
export const NeonButton: React.FC<NeonButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  loading = false,
  fullWidth = false,
  glowIntensity = 'medium',
  pulse = false,
  leftIcon,
  rightIcon,
  type = 'button',
  className = '',
  ariaLabel,
  testId,
}) => {
  /**
   * Base styles for all buttons
   */
  const baseStyles = `
    relative
    inline-flex
    items-center
    justify-center
    gap-2
    font-semibold
    rounded-lg
    transition-all
    duration-normal
    ease-out
    cursor-pointer
    disabled:opacity-50
    disabled:cursor-not-allowed
    disabled:hover:scale-100
    focus:outline-none
    focus:ring-2
    focus:ring-primary
    focus:ring-offset-2
    focus:ring-offset-bg-primary
    overflow-hidden
  `.trim().replace(/\s+/g, ' ');

  /**
   * Combined className
   */
  const combinedClassName = `
    ${baseStyles}
    ${getVariantStyles(variant)}
    ${getSizeStyles(size)}
    ${fullWidth ? 'w-full' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  /**
   * Accessibility props
   */
  const a11yProps = {
    'aria-label': ariaLabel,
    'aria-disabled': disabled || loading,
    'aria-busy': loading,
    'data-testid': testId,
  };

  /**
   * Determine animation state based on props
   */
  const getAnimateState = () => {
    if (pulse && !loading) {
      return 'pulse';
    }
    return 'idle';
  };

  return (
    <motion.button
      type={type}
      className={combinedClassName}
      onClick={disabled || loading ? undefined : onClick}
      disabled={disabled || loading}
      variants={buttonVariants}
      initial="idle"
      animate={getAnimateState()}
      whileHover={disabled || loading ? undefined : "hover"}
      whileTap={disabled || loading ? undefined : "tap"}
      {...a11yProps}
    >
      {/* Left Icon */}
      {leftIcon && !loading && (
        <span className="flex-shrink-0" aria-hidden="true">
          {leftIcon}
        </span>
      )}

      {/* Loading Spinner */}
      {loading && (
        <motion.span
          className="flex-shrink-0 w-5 h-5 border-2 border-text-primary border-t-transparent rounded-full"
          variants={spinnerVariants}
          animate="spin"
          aria-hidden="true"
        />
      )}

      {/* Button Content */}
      <span className="relative z-10">{children}</span>

      {/* Right Icon */}
      {rightIcon && !loading && (
        <span className="flex-shrink-0" aria-hidden="true">
          {rightIcon}
        </span>
      )}

      {/* Animated Glow Overlay on Hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-glow opacity-0"
        whileHover={{ opacity: 0.3 }}
        transition={{ duration: 0.3 }}
        aria-hidden="true"
      />
      <motion.div
        className="absolute bottom-0 left-0 h-0.5 bg-primary"
        initial={{ width: 0 }}
        whileHover="underline"
        variants={buttonVariants}
        aria-hidden="true"
      />
    </motion.button>
  );
};

// Display name for React DevTools
NeonButton.displayName = 'NeonButton';

export default NeonButton;
