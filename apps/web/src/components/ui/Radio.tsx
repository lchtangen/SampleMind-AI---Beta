/**
 * GLASS RADIO COMPONENT
 * Radio buttons with ripple effect
 */

'use client';

import React, { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface RadioOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface RadioGroupProps {
  name: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const RadioGroup = forwardRef<HTMLDivElement, RadioGroupProps>(
  ({ name, options, value, onChange, error, orientation = 'vertical', className }, ref) => {
    return (
      <div ref={ref} className={cn('w-full', className)}>
        <div
          className={cn(
            'flex gap-4',
            orientation === 'vertical' ? 'flex-col' : 'flex-row flex-wrap'
          )}
          role="radiogroup"
        >
          {options.map((option) => (
            <Radio
              key={option.value}
              name={name}
              value={option.value}
              label={option.label}
              checked={value === option.value}
              onChange={() => !option.disabled && onChange?.(option.value)}
              disabled={option.disabled}
            />
          ))}
        </div>

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

RadioGroup.displayName = 'RadioGroup';

interface RadioProps {
  name: string;
  value: string;
  label: string;
  checked?: boolean;
  onChange?: () => void;
  disabled?: boolean;
  className?: string;
}

export const Radio: React.FC<RadioProps> = ({
  name,
  value,
  label,
  checked = false,
  onChange,
  disabled = false,
  className,
}) => {
  return (
    <label className={cn('inline-flex items-center gap-3 cursor-pointer group', className)}>
      <div className="relative">
        <input
          type="radio"
          name={name}
          value={value}
          className="sr-only"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
        />
        
        <motion.div
          className={cn(
            'w-5 h-5 rounded-full glass border border-glass-border',
            'transition-all duration-fast',
            'group-hover:border-cyber-blue/50',
            'flex items-center justify-center',
            checked && 'bg-cyber-blue/20 border-cyber-blue shadow-glow-blue',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
          whileHover={!disabled ? { scale: 1.05 } : {}}
          whileTap={!disabled ? { scale: 0.95 } : {}}
        >
          <AnimatePresence>
            {checked && (
              <>
                {/* Inner dot */}
                <motion.div
                  className="w-2.5 h-2.5 rounded-full bg-cyber-blue"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  exit={{ scale: 0 }}
                  transition={{
                    type: 'spring',
                    stiffness: 400,
                    damping: 17,
                  }}
                />
                
                {/* Ripple effect */}
                <motion.div
                  className="absolute inset-0 rounded-full border-2 border-cyber-blue"
                  initial={{ scale: 1, opacity: 0.5 }}
                  animate={{ scale: 1.8, opacity: 0 }}
                  transition={{ duration: 0.6 }}
                />
              </>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      <span className={cn(
        'text-sm font-medium select-none',
        checked ? 'text-text-primary' : 'text-text-secondary',
        disabled && 'opacity-50'
      )}>
        {label}
      </span>
    </label>
  );
};

Radio.displayName = 'Radio';
