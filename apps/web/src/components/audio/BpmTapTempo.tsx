/**
 * BPM Tap Tempo Tool — Interactive rhythm detection widget (P2-024)
 *
 * Provides a large tap target that measures the interval between taps to
 * calculate BPM in real-time. Includes visual feedback with a pulsing ring
 * animation synced to the detected tempo.
 *
 * Features:
 *   - Tap via click, spacebar, or enter key
 *   - Running average of last 8 taps for stability
 *   - Auto-reset after 3 seconds of inactivity
 *   - Visual pulse ring at detected tempo
 *   - Copy BPM to clipboard
 *
 * @example
 * ```tsx
 * <BpmTapTempo onBpmChange={(bpm) => console.log('Detected:', bpm)} />
 * ```
 */

'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Copy, RotateCcw } from 'lucide-react';

// ── Types ────────────────────────────────────────────────────────────────────

interface BpmTapTempoProps {
  /** Callback fired when BPM changes */
  onBpmChange?: (bpm: number) => void;
  /** Maximum taps to average over */
  maxTaps?: number;
  /** Auto-reset timeout in ms */
  resetTimeout?: number;
  /** Additional className */
  className?: string;
}

// ── Constants ────────────────────────────────────────────────────────────────

const DEFAULT_MAX_TAPS = 8;
const DEFAULT_RESET_TIMEOUT = 3000;
const MIN_BPM = 20;
const MAX_BPM = 300;

// ── Component ────────────────────────────────────────────────────────────────

