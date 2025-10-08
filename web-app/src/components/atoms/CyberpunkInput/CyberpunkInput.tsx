/**
 * CyberpunkInput Component
 *
 * A cyberpunk-themed input field with animated borders, focus effects,
 * and validation state indicators using Framer Motion.
 *
 * @module CyberpunkInput
 */

import React, { useState } from 'react';
import { motion, type Variants } from 'framer-motion';
import type { CyberpunkInputProps, InputState, InputSize } from './CyberpunkInput.types';

/**
 * Border animation variants
 */
const borderVariants: Variants = {
  unfocused: {
    opacity: 0.3,
    scale: 1,
    transition: { duration: 0.2 },
  },
  focused: {
    opacity: 1,
    scale: 1.02,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

/**
 * Label animation variants
 */
const labelVariants: Variants = {
  default: {
    y: 0,
    scale: 1,
    color: '#94A3B8',
  },
  focused: {
    y: -24,
    scale: 0.85,
    color: '#8B5CF6',
    transition: { duration: 0.2 },
  },
};

/**
 * Get state-specific border colors
 */
const getStateStyles = (state: InputState): string => {
  const styles = {
    default: 'border-white/10 focus:border-primary',
    success: 'border-success/50 focus:border-success',
    error: 'border-error/50 focus:border-error',
    warning: 'border-warning/50 focus:border-warning',
  };

  return styles[state];
};

/**
 * Get state-specific glow colors
 */
const getStateGlow = (state: InputState): string => {
  const glows = {
    default: 'focus:shadow-[0_0_20px_rgba(139,92,246,0.5)]',
    success: 'focus:shadow-[0_0_20px_rgba(16,185,129,0.5)]',
    error: 'focus:shadow-[0_0_20px_rgba(239,68,68,0.5)]',
    warning: 'focus:shadow-[0_0_20px_rgba(245,158,11,0.5)]',
  };

  return glows[state];
};

/**
 * Get size-specific styles
 */
const getSizeStyles = (size: InputSize): string => {
  const styles = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  };

  return styles[size];
};

/**
 * CyberpunkInput - An atom-level input component with animated cyberpunk styling.
 *
 * @example
 * ```tsx
 * <CyberpunkInput
 *   label="Email"
 *   placeholder="Enter your email"
 *   state="default"
 *   onChange={(e) => setValue(e.target.value)}
 * />
 * ```
 */
export const CyberpunkInput: React.FC<CyberpunkInputProps> = ({
  label,
  helperText,
  errorMessage,
  error,
  state = 'default',
  size = 'md',
  leftIcon,
  rightElement,
  animatedBorder = true,
  fullWidth = false,
  onChange,
  onFocus,
  onBlur,
  className = '',
  containerClassName = '',
  testId,
  disabled,
  ...inputProps
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasValue, setHasValue] = useState(false);

  /**
   * Handle focus event
   */
  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    onFocus?.(e);
  };

  /**
   * Handle blur event
   */
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    setHasValue(e.target.value.length > 0);
    onBlur?.(e);
  };

  /**
   * Handle change event
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setHasValue(e.target.value.length > 0);
    onChange?.(e);
  };

  /**
   * Base container styles
   */
  const containerStyles = `
    relative
    ${fullWidth ? 'w-full' : ''}
    ${containerClassName}
  `.trim().replace(/\s+/g, ' ');

  /**
   * Base input styles
   */
  const inputStyles = `
    w-full
    bg-white/5
    backdrop-blur-md
    border
    rounded-lg
    text-text-primary
    placeholder-text-muted
    transition-all
    duration-normal
    ease-out
    focus:outline-none
    disabled:opacity-50
    disabled:cursor-not-allowed
    ${getSizeStyles(size)}
    ${getStateStyles(state)}
    ${getStateGlow(state)}
    ${leftIcon ? 'pl-10' : ''}
    ${rightElement ? 'pr-10' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  /**
   * Display error or helper text
   */
  const feedbackText = state === 'error' ? error || errorMessage : helperText;

  return (
    <div className={containerStyles}>
      {/* Floating Label */}
      {label && (
        <motion.label
          className="absolute left-4 pointer-events-none font-body"
          variants={labelVariants}
          animate={isFocused || hasValue ? 'focused' : 'default'}
          htmlFor={testId}
        >
          {label}
        </motion.label>
      )}

      {/* Input Container with Animated Border */}
      <div className="relative">
        {/* Animated Border Glow */}
        {animatedBorder && (
          <motion.div
            className="absolute inset-0 rounded-lg border-2 border-primary pointer-events-none"
            variants={borderVariants}
            animate={isFocused ? 'focused' : 'unfocused'}
            aria-hidden="true"
          />
        )}

        {/* Left Icon */}
        {leftIcon && (
          <div
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary"
            aria-hidden="true"
          >
            {leftIcon}
          </div>
        )}

        {/* Input Element */}
        <input
          {...inputProps}
          id={testId}
          className={inputStyles}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onChange={handleChange}
          disabled={disabled}
          data-testid={testId}
          aria-invalid={state === 'error'}
          aria-describedby={feedbackText ? `${testId}-feedback` : undefined}
        />

        {/* Right Element */}
        {rightElement && (
          <div
            className="absolute right-3 top-1/2 -translate-y-1/2"
            aria-hidden="true"
          >
            {rightElement}
          </div>
        )}
      </div>

      {/* Helper/Error Text */}
      {feedbackText && (
        <motion.p
          id={`${testId}-feedback`}
          className={`
            mt-2
            text-sm
            ${state === 'error' ? 'text-error' : 'text-text-secondary'}
            ${state === 'warning' ? 'text-warning' : ''}
            ${state === 'success' ? 'text-success' : ''}
          `.trim().replace(/\s+/g, ' ')}
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          {feedbackText}
        </motion.p>
      )}
    </div>
  );
};

// Display name for React DevTools
CyberpunkInput.displayName = 'CyberpunkInput';

export default CyberpunkInput;
