/**
 * PROGRESS BAR COMPONENT
 * Progress bar with sparking fill
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number; // 0-100
  max?: number;
  variant?: 'blue' | 'purple' | 'cyan' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'gradient',
  size = 'md',
  showLabel = false,
  className,
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  const sizeClasses: Record<string, string> = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const variantClasses: Record<string, string> = {
    blue: 'bg-cyber-blue',
    purple: 'bg-cyber-purple',
    cyan: 'bg-cyber-cyan',
    gradient: 'bg-spark-2',
  };

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-text-secondary">Progress</span>
          <span className="text-sm font-semibold text-text-primary">{Math.round(percentage)}%</span>
        </div>
      )}
      
      <div className={cn(
        'w-full glass rounded-full overflow-hidden relative',
        sizeClasses[size]
      )}>
        <motion.div
          className={cn(
            'h-full rounded-full',
            variantClasses[variant],
            variant === 'gradient' && 'bg-[length:200%_100%]'
          )}
          initial={{ width: 0 }}
          animate={{ 
            width: `${percentage}%`,
            ...(variant === 'gradient' && {
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }),
          }}
          transition={{
            width: {
              type: 'spring',
              stiffness: 100,
              damping: 15,
            },
            ...(variant === 'gradient' && {
              backgroundPosition: {
                duration: 3,
                repeat: Infinity,
                ease: 'linear',
              },
            }),
          }}
        />
        
        {/* Shimmer effect */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          animate={{
            x: ['-100%', '200%'],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'linear',
            repeatDelay: 1,
          }}
        />
      </div>
    </div>
  );
};

ProgressBar.displayName = 'ProgressBar';
