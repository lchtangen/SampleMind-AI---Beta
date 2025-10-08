/**
 * StatCard Component
 *
 * A cyberpunk-themed statistics card with animated counters,
 * trend indicators, and glassmorphic effects for dashboards.
 *
 * @module StatCard
 */

import React, { useEffect, useState } from 'react';
import { motion, useSpring, useTransform, useMotionValue } from 'framer-motion';
import { GlowingBadge } from '../../atoms/GlowingBadge/GlowingBadge';

/**
 * Trend direction
 */
export type TrendDirection = 'up' | 'down' | 'neutral';

/**
 * Props for the StatCard component
 */
export interface StatCardProps {
  /**
   * Stat label/title
   */
  label: string;

  /**
   * Current value to display
   */
  value: number;

  /**
   * Previous value for trend calculation
   */
  previousValue?: number;

  /**
   * Metric unit (e.g., '%', 'ms', 'files')
   */
  unit?: string;

  /**
   * Icon to display
   */
  icon?: React.ReactNode;

  /**
   * Trend direction
   */
  trend?: TrendDirection;

  /**
   * Trend percentage
   */
  trendPercentage?: number;

  /**
   * Enable animated counter
   */
  animateValue?: boolean;

  /**
   * Formatting function for value display
   */
  formatValue?: (value: number) => string;

  /**
   * Click handler
   */
  onClick?: () => void;

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
 * Get trend icon and color
 */
const getTrendInfo = (trend: TrendDirection) => {
  const configs = {
    up: {
      icon: '↗',
      color: 'success',
      label: 'increased',
    },
    down: {
      icon: '↘',
      color: 'error',
      label: 'decreased',
    },
    neutral: {
      icon: '→',
      color: 'info',
      label: 'unchanged',
    },
  };

  return configs[trend];
};

/**
 * Animated Counter Component
 */
const AnimatedCounter: React.FC<{
  value: number;
  unit?: string;
  formatValue?: (value: number) => string;
}> = ({ value, unit, formatValue }) => {
  const motionValue = useMotionValue(0);
  const rounded = useTransform(motionValue, (latest) => Math.round(latest));
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const unsubscribe = rounded.on('change', (latest) => {
      setDisplayValue(latest);
    });

    motionValue.set(value);

    return () => unsubscribe();
  }, [value, motionValue, rounded]);

  return (
    <div className="text-4xl md:text-5xl font-bold text-text-primary">
      {formatValue ? formatValue(displayValue) : displayValue.toLocaleString()}
      {unit && <span className="text-2xl text-text-secondary ml-1">{unit}</span>}
    </div>
  );
};

/**
 * StatCard - Dashboard statistics card with animated counters.
 *
 * @example
 * ```tsx
 * <StatCard
 *   label="Total Files"
 *   value={1250}
 *   previousValue={1100}
 *   trend="up"
 *   trendPercentage={13.6}
 *   icon={<FileIcon />}
 *   animateValue
 * />
 * ```
 */
export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  previousValue,
  unit = '',
  icon,
  trend,
  trendPercentage,
  animateValue = true,
  formatValue,
  onClick,
  className = '',
  testId,
}) => {
  /**
   * Calculate trend if not provided
   */
  const calculatedTrend =
    trend ||
    (previousValue !== undefined
      ? value > previousValue
        ? 'up'
        : value < previousValue
        ? 'down'
        : 'neutral'
      : undefined);

  const trendInfo = calculatedTrend ? getTrendInfo(calculatedTrend) : null;

  const isInteractive = Boolean(onClick);

  const baseStyles = `
    backdrop-blur-xl
    bg-white/5
    border
    border-white/10
    rounded-xl
    p-6
    transition-all
    duration-normal
    ${isInteractive ? 'cursor-pointer hover:border-primary/30 hover:shadow-glow-purple' : ''}
  `.trim().replace(/\s+/g, ' ');

  const CardElement = isInteractive ? motion.div : 'div';

  return (
    <CardElement
      className={`${baseStyles} ${className}`.trim()}
      onClick={onClick}
      data-testid={testId}
      {...(isInteractive && {
        whileHover: { scale: 1.02 },
        whileTap: { scale: 0.98 },
      })}
    >
      {/* Header with Icon and Label */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="text-primary" aria-hidden="true">
              {icon}
            </div>
          )}
          <span className="text-text-secondary text-sm font-medium uppercase tracking-wide">
            {label}
          </span>
        </div>

        {/* Trend Badge */}
        {trendInfo && trendPercentage !== undefined && (
          <GlowingBadge
            variant={trendInfo.color as any}
            size="sm"
          >
            {trendInfo.icon} {trendPercentage.toFixed(1)}%
          </GlowingBadge>
        )}
      </div>

      {/* Animated Value Display */}
      <div className="mb-2">
        {animateValue ? (
          <AnimatedCounter
            value={value}
            unit={unit}
            formatValue={formatValue}
          />
        ) : (
          <div className="text-4xl md:text-5xl font-bold text-text-primary">
            {formatValue ? formatValue(value) : value.toLocaleString()}
            {unit && <span className="text-2xl text-text-secondary ml-1">{unit}</span>}
          </div>
        )}
      </div>

      {/* Trend Description */}
      {trendInfo && previousValue !== undefined && (
        <p className="text-sm text-text-muted">
          {trendInfo.label} from {previousValue.toLocaleString()}
        </p>
      )}
    </CardElement>
  );
};

StatCard.displayName = 'StatCard';

export default StatCard;
