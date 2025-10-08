/**
 * HolographicPanel Component
 *
 * An organism-level component combining multiple glassmorphic elements
 * into a cohesive panel with headers, sections, and neon effects.
 *
 * @module HolographicPanel
 */

import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { NeonDivider } from '../../atoms/NeonDivider/NeonDivider';
import { GlowingBadge } from '../../atoms/GlowingBadge/GlowingBadge';

/**
 * Props for panel header
 */
export interface PanelHeaderProps {
  title: string;
  subtitle?: string;
  badge?: ReactNode;
  actions?: ReactNode;
}

/**
 * Props for panel sections
 */
export interface PanelSection {
  id: string;
  title?: string;
  content: ReactNode;
}

/**
 * Props for the HolographicPanel component
 */
export interface HolographicPanelProps {
  /**
   * Panel header configuration
   */
  header?: PanelHeaderProps;

  /**
   * Panel sections to display
   */
  sections?: PanelSection[];

  /**
   * Direct children content (alternative to sections)
   */
  children?: ReactNode;

  /**
   * Footer content
   */
  footer?: ReactNode;

  /**
   * Enable animated entrance
   */
  animated?: boolean;

  /**
   * Panel variant style
   */
  variant?: 'default' | 'elevated' | 'bordered';

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Test ID
   */
  testId?: string;
}

/**
 * Get variant-specific styles
 */
const getVariantStyles = (variant: 'default' | 'elevated' | 'bordered'): string => {
  const styles = {
    default: 'border border-white/10',
    elevated: 'border border-primary/30 shadow-glow-purple',
    bordered: 'border-2 border-primary/50 shadow-[0_0_30px_rgba(139,92,246,0.6)]',
  };

  return styles[variant];
};

/**
 * HolographicPanel - Complex organism-level component with multiple sections.
 *
 * @example
 * ```tsx
 * <HolographicPanel
 *   header={{
 *     title: "Audio Analysis",
 *     subtitle: "Real-time processing",
 *     badge: <GlowingBadge variant="success">Active</GlowingBadge>
 *   }}
 *   sections={[
 *     { id: '1', title: 'Waveform', content: <WaveformView /> },
 *     { id: '2', title: 'Spectrum', content: <SpectrumView /> }
 *   ]}
 * />
 * ```
 */
export const HolographicPanel: React.FC<HolographicPanelProps> = ({
  header,
  sections,
  children,
  footer,
  animated = true,
  variant = 'default',
  className = '',
  testId,
}) => {
  const baseStyles = `
    relative
    backdrop-blur-xl
    bg-white/5
    rounded-xl
    overflow-hidden
    ${getVariantStyles(variant)}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  const content = (
    <>
      {/* Header Section */}
      {header && (
        <div className="p-6 md:p-8">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h2 className="text-2xl md:text-3xl font-bold text-text-primary">
                  {header.title}
                </h2>
                {header.badge}
              </div>
              {header.subtitle && (
                <p className="text-text-secondary text-base md:text-lg">
                  {header.subtitle}
                </p>
              )}
            </div>

            {/* Header Actions */}
            {header.actions && (
              <div className="flex-shrink-0">
                {header.actions}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Divider after header */}
      {header && (sections || children) && (
        <NeonDivider gradient="cyber" animated />
      )}

      {/* Content Sections */}
      {sections ? (
        <div className="divide-y divide-white/10">
          {sections.map((section, index) => (
            <motion.div
              key={section.id}
              className="p-6 md:p-8"
              initial={animated ? { opacity: 0, x: -20 } : false}
              animate={animated ? { opacity: 1, x: 0 } : false}
              transition={{
                duration: 0.4,
                delay: index * 0.1,
              }}
            >
              {section.title && (
                <h3 className="text-xl font-semibold text-text-primary mb-4">
                  {section.title}
                </h3>
              )}
              <div className="text-text-secondary">
                {section.content}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="p-6 md:p-8">
          {children}
        </div>
      )}

      {/* Footer Section */}
      {footer && (
        <>
          <NeonDivider gradient="purple" animated />
          <div className="p-6 md:p-8 bg-white/5">
            {footer}
          </div>
        </>
      )}

      {/* Holographic Glow Overlay */}
      <div
        className="
          absolute
          inset-0
          bg-gradient-glow
          opacity-10
          pointer-events-none
        "
        aria-hidden="true"
      />
    </>
  );

  if (animated) {
    return (
      <motion.div
        className={baseStyles}
        data-testid={testId}
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{
          duration: 0.5,
        }}
      >
        {content}
      </motion.div>
    );
  }

  return (
    <div className={baseStyles} data-testid={testId}>
      {content}
    </div>
  );
};

HolographicPanel.displayName = 'HolographicPanel';

export default HolographicPanel;
