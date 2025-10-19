/**
 * BUTTON GROUP COMPONENT
 * Group multiple buttons together with connected styling
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ButtonGroupProps {
  children: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  orientation = 'horizontal',
  className,
}) => {
  return (
    <div
      className={cn(
        'inline-flex',
        orientation === 'horizontal' ? 'flex-row' : 'flex-col',
        className
      )}
      role="group"
    >
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child;

        const isFirst = index === 0;
        const isLast = index === React.Children.count(children) - 1;

        return React.cloneElement(child, {
          ...child.props,
          className: cn(
            child.props.className,
            orientation === 'horizontal' && !isFirst && '-ml-px',
            orientation === 'vertical' && !isFirst && '-mt-px',
            orientation === 'horizontal' && !isFirst && !isLast && 'rounded-none',
            orientation === 'horizontal' && isFirst && 'rounded-r-none',
            orientation === 'horizontal' && isLast && 'rounded-l-none',
            orientation === 'vertical' && !isFirst && !isLast && 'rounded-none',
            orientation === 'vertical' && isFirst && 'rounded-b-none',
            orientation === 'vertical' && isLast && 'rounded-t-none'
          ),
        } as any);
      })}
    </div>
  );
};

ButtonGroup.displayName = 'ButtonGroup';
