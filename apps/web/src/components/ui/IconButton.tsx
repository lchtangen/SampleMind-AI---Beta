/**
 * ICON BUTTON COMPONENT
 * Glass icon button with neon glow
 */

'use client';

import React from 'react';
import { motion, type MotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

type IconButtonSize = 'sm' | 'md' | 'lg';
type IconButtonVariant = 'primary' | 'secondary' | 'ghost';

interface IconButtonProps extends Omit<MotionProps, 'children'> {
  icon: React.ReactNode;
  size?: IconButtonSize;
  variant?: IconButtonVariant;
  disabled?: boolean;
  className?: string;
  'aria-label': string;
  onClick?: () => void;
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  size = 'md',
  variant = 'ghost',
  disabled = false,
  className,
  onClick,
  ...motionProps
}) => {
  const sizeClasses: Record<IconButtonSize, string> = {
    sm: 'w-8 h-8 p-1.5',
    md: 'w-10 h-10 p-2',
    lg: 'w-12 h-12 p-3',
  };

  const variantClasses: Record<IconButtonVariant, string> = {
    primary: 'glass text-cyber-blue border-cyber-blue/30 hover:border-cyber-blue/60 hover:shadow-glow-blue',
    secondary: 'glass text-cyber-purple border-cyber-purple/30 hover:border-cyber-purple/60 hover:shadow-glow-purple',
    ghost: 'text-text-secondary hover:text-text-primary hover:bg-white/5',
  };

  return (
    <motion.button
      className={cn(
        'inline-flex items-center justify-center',
        'rounded-glass',
        'transition-all duration-fast',
        'focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-500',
        disabled && 'opacity-50 cursor-not-allowed',
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      whileHover={disabled ? {} : { scale: 1.05 }}
      whileTap={disabled ? {} : { scale: 0.95 }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 17,
      }}
      {...motionProps}
    >
      {icon}
    </motion.button>
  );
};

IconButton.displayName = 'IconButton';
