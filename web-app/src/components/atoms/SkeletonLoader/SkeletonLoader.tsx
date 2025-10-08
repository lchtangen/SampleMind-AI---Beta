import React from 'react';
import { motion, Easing } from 'framer-motion';
import { SkeletonLoaderProps } from './SkeletonLoader.types';

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  className = '',
  width,
  height,
  variant = 'text',
  testId,
}) => {
  const shimmerVariants = {
    animate: {
      backgroundPosition: ['-1000px 0', '1000px 0'],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: 'linear' as Easing,
      },
    },
  };

  const baseClasses = 'bg-gray-800 rounded';
  const variantClasses = {
    text: 'h-4',
    rect: '',
    circle: 'rounded-full',
  };

  const style = {
    width: width ?? (variant === 'text' ? '100%' : undefined),
    height: height ?? (variant === 'text' ? undefined : '100%'),
  };

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
      data-testid={testId}
      variants={shimmerVariants}
      animate="animate"
    />
  );
};
