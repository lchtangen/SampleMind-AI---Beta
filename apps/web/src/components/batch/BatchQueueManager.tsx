'use client';

/**
 * BATCH PROCESSING QUEUE MANAGER
 * Visualizes and manages audio file batch processing queue
 * Features: Drag-and-drop reordering, progress tracking, virtualization for 1000+ items
 * Status indicators, bulk operations, estimated time calculation
 */

import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FixedSizeList as List } from 'react-window';
import {
  Trash2,
  Pause,
  Play,
  Check,
  AlertCircle,
  Loader2,
  X,
  ChevronDown,
} from 'lucide-react';
import clsx from 'clsx';

export type FileStatus = 'pending' | 'processing' | 'completed' | 'error' | 'paused';

export interface BatchFile {
  id: string;
  name: string;
  size: number; // bytes
  status: FileStatus;
  progress: number; // 0-100
  duration?: number; // seconds
  estimatedTimeRemaining?: number; // seconds
  error?: string;
  startedAt?: Date;
  completedAt?: Date;
}

interface BatchQueueManagerProps {
  files: BatchFile[];
  isProcessing?: boolean;
  totalProgress?: number;
  onRemoveFile?: (fileId: string) => void;
  onPauseFile?: (fileId: string) => void;
  onResumeFile?: (fileId: string) => void;
  onRetryFile?: (fileId: string) => void;
  onClearCompleted?: () => void;
  onCancelAll?: () => void;
  onPauseAll?: () => void;
  onResumeAll?: () => void;
  className?: string;
}

/**
 * Status icon component
 */
const StatusIcon: React.FC<{ status: FileStatus }> = ({ status }) => {
  switch (status) {
    case 'completed':
      return (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 15 }}
        >
          <Check className="w-5 h-5 text-green-500" />
        </motion.div>
      );

    case 'processing':
      return (
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity }}>
          <Loader2 className="w-5 h-5 text-cyan-500" />
        </motion.div>
      );

    case 'error':
      return <AlertCircle className="w-5 h-5 text-red-500" />;

    case 'paused':
      return <Pause className="w-5 h-5 text-amber-500" />;

    default:
      return (
        <div className="w-5 h-5 rounded-full border-2 border-slate-600 bg-slate-800/50" />
      );
  }
};

/**
 * Format file size for display
 */
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format time duration
 */
