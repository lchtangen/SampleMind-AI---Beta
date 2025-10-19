/**
 * GLASS BUTTON COMPONENT
 * Cyberpunk glassmorphism button with neon glow effects
 */

'use client';

import React from 'react';
import { motion, type MotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'outline';
type ButtonSize = 'sm' | 'md' | 'lg';

interface GlassButtonProps extends Omit<MotionProps, 'children'> {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  className,
  onClick,
  ...motionProps
}) => {
  // Variant styles
  const variantClasses: Record<ButtonVariant, string> = {
    primary: 'glass text-cyber-blue border-cyber-blue/30 hover:border-cyber-blue/60 hover:shadow-glow-blue',
    secondary: 'glass text-cyber-purple border-cyber-purple/30 hover:border-cyber-purple/60 hover:shadow-glow-purple',
    ghost: 'bg-transparent text-text-primary hover:bg-white/5',
    outline: 'border border-glass-border text-text-primary hover:bg-white/5 hover:border-cyber-blue/50',
  };

  // Size styles
  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const iconSizeClasses: Record<ButtonSize, string> = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <motion.button
      className={cn(
        // Base styles
        'relative inline-flex items-center justify-center gap-2',
        'rounded-glass font-semibold',
        'transition-all duration-fast',
        'focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-500',
        
        // Disabled styles
        disabled && 'opacity-50 cursor-not-allowed',
        
        // Variant & size
        variantClasses[variant],
        sizeClasses[size],
        
        className
      )}
      onClick={disabled || isLoading ? undefined : onClick}
      disabled={disabled || isLoading}
      
      // Framer Motion animations
      whileHover={disabled || isLoading ? {} : { 
        scale: 1.02,
        y: -2,
      }}
      whileTap={disabled || isLoading ? {} : { 
        scale: 0.98,
        y: 0,
      }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 17,
      }}
      
      {...motionProps}
    >
      {/* Loading spinner */}
      {isLoading && (
        <Loader2 className={cn('animate-spin', iconSizeClasses[size])} />
      )}
      
      {/* Left icon */}
      {!isLoading && leftIcon && (
        <span className={iconSizeClasses[size]}>{leftIcon}</span>
      )}
      
      {/* Button text */}
      <span>{children}</span>
      
      {/* Right icon */}
      {!isLoading && rightIcon && (
        <span className={iconSizeClasses[size]}>{rightIcon}</span>
      )}
      
      {/* Glow effect on hover */}
      <motion.span 
        className="absolute inset-0 rounded-glass opacity-0 transition-opacity duration-fast pointer-events-none"
        style={{
          background: variant === 'primary' 
            ? 'radial-gradient(circle at center, hsl(220, 90%, 60%, 0.2), transparent)'
            : 'radial-gradient(circle at center, hsl(270, 85%, 65%, 0.2), transparent)',
        }}
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
      />
    </motion.button>
  );
};

GlassButton.displayName = 'GlassButton';
