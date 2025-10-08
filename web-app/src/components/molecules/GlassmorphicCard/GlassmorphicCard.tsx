/**
 * GlassmorphicCard Component
 *
 * A production-ready glassmorphic card component with neon glow effects
 * for the SampleMind AI application. Features responsive design, full
 * accessibility support, and smooth micro-interactions.
 *
 * @module GlassmorphicCard
 */

import React, { KeyboardEvent as ReactKeyboardEvent } from 'react';
import { GlassmorphicCardProps } from './GlassmorphicCard.types';

/**
 * GlassmorphicCard - A molecule-level component following atomic design principles.
 *
 * Displays content in a glassmorphic card with animated neon glow effects.
 * Supports interactive states with keyboard navigation and hover effects.
 *
 * @example
 * ```tsx
 * <GlassmorphicCard
 *   title="Audio Waveform"
 *   description="View detailed spectral analysis"
 *   icon={<MusicIcon />}
 *   onClick={() => handleCardClick()}
 *   ariaLabel="Open audio waveform analysis panel"
 * />
 * ```
 */
export const GlassmorphicCard: React.FC<GlassmorphicCardProps> = ({
  title,
  description,
  icon,
  onClick,
  className = '',
  ariaLabel,
  testId,
}) => {
  /**
   * Determines if the card is interactive based on onClick prop
   */
  const isInteractive = Boolean(onClick);

  /**
   * Handles keyboard navigation for interactive cards
   * Activates on Enter or Space key press
   */
  const handleKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (isInteractive && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onClick?.();
    }
  };

  /**
   * Base styles for glassmorphism effect
   * - backdrop-blur-xl: Strong blur for glass effect
   * - bg-white/5: Semi-transparent white for dark mode
   * - dark:bg-white/5: Maintains consistency in dark mode
   * - bg-black/5: Semi-transparent black for light mode (if needed)
   * - border: Subtle border with 10% opacity
   * - rounded-xl: 16px border radius from design tokens
   */
  const baseStyles = `
    backdrop-blur-xl
    bg-white/5
    border border-white/10
    rounded-xl
    p-6 md:p-8
    transition-all duration-slow ease-out
    relative
    overflow-hidden
  `.trim().replace(/\s+/g, ' ');

  /**
   * Multi-layer neon glow effect using custom CSS
   * Combines purple primary glow with cyan accent for depth
   */
  const glowStyles = `
    shadow-[0_0_20px_rgba(139,92,246,0.5),0_0_40px_rgba(139,92,246,0.3),0_0_60px_rgba(6,182,212,0.2),0_8px_32px_rgba(0,0,0,0.37)]
  `.trim();

  /**
   * Hover state styles with intensified glow and scale transform
   * Only applied when card is interactive
   */
  const hoverStyles = isInteractive
    ? `
      hover:shadow-[0_0_30px_rgba(139,92,246,0.75),0_0_60px_rgba(139,92,246,0.45),0_0_90px_rgba(6,182,212,0.3),0_8px_32px_rgba(0,0,0,0.37)]
      hover:scale-105
      hover:border-primary/30
      cursor-pointer
      active:scale-[1.02]
    `.trim().replace(/\s+/g, ' ')
    : '';

  /**
   * Focus styles for keyboard navigation
   * Custom focus ring with purple glow
   */
  const focusStyles = isInteractive
    ? `
      focus:outline-none
      focus:ring-2
      focus:ring-primary
      focus:ring-offset-2
      focus:ring-offset-bg-primary
      focus:shadow-[0_0_40px_rgba(139,92,246,0.9),0_0_80px_rgba(139,92,246,0.6)]
    `.trim().replace(/\s+/g, ' ')
    : '';

  /**
   * Combined className string
   */
  const combinedClassName = `
    ${baseStyles}
    ${glowStyles}
    ${hoverStyles}
    ${focusStyles}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  /**
   * Accessibility attributes
   */
  const accessibilityProps = {
    'aria-label': ariaLabel || title,
    'data-testid': testId,
    ...(isInteractive && {
      role: 'button',
      tabIndex: 0,
      'aria-pressed': false,
    }),
  };

  /**
   * Element type based on interactivity
   * Uses semantic HTML - article for display, interactive element for actions
   */
  const ElementType = isInteractive ? 'div' : 'article';

  return (
    <ElementType
      className={combinedClassName}
      onClick={isInteractive ? onClick : undefined}
      onKeyDown={isInteractive ? handleKeyDown : undefined}
      {...accessibilityProps}
    >
      {/* Card Content Container */}
      <div className="relative z-10 flex flex-col gap-4">
        {/* Header Section with Optional Icon */}
        <div className="flex items-start gap-4">
          {icon && (
            <div
              className="flex-shrink-0 text-primary"
              aria-hidden="true"
            >
              {icon}
            </div>
          )}

          <div className="flex-1 min-w-0">
            {/* Title */}
            <h3
              className="
                font-heading
                text-xl md:text-2xl
                font-semibold
                text-text-primary
                mb-2
                leading-tight
              "
            >
              {title}
            </h3>

            {/* Description */}
            <p
              className="
                font-body
                text-base md:text-lg
                text-text-secondary
                leading-relaxed
              "
            >
              {description}
            </p>
          </div>
        </div>

        {/* Interactive Indicator for Clickable Cards */}
        {isInteractive && (
          <div
            className="
              absolute
              bottom-4 right-4
              text-primary
              opacity-50
              group-hover:opacity-100
              transition-opacity
              duration-normal
            "
            aria-hidden="true"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        )}
      </div>

      {/* Background Glow Gradient Effect */}
      <div
        className="
          absolute
          inset-0
          bg-gradient-glow
          opacity-0
          group-hover:opacity-100
          transition-opacity
          duration-slow
          pointer-events-none
        "
        aria-hidden="true"
      />
    </ElementType>
  );
};

// Display name for React DevTools
GlassmorphicCard.displayName = 'GlassmorphicCard';

export default GlassmorphicCard;
