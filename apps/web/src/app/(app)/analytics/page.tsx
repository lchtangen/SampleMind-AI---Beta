/**
 * @fileoverview Analytics page for the SampleMind AI app shell.
 *
 * Displays summary stat cards, BPM distribution bar chart, key distribution,
 * genre breakdown, and an energy pie chart — all as styled placeholders
 * using cyberpunk glassmorphism.
 *
 * @module app/(app)/analytics/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  Music2,
  Gauge,
  KeyRound,
  Tag,
  BarChart3,
  PieChart,
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

const SUMMARY_CARDS = [
  { label: 'Total Samples', value: '1,284', icon: Music2, color: 'text-cyber-cyan' },
  { label: 'Avg BPM', value: '128', icon: Gauge, color: 'text-cyber-purple' },
  { label: 'Top Key', value: 'A minor', icon: KeyRound, color: 'text-cyber-magenta' },
  { label: 'Top Genre', value: 'Electronic', icon: Tag, color: 'text-cyber-blue' },
];

const BPM_BINS = [
  { range: '60–80', pct: 12 },
  { range: '80–100', pct: 22 },
  { range: '100–120', pct: 35 },
  { range: '120–140', pct: 58 },
  { range: '140–160', pct: 45 },
  { range: '160–180', pct: 18 },
  { range: '180+', pct: 8 },
];

const KEY_DATA = [
  { key: 'C', pct: 18 },
  { key: 'C#', pct: 8 },
  { key: 'D', pct: 14 },
  { key: 'D#', pct: 6 },
  { key: 'E', pct: 12 },
  { key: 'F', pct: 10 },
  { key: 'F#', pct: 7 },
  { key: 'G', pct: 11 },
  { key: 'G#', pct: 5 },
  { key: 'A', pct: 20 },
  { key: 'A#', pct: 4 },
  { key: 'B', pct: 9 },
];

const GENRE_DATA = [
  { genre: 'Electronic', pct: 35, color: 'from-cyber-cyan to-cyber-blue' },
  { genre: 'Hip Hop', pct: 28, color: 'from-cyber-purple to-cyber-magenta' },
  { genre: 'Lo-Fi', pct: 15, color: 'from-cyber-magenta to-cyber-cyan' },
  { genre: 'Ambient', pct: 12, color: 'from-cyber-blue to-cyber-purple' },
  { genre: 'Other', pct: 10, color: 'from-text-tertiary to-text-muted' },
];

const ENERGY_SLICES = [
  { label: 'High', pct: 40, color: 'bg-cyber-magenta' },
  { label: 'Medium', pct: 35, color: 'bg-cyber-cyan' },
  { label: 'Low', pct: 25, color: 'bg-cyber-purple' },
];

// ─── Page Component ──────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* ── Summary Cards ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {SUMMARY_CARDS.map((card) => (
          <motion.div
            key={card.label}
            variants={itemVariants}
            className="glass rounded-glass p-5 flex items-center gap-4"
          >
            <div className="h-11 w-11 rounded-xl bg-glass-light border border-glass-border
                            flex items-center justify-center">
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
            <div>
              <p className="text-xl font-bold text-text-primary">{card.value}</p>
              <p className="text-xs text-text-tertiary">{card.label}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* ── BPM Distribution ──────────────────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-6">
        <div className="flex items-center gap-2 mb-6">
          <BarChart3 className="h-5 w-5 text-cyber-cyan" />
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            BPM Distribution
          </h2>
        </div>
        <div className="flex items-end gap-3 h-44">
          {BPM_BINS.map((bin) => (
            <div key={bin.range} className="flex-1 flex flex-col items-center gap-2">
              <motion.div
                initial={{ height: 0 }}
                animate={{ height: `${bin.pct}%` }}
                transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1], delay: 0.2 }}
                className="w-full rounded-t-md bg-gradient-to-t from-cyber-cyan to-cyber-purple"
              />
              <span className="text-[10px] text-text-tertiary whitespace-nowrap">{bin.range}</span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* ── Key Distribution + Genre Breakdown ────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Key Distribution */}
        <motion.div variants={itemVariants} className="glass rounded-glass p-6">
          <div className="flex items-center gap-2 mb-5">
            <KeyRound className="h-5 w-5 text-cyber-purple" />
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Key Distribution
            </h2>
          </div>
          <div className="flex items-end gap-2 h-36">
            {KEY_DATA.map((k) => (
              <div key={k.key} className="flex-1 flex flex-col items-center gap-1">
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${k.pct * 1.5}%` }}
                  transition={{ duration: 0.6, ease: [0.4, 0, 0.2, 1], delay: 0.3 }}
                  className="w-full rounded-t-sm bg-gradient-to-t from-cyber-purple to-cyber-magenta"
                />
                <span className="text-[9px] text-text-tertiary">{k.key}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Genre Breakdown */}
        <motion.div variants={itemVariants} className="glass rounded-glass p-6">
          <div className="flex items-center gap-2 mb-5">
            <Tag className="h-5 w-5 text-cyber-magenta" />
            <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Genre Breakdown
            </h2>
          </div>
          <div className="space-y-3">
            {GENRE_DATA.map((g) => (
              <div key={g.genre}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-text-secondary">{g.genre}</span>
                  <span className="text-text-tertiary">{g.pct}%</span>
                </div>
                <div className="h-2 rounded-full bg-dark-300 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${g.pct}%` }}
                    transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1], delay: 0.3 }}
                    className={`h-full rounded-full bg-gradient-to-r ${g.color}`}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* ── Energy Pie Chart Placeholder ──────────────────────────────── */}
      <motion.div variants={itemVariants} className="glass rounded-glass p-6">
        <div className="flex items-center gap-2 mb-6">
          <PieChart className="h-5 w-5 text-cyber-blue" />
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
            Energy Breakdown
          </h2>
        </div>
        <div className="flex items-center gap-8">
          {/* Pseudo-pie: stacked ring */}
          <div className="relative h-36 w-36 flex-shrink-0">
            <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
              <circle
                cx="18" cy="18" r="15.9"
                fill="none" stroke="hsl(220, 15%, 12%)" strokeWidth="3.5"
              />
              {/* High energy */}
              <circle
                cx="18" cy="18" r="15.9"
                fill="none" stroke="hsl(320, 90%, 60%)" strokeWidth="3.5"
                strokeDasharray="40 60" strokeDashoffset="0"
                className="transition-all duration-700"
              />
              {/* Medium energy */}
              <circle
                cx="18" cy="18" r="15.9"
                fill="none" stroke="hsl(180, 95%, 55%)" strokeWidth="3.5"
                strokeDasharray="35 65" strokeDashoffset="-40"
                className="transition-all duration-700"
              />
              {/* Low energy */}
              <circle
                cx="18" cy="18" r="15.9"
                fill="none" stroke="hsl(270, 85%, 65%)" strokeWidth="3.5"
                strokeDasharray="25 75" strokeDashoffset="-75"
                className="transition-all duration-700"
              />
            </svg>
          </div>

          {/* Legend */}
          <div className="space-y-3">
            {ENERGY_SLICES.map((slice) => (
              <div key={slice.label} className="flex items-center gap-3">
                <div className={`h-3 w-3 rounded-full ${slice.color}`} />
                <span className="text-sm text-text-secondary">{slice.label}</span>
                <span className="text-sm font-semibold text-text-primary">{slice.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
