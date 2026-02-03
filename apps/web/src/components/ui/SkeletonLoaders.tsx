'use client';

/**
 * SKELETON LOADING COMPONENTS
 * Animated placeholder components for loading states
 * Prevents layout shift and provides perceived performance improvements
 */

import React from 'react';
import { motion } from 'framer-motion';
import { skeletonShimmer } from '@/design-system/animations/presets';

/**
 * Base Skeleton Component with shimmer animation
 */
const SkeletonBase: React.FC<{
  className?: string;
  width?: string;
  height?: string;
  rounded?: 'sm' | 'md' | 'lg' | 'full';
}> = ({
  className = '',
  width = 'w-full',
  height = 'h-4',
  rounded = 'md',
}) => {
  const roundedClass = {
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  }[rounded];

  return (
    <motion.div
      variants={skeletonShimmer}
      initial="initial"
      animate="animate"
      className={`${width} ${height} ${roundedClass} bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700 bg-[length:200%_100%] ${className}`}
    />
  );
};

/**
 * Text Skeleton (simulates paragraph)
 */
export const TextSkeleton: React.FC<{
  lines?: number;
  className?: string;
}> = ({ lines = 3, className = '' }) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonBase
          key={i}
          width="w-full"
          height="h-4"
          className={i === lines - 1 ? 'w-3/4' : ''}
        />
      ))}
    </div>
  );
};

/**
 * Waveform Skeleton
 */
export const WaveformSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <SkeletonBase width="w-1/3" height="h-6" rounded="md" />
        <div className="flex gap-2">
          <SkeletonBase width="w-8" height="h-8" rounded="md" />
          <SkeletonBase width="w-8" height="h-8" rounded="md" />
        </div>
      </div>

      {/* Waveform bar */}
      <div className="w-full h-32 rounded-lg bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700 bg-[length:200%_100%]" />

      {/* Controls */}
      <div className="flex items-center justify-between">
        <SkeletonBase width="w-20" height="h-4" rounded="md" />
        <div className="flex gap-2">
          <SkeletonBase width="w-16" height="h-4" rounded="md" />
          <SkeletonBase width="w-16" height="h-4" rounded="md" />
        </div>
      </div>
    </div>
  );
};

/**
 * Analysis Card Skeleton
 */
export const AnalysisCardSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-4 p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <SkeletonBase width="w-1/2" height="h-5" rounded="md" />
          <SkeletonBase width="w-2/3" height="h-4" rounded="md" />
        </div>
        <SkeletonBase width="w-12" height="h-12" rounded="full" />
      </div>

      {/* Content */}
      <div className="space-y-3">
        <SkeletonBase width="w-full" height="h-3" rounded="md" />
        <SkeletonBase width="w-5/6" height="h-3" rounded="md" />
        <SkeletonBase width="w-4/5" height="h-3" rounded="md" />
      </div>

      {/* Footer */}
      <div className="flex gap-2 pt-2">
        <SkeletonBase width="w-1/4" height="h-6" rounded="md" />
        <SkeletonBase width="w-1/4" height="h-6" rounded="md" />
      </div>
    </div>
  );
};

/**
 * Music Theory Card Skeleton
 */
