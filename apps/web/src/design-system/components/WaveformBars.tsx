/**
 * @fileoverview Animated waveform bar visualization component.
 *
 * Renders a row of vertical bars that animate in a wave pattern,
 * simulating an audio waveform / equalizer effect. Commonly used as
 * a "now playing" indicator or decorative loading state.
 *
 * @example
 * ```tsx
 * <WaveformBars barCount={16} color="cyan" />
 * ```
 *
 * @module design-system/components/WaveformBars
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

type WaveColor = 'cyan' | 'purple' | 'magenta' | 'gradient';

interface WaveformBarsProps {
  /** Number of bars to render */
  barCount?: number;
  /** Bar accent color */
  color?: WaveColor;
  /** Height of the entire visualizer in pixels */
  height?: number;
  className?: string;
}

const BAR_COLORS: Record<WaveColor, string> = {
  cyan: 'bg-cyber-cyan',
  purple: 'bg-cyber-purple',
  magenta: 'bg-cyber-magenta',
  gradient: 'bg-gradient-to-t from-cyber-cyan to-cyber-purple',
};

export const WaveformBars: React.FC<WaveformBarsProps> = ({
  barCount = 24,
  color = 'gradient',
  height = 48,
  className,
}) => (
  <div
    className={cn('flex items-end gap-[2px]', className)}
    style={{ height }}
    role="img"
    aria-label="Audio waveform visualization"
  >
    {Array.from({ length: barCount }).map((_, i) => (
      <motion.div
        key={i}
        className={cn('w-1 rounded-full opacity-80', BAR_COLORS[color])}
        animate={{
          height: ['20%', `${40 + Math.random() * 50}%`, '20%'],
        }}
        transition={{
          duration: 0.6 + Math.random() * 0.4,
          ease: 'easeInOut',
          repeat: Infinity,
          delay: i * 0.04,
        }}
      />
    ))}
  </div>
);

WaveformBars.displayName = 'WaveformBars';
