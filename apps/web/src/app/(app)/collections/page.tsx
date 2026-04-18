/**
 * @fileoverview Collections page for the SampleMind AI app shell.
 *
 * Displays a header with "New Collection" button and a grid of collection
 * cards with placeholder cover art, name, and sample count.
 *
 * @module app/(app)/collections/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  FolderOpen,
  Plus,
  Music2,
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

const COLLECTIONS = [
  { name: 'Dark Trap Essentials', count: 48, gradient: 'from-cyber-magenta/30 to-cyber-purple/30' },
  { name: 'Lo-Fi Chill Pack', count: 32, gradient: 'from-cyber-cyan/30 to-cyber-blue/30' },
  { name: 'Festival Bangers', count: 65, gradient: 'from-cyber-purple/30 to-cyber-cyan/30' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function CollectionsPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* ── Header ────────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-text-primary">Your Collections</h2>
          <p className="text-sm text-text-tertiary mt-1">Organize samples into curated packs</p>
        </div>
        <button
          className="flex items-center gap-2 px-4 py-2.5 rounded-glass-sm text-sm font-semibold
                     bg-gradient-to-r from-cyber-cyan to-cyber-purple text-white
                     hover:shadow-glow-cyan transition-shadow duration-300"
        >
          <Plus className="h-4 w-4" />
          New Collection
        </button>
      </motion.div>

      {/* ── Collection Grid ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {COLLECTIONS.map((col) => (
          <motion.div
            key={col.name}
            variants={itemVariants}
            className="glass rounded-glass overflow-hidden group cursor-pointer
                       hover:shadow-glow-purple transition-shadow duration-300"
          >
            {/* Cover art placeholder */}
            <div
              className={`h-40 bg-gradient-to-br ${col.gradient}
                          flex items-center justify-center relative`}
            >
              <FolderOpen className="h-12 w-12 text-white/20 group-hover:text-white/40 transition-colors" />
              {/* Sample count badge */}
              <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full text-[10px] font-bold
                               bg-dark-500/60 text-text-secondary backdrop-blur-sm">
                {col.count} samples
              </span>
            </div>

            {/* Info */}
            <div className="p-4">
              <p className="text-sm font-semibold text-text-primary">{col.name}</p>
              <p className="text-xs text-text-tertiary mt-1 flex items-center gap-1">
                <Music2 className="h-3 w-3" />
                {col.count} tracks
              </p>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
