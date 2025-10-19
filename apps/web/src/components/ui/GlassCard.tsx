/**
 * GLASS CARD COMPONENT
 * Card with gradient border and cyberpunk styling
 */

'use client';

import React from 'react';
import { motion, type MotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

interface GlassCardProps extends MotionProps {
  children: React.ReactNode;
  variant?: 'base' | 'light' | 'strong';
  withBorder?: boolean;
  className?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  variant = 'base',
  withBorder = false,
  className,
  ...motionProps
}) => {
  const variantClasses: Record<string, string> = {
    base: 'glass',
    light: 'glass-light',
    strong: 'glass-strong',
  };

  return (
    <motion.div
      className={cn(
        'rounded-glass-lg p-6',
        variantClasses[variant],
        withBorder && 'border-neon',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        type: 'spring',
        stiffness: 200,
        damping: 20,
      }}
      {...motionProps}
    >
      {children}
    </motion.div>
  );
};

GlassCard.displayName = 'GlassCard';
