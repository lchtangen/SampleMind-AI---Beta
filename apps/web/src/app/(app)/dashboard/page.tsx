/**
 * @fileoverview Dashboard page for the SampleMind AI app shell.
 *
 * Displays stat cards, an audio visualizer hero, recent activity, and
 * quick-action shortcuts. All panels use the cyberpunk glassmorphism
 * design system with framer-motion staggered animations.
 *
 * @module app/(app)/dashboard/page
 */

'use client';

import { motion } from 'framer-motion';
import {
  Music2,
  BarChart3,
  Cpu,
  Zap,
  Upload,
  Search,
  Sliders,
  Sparkles,
  Play,
  CheckCircle2,
  Clock,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import Link from 'next/link';

// ─── Animation variants ──────────────────────────────────────────────────────

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.4, 0, 0.2, 1] } },
};

// ─── Static data ─────────────────────────────────────────────────────────────

const STAT_CARDS = [
  { label: 'Total Tracks', value: '1,284', icon: Music2, color: 'cyan' as const },
  { label: 'Analyzed', value: '1,102', icon: BarChart3, color: 'purple' as const },
  { label: 'Processing', value: '7', icon: Cpu, color: 'magenta' as const },
  { label: 'AI Credits', value: '4,500', icon: Zap, color: 'blue' as const },
];

const RECENT_ACTIVITY = [
  { file: 'dark_trap_kick_01.wav', status: 'completed', time: '2 min ago' },
  { file: 'ambient_pad_C#.flac', status: 'completed', time: '8 min ago' },
  { file: 'vocal_chop_pack.zip', status: 'processing', time: '12 min ago' },
  { file: '808_sub_bass.wav', status: 'completed', time: '25 min ago' },
  { file: 'hi_hat_roll_140bpm.wav', status: 'failed', time: '1 hr ago' },
];

const QUICK_ACTIONS = [
  { label: 'Upload', icon: Upload, href: '/upload', color: 'cyan' as const },
  { label: 'Search', icon: Search, href: '/search', color: 'purple' as const },
  { label: 'Effects', icon: Sliders, href: '/effects', color: 'magenta' as const },
  { label: 'Generate', icon: Sparkles, href: '/generate', color: 'blue' as const },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

const glowMap = {
  cyan: 'hover:shadow-glow-cyan',
  purple: 'hover:shadow-glow-purple',
  magenta: 'hover:shadow-glow-magenta',
  blue: 'hover:shadow-glow-blue',
} as const;

const borderMap = {
  cyan: 'border-cyber-cyan/30',
  purple: 'border-cyber-purple/30',
  magenta: 'border-cyber-magenta/30',
  blue: 'border-cyber-blue/30',
} as const;

const textMap = {
  cyan: 'text-cyber-cyan',
  purple: 'text-cyber-purple',
  magenta: 'text-cyber-magenta',
  blue: 'text-cyber-blue',
} as const;

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { icon: React.ComponentType<{ className?: string }>; cls: string; label: string }> = {
    completed: { icon: CheckCircle2, cls: 'text-success bg-success/10', label: 'Completed' },
    processing: { icon: Loader2, cls: 'text-warning bg-warning/10 animate-spin-slow', label: 'Processing' },
    failed: { icon: AlertCircle, cls: 'text-error bg-error/10', label: 'Failed' },
  };
  const s = map[status] ?? map.completed;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${s.cls}`}>
      <s.icon className="h-3 w-3" />
      {s.label}
    </span>
  );
}

// ─── Page Component ──────────────────────────────────────────────────────────

export default function DashboardPage() {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* ── Stat Cards ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {STAT_CARDS.map((card) => (
          <motion.div
            key={card.label}
            variants={itemVariants}
            className={`glass rounded-glass p-5 flex items-center gap-4
                        transition-shadow duration-300 ${glowMap[card.color]}`}
          >
            <div
              className={`h-12 w-12 rounded-xl flex items-center justify-center
                          bg-glass-light border ${borderMap[card.color]}`}
            >
              <card.icon className={`h-6 w-6 ${textMap[card.color]}`} />
            </div>
            <div>
              <p className="text-2xl font-bold text-text-primary">{card.value}</p>
              <p className="text-xs text-text-tertiary">{card.label}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* ── Audio Visualizer Hero ───────────────────────────────────── */}
      <motion.div
        variants={itemVariants}
        className="glass rounded-glass-lg overflow-hidden"
      >
        <div
          className="relative h-48 bg-spark-2 flex items-center justify-center"
        >
          {/* Decorative bars */}
          <div className="absolute inset-0 flex items-end justify-center gap-1 px-12 pb-6 opacity-30">
            {Array.from({ length: 48 }).map((_, i) => (
              <div
                key={i}
                className="flex-1 rounded-t bg-white/40"
                style={{ height: `${20 + Math.sin(i * 0.5) * 40 + Math.random() * 30}%` }}
              />
            ))}
          </div>
          <div className="relative z-10 text-center">
            <Play className="h-10 w-10 text-white/80 mx-auto mb-2" />
            <p className="text-lg font-semibold text-white/90">Audio Visualizer</p>
            <p className="text-sm text-white/60">Select a track to visualize</p>
          </div>
        </div>
      </motion.div>

      {/* ── Recent Activity + Quick Actions ─────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <motion.div
          variants={itemVariants}
          className="lg:col-span-2 glass rounded-glass p-5"
        >
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
            Recent Activity
          </h2>
          <ul className="divide-y divide-glass-border">
            {RECENT_ACTIVITY.map((item) => (
              <li key={item.file} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <Music2 className="h-4 w-4 text-text-tertiary flex-shrink-0" />
                  <span className="text-sm text-text-primary truncate">{item.file}</span>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0">
                  <StatusBadge status={item.status} />
                  <span className="text-xs text-text-tertiary flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {item.time}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="space-y-3">
          <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-1">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {QUICK_ACTIONS.map((action) => (
              <Link key={action.label} href={action.href}>
                <div
                  className={`glass rounded-glass p-4 flex flex-col items-center gap-2
                              text-center cursor-pointer transition-all duration-300
                              hover:bg-glass-strong ${glowMap[action.color]}`}
                >
                  <action.icon className={`h-6 w-6 ${textMap[action.color]}`} />
                  <span className="text-xs font-medium text-text-secondary">
                    {action.label}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
