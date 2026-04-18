/**
 * @fileoverview Animated stat card with neon glow-on-hover.
 *
 * Displays a single KPI with an icon, value, label, and optional trend
 * indicator. Designed for dashboard summary rows.
 *
 * @example
 * ```tsx
 * <StatCard
 *   icon={<Music2 className="h-5 w-5" />}
 *   value={1_247}
 *   label="Total Samples"
 *   trend={{ value: 12, direction: 'up' }}
 *   glowColor="cyan"
 * />
 * ```
 *
 * @module design-system/components/StatCard
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

type GlowColor = 'cyan' | 'purple' | 'magenta' | 'blue';

interface StatCardProps {
  /** Leading icon (rendered at top-left) */
  icon: React.ReactNode;
  /** Numeric or string value */
  value: number | string;
  /** Description label shown below the value */
  label: string;
  /** Optional trend badge with ↑/↓ and percentage */
  trend?: { value: number; direction: 'up' | 'down' };
  /** Neon glow color on hover */
  glowColor?: GlowColor;
  className?: string;
}

const GLOW_MAP: Record<GlowColor, string> = {
  cyan: 'hover:shadow-glow-cyan hover:border-cyber-cyan/30',
  purple: 'hover:shadow-glow-purple hover:border-cyber-purple/30',
  magenta: 'hover:shadow-glow-magenta hover:border-cyber-magenta/30',
  blue: 'hover:shadow-glow-blue hover:border-cyber-blue/30',
};

const COLOR_MAP: Record<GlowColor, string> = {
  cyan: 'text-cyber-cyan',
  purple: 'text-cyber-purple',
  magenta: 'text-cyber-magenta',
  blue: 'text-cyber-blue',
};

export const StatCard: React.FC<StatCardProps> = ({
  icon,
  value,
  label,
  trend,
  glowColor = 'cyan',
  className,
}) => (
  <motion.div
    whileHover={{ y: -2 }}
    transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    className={cn(
      'glass rounded-glass p-5 transition-shadow duration-300',
      GLOW_MAP[glowColor],
      className,
    )}
  >
    <div className="flex items-center justify-between mb-3">
      <div className={cn('p-2 rounded-lg bg-glass-light', COLOR_MAP[glowColor])}>
        {icon}
      </div>
      {trend && (
        <span
          className={cn(
            'flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full',
            trend.direction === 'up'
              ? 'bg-success/10 text-success'
              : 'bg-error/10 text-error',
          )}
        >
          {trend.direction === 'up' ? (
            <TrendingUp className="h-3 w-3" />
          ) : (
            <TrendingDown className="h-3 w-3" />
          )}
          {trend.value}%
        </span>
      )}
    </div>
    <p className="text-2xl font-bold text-text-primary">{value}</p>
    <p className="text-sm text-text-tertiary mt-1">{label}</p>
  </motion.div>
);

StatCard.displayName = 'StatCard';
