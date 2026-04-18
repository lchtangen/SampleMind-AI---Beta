/**
 * @fileoverview Gallery page for the SampleMind AI app shell.
 *
 * Masonry-style grid of audio visualization placeholder cards with
 * gradient backgrounds and cyberpunk glass styling.
 *
 * @module app/(app)/gallery/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  AudioWaveform,
  Play,
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
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] } },
};

// ─── Static data ─────────────────────────────────────────────────────────────

const GALLERY_ITEMS = [
  { title: 'Spectral Analysis — Kick',    gradient: 'bg-spark-1', height: 'h-52' },
  { title: 'Waveform — Ambient Pad',      gradient: 'bg-spark-2', height: 'h-72' },
  { title: 'MFCC Heatmap — Vocal',        gradient: 'bg-spark-3', height: 'h-56' },
  { title: 'Chromagram — Piano',          gradient: 'bg-spark-4', height: 'h-64' },
  { title: 'Mel Spectrogram — Synth',     gradient: 'bg-mesh-1',  height: 'h-48' },
  { title: 'Onset Envelope — Hi-Hats',    gradient: 'bg-mesh-2',  height: 'h-60' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function GalleryPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* ── Header ────────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        <h2 className="text-2xl font-bold text-text-primary">Audio Gallery</h2>
        <p className="text-sm text-text-tertiary mt-1">
          Visual representations of your audio analyses
        </p>
      </motion.div>

      {/* ── Masonry Grid ──────────────────────────────────────────────── */}
      <div className="columns-1 sm:columns-2 lg:columns-3 gap-4 space-y-4">
        {GALLERY_ITEMS.map((item) => (
          <motion.div
            key={item.title}
            variants={itemVariants}
            className={`glass rounded-glass overflow-hidden break-inside-avoid group
                        cursor-pointer hover:shadow-glow-cyan transition-shadow duration-300`}
          >
            {/* Visualization placeholder */}
            <div
              className={`${item.gradient} ${item.height} relative flex items-center justify-center`}
            >
              <AudioWaveform className="h-10 w-10 text-white/15 group-hover:text-white/30 transition-colors" />
              {/* Play overlay on hover */}
              <div className="absolute inset-0 flex items-center justify-center bg-dark-500/0
                              group-hover:bg-dark-500/40 transition-colors duration-300">
                <Play
                  className="h-8 w-8 text-white opacity-0 group-hover:opacity-80
                             transition-opacity duration-300 ml-0.5"
                />
              </div>
            </div>
            {/* Label */}
            <div className="p-3">
              <p className="text-sm font-medium text-text-primary">{item.title}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
