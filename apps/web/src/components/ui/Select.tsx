/**
 * GLASS SELECT COMPONENT
 * Dropdown select with animations
 */

'use client';

import React, { forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ChevronDown, Check } from 'lucide-react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  label?: string;
  error?: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export const Select = forwardRef<HTMLButtonElement, SelectProps>(
  ({ className, label, error, options, value, onChange, placeholder = 'Select...', disabled = false }, ref) => {
    const [isOpen, setIsOpen] = React.useState(false);
    const [isFocused, setIsFocused] = React.useState(false);
    const containerRef = React.useRef<HTMLDivElement>(null);

    const selectedOption = options.find(opt => opt.value === value);

    // Close on outside click
    React.useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
          setIsOpen(false);
        }
      };

      if (isOpen) {
        document.addEventListener('mousedown', handleClickOutside);
      }

      return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [isOpen]);

    const handleSelect = (optionValue: string) => {
      onChange?.(optionValue);
      setIsOpen(false);
    };

    return (
      <div className="w-full" ref={containerRef}>
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        
        <div className="relative">
          <motion.button
            ref={ref}
            type="button"
            className={cn(
              'w-full glass rounded-glass px-4 py-3 text-left',
              'flex items-center justify-between',
              'text-text-primary',
              'border border-glass-border',
              'transition-all duration-fast',
              'focus:outline-none focus:border-cyber-blue focus:shadow-glow-blue',
              error && 'border-error focus:border-error',
              disabled && 'opacity-50 cursor-not-allowed',
              className
            )}
            onClick={() => !disabled && setIsOpen(!isOpen)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            disabled={disabled}
            animate={{
              borderColor: isFocused 
                ? 'hsl(220, 90%, 60%)' 
                : error 
                  ? 'hsl(0, 90%, 60%)' 
                  : 'rgba(255, 255, 255, 0.1)',
            }}
          >
            <span className={cn(!selectedOption && 'text-text-tertiary')}>
              {selectedOption?.label || placeholder}
            </span>
            <ChevronDown 
              className={cn(
                'w-5 h-5 transition-transform duration-fast',
                isOpen && 'rotate-180'
              )}
            />
          </motion.button>

          <AnimatePresence>
            {isOpen && (
              <motion.div
                className="absolute z-50 w-full mt-2 glass-strong rounded-glass border border-glass-border shadow-glass-lg overflow-hidden"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <div className="max-h-60 overflow-y-auto scrollbar-hide">
                  {options.map((option) => (
                    <motion.button
                      key={option.value}
                      type="button"
                      className={cn(
                        'w-full px-4 py-3 text-left flex items-center justify-between',
                        'transition-colors duration-fast',
                        'hover:bg-white/5',
                        option.disabled && 'opacity-50 cursor-not-allowed',
                        value === option.value && 'bg-cyber-blue/10 text-cyber-blue'
                      )}
                      onClick={() => !option.disabled && handleSelect(option.value)}
                      disabled={option.disabled}
                      whileHover={!option.disabled ? { x: 4 } : {}}
                    >
                      <span>{option.label}</span>
                      {value === option.value && (
                        <Check className="w-4 h-4 text-cyber-blue" />
                      )}
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
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

Select.displayName = 'Select';
