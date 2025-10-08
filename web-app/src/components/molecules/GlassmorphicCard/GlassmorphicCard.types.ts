/**
 * GlassmorphicCard Component Types
 *
 * Type definitions for the production-ready glassmorphic card component
 * with neon glow effects for SampleMind AI.
 *
 * @module GlassmorphicCard.types
 */

import { ReactNode, MouseEvent, KeyboardEvent } from 'react';

/**
 * Props for the GlassmorphicCard component.
 *
 * @interface GlassmorphicCardProps
 *
 * @example
 * ```tsx
 * <GlassmorphicCard
 *   title="Audio Analysis"
 *   description="View detailed waveform analysis"
 *   icon={<AudioIcon />}
 *   onClick={() => console.log('Card clicked')}
 *   ariaLabel="Open audio analysis panel"
 * />
 * ```
 */
export interface GlassmorphicCardProps {
  /**
   * The main title text displayed in the card header.
   *
   * @required
   * @type {string}
   */
  title: string;

  /**
   * The description or content text displayed below the title.
   *
   * @required
   * @type {string}
   */
  description: string;

  /**
   * Optional icon component or element displayed before the title.
   * Can be any React node (component, SVG, image, etc.).
   *
   * @optional
   * @type {ReactNode}
   *
   * @example
   * ```tsx
   * icon={<MusicIcon className="w-6 h-6" />}
   * ```
   */
  icon?: ReactNode;

  /**
   * Click handler function called when the card is clicked or activated via keyboard.
   * If provided, the card becomes interactive with hover effects.
   *
   * @optional
   * @type {() => void}
   *
   * @example
   * ```tsx
   * onClick={() => navigateToDetail()}
   * ```
   */
  onClick?: () => void;

  /**
   * Additional CSS classes to apply to the card container.
   * Useful for custom spacing, sizing, or layout adjustments.
   *
   * @optional
   * @type {string}
   *
   * @example
   * ```tsx
   * className="w-full max-w-md"
   * ```
   */
  className?: string;

  /**
   * ARIA label for accessibility.
   * If not provided, the title will be used as the accessible name.
   *
   * @optional
   * @type {string}
   *
   * @example
   * ```tsx
   * ariaLabel="Open audio waveform details in new panel"
   * ```
   */
  ariaLabel?: string;

  /**
   * Optional test ID for component testing.
   *
   * @optional
   * @type {string}
   *
   * @example
   * ```tsx
   * testId="audio-card-123"
   * ```
   */
  testId?: string;
}

/**
 * Internal event handler types for improved type safety.
 */
export type CardClickHandler = (event: MouseEvent<HTMLElement> | KeyboardEvent<HTMLElement>) => void;

/**
 * Card variant types for potential future expansion.
 * Currently using default glassmorphic style.
 */
export type CardVariant = 'default' | 'compact' | 'expanded';

/**
 * Re-export for convenience.
 */
export type { ReactNode };
