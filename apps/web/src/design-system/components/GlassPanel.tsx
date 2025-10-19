/**
 * GLASS PANEL COMPONENT
 * Reusable glass effect panel with variants
 */

'use client';

import React from 'react';
import { motion, MotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassPanelProps extends MotionProps {
  children: React.ReactNode;
  variant?: 'base' | 'light' | 'strong' | 'subtle';
  className?: string;
  as?: 'div' | 'section' | 'article' | 'aside';
}

export const GlassPanel: React.FC<GlassPanelProps> = ({
  children,
  variant = 'base',
  className,
  as = 'div',
  ...motionProps
}) => {
  const Component = motion[as];

  const variantClasses: Record<string, string> = {
    base: 'glass',
    light: 'glass-light',
    strong: 'glass-strong',
    subtle: 'backdrop-blur-sm bg-white/[0.03] border border-white/5',
  };

  return (
    <Component
      className={cn(
        'rounded-glass',
        variantClasses[variant],
        className
      )}
      {...motionProps}
    >
      {children}
    </Component>
  );
};

GlassPanel.displayName = 'GlassPanel';
