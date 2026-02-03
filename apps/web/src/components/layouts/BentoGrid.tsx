'use client';

/**
 * BENTO GRID LAYOUT COMPONENT
 * Flexible CSS Grid-based layout for dashboard-style UIs
 * Features: Variable span sizes, responsive breakpoints, hover effects, animation
 */

import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { bentoItemEnter, bentoItemHover } from '@/design-system/animations/presets';

export type ItemSpan = 4 | 6 | 8 | 12; // Column units (out of 12)
export type ItemHeight = 'auto' | 'small' | 'medium' | 'large' | 'full';

interface BentoGridItem {
  id: string;
  span?: ItemSpan; // Default: 4
  height?: ItemHeight; // Default: auto
  children: ReactNode;
  className?: string;
}

interface BentoGridProps {
  items: BentoGridItem[];
  gap?: number; // Gap in pixels
  className?: string;
  onItemClick?: (itemId: string) => void;
  animateItems?: boolean;
}

/**
 * Get height class from ItemHeight type
 */
const getHeightClass = (height?: ItemHeight): string => {
  switch (height) {
    case 'small':
      return 'min-h-[200px]';
    case 'medium':
      return 'min-h-[300px]';
    case 'large':
      return 'min-h-[400px]';
    case 'full':
      return 'min-h-screen';
    default:
      return 'min-h-auto';
  }
};

/**
 * Get grid column span class
 */
const getSpanClass = (span?: ItemSpan): string => {
  switch (span) {
    case 4:
      return 'col-span-1 md:col-span-1 lg:col-span-1';
    case 6:
      return 'col-span-1 md:col-span-2 lg:col-span-2';
    case 8:
      return 'col-span-1 md:col-span-3 lg:col-span-2';
    case 12:
      return 'col-span-1 md:col-span-4 lg:col-span-3';
    default:
      return 'col-span-1 md:col-span-1 lg:col-span-1';
  }
};

/**
 * Individual Bento Grid Item
 */
const BentoItem: React.FC<{
  item: BentoGridItem;
  index: number;
  onClick?: (id: string) => void;
  shouldAnimate?: boolean;
}> = ({ item, index, onClick, shouldAnimate = true }) => {
  return (
    <motion.div
      className={`relative rounded-xl overflow-hidden group cursor-pointer
        ${getSpanClass(item.span)} ${getHeightClass(item.height)}
        ${item.className || ''}`}
      onClick={() => onClick?.(item.id)}
      {...(shouldAnimate && {
        variants: bentoItemEnter,
        initial: 'initial',
        animate: 'animate',
        transition: { delay: index * 0.05 },
      })}
      {...bentoItemHover}
    >
      {/* Background with glassmorphism */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />

      {/* Content */}
      <div className="relative h-full w-full">
        {item.children}
      </div>
    </motion.div>
  );
};

/**
 * Main Bento Grid Component
 */
export const BentoGrid: React.FC<BentoGridProps> = ({
  items,
  gap = 16,
  className = '',
  onItemClick,
  animateItems = true,
}) => {
  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-4 lg:grid-cols-12 ${className}`}
      style={{
        gap: `${gap}px`,
      }}
    >
      {items.map((item, index) => (
        <BentoItem
          key={item.id}
          item={item}
          index={index}
          onClick={onItemClick}
          shouldAnimate={animateItems}
        />
      ))}
    </div>
  );
};

/**
 * Preset grid layouts for common dashboard patterns
 */

/**
 * Analytics Dashboard Layout (3 cols: 8, 4, 4, 12)
 */
export const AnalyticsDashboardLayout = (items: BentoGridItem[]) => {
  return (
    <BentoGrid
      items={[
        { ...items[0], span: 8, height: 'medium' },
        { ...items[1], span: 4, height: 'medium' },
        { ...items[2], span: 4, height: 'medium' },
        { ...items[3], span: 12, height: 'large' },
        ...items.slice(4),
      ]}
    />
  );
};

/**
 * Feature Showcase Layout (2-2-2-3 grid)
 */
export const FeatureShowcaseLayout = (items: BentoGridItem[]) => {
  const layouts = items.map((item, index) => {
    if (index < 2) return { ...item, span: 6 as ItemSpan };
    if (index < 4) return { ...item, span: 6 as ItemSpan };
    if (index < 6) return { ...item, span: 4 as ItemSpan };
    return { ...item, span: 4 as ItemSpan };
  });

  return <BentoGrid items={layouts} />;
};

/**
 * Media Grid Layout (for image/audio focused layouts)
 */
export const MediaGridLayout = (items: BentoGridItem[]) => {
  return (
    <BentoGrid
      items={items.map((item) => ({
        ...item,
        span: 6 as ItemSpan,
        height: 'medium',
      }))}
    />
  );
};

/**
 * Full Width + Sidebar Layout
 */
export const FullWidthSidebarLayout = (
  mainItem: BentoGridItem,
  sidebarItems: BentoGridItem[]
) => {
  return (
    <BentoGrid
      items={[
        { ...mainItem, span: 8, height: 'large' },
        ...sidebarItems.map((item) => ({
          ...item,
          span: 4 as ItemSpan,
          height: 'medium' as ItemHeight,
        })),
      ]}
    />
  );
};

export default BentoGrid;
