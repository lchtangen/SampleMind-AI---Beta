/**
 * @fileoverview Library page for the SampleMind AI app shell.
 *
 * Provides a searchable, filterable grid/list view of audio samples with
 * category filter chips, view mode toggle, sample cards and pagination.
 *
 * @module app/(app)/library/page
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  LayoutGrid,
  List,
  Play,
  Clock,
  Music2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

// ─── Animation variants ──────────────────────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] } },
};

// ─── Static data ─────────────────────────────────────────────────────────────

const CATEGORIES = ['All', 'Drums', 'Bass', 'Synth', 'Vocal', 'FX'] as const;

const SAMPLES = [
  { name: 'dark_trap_kick.wav', bpm: 140, key: 'C min', duration: '0:02' },
  { name: 'ambient_pad_Csharp.flac', bpm: 90, key: 'C# maj', duration: '0:08' },
  { name: 'hi_hat_roll_loop.wav', bpm: 128, key: '—', duration: '0:04' },
  { name: '808_sub_bass_E.wav', bpm: 145, key: 'E min', duration: '0:03' },
  { name: 'vocal_chop_slice_01.wav', bpm: 120, key: 'A min', duration: '0:01' },
  { name: 'synth_pluck_Fsharp.wav', bpm: 130, key: 'F# min', duration: '0:05' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function LibraryPage() {
  const [activeCategory, setActiveCategory] = useState<string>('All');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* ── Search Bar ────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-3 flex items-center gap-3">
        <Search className="h-5 w-5 text-text-tertiary flex-shrink-0" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search your library…"
          className="flex-1 bg-transparent text-text-primary placeholder-text-tertiary
                     text-sm outline-none"
        />
      </motion.div>

      {/* ── Filters + View Toggle ─────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex items-center justify-between gap-4 flex-wrap">
        {/* Category chips */}
        <div className="flex items-center gap-2 flex-wrap">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all duration-200
                ${activeCategory === cat
                  ? 'bg-cyber-cyan/20 text-cyber-cyan border border-cyber-cyan/40 shadow-glow-cyan'
                  : 'bg-glass-light text-text-secondary border border-glass-border hover:text-text-primary'
                }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-1 bg-glass-light rounded-lg p-0.5 border border-glass-border">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'grid' ? 'bg-cyber-cyan/20 text-cyber-cyan' : 'text-text-tertiary hover:text-text-secondary'
            }`}
            aria-label="Grid view"
          >
            <LayoutGrid className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md transition-colors ${
              viewMode === 'list' ? 'bg-cyber-cyan/20 text-cyber-cyan' : 'text-text-tertiary hover:text-text-secondary'
            }`}
            aria-label="List view"
          >
            <List className="h-4 w-4" />
          </button>
        </div>
      </motion.div>

      {/* ── Sample Grid ───────────────────────────────────────────────── */}
      <div
        className={
          viewMode === 'grid'
            ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4'
            : 'flex flex-col gap-3'
        }
      >
        {SAMPLES.map((sample) => (
          <motion.div
            key={sample.name}
            variants={itemVariants}
            className={`glass rounded-glass overflow-hidden transition-shadow duration-300
                        hover:shadow-glow-cyan group ${viewMode === 'list' ? 'flex items-center gap-4 p-4' : ''}`}
          >
            {viewMode === 'grid' && (
              <>
                {/* Waveform placeholder */}
                <div className="h-24 bg-gradient-to-r from-cyber-cyan/10 via-cyber-purple/10 to-cyber-magenta/10
                                flex items-center justify-center relative">
                  {/* Waveform bars */}
                  <div className="absolute inset-0 flex items-center justify-center gap-[2px] px-4 opacity-40">
                    {Array.from({ length: 40 }).map((_, i) => (
                      <div
                        key={i}
                        className="flex-1 rounded-sm bg-cyber-cyan/60"
                        style={{ height: `${15 + Math.sin(i * 0.7) * 30 + Math.random() * 20}%` }}
                      />
                    ))}
                  </div>
                  <button
                    className="relative z-10 h-10 w-10 rounded-full bg-cyber-cyan/20 border border-cyber-cyan/40
                               flex items-center justify-center opacity-0 group-hover:opacity-100
                               transition-opacity duration-200"
                    aria-label={`Play ${sample.name}`}
                  >
                    <Play className="h-5 w-5 text-cyber-cyan ml-0.5" />
                  </button>
                </div>

                {/* Info */}
                <div className="p-4 space-y-2">
                  <p className="text-sm font-medium text-text-primary truncate">{sample.name}</p>
                  <div className="flex items-center gap-3 text-xs text-text-tertiary">
                    <span className="flex items-center gap-1">
                      <Music2 className="h-3 w-3" />
                      {sample.bpm} BPM
                    </span>
                    <span>{sample.key}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {sample.duration}
                    </span>
                  </div>
                </div>
              </>
            )}

            {viewMode === 'list' && (
              <>
                <button
                  className="h-9 w-9 rounded-full bg-glass-light border border-glass-border
                             flex items-center justify-center flex-shrink-0
                             group-hover:border-cyber-cyan/40 transition-colors"
                  aria-label={`Play ${sample.name}`}
                >
                  <Play className="h-4 w-4 text-text-tertiary group-hover:text-cyber-cyan ml-0.5" />
                </button>
                <p className="text-sm font-medium text-text-primary truncate flex-1">{sample.name}</p>
                <span className="text-xs text-text-tertiary">{sample.bpm} BPM</span>
                <span className="text-xs text-text-tertiary">{sample.key}</span>
                <span className="text-xs text-text-tertiary flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {sample.duration}
                </span>
              </>
            )}
          </motion.div>
        ))}
      </div>

      {/* ── Pagination ────────────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex items-center justify-center gap-3 pt-2">
        <button
          className="glass rounded-glass-sm px-4 py-2 text-sm text-text-secondary
                     flex items-center gap-1.5 hover:text-text-primary transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Previous
        </button>
        <span className="text-xs text-text-tertiary">Page 1 of 12</span>
        <button
          className="glass rounded-glass-sm px-4 py-2 text-sm text-text-secondary
                     flex items-center gap-1.5 hover:text-text-primary transition-colors"
        >
          Next
          <ChevronRight className="h-4 w-4" />
        </button>
      </motion.div>
    </motion.div>
  );
}