export function BpmTapTempo({
  onBpmChange,
  maxTaps = DEFAULT_MAX_TAPS,
  resetTimeout = DEFAULT_RESET_TIMEOUT,
  className = '',
}: BpmTapTempoProps) {
  const [bpm, setBpm] = useState<number | null>(null);
  const [tapCount, setTapCount] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [copied, setCopied] = useState(false);

  const tapTimesRef = useRef<number[]>([]);
  const resetTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Calculate BPM from tap intervals ─────────────────────────────────

  const calculateBpm = useCallback(
    (times: number[]): number | null => {
      if (times.length < 2) return null;

      const recentTimes = times.slice(-maxTaps);
      const intervals: number[] = [];

      for (let i = 1; i < recentTimes.length; i++) {
        intervals.push(recentTimes[i] - recentTimes[i - 1]);
      }

      if (intervals.length === 0) return null;

      const avgInterval =
        intervals.reduce((sum, val) => sum + val, 0) / intervals.length;

      if (avgInterval <= 0) return null;

      const calculatedBpm = 60000 / avgInterval;

      if (calculatedBpm < MIN_BPM || calculatedBpm > MAX_BPM) return null;

      return Math.round(calculatedBpm * 10) / 10;
    },
    [maxTaps]
  );

  // ── Handle tap ────────────────────────────────────────────────────────

  const handleTap = useCallback(() => {
    const now = performance.now();

    if (resetTimerRef.current) {
      clearTimeout(resetTimerRef.current);
    }

    tapTimesRef.current.push(now);
    setTapCount((prev) => prev + 1);
    setIsActive(true);

    const newBpm = calculateBpm(tapTimesRef.current);
    if (newBpm !== null) {
      setBpm(newBpm);
      onBpmChange?.(newBpm);
    }

    resetTimerRef.current = setTimeout(() => {
      setIsActive(false);
    }, resetTimeout);
  }, [calculateBpm, onBpmChange, resetTimeout]);

  // ── Reset ─────────────────────────────────────────────────────────────

  const handleReset = useCallback(() => {
    tapTimesRef.current = [];
    setBpm(null);
    setTapCount(0);
    setIsActive(false);
    setCopied(false);
    if (resetTimerRef.current) {
      clearTimeout(resetTimerRef.current);
    }
  }, []);

  // ── Copy to clipboard ─────────────────────────────────────────────────

  const handleCopy = useCallback(async () => {
    if (bpm === null) return;
    try {
      await navigator.clipboard.writeText(Math.round(bpm).toString());
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard API not available
    }
  }, [bpm]);

  // ── Keyboard handler ──────────────────────────────────────────────────

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' || e.code === 'Enter') {
        e.preventDefault();
        handleTap();
      }
      if (e.code === 'Escape') {
        handleReset();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [handleTap, handleReset]);

  // ── Cleanup timer ─────────────────────────────────────────────────────

  useEffect(() => {
    return () => {
      if (resetTimerRef.current) {
        clearTimeout(resetTimerRef.current);
      }
    };
  }, []);

  // ── Pulse animation duration synced to BPM ───────────────────────────

  const pulseDuration = bpm && bpm > 0 ? 60 / bpm : 1;

  return (
    <div
      className={`flex flex-col items-center gap-6 select-none ${className}`}
    >
      {/* BPM Display */}
      <div className="text-center">
        <AnimatePresence mode="wait">
          {bpm !== null ? (
            <motion.div
              key="bpm-value"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="relative"
            >
              <span className="text-6xl font-bold tabular-nums bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                {Math.round(bpm)}
              </span>
              <span className="text-lg text-white/40 ml-2">BPM</span>
              {bpm % 1 !== 0 && (
                <span className="absolute -bottom-5 left-1/2 -translate-x-1/2 text-xs text-white/30">
                  {bpm.toFixed(1)}
                </span>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="bpm-placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-6xl font-bold text-white/10"
            >
              ---
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Tap Button with Pulse Ring */}
      <div className="relative">
        {isActive && bpm && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-cyan-400/30"
            animate={{
              scale: [1, 1.5],
              opacity: [0.6, 0],
            }}
            transition={{
              duration: pulseDuration,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        )}

        <motion.button
          whileTap={{ scale: 0.92 }}
          whileHover={{ scale: 1.02 }}
          onClick={handleTap}
          className={`
            relative z-10 w-40 h-40 rounded-full
            flex flex-col items-center justify-center gap-2
            cursor-pointer transition-colors duration-200
            border-2
            ${
              isActive
                ? 'bg-cyan-500/10 border-cyan-400/50 shadow-[0_0_30px_rgba(0,255,255,0.15)]'
                : 'bg-white/5 border-white/10 hover:border-white/20'
            }
          `}
          aria-label="Tap to detect BPM"
        >
          <Activity
            className={`w-8 h-8 ${isActive ? 'text-cyan-400' : 'text-white/40'}`}
          />
          <span
            className={`text-sm font-medium ${
              isActive ? 'text-cyan-300' : 'text-white/40'
            }`}
          >
            TAP
          </span>
        </motion.button>
      </div>

      {/* Tap count & info */}
      <div className="text-center space-y-1">
        <p className="text-xs text-white/30">
          {tapCount > 0 ? `${tapCount} taps` : 'Tap the button or press Space'}
        </p>
        {tapCount > 0 && tapCount < 3 && (
          <p className="text-xs text-amber-400/50">
            Keep tapping for more accuracy...
          </p>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          onClick={handleReset}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg
                     bg-white/5 text-white/40 hover:text-white/70 hover:bg-white/10
                     transition-colors"
          aria-label="Reset"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset
        </button>

        {bpm !== null && (
          <motion.button
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg
                       bg-cyan-500/10 text-cyan-400/70 hover:text-cyan-300 hover:bg-cyan-500/20
                       transition-colors"
            aria-label="Copy BPM"
          >
            <Copy className="w-3.5 h-3.5" />
            {copied ? 'Copied!' : 'Copy'}
          </motion.button>
        )}
      </div>

      {/* Keyboard hint */}
      <p className="text-[10px] text-white/15">
        Space to tap · Esc to reset
      </p>
    </div>
  );
}

export default BpmTapTempo;
