/**
 * @fileoverview Semantic search page for the SampleMind AI app shell.
 *
 * Provides a large search input with gradient glow, search-type tabs
 * (Text / Audio / Similar), and a results area placeholder. Uses FAISS
 * 512-dim CLAP embeddings on the backend.
 *
 * @module app/(app)/search/page
 */

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Type,
  AudioWaveform,
  GitCompareArrows,
  Music2,
  Sparkles,
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

type SearchTab = 'text' | 'audio' | 'similar';

const TABS: { id: SearchTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'text', label: 'Text', icon: Type },
  { id: 'audio', label: 'Audio', icon: AudioWaveform },
  { id: 'similar', label: 'Similar', icon: GitCompareArrows },
];

const PLACEHOLDER_RESULTS = [
  { name: 'dark_trap_kick_01.wav', score: 0.96, bpm: 140, key: 'C min' },
  { name: 'heavy_808_bass.wav', score: 0.91, bpm: 145, key: 'E min' },
  { name: 'cinematic_hit_boom.flac', score: 0.87, bpm: 100, key: 'D min' },
  { name: 'lo-fi_dusty_snare.wav', score: 0.83, bpm: 85, key: '—' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState<SearchTab>('text');
  const [query, setQuery] = useState('');
  const hasQuery = query.trim().length > 0;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-3xl mx-auto space-y-8"
    >
      {/* ── Search Input with gradient glow ────────────────────────── */}
      <motion.div variants={itemVariants} className="relative group">
        {/* Glow ring behind input */}
        <div
          className="absolute -inset-[2px] rounded-glass-lg opacity-60 blur-sm
                     bg-gradient-to-r from-cyber-cyan via-cyber-purple to-cyber-magenta
                     group-focus-within:opacity-100 transition-opacity duration-300"
        />
        <div className="relative glass rounded-glass-lg p-4 flex items-center gap-3">
          <Search className="h-5 w-5 text-text-tertiary flex-shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search your library with natural language…"
            className="flex-1 bg-transparent text-text-primary placeholder-text-tertiary
                       text-base outline-none"
          />
          {hasQuery && (
            <Sparkles className="h-4 w-4 text-cyber-purple animate-pulse" />
          )}
        </div>
      </motion.div>

      {/* ── Search Type Tabs ──────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="flex items-center gap-2">
        {TABS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-glass-sm text-sm font-medium
                          transition-all duration-200
                          ${isActive
                            ? 'glass text-cyber-cyan shadow-glow-cyan border-cyber-cyan/30'
                            : 'bg-glass-light text-text-secondary border border-glass-border hover:text-text-primary'
                          }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </motion.div>

      {/* ── Results Area ──────────────────────────────────────────────── */}
      <motion.div variants={itemVariants}>
        {!hasQuery ? (
          <div className="glass rounded-glass-lg py-20 flex flex-col items-center justify-center text-center">
            <Search className="h-12 w-12 text-text-tertiary/30 mb-3" />
            <p className="text-text-secondary font-medium">
              Enter a query to search your library
            </p>
            <p className="text-sm text-text-tertiary mt-1">
              Try &quot;dark trap kick&quot; or &quot;ambient pad in C# major&quot;
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {PLACEHOLDER_RESULTS.map((r) => (
              <div
                key={r.name}
                className="glass rounded-glass p-4 hover:shadow-glow-purple
                           transition-shadow duration-300 group"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyber-purple/20 to-cyber-cyan/20
                                  border border-glass-border flex items-center justify-center">
                    <Music2 className="h-5 w-5 text-cyber-purple" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-text-primary truncate">{r.name}</p>
                    <p className="text-xs text-text-tertiary">{r.bpm} BPM · {r.key}</p>
                  </div>
                </div>
                {/* Confidence bar */}
                <div className="h-1.5 rounded-full bg-dark-300 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyber-cyan to-cyber-purple"
                    style={{ width: `${r.score * 100}%` }}
                  />
                </div>
                <p className="text-[10px] text-text-tertiary mt-1 text-right">
                  {(r.score * 100).toFixed(0)}% match
                </p>
              </div>
            ))}
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
