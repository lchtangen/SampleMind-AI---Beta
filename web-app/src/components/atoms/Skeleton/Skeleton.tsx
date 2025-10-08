/**
 * Skeleton Component
 * Loading placeholders with animated shimmer effect
 */

import React from 'react';
import { motion } from 'framer-motion';
import { shimmerVariants } from '@/animations';

export interface SkeletonProps {
  /** Width of the skeleton (CSS value or number in px) */
  width?: string | number;
  /** Height of the skeleton (CSS value or number in px) */
  height?: string | number;
  /** Shape variant */
  variant?: 'rectangular' | 'circular' | 'rounded' | 'text';
  /** Custom className */
  className?: string;
  /** Whether to animate the shimmer effect */
  animate?: boolean;
  /** Number of lines for text variant */
  lines?: number;
}

/**
 * Skeleton Component
 * Displays loading placeholder with shimmer animation
 *
 * @example
 * ```tsx
 * <Skeleton width="100%" height={200} variant="rectangular" />
 * <Skeleton variant="circular" width={48} height={48} />
 * <Skeleton variant="text" lines={3} />
 * ```
 */
export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  variant = 'rectangular',
  className = '',
  animate = true,
  lines = 1,
}) => {
  // Convert number to px string
  const getSize = (size?: string | number) => {
    if (typeof size === 'number') return `${size}px`;
    return size;
  };

  // Base styles
  const baseStyles = 'bg-white/5 backdrop-blur-sm overflow-hidden relative';

  // Variant-specific styles
  const variantStyles = {
    rectangular: 'rounded-md',
    circular: 'rounded-full',
    rounded: 'rounded-lg',
    text: 'rounded-md',
  };

  // Shimmer gradient animation
  const shimmerStyles = animate
    ? 'before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent'
    : '';

  // If text variant with multiple lines
  if (variant === 'text' && lines > 1) {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, index) => (
          <motion.div
            key={index}
            className={`${baseStyles} ${variantStyles[variant]} ${shimmerStyles} h-4`}
            style={{
              width: index === lines - 1 ? '80%' : '100%',
            }}
            variants={animate ? shimmerVariants : undefined}
            initial={animate ? 'initial' : undefined}
            animate={animate ? 'animate' : undefined}
            aria-live="polite"
            aria-busy="true"
          />
        ))}
      </div>
    );
  }

  return (
    <motion.div
      className={`${baseStyles} ${variantStyles[variant]} ${shimmerStyles} ${className}`}
      style={{
        width: getSize(width) || (variant === 'text' ? '100%' : undefined),
        height: getSize(height) || (variant === 'text' ? '16px' : undefined),
      }}
      variants={animate ? shimmerVariants : undefined}
      initial={animate ? 'initial' : undefined}
      animate={animate ? 'animate' : undefined}
      aria-live="polite"
      aria-busy="true"
      role="status"
    />
  );
};

Skeleton.displayName = 'Skeleton';

/**
 * SkeletonCard Component
 * Pre-configured skeleton for card layouts
 */
export interface SkeletonCardProps {
  /** Whether to show avatar */
  showAvatar?: boolean;
  /** Number of text lines */
  lines?: number;
  /** Custom className */
  className?: string;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  showAvatar = false,
  lines = 3,
  className = '',
}) => {
  return (
    <div className={`space-y-4 p-6 ${className}`}>
      {showAvatar && (
        <div className="flex items-center gap-4">
          <Skeleton variant="circular" width={48} height={48} />
          <div className="flex-1 space-y-2">
            <Skeleton width="60%" height={16} />
            <Skeleton width="40%" height={12} />
          </div>
        </div>
      )}
      <Skeleton variant="text" lines={lines} />
    </div>
  );
};

SkeletonCard.displayName = 'SkeletonCard';

/**
 * SkeletonImage Component
 * Pre-configured skeleton for image placeholders
 */
export interface SkeletonImageProps {
  /** Width of the image skeleton */
  width?: string | number;
  /** Height of the image skeleton */
  height?: string | number;
  /** Aspect ratio (e.g., '16/9', '4/3', '1/1') */
  aspectRatio?: string;
  /** Custom className */
  className?: string;
}

export const SkeletonImage: React.FC<SkeletonImageProps> = ({
  width = '100%',
  height,
  aspectRatio,
  className = '',
}) => {
  const imageClassName = aspectRatio ? `${className}` : className;
  const imageStyle = aspectRatio ? { aspectRatio } : {};

  return (
    <div style={imageStyle} className={imageClassName}>
      <Skeleton
        variant="rounded"
        width={width}
        height={height}
        className="w-full h-full"
      />
    </div>
  );
};

SkeletonImage.displayName = 'SkeletonImage';

/**
 * SkeletonButton Component
 * Pre-configured skeleton for button placeholders
 */
export interface SkeletonButtonProps {
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Full width button */
  fullWidth?: boolean;
  /** Custom className */
  className?: string;
}

export const SkeletonButton: React.FC<SkeletonButtonProps> = ({
  size = 'md',
  fullWidth = false,
  className = '',
}) => {
  const sizeStyles = {
    sm: { width: 80, height: 32 },
    md: { width: 120, height: 40 },
    lg: { width: 160, height: 48 },
  };

  return (
    <Skeleton
      variant="rounded"
      width={fullWidth ? '100%' : sizeStyles[size].width}
      height={sizeStyles[size].height}
      className={className}
    />
  );
};

SkeletonButton.displayName = 'SkeletonButton';

/**
 * SkeletonList Component
 * Pre-configured skeleton for list layouts
 */
export interface SkeletonListProps {
  /** Number of list items */
  items?: number;
  /** Whether to show avatar in list items */
  showAvatar?: boolean;
  /** Custom className */
  className?: string;
}

export const SkeletonList: React.FC<SkeletonListProps> = ({
  items = 3,
  showAvatar = true,
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center gap-4">
          {showAvatar && <Skeleton variant="circular" width={40} height={40} />}
          <div className="flex-1 space-y-2">
            <Skeleton width="70%" height={16} />
            <Skeleton width="50%" height={12} />
          </div>
        </div>
      ))}
    </div>
  );
};

SkeletonList.displayName = 'SkeletonList';
