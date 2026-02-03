'use client';

/**
 * AI CONFIDENCE METER COMPONENT
 * Animated progress bar showing AI model confidence levels
 * Color-coded: High (green) > Medium (blue) > Low (magenta)
 * Includes expandable details for model info and factors
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, AlertCircle, CheckCircle2 } from 'lucide-react';

interface ConfidenceFactor {
  name: string;
  weight: number; // 0-1
  contribution: number; // -1 to 1 (negative = reduces confidence)
}

interface AIConfidenceMeterProps {
  confidence: number; // 0-100
  modelName?: string;
  timestamp?: Date;
  factors?: ConfidenceFactor[];
  showDetails?: boolean;
  className?: string;
  onToggleDetails?: (expanded: boolean) => void;
}

/**
 * Get confidence color based on level
 */
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 80) {
    return {
      bg: 'from-green-500 to-green-400',
      glow: 'glow-text-green-500',
      label: 'High Confidence',
      textColor: 'text-green-400',
    };
  }

  if (confidence >= 60) {
    return {
      bg: 'from-blue-500 to-cyan-400',
      glow: 'glow-text-blue-500',
      label: 'Medium Confidence',
      textColor: 'text-blue-400',
    };
  }

  return {
    bg: 'from-magenta-500 to-pink-400',
    glow: 'glow-text-magenta-500',
    label: 'Low Confidence',
    textColor: 'text-magenta-400',
  };
};

/**
 * Main AI Confidence Meter Component
 */
export const AIConfidenceMeter: React.FC<AIConfidenceMeterProps> = ({
  confidence,
  modelName = 'Gemini 3 Flash',
  timestamp,
  factors = [],
  showDetails: initialShowDetails = false,
  className = '',
  onToggleDetails,
}) => {
  const [showDetails, setShowDetails] = useState(initialShowDetails);
  const colorConfig = getConfidenceColor(confidence);

  const handleToggleDetails = (expanded: boolean) => {
    setShowDetails(expanded);
    onToggleDetails?.(expanded);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gradient-to-r from-slate-800/50 to-slate-900/30 border border-slate-700/50 rounded-lg p-4 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {confidence >= 60 ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
            >
              <CheckCircle2
                className={`w-5 h-5 ${colorConfig.textColor}`}
              />
            </motion.div>
          ) : (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 400, damping: 15 }}
            >
              <AlertCircle className="w-5 h-5 text-amber-400" />
            </motion.div>
          )}

          <div>
            <h4 className="font-semibold text-slate-200 text-sm">
              AI Confidence
            </h4>
            <p className={`text-xs ${colorConfig.textColor}`}>
              {colorConfig.label}
            </p>
          </div>
        </div>

        {/* Confidence percentage */}
        <motion.div
          className="text-right"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
        >
          <div
            className={`text-2xl font-bold ${colorConfig.textColor}`}
          >
            {confidence.toFixed(0)}%
          </div>
          <p className="text-xs text-slate-500">{modelName}</p>
        </motion.div>
      </div>

      {/* Main confidence bar */}
      <div className="mb-4">
        <div className="h-3 bg-slate-700/50 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${confidence}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full bg-gradient-to-r ${colorConfig.bg} rounded-full shadow-lg`}
            style={{
              boxShadow: `0 0 20px ${
                confidence >= 80
                  ? 'hsl(142, 71%, 45%)'
                  : confidence >= 60
                  ? 'hsl(206, 100%, 50%)'
                  : 'hsl(280, 85%, 60%)'
              }`,
            }}
          />
        </div>

        {/* Scale indicators */}
        <div className="flex justify-between mt-1">
          <span className="text-xs text-slate-600">0%</span>
          <span className="text-xs text-slate-600">50%</span>
          <span className="text-xs text-slate-600">100%</span>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
        <span>{modelName}</span>
        {timestamp && (
          <span>{timestamp.toLocaleTimeString()}</span>
        )}
      </div>

      {/* Toggle details button */}
      {factors.length > 0 && (
        <motion.button
          onClick={() => handleToggleDetails(!showDetails)}
          className="w-full px-3 py-2 text-sm text-slate-400 hover:text-slate-300 hover:bg-slate-700/30 rounded transition-colors flex items-center justify-between"
        >
          <span>Confidence Factors</span>
          <motion.div
            animate={{ rotate: showDetails ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <ChevronDown size={16} />
          </motion.div>
        </motion.button>
      )}

      {/* Expanded factors view */}
      <AnimatePresence>
        {showDetails && factors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-3 pt-3 border-t border-slate-700/30 space-y-2"
          >
            {factors.map((factor, index) => {
              const isPositive = factor.contribution > 0;
              const absContribution = Math.abs(factor.contribution);

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="text-xs"
                >
                  {/* Factor name and contribution */}
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-slate-300">{factor.name}</span>
                    <span
                      className={`font-mono ${
                        isPositive
                          ? 'text-green-400'
                          : 'text-red-400'
                      }`}
                    >
                      {isPositive ? '+' : '-'}
                      {(absContribution * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Factor weight bar */}
                  <div className="h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: '0%' }}
                      animate={{ width: `${factor.weight * 100}%` }}
                      transition={{ duration: 0.5, ease: 'easeOut', delay: index * 0.05 }}
                      className={`h-full bg-gradient-to-r ${
                        isPositive
                          ? 'from-green-500 to-green-400'
                          : 'from-red-500 to-red-400'
                      }`}
                    />
                  </div>
                </motion.div>
              );
            })}

            {/* Summary */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: factors.length * 0.05 + 0.1 }}
              className="mt-3 pt-3 border-t border-slate-700/30 text-xs text-slate-500"
            >
              <p>
                Based on {factors.length} confidence factors from{' '}
                <span className="text-slate-300">{modelName}</span>
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default AIConfidenceMeter;
