/**
 * LOADING SPINNER COMPONENT
 * Animated loading spinner with gradient
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'blue' | 'purple' | 'cyan';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  variant = 'blue',
  className,
}) => {
  const sizeClasses: Record<string, string> = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const variantClasses: Record<string, string> = {
    blue: 'from-cyber-blue to-cyber-purple',
    purple: 'from-cyber-purple to-cyber-magenta',
    cyan: 'from-cyber-cyan to-cyber-blue',
  };

  return (
    <motion.div
      className={cn('relative', sizeClasses[size], className)}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear',
      }}
    >
      <div className={cn(
        'absolute inset-0 rounded-full',
        'bg-gradient-to-r', 
        variantClasses[variant],
        'opacity-20'
      )} />
      <div className={cn(
        'absolute inset-0 rounded-full',
        'bg-gradient-to-r',
        variantClasses[variant],
        'opacity-75',
        '[mask-image:linear-gradient(to_right,transparent,black,black)]'
      )} />
    </motion.div>
  );
};

LoadingSpinner.displayName = 'LoadingSpinner';
