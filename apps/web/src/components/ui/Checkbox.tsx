/**
 * GLASS CHECKBOX COMPONENT
 * Checkbox with electric check animation
 */

'use client';

import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, checked, onChange, ...props }, ref) => {
    return (
      <div className="w-full">
        <label className="inline-flex items-center gap-3 cursor-pointer group">
          <div className="relative">
            <input
              ref={ref}
              type="checkbox"
              className="sr-only"
              checked={checked}
              onChange={onChange}
              {...props}
            />
            
            <motion.div
              className={cn(
                'w-5 h-5 rounded glass border border-glass-border',
                'transition-all duration-fast',
                'group-hover:border-cyber-blue/50',
                'flex items-center justify-center',
                checked && 'bg-cyber-blue/20 border-cyber-blue shadow-glow-blue',
                error && 'border-error',
                props.disabled && 'opacity-50 cursor-not-allowed',
                className
              )}
              whileHover={!props.disabled ? { scale: 1.05 } : {}}
              whileTap={!props.disabled ? { scale: 0.95 } : {}}
            >
              <AnimatePresence>
                {checked && (
                  <motion.div
                    initial={{ scale: 0, rotate: -180 }}
                    animate={{ scale: 1, rotate: 0 }}
                    exit={{ scale: 0, rotate: 180 }}
                    transition={{
                      type: 'spring',
                      stiffness: 400,
                      damping: 17,
                    }}
                  >
                    <Check className="w-4 h-4 text-cyber-blue" strokeWidth={3} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {label && (
            <span className={cn(
              'text-sm font-medium select-none',
              checked ? 'text-text-primary' : 'text-text-secondary',
              props.disabled && 'opacity-50'
            )}>
              {label}
            </span>
          )}
        </label>

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

Checkbox.displayName = 'Checkbox';
