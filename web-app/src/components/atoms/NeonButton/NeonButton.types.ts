/**
 * NeonButton Component Types
 *
 * Type definitions for the cyberpunk-themed neon button component
 * with glowing hover effects and pulse animations using Framer Motion.
 *
 * @module NeonButton.types
 */

import { ReactNode, MouseEvent, KeyboardEvent } from 'react';

/**
 * Button visual variants following cyberpunk aesthetic
 */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

/**
 * Button size options following 8pt grid
 */
export type ButtonSize = 'sm' | 'md' | 'lg';

/**
 * Props for the NeonButton component.
 *
 * @interface NeonButtonProps
 *
 * @example
 * ```tsx
 * <NeonButton
 *   variant="primary"
 *   size="md"
 *   onClick={() => handleClick()}
 *   glowIntensity="high"
 * >
 *   Click Me
 * </NeonButton>
 * ```
 */
export interface NeonButtonProps {
  /**
   * Button content (text, icons, or components).
   *
   * @required
   * @type {ReactNode}
   */
  children: ReactNode;

  /**
   * Visual variant of the button.
   *
   * @optional
   * @default 'primary'
   * @type {ButtonVariant}
   */
  variant?: ButtonVariant;

  /**
   * Size of the button following 8pt grid system.
   *
   * @optional
   * @default 'md'
   * @type {ButtonSize}
   */
  size?: ButtonSize;

  /**
   * Click handler function.
   *
   * @optional
   * @type {(event: MouseEvent<HTMLButtonElement>) => void}
   */
  onClick?: (event: MouseEvent<HTMLButtonElement>) => void;

  /**
   * Disabled state of the button.
   *
   * @optional
   * @default false
   * @type {boolean}
   */
  disabled?: boolean;

  /**
   * Loading state with pulse animation.
   *
   * @optional
   * @default false
   * @type {boolean}
   */
  loading?: boolean;

  /**
   * Full width button.
   *
   * @optional
   * @default false
   * @type {boolean}
   */
  fullWidth?: boolean;

  /**
   * Intensity of neon glow effect.
   *
   * @optional
   * @default 'medium'
   * @type {'low' | 'medium' | 'high'}
   */
  glowIntensity?: 'low' | 'medium' | 'high';

  /**
   * Enable pulse animation on idle.
   *
   * @optional
   * @default false
   * @type {boolean}
   */
  pulse?: boolean;

  /**
   * Icon to display before children.
   *
   * @optional
   * @type {ReactNode}
   */
  leftIcon?: ReactNode;

  /**
   * Icon to display after children.
   *
   * @optional
   * @type {ReactNode}
   */
  rightIcon?: ReactNode;

  /**
   * HTML button type.
   *
   * @optional
   * @default 'button'
   * @type {'button' | 'submit' | 'reset'}
   */
  type?: 'button' | 'submit' | 'reset';

  /**
   * Additional CSS classes.
   *
   * @optional
   * @type {string}
   */
  className?: string;

  /**
   * ARIA label for accessibility.
   *
   * @optional
   * @type {string}
   */
  ariaLabel?: string;

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
export type { ReactNode };
