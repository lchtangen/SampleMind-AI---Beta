/**
 * @fileoverview Genre Classification dashboard for the SampleMind AI app shell.
 *
 * Upload / select audio for genre analysis, view confidence bars with gradient
 * fills, a genre tag cloud, and a detailed breakdown panel. Uses the SVM +
 * XGBoost + KNN soft-voting ensemble classifier on the backend.
 *
 * @module app/(app)/genre/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  Tag,
  Upload,
  Music2,
  BarChart3,
  Layers,
} from 'lucide-react';

// ─── Animation variants ──────────────────────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] } },
};

// ─── Static data ─────────────────────────────────────────────────────────────

const GENRE_RESULTS = [
  { genre: 'Electronic', confidence: 85, color: 'from-cyber-cyan to-cyber-blue' },
  { genre: 'Hip Hop', confidence: 62, color: 'from-cyber-purple to-cyber-magenta' },
  { genre: 'Trap', confidence: 54, color: 'from-cyber-magenta to-cyber-purple' },
  { genre: 'Lo-Fi', confidence: 38, color: 'from-cyber-blue to-cyber-cyan' },
  { genre: 'Ambient', confidence: 21, color: 'from-cyber-cyan to-cyber-purple' },
];

const TAG_CLOUD = [
  'Electronic', 'Trap', 'Hip Hop', 'Lo-Fi', 'Ambient', 'Bass Music',
  'Future Bass', 'Synthwave', 'Dubstep', 'Drum & Bass', 'House', 'Techno',
  'Chill', 'Dark', 'Experimental',
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function GenrePage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* ── Header ────────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-text-primary flex items-center gap-2">
          <Tag className="h-6 w-6 text-cyber-magenta" />
          Genre Classification
        </h2>
        <p className="text-sm text-text-tertiary mt-1">
          AI-powered genre detection using ensemble classifiers
        </p>
      </motion.div>

      {/* ── Upload / Select Section ───────────────────────────────────── */}
      <motion.div
        variants={itemVariants}
        className="glass rounded-glass-lg border-2 border-dashed border-glass-border
                   p-8 flex flex-col items-center justify-center text-center
                   hover:border-cyber-magenta/40 transition-colors duration-300 cursor-pointer"
      >
        <div className="h-14 w-14 rounded-2xl bg-glass-light border border-glass-border
                        flex items-center justify-center mb-3">
          <Upload className="h-7 w-7 text-text-tertiary" />
        </div>
        <p className="text-base font-semibold text-text-primary mb-1">
          Upload or select an audio file
        </p>
        <p className="text-sm text-text-tertiary">
          Drop a file here or click to browse your library
        </p>
      </motion.div>

      {/* ── Confidence Bars ───────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-6 space-y-5">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-cyber-purple" />
          <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Classification Results
          </h3>
        </div>
        <div className="space-y-4">
          {GENRE_RESULTS.map((g) => (
            <div key={g.genre}>
              <div className="flex items-center justify-between text-sm mb-1.5">
                <span className="text-text-primary font-medium">{g.genre}</span>
                <span className="text-text-tertiary font-mono">{g.confidence}%</span>
              </div>
              <div className="h-3 rounded-full bg-dark-300 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${g.confidence}%` }}
                  transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1], delay: 0.3 }}
                  className={`h-full rounded-full bg-gradient-to-r ${g.color}`}
                />
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Tag Cloud + Detailed Breakdown ────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tag Cloud */}
        <motion.div variants={itemVariants} className="glass rounded-glass p-6">
          <div className="flex items-center gap-2 mb-4">
            <Tag className="h-5 w-5 text-cyber-cyan" />
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Genre Tags
            </h3>
          </div>
          <div className="flex flex-wrap gap-2">
            {TAG_CLOUD.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1.5 rounded-full text-xs font-medium
                           bg-glass-light border border-glass-border text-text-secondary
                           hover:bg-cyber-cyan/10 hover:text-cyber-cyan hover:border-cyber-cyan/30
                           transition-all duration-200 cursor-pointer"
              >
                {tag}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Detailed Breakdown */}
        <motion.div variants={itemVariants} className="glass rounded-glass p-6">
          <div className="flex items-center gap-2 mb-4">
            <Layers className="h-5 w-5 text-cyber-magenta" />
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Detailed Breakdown
            </h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-glass-border">
              <span className="text-sm text-text-secondary">Primary Genre</span>
              <span className="text-sm font-semibold text-cyber-cyan">Electronic</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-glass-border">
              <span className="text-sm text-text-secondary">Sub-genre</span>
              <span className="text-sm font-semibold text-cyber-purple">Future Bass</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-glass-border">
              <span className="text-sm text-text-secondary">Mood</span>
              <span className="text-sm font-semibold text-cyber-magenta">Energetic</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm text-text-secondary">Classifier</span>
              <span className="text-sm text-text-tertiary">SVM + XGBoost + KNN ensemble</span>
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
