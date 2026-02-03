'use client';

/**
 * MUSIC THEORY CARD COMPONENT
 * Displays musical information (BPM, Key, Mood) with audio-reactive animations
 * Features: Glassmorphism, glow effects, confidence indicators, animated values
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Music,
  Zap,
  Smile,
  Gauge,
  Music2,
  BarChart3,
  ChevronUp,
} from 'lucide-react';

export type CardType = 'tempo' | 'key' | 'mood' | 'energy' | 'genre' | 'confidence';

interface MusicTheoryCardProps {
  type: CardType;
  value: string;
  label?: string;
  confidence?: number; // 0-100
  icon?: React.ReactNode;
  gradient?: string;
  glowColor?: string;
  subValue?: string;
  subLabel?: string;
  isAudioReactive?: boolean;
  amplitude?: number;
  className?: string;
  showDetails?: boolean;
}

/**
 * Get default configuration for card type
 */
const getCardConfig = (type: CardType) => {
  const configs: Record<CardType, {
    label: string;
    icon: React.ReactNode;
    gradient: string;
    glowColor: string;
    hslColor: string;
  }> = {
    tempo: {
      label: 'Tempo (BPM)',
      icon: <Gauge className="w-5 h-5" />,
      gradient: 'from-cyan-500 to-blue-500',
      glowColor: 'cyan',
      hslColor: 'hsl(180, 95%, 55%)',
    },
    key: {
      label: 'Musical Key',
      icon: <Music className="w-5 h-5" />,
      gradient: 'from-purple-500 to-magenta-500',
      glowColor: 'purple',
      hslColor: 'hsl(270, 85%, 65%)',
    },
    mood: {
      label: 'Mood',
      icon: <Smile className="w-5 h-5" />,
      gradient: 'from-green-500 to-emerald-500',
      glowColor: 'green',
      hslColor: 'hsl(142, 71%, 45%)',
    },
    energy: {
      label: 'Energy Level',
      icon: <Zap className="w-5 h-5" />,
      gradient: 'from-orange-500 to-red-500',
      glowColor: 'orange',
      hslColor: 'hsl(39, 100%, 50%)',
    },
    genre: {
      label: 'Genre',
      icon: <Music2 className="w-5 h-5" />,
      gradient: 'from-indigo-500 to-purple-500',
      glowColor: 'indigo',
      hslColor: 'hsl(262, 80%, 50%)',
    },
    confidence: {
      label: 'Confidence',
      icon: <BarChart3 className="w-5 h-5" />,
      gradient: 'from-teal-500 to-cyan-500',
      glowColor: 'teal',
      hslColor: 'hsl(174, 77%, 47%)',
    },
  };

  return configs[type];
};

/**
 * Individual Music Theory Card
 */
export const MusicTheoryCard: React.FC<MusicTheoryCardProps> = ({
  type,
  value,
  label,
  confidence = 85,
  icon,
  gradient,
  glowColor,
  subValue,
  subLabel = 'Range',
  isAudioReactive = false,
  amplitude = 0.5,
  className = '',
  showDetails = false,
}) => {
  const config = getCardConfig(type);
  const displayLabel = label || config.label;
  const displayGradient = gradient || config.gradient;
  const displayGlowColor = glowColor || config.glowColor;
  const displayIcon = icon || config.icon;

  const confidenceColor =
    confidence >= 80
      ? 'text-green-400'
      : confidence >= 60
      ? 'text-blue-400'
      : 'text-red-400';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{
        type: 'spring',
        stiffness: 400,
        damping: 25,
      }}
      className={`relative rounded-xl overflow-hidden group cursor-pointer ${className}`}
    >
      {/* Background with glassmorphism */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />

      {/* Animated gradient background */}
      <motion.div
        className={`absolute inset-0 opacity-0 group-hover:opacity-10 bg-gradient-to-br ${displayGradient} rounded-xl transition-opacity duration-300`}
      />

      {/* Glow effect on hover */}
      <motion.div
        initial={{ opacity: 0 }}
        whileHover={{ opacity: 1 }}
        className={`absolute -inset-1 bg-gradient-to-br ${displayGradient} rounded-xl blur-xl -z-10 group-hover:blur-2xl transition-all duration-300`}
      />

      {/* Content */}
      <div className="relative p-5 h-full flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className={`text-slate-400 group-hover:text-slate-300 transition-colors`}>
              {displayIcon}
            </div>
            <h3 className="text-xs font-semibold text-slate-400 group-hover:text-slate-300 transition-colors uppercase tracking-wider">
              {displayLabel}
            </h3>
          </div>

          {/* Confidence badge */}
          <motion.div
            className={`text-xs font-mono ${confidenceColor}`}
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            {confidence}%
          </motion.div>
        </div>

        {/* Main value */}
        <div className="flex-1 flex flex-col justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, type: 'spring', stiffness: 300 }}
            className={`text-3xl font-bold bg-gradient-to-r ${displayGradient} bg-clip-text text-transparent mb-2`}
          >
            {isAudioReactive ? (
              <motion.span
                animate={{ scale: [1, 1 + amplitude * 0.1, 1] }}
                transition={{ duration: 0.1 }}
              >
                {value}
              </motion.span>
            ) : (
              value
            )}
          </motion.div>

          {/* Sub value */}
          {subValue && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-sm text-slate-500"
            >
              <span className="text-slate-400">{subValue}</span>
              <span className="text-slate-600 ml-1">{subLabel}</span>
            </motion.p>
          )}
        </div>

        {/* Confidence meter */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-3 pt-3 border-t border-slate-700/30"
        >
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: '0%' }}
                animate={{ width: `${confidence}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className={`h-full bg-gradient-to-r ${displayGradient}`}
              />
            </div>
            <span className="text-xs text-slate-600 font-mono">
              {confidence}%
            </span>
          </div>
        </motion.div>

        {/* Expand indicator */}
        {showDetails && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-2 right-2"
          >
            <ChevronUp className="w-4 h-4 text-slate-500" />
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

/**
 * Music Theory Card Grid Container
 * Displays multiple theory cards in a responsive grid
 */
interface MusicTheoryGridProps {
  cards: MusicTheoryCardProps[];
  columns?: number;
  className?: string;
}

export const MusicTheoryGrid: React.FC<MusicTheoryGridProps> = ({
  cards,
  columns = 3,
  className = '',
}) => {
  return (
    <div
      className={`grid gap-4 ${
        columns === 2
          ? 'grid-cols-1 md:grid-cols-2'
          : columns === 3
          ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
          : 'grid-cols-1'
      } ${className}`}
    >
      {cards.map((card, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <MusicTheoryCard {...card} />
        </motion.div>
      ))}
    </div>
  );
};

export default MusicTheoryCard;
