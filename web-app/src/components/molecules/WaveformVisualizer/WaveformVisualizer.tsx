/**
 * WaveformVisualizer Component
 *
 * A cyberpunk-themed audio waveform visualizer with animated bars,
 * neon gradients, and interactive hover effects.
 *
 * @module WaveformVisualizer
 */

import React from 'react';
import { motion } from 'framer-motion';

/**
 * Waveform data point
 */
export interface WaveformDataPoint {
  value: number; // 0-100
  frequency?: number;
}

/**
 * Props for the WaveformVisualizer component
 */
export interface WaveformVisualizerProps {
  /**
   * Waveform data array (values 0-100)
   */
  data: number[] | WaveformDataPoint[];

  /**
   * Height of the visualizer in pixels
   */
  height?: number;

  /**
   * Number of bars to display
   */
  barCount?: number;

  /**
   * Gap between bars in pixels
   */
  barGap?: number;

  /**
   * Enable animated bars
   */
  animated?: boolean;

  /**
   * Enable hover interaction
   */
  interactive?: boolean;

  /**
   * Color scheme
   */
  colorScheme?: 'purple' | 'cyber' | 'neon';

  /**
   * Show frequency labels
   */
  showLabels?: boolean;

  /**
   * Click handler for bars
   */
  onBarClick?: (index: number, value: number) => void;

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
 * Color gradients for different schemes
 */
const colorGradients = {
  purple: {
    from: '#8B5CF6',
    to: '#A78BFA',
    glow: 'rgba(139, 92, 246, 0.6)',
  },
  cyber: {
    from: '#8B5CF6',
    to: '#06B6D4',
    glow: 'rgba(6, 182, 212, 0.6)',
  },
  neon: {
    from: '#EC4899',
    to: '#8B5CF6',
    glow: 'rgba(236, 72, 153, 0.6)',
  },
};

/**
 * WaveformVisualizer - Animated audio waveform display.
 *
 * @example
 * ```tsx
 * <WaveformVisualizer
 *   data={audioData}
 *   height={200}
 *   colorScheme="cyber"
 *   animated
 *   interactive
 *   onBarClick={(index, value) => console.log(index, value)}
 * />
 * ```
 */
export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  data,
  height = 200,
  barCount = 64,
  barGap = 2,
  animated = true,
  interactive = true,
  colorScheme = 'cyber',
  showLabels = false,
  onBarClick,
  className = '',
  testId,
}) => {
  /**
   * Normalize data to array of numbers
   */
  const normalizedData = data.map(d =>
    typeof d === 'number' ? d : d.value
  ).slice(0, barCount);

  /**
   * Fill remaining slots if needed
   */
  while (normalizedData.length < barCount) {
    normalizedData.push(Math.random() * 50);
  }

  const colors = colorGradients[colorScheme];

  return (
    <div
      className={`relative ${className}`}
      data-testid={testId}
      role="img"
      aria-label="Audio waveform visualization"
    >
      <div
        className="flex items-end justify-between gap-[${barGap}px]"
        style={{ height: `${height}px`, gap: `${barGap}px` }}
      >
        {normalizedData.map((value, index) => {
          const barHeight = Math.max((value / 100) * height, 4);

          return (
            <motion.div
              key={index}
              className={`
                flex-1
                rounded-full
                cursor-pointer
                transition-all
                duration-fast
              `.trim().replace(/\s+/g, ' ')}
              style={{
                height: `${barHeight}px`,
                background: `linear-gradient(to top, ${colors.from}, ${colors.to})`,
                boxShadow: `0 0 10px ${colors.glow}`,
              }}
              initial={animated ? { height: 0, opacity: 0 } : false}
              animate={animated ? { height: `${barHeight}px`, opacity: 1 } : false}
              transition={{
                duration: 0.5,
                delay: animated ? index * 0.01 : 0,
                ease: 'easeOut',
              }}
              whileHover={
                interactive
                  ? {
                      scaleY: 1.1,
                      filter: 'brightness(1.3)',
                      boxShadow: `0 0 20px ${colors.glow}`,
                    }
                  : undefined
              }
              onClick={
                onBarClick ? () => onBarClick(index, value) : undefined
              }
              role={onBarClick ? 'button' : undefined}
              tabIndex={onBarClick ? 0 : undefined}
              aria-label={
                onBarClick
                  ? `Waveform bar ${index + 1}, value ${value.toFixed(0)}`
                  : undefined
              }
            />
          );
        })}
      </div>

      {/* Optional Frequency Labels */}
      {showLabels && (
        <div className="flex justify-between mt-2 text-xs text-text-muted">
          <span>Low</span>
          <span>Mid</span>
          <span>High</span>
        </div>
      )}
    </div>
  );
};

WaveformVisualizer.displayName = 'WaveformVisualizer';

export default WaveformVisualizer;
