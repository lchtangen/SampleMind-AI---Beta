/**
 * CyberpunkInput Component Types
 *
 * Type definitions for the cyberpunk-themed input field component
 * with animated borders and focus state effects.
 *
 * @module CyberpunkInput.types
 */

import { ChangeEvent, FocusEvent, InputHTMLAttributes, ReactNode } from 'react';

/**
 * Input validation states
 */
export type InputState = 'default' | 'success' | 'error' | 'warning';

/**
 * Input size variants
 */
export type InputSize = 'sm' | 'md' | 'lg';

/**
 * Props for the CyberpunkInput component.
 *
 * @interface CyberpunkInputProps
 *
 * @example
 * ```tsx
 * <CyberpunkInput
 *   label="Email Address"
 *   placeholder="Enter your email"
 *   state="default"
 *   onChange={(e) => setValue(e.target.value)}
 * />
 * ```
 */
export interface CyberpunkInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /**
   * Input label text.
   *
   * @optional
   * @type {string}
   */
  label?: string;

  /**
   * Helper text displayed below the input.
   *
   * @optional
   * @type {string}
   */
  helperText?: string;

  /**
   * Error message displayed when state is 'error'.
   *
   * @optional
   * @type {string}
   */
  errorMessage?: string;

  /**
   * Error message to display.
   *
   * @optional
   * @type {string}
   */
  error?: string;

  /**
   * Validation state of the input.
   *
   * @optional
   * @default 'default'
   * @type {InputState}
   */
  state?: InputState;

  /**
   * Size variant of the input.
   *
   * @optional
   * @default 'md'
   * @type {InputSize}
   */
  size?: InputSize;

  /**
   * Icon to display at the start of the input.
   *
   * @optional
   * @type {ReactNode}
   */
  leftIcon?: ReactNode;

  /**
   * Icon or element to display at the end of the input.
   *
   * @optional
   * @type {ReactNode}
   */
  rightElement?: ReactNode;

  /**
   * Enable animated border glow on focus.
   *
   * @optional
   * @default true
   * @type {boolean}
   */
  animatedBorder?: boolean;

  /**
   * Full width input.
   *
   * @optional
   * @default false
   * @type {boolean}
   */
  fullWidth?: boolean;

  /**
   * Change handler function.
   *
   * @optional
   * @type {(event: ChangeEvent<HTMLInputElement>) => void}
   */
  onChange?: (event: ChangeEvent<HTMLInputElement>) => void;

  /**
   * Focus handler function.
   *
   * @optional
   * @type {(event: FocusEvent<HTMLInputElement>) => void}
   */
  onFocus?: (event: FocusEvent<HTMLInputElement>) => void;

  /**
   * Blur handler function.
   *
   * @optional
   * @type {(event: FocusEvent<HTMLInputElement>) => void}
   */
  onBlur?: (event: FocusEvent<HTMLInputElement>) => void;

  /**
   * Additional CSS classes for the input element.
   *
   * @optional
   * @type {string}
   */
  className?: string;

  /**
   * Additional CSS classes for the container.
   *
   * @optional
   * @type {string}
   */
  containerClassName?: string;

  /**
   * Test ID for component testing.
   *
   * @optional
   * @type {string}
   */
  testId?: string;
}

/**
 * Re-export for convenience.
 */
export type { ChangeEvent, FocusEvent, ReactNode };