export const MusicTheoryCardSkeleton: React.FC<{
  className?: string;
}> = ({ className = '' }) => {
  return (
    <div className={`space-y-4 p-5 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SkeletonBase width="w-5" height="h-5" rounded="md" />
          <SkeletonBase width="w-24" height="h-4" rounded="md" />
        </div>
        <SkeletonBase width="w-12" height="h-5" rounded="md" />
      </div>

      {/* Main value */}
      <div className="space-y-2">
        <SkeletonBase width="w-2/3" height="h-12" rounded="md" />
        <SkeletonBase width="w-1/2" height="h-4" rounded="md" />
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <SkeletonBase width="w-full" height="h-1.5" rounded="full" />
      </div>
    </div>
  );
};

/**
 * Batch Queue Item Skeleton
 */
export const BatchQueueItemSkeleton: React.FC<{
  className?: string;
}> = ({ className = '' }) => {
  return (
    <div className={`flex items-center gap-3 p-3 ${className}`}>
      <SkeletonBase width="w-5" height="h-5" rounded="md" />
      <div className="flex-1 space-y-2">
        <SkeletonBase width="w-2/3" height="h-4" rounded="md" />
        <SkeletonBase width="w-1/2" height="h-3" rounded="md" />
      </div>
      <div className="space-y-2">
        <SkeletonBase width="w-12" height="h-4" rounded="md" />
        <SkeletonBase width="w-16" height="h-3" rounded="md" />
      </div>
    </div>
  );
};

/**
 * Dashboard Skeleton (full page layout)
 */
export const DashboardSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header */}
      <div className="space-y-4">
        <SkeletonBase width="w-1/3" height="h-8" rounded="md" />
        <SkeletonBase width="w-1/2" height="h-4" rounded="md" />
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <AnalysisCardSkeleton key={i} />
        ))}
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <WaveformSkeleton />
        </div>
        <div className="space-y-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <AnalysisCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * Library Grid Skeleton
 */
export const LibraryGridSkeleton: React.FC<{
  count?: number;
  className?: string;
}> = ({ count = 8, className = '' }) => {
  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}
    >
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="space-y-3">
          {/* Image/thumbnail */}
          <SkeletonBase width="w-full" height="h-48" rounded="lg" />

          {/* Title */}
          <SkeletonBase width="w-3/4" height="h-4" rounded="md" />

          {/* Metadata */}
          <div className="flex gap-2">
            <SkeletonBase width="w-1/3" height="h-3" rounded="md" />
            <SkeletonBase width="w-1/3" height="h-3" rounded="md" />
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * Upload Area Skeleton
 */
export const UploadAreaSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload zone */}
      <div className="w-full h-48 rounded-lg border-2 border-dashed border-slate-600 flex items-center justify-center bg-slate-700/10">
        <SkeletonBase width="w-32" height="h-32" rounded="lg" />
      </div>

      {/* File list */}
      <div className="space-y-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <BatchQueueItemSkeleton key={i} />
        ))}
      </div>
    </div>
  );
};

/**
 * Analysis Progress Skeleton
 */
export const AnalysisProgressSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-4 p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <SkeletonBase width="w-1/2" height="h-5" rounded="md" />
        <SkeletonBase width="w-16" height="h-5" rounded="md" />
      </div>

      {/* Progress bar */}
      <SkeletonBase width="w-full" height="h-2" rounded="full" />

      {/* Stages */}
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <SkeletonBase width="w-5" height="h-5" rounded="full" />
            <SkeletonBase width="w-1/3" height="h-4" rounded="md" />
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Full Page Skeleton (analysis detail page)
 */
export const AnalysisDetailSkeleton: React.FC<{ className?: string }> = ({
  className = '',
}) => {
  return (
    <div className={`space-y-8 ${className}`}>
      {/* Header with file info */}
      <div className="space-y-4">
        <SkeletonBase width="w-1/2" height="h-8" rounded="md" />
        <div className="flex gap-4">
          <SkeletonBase width="w-20" height="h-4" rounded="md" />
          <SkeletonBase width="w-20" height="h-4" rounded="md" />
          <SkeletonBase width="w-20" height="h-4" rounded="md" />
        </div>
      </div>

      {/* Waveform */}
      <WaveformSkeleton />

      {/* Music theory cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <MusicTheoryCardSkeleton key={i} />
        ))}
      </div>

      {/* Analysis results */}
      <div className="space-y-4">
        <SkeletonBase width="w-1/4" height="h-6" rounded="md" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <AnalysisCardSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default {
  SkeletonBase,
  TextSkeleton,
  WaveformSkeleton,
  AnalysisCardSkeleton,
  MusicTheoryCardSkeleton,
  BatchQueueItemSkeleton,
  DashboardSkeleton,
  LibraryGridSkeleton,
  UploadAreaSkeleton,
  AnalysisProgressSkeleton,
  AnalysisDetailSkeleton,
};
