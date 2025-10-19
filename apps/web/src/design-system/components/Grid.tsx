/**
 * GRID COMPONENT
 * 12-column responsive grid system
 */

'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface GridProps {
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export const Grid: React.FC<GridProps> = ({
  children,
  cols = 12,
  gap = 'md',
  className,
}) => {
  const colClasses: Record<number, string> = {
    1: 'grid-cols-1',
    2: 'grid-cols-2',
    3: 'grid-cols-3',
    4: 'grid-cols-4',
    6: 'grid-cols-6',
    12: 'grid-cols-12',
  };

  const gapClasses: Record<string, string> = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
    xl: 'gap-8',
  };

  return (
    <div
      className={cn(
        'grid',
        colClasses[cols],
        gapClasses[gap],
        className
      )}
    >
      {children}
    </div>
  );
};

Grid.displayName = 'Grid';

interface GridItemProps {
  children: React.ReactNode;
  span?: 1 | 2 | 3 | 4 | 6 | 12;
  className?: string;
}

export const GridItem: React.FC<GridItemProps> = ({
  children,
  span = 1,
  className,
}) => {
  const spanClasses: Record<number, string> = {
    1: 'col-span-1',
    2: 'col-span-2',
    3: 'col-span-3',
    4: 'col-span-4',
    6: 'col-span-6',
    12: 'col-span-12',
  };

  return (
    <div className={cn(spanClasses[span], className)}>
      {children}
    </div>
  );
};

GridItem.displayName = 'GridItem';
