/**
 * @fileoverview Upload page for the SampleMind AI app shell.
 *
 * Large drag-and-drop zone, supported format list, upload queue,
 * analysis level selector, and upload trigger button — all styled with
 * cyberpunk glassmorphism.
 *
 * @module app/(app)/upload/page
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Upload,
  FileAudio,
  Inbox,
  Gauge,
  BarChart3,
  Microscope,
  Crown,
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

const FORMATS = ['WAV', 'MP3', 'FLAC', 'OGG', 'AIFF'] as const;

interface AnalysisLevel {
  id: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const ANALYSIS_LEVELS: AnalysisLevel[] = [
  { id: 'basic', label: 'Basic', description: 'BPM, key, duration — <0.5 s', icon: Gauge },
  { id: 'standard', label: 'Standard', description: '+ MFCC, chroma, spectral — <1 s', icon: BarChart3 },
  { id: 'detailed', label: 'Detailed', description: '+ harmonic / percussive sep — <2 s', icon: Microscope },
  { id: 'professional', label: 'Professional', description: '+ AI analysis, CLAP, embeddings — <5 s', icon: Crown },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function UploadPage() {
  const [selectedLevel, setSelectedLevel] = useState('standard');
  const [isDragging, setIsDragging] = useState(false);

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-3xl mx-auto space-y-8"
    >
      {/* ── Drop Zone ─────────────────────────────────────────────────── */}
      <motion.div
        variants={itemVariants}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); }}
        className={`relative rounded-glass-lg border-2 border-dashed p-12
                    flex flex-col items-center justify-center text-center
                    transition-all duration-300 cursor-pointer
                    ${isDragging
                      ? 'border-cyber-cyan bg-cyber-cyan/5 shadow-glow-cyan'
                      : 'border-glass-border bg-glass-light hover:border-cyber-cyan/40'
                    }`}
      >
        <div
          className={`h-16 w-16 rounded-2xl flex items-center justify-center mb-4
                      transition-colors duration-300
                      ${isDragging ? 'bg-cyber-cyan/20' : 'bg-glass-light border border-glass-border'}`}
        >
          <Upload className={`h-8 w-8 ${isDragging ? 'text-cyber-cyan' : 'text-text-tertiary'}`} />
        </div>
        <p className="text-lg font-semibold text-text-primary mb-1">
          Drop audio files here
        </p>
        <p className="text-sm text-text-tertiary mb-4">or click to browse</p>
        <div className="flex items-center gap-2 flex-wrap justify-center">
          {FORMATS.map((fmt) => (
            <span
              key={fmt}
              className="px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wider
                         bg-glass-light border border-glass-border text-text-tertiary"
            >
              {fmt}
            </span>
          ))}
        </div>
      </motion.div>

      {/* ── Upload Queue ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-5">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
          Upload Queue
        </h2>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Inbox className="h-10 w-10 text-text-tertiary/40 mb-2" />
          <p className="text-sm text-text-tertiary">No files in queue</p>
        </div>
      </motion.div>

      {/* ── Analysis Level Selector ───────────────────────────────────── */}
      <motion.div variants={itemVariants} className="space-y-3">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
          Analysis Level
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {ANALYSIS_LEVELS.map((level) => {
            const active = selectedLevel === level.id;
            return (
              <button
                key={level.id}
                onClick={() => setSelectedLevel(level.id)}
                className={`glass rounded-glass p-4 text-left flex items-start gap-3
                            transition-all duration-200
                            ${active
                              ? 'border-cyber-cyan/50 shadow-glow-cyan bg-cyber-cyan/5'
                              : 'hover:bg-glass-strong'
                            }`}
              >
                <div
                  className={`h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0
                              ${active
                                ? 'bg-cyber-cyan/20 text-cyber-cyan'
                                : 'bg-glass-light text-text-tertiary border border-glass-border'
                              }`}
                >
                  <level.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className={`text-sm font-semibold ${active ? 'text-cyber-cyan' : 'text-text-primary'}`}>
                    {level.label}
                  </p>
                  <p className="text-xs text-text-tertiary mt-0.5">{level.description}</p>
                </div>
                {/* Radio indicator */}
                <div
                  className={`ml-auto mt-1 h-4 w-4 rounded-full border-2 flex-shrink-0
                              flex items-center justify-center
                              ${active ? 'border-cyber-cyan' : 'border-text-tertiary/40'}`}
                >
                  {active && <div className="h-2 w-2 rounded-full bg-cyber-cyan" />}
                </div>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* ── Upload Button ─────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex justify-center">
        <button
          disabled
          className="px-8 py-3 rounded-glass font-semibold text-sm
                     bg-cyber-cyan/20 text-cyber-cyan/40 border border-cyber-cyan/20
                     cursor-not-allowed flex items-center gap-2"
        >
          <FileAudio className="h-4 w-4" />
          Upload &amp; Analyze
        </button>
      </motion.div>
    </motion.div>
  );
}
