/**
 * GLASS INPUT COMPONENT
 * Text input with cyberpunk neon focus state
 */

'use client';

import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, leftIcon, rightIcon, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        
        <div className="relative">
          {/* Left icon */}
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {leftIcon}
            </div>
          )}
          
          {/* Input field */}
          <motion.input
            ref={ref}
            className={cn(
              'w-full glass rounded-glass px-4 py-3',
              'text-text-primary placeholder:text-text-tertiary',
              'border border-glass-border',
              'transition-all duration-fast',
              'focus:outline-none focus:border-cyber-blue focus:shadow-glow-blue',
              error && 'border-error focus:border-error focus:shadow-glow-magenta',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className
            )}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            animate={{
              borderColor: isFocused 
                ? 'hsl(220, 90%, 60%)' 
                : error 
                  ? 'hsl(0, 90%, 60%)' 
                  : 'rgba(255, 255, 255, 0.1)',
            }}
            transition={{ duration: 0.2 }}
            {...props}
          />
          
          {/* Right icon */}
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary">
              {rightIcon}
            </div>
          )}
        </div>
        
        {/* Error message */}
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-sm text-error"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
