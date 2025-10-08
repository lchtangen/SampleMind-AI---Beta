import React from 'react';
import { motion } from 'framer-motion';
import { CyberpunkProgressBarProps, ProgressBarSize } from './CyberpunkProgressBar.types';

const sizeMap: Record<ProgressBarSize, string> = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
};

export const CyberpunkProgressBar: React.FC<CyberpunkProgressBarProps> = ({
  progress,
  size = 'md',
  className = '',
  testId,
}) => {
  const clampedProgress = Math.min(100, Math.max(0, progress));

  return (
    <div
      className={`w-full bg-gray-800 rounded-full ${sizeMap[size]} ${className}`}
      data-testid={testId}
      role="progressbar"
      aria-valuenow={clampedProgress}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <motion.div
        className="h-full rounded-full bg-gradient-to-r from-primary to-accent-cyan"
        initial={{ width: 0 }}
        animate={{ width: `${clampedProgress}%` }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
      />
    </div>
  );
};
