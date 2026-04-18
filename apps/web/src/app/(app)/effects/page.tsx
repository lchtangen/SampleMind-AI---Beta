/**
 * @fileoverview Effects Chain Builder page for the SampleMind AI app shell.
 *
 * Displays available audio effects as a grid, a horizontal chain area for
 * drag-and-drop composition, audio input/output endpoints, and an apply
 * button. Powered by Pedalboard on the backend.
 *
 * @module app/(app)/effects/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  Sliders,
  AudioWaveform,
  ArrowRight,
  Waves,
  Timer,
  Music2,
  Disc3,
  Gauge,
  Zap,
  Plus,
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

interface Effect {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  border: string;
  glow: string;
}

const EFFECTS: Effect[] = [
  { name: 'EQ',         icon: Sliders, color: 'text-cyber-cyan',    border: 'border-cyber-cyan/30',    glow: 'hover:shadow-glow-cyan' },
  { name: 'Compressor', icon: Gauge,   color: 'text-cyber-purple',  border: 'border-cyber-purple/30',  glow: 'hover:shadow-glow-purple' },
  { name: 'Reverb',     icon: Waves,   color: 'text-cyber-blue',    border: 'border-cyber-blue/30',    glow: 'hover:shadow-glow-blue' },
  { name: 'Delay',      icon: Timer,   color: 'text-cyber-magenta', border: 'border-cyber-magenta/30', glow: 'hover:shadow-glow-magenta' },
  { name: 'Chorus',     icon: Music2,  color: 'text-cyber-cyan',    border: 'border-cyber-cyan/30',    glow: 'hover:shadow-glow-cyan' },
  { name: 'Distortion', icon: Zap,     color: 'text-cyber-magenta', border: 'border-cyber-magenta/30', glow: 'hover:shadow-glow-magenta' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function EffectsPage() {
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
          <Sliders className="h-6 w-6 text-cyber-cyan" />
          Effects Chain Builder
        </h2>
        <p className="text-sm text-text-tertiary mt-1">
          Drag effects to build your processing chain
        </p>
      </motion.div>

      {/* ── Available Effects Grid ─────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="space-y-3">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          Available Effects
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {EFFECTS.map((fx) => (
            <div
              key={fx.name}
              className={`glass rounded-glass p-4 flex flex-col items-center gap-2
                          cursor-grab active:cursor-grabbing transition-all duration-300
                          ${fx.glow}`}
            >
              <div className={`h-11 w-11 rounded-xl bg-glass-light border ${fx.border}
                               flex items-center justify-center`}>
                <fx.icon className={`h-5 w-5 ${fx.color}`} />
              </div>
              <span className="text-xs font-medium text-text-secondary">{fx.name}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Chain Area ─────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="space-y-3">
        <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
          Processing Chain
        </h3>
        <div className="glass rounded-glass-lg p-6">
          <div className="flex items-center gap-4">
            {/* Audio Input */}
            <div className="flex flex-col items-center gap-1 flex-shrink-0">
              <div className="h-12 w-12 rounded-xl bg-cyber-cyan/10 border border-cyber-cyan/30
                              flex items-center justify-center">
                <AudioWaveform className="h-5 w-5 text-cyber-cyan" />
              </div>
              <span className="text-[10px] text-text-tertiary">Input</span>
            </div>

            <ArrowRight className="h-4 w-4 text-text-tertiary flex-shrink-0" />

            {/* Drop zone */}
            <div className="flex-1 border-2 border-dashed border-glass-border rounded-glass
                            py-8 flex items-center justify-center text-center
                            hover:border-cyber-cyan/30 transition-colors duration-200">
              <div className="flex flex-col items-center gap-2">
                <Plus className="h-6 w-6 text-text-tertiary/40" />
                <p className="text-sm text-text-tertiary">
                  Drop effects here to build your chain
                </p>
              </div>
            </div>

            <ArrowRight className="h-4 w-4 text-text-tertiary flex-shrink-0" />

            {/* Audio Output */}
            <div className="flex flex-col items-center gap-1 flex-shrink-0">
              <div className="h-12 w-12 rounded-xl bg-cyber-purple/10 border border-cyber-purple/30
                              flex items-center justify-center">
                <Disc3 className="h-5 w-5 text-cyber-purple" />
              </div>
              <span className="text-[10px] text-text-tertiary">Output</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* ── Apply Button ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex justify-center">
        <button
          disabled
          className="px-8 py-3 rounded-glass font-semibold text-sm
                     bg-cyber-cyan/20 text-cyber-cyan/40 border border-cyber-cyan/20
                     cursor-not-allowed flex items-center gap-2"
        >
          <Zap className="h-4 w-4" />
          Apply Chain
        </button>
      </motion.div>
    </motion.div>
  );
}
