/**
 * FLOATING ACTION BUTTON (FAB)
 * Glass FAB with trail effect and extended variant
 */

'use client';

import React from 'react';
import { motion, type MotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface FloatingActionButtonProps extends Omit<MotionProps, 'children'> {
  icon: React.ReactNode;
  label?: string;
  extended?: boolean;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  onClick?: () => void;
  className?: string;
}

export const FloatingActionButton: React.FC<FloatingActionButtonProps> = ({
  icon,
  label,
  extended = false,
  position = 'bottom-right',
  onClick,
  className,
  ...motionProps
}) => {
  const positionClasses: Record<string, string> = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  return (
    <motion.button
      className={cn(
        'fixed z-[1200]',
        'glass-strong',
        'inline-flex items-center gap-3',
        extended ? 'rounded-full px-6 py-4' : 'rounded-full p-4',
        'text-cyber-blue border border-cyber-blue/30',
        'shadow-glass-glow-blue',
        'transition-all duration-fast',
        'focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-500',
        positionClasses[position],
        className
      )}
      onClick={onClick}
      whileHover={{ 
        scale: 1.05,
        boxShadow: '0 0 30px hsl(220, 90%, 60%, 0.6), 0 0 60px hsl(220, 90%, 60%, 0.4)',
      }}
      whileTap={{ scale: 0.95 }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      {...motionProps}
    >
      <span className="w-6 h-6">{icon}</span>
      {extended && label && (
        <motion.span
          className="font-semibold text-base whitespace-nowrap"
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 'auto', opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          {label}
        </motion.span>
      )}
      
      {/* Trail effect */}
      <motion.span
        className="absolute inset-0 rounded-full bg-cyber-blue/20"
        initial={{ scale: 1, opacity: 0.5 }}
        animate={{ scale: 1.5, opacity: 0 }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          repeatDelay: 0.5,
        }}
      />
    </motion.button>
  );
};

FloatingActionButton.displayName = 'FloatingActionButton';
