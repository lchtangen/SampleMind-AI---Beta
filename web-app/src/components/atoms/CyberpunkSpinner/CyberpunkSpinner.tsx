import React from 'react';
import { motion } from 'framer-motion';
import { CyberpunkSpinnerProps, SpinnerSize } from './CyberpunkSpinner.types';

const sizeMap: Record<SpinnerSize, string> = {
  sm: 'w-4 h-4 border-2',
  md: 'w-8 h-8 border-4',
  lg: 'w-12 h-12 border-4',
};

export const CyberpunkSpinner: React.FC<CyberpunkSpinnerProps> = ({
  size = 'md',
  className = '',
  testId,
}) => {
  return (
    <motion.div
      className={`rounded-full border-primary border-t-transparent animate-spin ${sizeMap[size]} ${className}`}
      data-testid={testId}
      aria-label="Loading"
      role="status"
    />
  );
};