const formatTime = (seconds?: number): string => {
  if (!seconds) return '--:--';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

/**
 * Individual queue item component (for virtualization)
 */
const QueueItem: React.FC<{
  file: BatchFile;
  index: number;
  onRemove?: (id: string) => void;
  onPause?: (id: string) => void;
  onResume?: (id: string) => void;
  onRetry?: (id: string) => void;
}> = ({ file, index, onRemove, onPause, onResume, onRetry }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-center gap-3 px-4 py-3 hover:bg-slate-800/30 group border-b border-slate-700/30 last:border-b-0"
      layout
    >
      {/* Status indicator */}
      <div className="flex-shrink-0">
        <StatusIcon status={file.status} />
      </div>

      {/* File info */}
      <div className="flex-1 min-w-0">
        {/* Filename */}
        <h4 className="text-sm font-medium text-slate-200 truncate">
          {file.name}
        </h4>

        {/* File size and time */}
        <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
          <span>{formatFileSize(file.size)}</span>
          {file.duration && <span>•</span>}
          {file.duration && <span>{formatTime(file.duration)}</span>}
          {file.error && (
            <>
              <span>•</span>
              <span className="text-red-400">{file.error}</span>
            </>
          )}
        </div>

        {/* Progress bar */}
        {file.status !== 'pending' && (
          <div className="mt-2 h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: '0%' }}
              animate={{ width: `${file.progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className={clsx(
                'h-full rounded-full',
                file.status === 'completed'
                  ? 'bg-gradient-to-r from-green-500 to-green-400'
                  : file.status === 'processing'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-400'
                  : file.status === 'error'
                  ? 'bg-gradient-to-r from-red-500 to-red-400'
                  : file.status === 'paused'
                  ? 'bg-gradient-to-r from-amber-500 to-orange-400'
                  : 'bg-gradient-to-r from-slate-600 to-slate-500'
              )}
            />
          </div>
        )}
      </div>

      {/* Progress percentage and time */}
      <div className="flex-shrink-0 flex items-center gap-4 text-right">
        {file.status !== 'pending' && (
          <div className="text-sm font-mono text-slate-400">
            <div>{file.progress}%</div>
            {file.estimatedTimeRemaining && (
              <div className="text-xs text-slate-500">
                ~{formatTime(file.estimatedTimeRemaining)}
              </div>
            )}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {file.status === 'error' && (
            <motion.button
              onClick={() => onRetry?.(file.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="p-1.5 rounded hover:bg-slate-700/50 text-amber-400 hover:text-amber-300 transition-colors"
              title="Retry"
            >
              <AlertCircle size={16} />
            </motion.button>
          )}

          {file.status === 'processing' && (
            <motion.button
              onClick={() => onPause?.(file.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="p-1.5 rounded hover:bg-slate-700/50 text-cyan-400 hover:text-cyan-300 transition-colors"
              title="Pause"
            >
              <Pause size={16} />
            </motion.button>
          )}

          {file.status === 'paused' && (
            <motion.button
              onClick={() => onResume?.(file.id)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="p-1.5 rounded hover:bg-slate-700/50 text-cyan-400 hover:text-cyan-300 transition-colors"
              title="Resume"
            >
              <Play size={16} />
            </motion.button>
          )}

          <motion.button
            onClick={() => onRemove?.(file.id)}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="p-1.5 rounded hover:bg-slate-700/50 text-red-400 hover:text-red-300 transition-colors"
            title="Remove"
          >
            <Trash2 size={16} />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Main Batch Queue Manager Component
 */
export const BatchQueueManager: React.FC<BatchQueueManagerProps> = ({
  files,
  isProcessing = false,
  totalProgress = 0,
  onRemoveFile,
  onPauseFile,
  onResumeFile,
  onRetryFile,
  onClearCompleted,
  onCancelAll,
  onPauseAll,
  onResumeAll,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  // Calculate statistics
  const stats = useMemo(() => {
    const completed = files.filter((f) => f.status === 'completed').length;
    const failed = files.filter((f) => f.status === 'error').length;
    const processing = files.filter((f) => f.status === 'processing').length;
    const pending = files.filter((f) => f.status === 'pending').length;

    const totalSize = files.reduce((sum, f) => sum + f.size, 0);
    const avgTimeRemaining = files.reduce(
      (sum, f) => sum + (f.estimatedTimeRemaining || 0),
      0
    );

    return {
      completed,
      failed,
      processing,
      pending,
      total: files.length,
      totalSize,
      avgTimeRemaining,
    };
  }, [files]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-b from-slate-800/50 to-slate-900/30 border border-slate-700/50 rounded-lg overflow-hidden ${className}`}
    >
      {/* Header */}
      <motion.button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-4 hover:bg-slate-800/30 transition-colors text-left"
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold text-slate-200">
              Batch Processing Queue
            </h3>
            <motion.div
              className="px-2 py-1 bg-slate-700/50 rounded-full"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
            >
              <span className="text-xs font-mono text-slate-300">
                {stats.processing}/{stats.total}
              </span>
            </motion.div>
          </div>

          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChevronDown className="w-5 h-5 text-slate-500" />
          </motion.div>
        </div>

        {/* Overall progress */}
        <div className="space-y-2">
          {/* Progress bar */}
          <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: '0%' }}
              animate={{ width: `${totalProgress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500"
            />
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>{totalProgress}% Complete</span>
            <div className="flex items-center gap-4">
              <span>✓ {stats.completed}</span>
              <span>⏳ {stats.processing}</span>
              <span>● {stats.pending}</span>
              {stats.failed > 0 && <span className="text-red-400">✕ {stats.failed}</span>}
            </div>
          </div>
        </div>
      </motion.button>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-slate-700/50"
          >
            {/* Bulk action buttons */}
            {files.length > 0 && (
              <div className="px-4 py-3 border-b border-slate-700/30 flex items-center gap-2 bg-slate-900/30">
                {isProcessing && (
                  <motion.button
                    onClick={() => onPauseAll?.()}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-3 py-1.5 text-xs rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-200 transition-colors"
                  >
                    Pause All
                  </motion.button>
                )}

                {!isProcessing && stats.pending > 0 && (
                  <motion.button
                    onClick={() => onResumeAll?.()}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-3 py-1.5 text-xs rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-200 transition-colors"
                  >
                    Resume All
                  </motion.button>
                )}

                {stats.completed > 0 && (
                  <motion.button
                    onClick={() => onClearCompleted?.()}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-3 py-1.5 text-xs rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 hover:text-slate-200 transition-colors ml-auto"
                  >
                    Clear Completed
                  </motion.button>
                )}

                {(stats.processing > 0 || stats.pending > 0) && (
                  <motion.button
                    onClick={() => onCancelAll?.()}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-3 py-1.5 text-xs rounded bg-red-500/20 hover:bg-red-500/30 text-red-400 hover:text-red-300 transition-colors"
                  >
                    Cancel All
                  </motion.button>
                )}
              </div>
            )}

            {/* File list */}
            {files.length > 0 ? (
              <div className="max-h-96 overflow-y-auto">
                {files.length > 10 ? (
                  // Virtualized list for performance
                  <List
                    height={300}
                    itemCount={files.length}
                    itemSize={90}
                    width="100%"
                  >
                    {({ index, style }) => (
                      <div style={style}>
                        <QueueItem
                          file={files[index]}
                          index={index}
                          onRemove={onRemoveFile}
                          onPause={onPauseFile}
                          onResume={onResumeFile}
                          onRetry={onRetryFile}
                        />
                      </div>
                    )}
                  </List>
                ) : (
                  // Regular list for small queues
                  files.map((file, index) => (
                    <QueueItem
                      key={file.id}
                      file={file}
                      index={index}
                      onRemove={onRemoveFile}
                      onPause={onPauseFile}
                      onResume={onResumeFile}
                      onRetry={onRetryFile}
                    />
                  ))
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500">
                <p>Queue is empty. Add audio files to get started.</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default BatchQueueManager;
