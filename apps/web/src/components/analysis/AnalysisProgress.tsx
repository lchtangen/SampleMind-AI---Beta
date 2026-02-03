'use client';

/**
 * ANALYSIS PROGRESS COMPONENT
 * Real-time multi-stage progress tracking for audio analysis
 * Shows current stage, progress percentage, and estimated time remaining
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, AlertCircle, ChevronDown } from 'lucide-react';

export type AnalysisStage =
  | 'loading'
  | 'preprocessing'
  | 'feature_extraction'
  | 'neural_analysis'
  | 'semantic_search'
  | 'ai_analysis'
  | 'completed'
  | 'error';

export interface AnalysisProgressStage {
  id: string;
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'error';
  progress: number; // 0-100
  startedAt?: Date;
  completedAt?: Date;
  duration?: number; // milliseconds
  error?: string;
}

interface AnalysisProgressProps {
  currentStage: AnalysisStage;
  stages: AnalysisProgressStage[];
  totalProgress: number; // 0-100
  estimatedTimeRemaining?: number; // seconds
  isExpanded?: boolean;
  onToggleExpanded?: (expanded: boolean) => void;
  className?: string;
}

/**
 * Stage icon component
 */
const StageIcon: React.FC<{
  status: AnalysisProgressStage['status'];
}> = ({ status }) => {
  if (status === 'completed') {
    return (
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 400, damping: 15 }}
      >
        <CheckCircle2 className="w-5 h-5 text-green-500" />
      </motion.div>
    );
  }

  if (status === 'in-progress') {
    return (
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}>
        <Loader2 className="w-5 h-5 text-cyan-500" />
      </motion.div>
    );
  }

  if (status === 'error') {
    return <AlertCircle className="w-5 h-5 text-red-500" />;
  }

  return (
    <div className="w-5 h-5 rounded-full border border-slate-600 bg-slate-800/50" />
  );
};

/**
 * Individual stage component
 */
const Stage: React.FC<{
  stage: AnalysisProgressStage;
  index: number;
  isExpanded: boolean;
}> = ({ stage, index, isExpanded }) => {
  const durationMs = stage.duration || 0;
  const durationSecs = (durationMs / 1000).toFixed(2);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="relative"
    >
      {/* Connector line */}
      {index < 6 && (
        <div
          className={`absolute left-2.5 top-10 w-0.5 h-8 ${
            stage.status === 'completed'
              ? 'bg-gradient-to-b from-green-500 to-green-500/20'
              : 'bg-gradient-to-b from-slate-600 to-slate-600/20'
          }`}
        />
      )}

      {/* Stage item */}
      <div className="flex items-start gap-4 pb-6 relative z-10">
        <StageIcon status={stage.status} />

        <div className="flex-1 min-w-0">
          {/* Stage name and status */}
          <div className="flex items-center justify-between mb-2">
            <h4
              className={`font-medium text-sm ${
                stage.status === 'completed'
                  ? 'text-slate-300'
                  : stage.status === 'in-progress'
                  ? 'text-cyan-400'
                  : stage.status === 'error'
                  ? 'text-red-400'
                  : 'text-slate-500'
              }`}
            >
              {stage.name}
            </h4>

            {stage.status === 'in-progress' && (
              <span className="text-xs text-cyan-400/70 font-mono">
                {stage.progress}%
              </span>
            )}

            {stage.completedAt && (
              <span className="text-xs text-slate-500 font-mono">
                {durationSecs}s
              </span>
            )}
          </div>

          {/* Progress bar */}
          {isExpanded && stage.status !== 'pending' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="w-full h-1.5 bg-slate-700/50 rounded-full overflow-hidden mb-2"
            >
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: `${stage.progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className={`h-full rounded-full ${
                  stage.status === 'completed'
                    ? 'bg-gradient-to-r from-green-500 to-green-400'
                    : stage.status === 'in-progress'
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-400'
                    : stage.status === 'error'
                    ? 'bg-gradient-to-r from-red-500 to-red-400'
                    : 'bg-gradient-to-r from-slate-600 to-slate-500'
                }`}
              />
            </motion.div>
          )}

          {/* Error message */}
          <AnimatePresence>
            {stage.error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="text-xs text-red-400/70 mt-1"
              >
                {stage.error}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Main Analysis Progress Component
 */
export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  currentStage,
  stages,
  totalProgress,
  estimatedTimeRemaining = 0,
  isExpanded: initialIsExpanded = false,
  onToggleExpanded,
  className = '',
}) => {
  const [isExpanded, setIsExpanded] = useState(initialIsExpanded);

  const handleToggle = (expanded: boolean) => {
    setIsExpanded(expanded);
    onToggleExpanded?.(expanded);
  };

  const currentStageData = stages.find(
    (s) => s.id === currentStage || s.status === 'in-progress'
  );

  const completedCount = stages.filter(
    (s) => s.status === 'completed'
  ).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-b from-slate-800/50 to-slate-900/30 border border-slate-700/50 rounded-lg overflow-hidden ${className}`}
    >
      {/* Header - Compact view */}
      <motion.button
        onClick={() => handleToggle(!isExpanded)}
        className="w-full px-4 py-4 hover:bg-slate-800/30 transition-colors text-left"
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {/* Title */}
            <div className="flex items-center gap-3 mb-3">
              <div className="flex-shrink-0">
                {currentStage === 'completed' || currentStage === 'error' ? (
                  currentStage === 'error' ? (
                    <AlertCircle className="w-5 h-5 text-red-500" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  )
                ) : (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  >
                    <Loader2 className="w-5 h-5 text-cyan-500" />
                  </motion.div>
                )}
              </div>
              <h3 className="font-semibold text-slate-200">
                {currentStage === 'completed'
                  ? 'Analysis Complete'
                  : currentStage === 'error'
                  ? 'Analysis Failed'
                  : `Analyzing... ${currentStageData?.name || 'Processing'}`}
              </h3>
            </div>

            {/* Progress bar */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2 bg-slate-700/50 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: '0%' }}
                  animate={{ width: `${totalProgress}%` }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                  className={`h-full rounded-full ${
                    currentStage === 'error'
                      ? 'bg-gradient-to-r from-red-500 to-red-400'
                      : currentStage === 'completed'
                      ? 'bg-gradient-to-r from-green-500 to-green-400'
                      : 'bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500'
                  }`}
                />
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-mono text-slate-400 min-w-[3rem] text-right">
                  {totalProgress}%
                </span>

                {estimatedTimeRemaining > 0 && currentStage !== 'completed' && (
                  <span className="text-xs text-slate-500 min-w-[4rem] text-right">
                    ~{Math.ceil(estimatedTimeRemaining)}s left
                  </span>
                )}
              </div>
            </div>

            {/* Stage summary */}
            <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
              <span>{completedCount} of {stages.length} stages complete</span>
              {currentStageData && (
                <span className="text-cyan-400/60">
                  • Currently: {currentStageData.name}
                </span>
              )}
            </div>
          </div>

          {/* Toggle button */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
            className="flex-shrink-0 ml-4"
          >
            <ChevronDown className="w-5 h-5 text-slate-500" />
          </motion.div>
        </div>
      </motion.button>

      {/* Expanded view - Detailed stages */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-slate-700/50 px-4 py-4 bg-slate-900/30"
          >
            <div className="space-y-2">
              {stages.map((stage, index) => (
                <Stage
                  key={stage.id}
                  stage={stage}
                  index={index}
                  isExpanded={isExpanded}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default AnalysisProgress;
