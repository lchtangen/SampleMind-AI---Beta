'use client';

/**
 * ONBOARDING FLOW COMPONENT
 * Interactive 4-step tutorial for new users
 * Features: Progress tracking, skip option, animations, feature highlights
 */

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, X, Check } from 'lucide-react';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  highlights?: {
    title: string;
    icon?: React.ReactNode;
  }[];
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingFlowProps {
  steps: OnboardingStep[];
  onComplete: () => void;
  onSkip?: () => void;
  allowSkip?: boolean;
}

/**
 * Main Onboarding Flow Component
 */
export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({
  steps,
  onComplete,
  onSkip,
  allowSkip = true,
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  const handleNext = useCallback(() => {
    if (isLastStep) {
      onComplete();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  }, [isLastStep, onComplete]);

  const handlePrevious = useCallback(() => {
    if (!isFirstStep) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [isFirstStep]);

  const handleSkip = useCallback(() => {
    onSkip?.();
  }, [onSkip]);

  const step = steps[currentStep];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={handleSkip}
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
      />

      {/* Modal */}
      <motion.div
        key={currentStep}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{
          type: 'spring',
          stiffness: 400,
          damping: 25,
        }}
        className="relative w-full max-w-2xl mx-4 rounded-2xl bg-gradient-to-b from-slate-800/95 to-slate-900/95 border border-slate-700/50 shadow-2xl overflow-hidden"
      >
        {/* Close button */}
        {allowSkip && (
          <button
            onClick={handleSkip}
            className="absolute top-4 right-4 p-2 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-slate-300 transition-colors z-10"
          >
            <X className="w-5 h-5" />
          </button>
        )}

        {/* Content */}
        <div className="p-8 md:p-12">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <h2 className="text-3xl font-bold text-slate-100 mb-2">
              {step.title}
            </h2>
            <p className="text-slate-400">{step.description}</p>
          </motion.div>

          {/* Main content */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            {step.content}
          </motion.div>

          {/* Highlights */}
          {step.highlights && step.highlights.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              {step.highlights.map((highlight, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-start gap-3 p-4 rounded-lg bg-slate-700/20 border border-slate-700/50"
                >
                  {highlight.icon && (
                    <div className="flex-shrink-0 mt-1 text-cyan-400">
                      {highlight.icon}
                    </div>
                  )}
                  <div>
                    <h4 className="font-semibold text-slate-200">
                      {highlight.title}
                    </h4>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {/* Custom action button */}
          {step.action && (
            <motion.button
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              onClick={step.action.onClick}
              className="w-full mb-8 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-900 font-semibold hover:from-cyan-400 hover:to-blue-400 transition-all"
            >
              {step.action.label}
            </motion.button>
          )}

          {/* Progress indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-between mb-8"
          >
            <div className="flex gap-2">
              {steps.map((_, index) => (
                <motion.div
                  key={index}
                  className={`h-2 rounded-full transition-all ${
                    index === currentStep
                      ? 'w-8 bg-cyan-500'
                      : index < currentStep
                      ? 'w-2 bg-green-500'
                      : 'w-2 bg-slate-600'
                  }`}
                  layoutId={`progress-${index}`}
                />
              ))}
            </div>
            <span className="text-sm text-slate-400">
              {currentStep + 1} of {steps.length}
            </span>
          </motion.div>

          {/* Navigation buttons */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex items-center justify-between gap-4"
          >
            <div className="flex gap-3">
              {!isFirstStep && (
                <button
                  onClick={handlePrevious}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg text-slate-400 hover:text-slate-300 hover:bg-slate-700/50 transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
              )}
            </div>

            <div className="flex items-center gap-3">
              {allowSkip && !isLastStep && (
                <button
                  onClick={handleSkip}
                  className="px-4 py-2 rounded-lg text-slate-400 hover:text-slate-300 hover:bg-slate-700/50 transition-colors"
                >
                  Skip
                </button>
              )}

              <button
                onClick={handleNext}
                className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-900 font-semibold hover:from-cyan-400 hover:to-blue-400 transition-all"
              >
                {isLastStep ? (
                  <>
                    <Check className="w-4 h-4" />
                    Complete
                  </>
                ) : (
                  <>
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

/**
 * Default onboarding steps for SampleMind AI
 */
export const DEFAULT_ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to SampleMind AI',
    description:
      'Professional audio intelligence powered by advanced AI and neural networks',
    content: (
      <div className="space-y-4">
        <div className="w-full h-48 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-slate-700/50 flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-2">🎵</div>
            <p className="text-slate-400">Advanced Audio Analysis Platform</p>
          </div>
        </div>
      </div>
    ),
    highlights: [
      {
        title: 'Neural Analysis',
        icon: '🧠',
      },
      {
        title: 'Semantic Search',
        icon: '🔍',
      },
      {
        title: 'AI Insights',
        icon: '✨',
      },
      {
        title: 'Batch Processing',
        icon: '⚡',
      },
    ],
  },
  {
    id: 'upload',
    title: 'Upload Audio Files',
    description: 'Start by uploading your audio samples for analysis',
    content: (
      <div className="space-y-4">
        <div className="w-full h-48 rounded-lg bg-slate-700/30 border-2 border-dashed border-slate-600 flex items-center justify-center cursor-pointer hover:border-cyan-500 transition-colors">
          <div className="text-center">
            <div className="text-4xl mb-2">📁</div>
            <p className="text-slate-400">Drag files here or click to browse</p>
          </div>
        </div>
        <p className="text-sm text-slate-500">
          Supported formats: MP3, WAV, FLAC, AIFF, OGG, M4A (up to 100 MB)
        </p>
      </div>
    ),
    highlights: [
      {
        title: 'Drag & Drop Support',
        icon: '📥',
      },
      {
        title: 'Multiple File Upload',
        icon: '📚',
      },
    ],
    action: {
      label: 'Start Uploading',
      onClick: () => console.log('Upload action'),
    },
  },
  {
    id: 'analyze',
    title: 'Analyze Your Audio',
    description:
      'Run analysis to extract features, tags, and AI insights from your audio',
    content: (
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {['🎶 Tempo & Key', '📊 Spectrum', '🎯 Genre', '💫 Mood'].map(
            (item, i) => (
              <div
                key={i}
                className="p-4 rounded-lg bg-slate-700/20 border border-slate-700/50 text-center"
              >
                <p className="text-slate-300">{item}</p>
              </div>
            )
          )}
        </div>
      </div>
    ),
    highlights: [
      {
        title: 'Multiple Analysis Levels',
        icon: '📈',
      },
      {
        title: 'Real-time Processing',
        icon: '⚡',
      },
    ],
  },
  {
    id: 'explore',
    title: 'Explore Results & Library',
    description:
      'Browse analysis results, create collections, and search your library',
    content: (
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-3">
          {['Dashboard', 'Library', 'Search'].map((item, i) => (
            <div
              key={i}
              className="p-4 rounded-lg bg-gradient-to-br from-slate-700/30 to-slate-800/30 border border-slate-700/50 text-center cursor-pointer hover:border-cyan-500/50 transition-colors"
            >
              <p className="text-slate-300 text-sm font-medium">{item}</p>
            </div>
          ))}
        </div>
      </div>
    ),
    highlights: [
      {
        title: 'Semantic Search',
        icon: '🔍',
      },
      {
        title: 'Smart Collections',
        icon: '📂',
      },
    ],
    action: {
      label: "Let's Get Started",
      onClick: () => console.log('Complete onboarding'),
    },
  },
];

export default OnboardingFlow;
