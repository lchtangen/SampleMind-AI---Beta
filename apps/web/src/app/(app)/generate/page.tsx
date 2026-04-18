/**
 * @fileoverview AI Generate page for the SampleMind AI app shell.
 *
 * Prompt textarea, generation settings (duration, style, temperature),
 * generate button, and output area — powered by Meta AudioCraft on the
 * backend.
 *
 * @module app/(app)/generate/page
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Sparkles,
  Clock,
  Palette,
  Thermometer,
  AudioWaveform,
  Wand2,
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

const STYLES = ['Electronic', 'Lo-Fi', 'Ambient', 'Hip Hop', 'Cinematic', 'Experimental'] as const;

// ─── Page Component ──────────────────────────────────────────────────────────

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('Electronic');

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-3xl mx-auto space-y-8"
    >
      {/* ── Header ────────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-text-primary flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-cyber-purple" />
          AI Audio Generation
        </h2>
        <p className="text-sm text-text-tertiary mt-1">
          Describe the sound you want and let AI create it
        </p>
      </motion.div>

      {/* ── Prompt Input ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-5 space-y-2">
        <label htmlFor="gen-prompt" className="text-xs font-medium text-text-secondary uppercase tracking-wider">
          Prompt
        </label>
        <textarea
          id="gen-prompt"
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. A dark, punchy 808 kick with a long sub-bass tail at 140 BPM…"
          className="w-full bg-dark-400 border border-glass-border rounded-glass-sm p-4
                     text-text-primary placeholder-text-tertiary text-sm outline-none resize-none
                     focus:border-cyber-purple/50 focus:shadow-glow-purple transition-all duration-200"
        />
      </motion.div>

      {/* ── Generation Settings ───────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Duration */}
        <div className="glass rounded-glass p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-medium text-text-secondary uppercase tracking-wider">
            <Clock className="h-3.5 w-3.5 text-cyber-cyan" />
            Duration
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-1.5 rounded-full bg-dark-300 relative">
              <div className="absolute left-0 top-0 h-full w-1/2 rounded-full bg-gradient-to-r from-cyber-cyan to-cyber-purple" />
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                              h-4 w-4 rounded-full bg-dark-200 border-2 border-cyber-cyan shadow-glow-cyan" />
            </div>
            <span className="text-sm text-text-primary font-mono">5.0 s</span>
          </div>
        </div>

        {/* Style */}
        <div className="glass rounded-glass p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-medium text-text-secondary uppercase tracking-wider">
            <Palette className="h-3.5 w-3.5 text-cyber-purple" />
            Style
          </div>
          <div className="flex flex-wrap gap-1.5">
            {STYLES.map((s) => (
              <button
                key={s}
                onClick={() => setSelectedStyle(s)}
                className={`px-2 py-1 rounded-full text-[10px] font-medium transition-all duration-200
                  ${selectedStyle === s
                    ? 'bg-cyber-purple/20 text-cyber-purple border border-cyber-purple/40'
                    : 'bg-glass-light text-text-tertiary border border-glass-border hover:text-text-secondary'
                  }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Temperature */}
        <div className="glass rounded-glass p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-medium text-text-secondary uppercase tracking-wider">
            <Thermometer className="h-3.5 w-3.5 text-cyber-magenta" />
            Temperature
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1 h-1.5 rounded-full bg-dark-300 relative">
              <div className="absolute left-0 top-0 h-full w-[70%] rounded-full bg-gradient-to-r from-cyber-magenta to-cyber-purple" />
              <div className="absolute top-1/2 left-[70%] -translate-x-1/2 -translate-y-1/2
                              h-4 w-4 rounded-full bg-dark-200 border-2 border-cyber-magenta shadow-glow-magenta" />
            </div>
            <span className="text-sm text-text-primary font-mono">0.7</span>
          </div>
        </div>
      </motion.div>

      {/* ── Generate Button ───────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex justify-center">
        <button
          disabled={!prompt.trim()}
          className={`px-8 py-3 rounded-glass font-semibold text-sm flex items-center gap-2
                      transition-all duration-300
                      ${prompt.trim()
                        ? 'bg-gradient-to-r from-cyber-purple to-cyber-magenta text-white hover:shadow-glow-purple'
                        : 'bg-cyber-purple/10 text-cyber-purple/40 border border-cyber-purple/20 cursor-not-allowed'
                      }`}
        >
          <Wand2 className="h-4 w-4" />
          Generate Audio
        </button>
      </motion.div>

      {/* ── Output Area ───────────────────────────────────────────────── */}
      <motion.div
        variants={itemVariants}
        className="glass rounded-glass-lg py-16 flex flex-col items-center justify-center text-center"
      >
        <AudioWaveform className="h-12 w-12 text-text-tertiary/30 mb-3" />
        <p className="text-text-secondary font-medium">Generated audio will appear here</p>
        <p className="text-sm text-text-tertiary mt-1">
          Enter a prompt and click Generate to create audio
        </p>
      </motion.div>
    </motion.div>
  );
}
