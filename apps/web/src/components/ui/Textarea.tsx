/**
 * GLASS TEXTAREA COMPONENT
 * Multi-line text input with auto-resize
 */

'use client';

import React, { forwardRef, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  autoResize?: boolean;
  minRows?: number;
  maxRows?: number;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, autoResize = false, minRows = 3, maxRows = 10, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);

    // Auto-resize functionality
    useEffect(() => {
      if (!autoResize || !textareaRef.current) return;

      const textarea = textareaRef.current;
      const lineHeight = parseInt(getComputedStyle(textarea).lineHeight);
      
      const handleResize = () => {
        textarea.style.height = 'auto';
        const scrollHeight = textarea.scrollHeight;
        const minHeight = lineHeight * minRows;
        const maxHeight = lineHeight * maxRows;
        
        textarea.style.height = `${Math.min(Math.max(scrollHeight, minHeight), maxHeight)}px`;
      };

      textarea.addEventListener('input', handleResize);
      handleResize(); // Initial resize

      return () => textarea.removeEventListener('input', handleResize);
    }, [autoResize, minRows, maxRows]);

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-2">
            {label}
          </label>
        )}
        
        <motion.textarea
          ref={(el) => {
            textareaRef.current = el;
            if (typeof ref === 'function') {
              ref(el);
            } else if (ref) {
              ref.current = el;
            }
          }}
          className={cn(
            'w-full glass rounded-glass px-4 py-3',
            'text-text-primary placeholder:text-text-tertiary',
            'border border-glass-border',
            'transition-all duration-fast',
            'focus:outline-none focus:border-cyber-blue focus:shadow-glow-blue',
            'resize-none',
            error && 'border-error focus:border-error focus:shadow-glow-magenta',
            className
          )}
          rows={minRows}
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

Textarea.displayName = 'Textarea';
