'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Scissors,
  Wand2,
  Play,
  Pause,
  Volume2,
  Loader2,
  Music,
  Lightbulb,
  RefreshCw,
} from 'lucide-react';
import {
  separateStems,
  getStemResults,
  getStemMixSuggestions,
  type StemInfo,
  type MixSuggestion,
} from '@/lib/feature-endpoints';
import { cn } from '@/lib/utils';

type Status = 'idle' | 'separating' | 'ready' | 'error';

const STEM_COLORS: Record<string, string> = {
  vocals: 'from-pink-500 to-rose-500',
  drums: 'from-orange-500 to-amber-500',
  bass: 'from-violet-500 to-purple-500',
  guitar: 'from-cyan-500 to-blue-500',
  piano: 'from-emerald-500 to-green-500',
  other: 'from-slate-400 to-slate-500',
};

export default function RemixPage() {
  const [filePath, setFilePath] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [stems, setStems] = useState<StemInfo[]>([]);
  const [suggestions, setSuggestions] = useState<MixSuggestion[]>([]);
  const [narrative, setNarrative] = useState('');
  const [error, setError] = useState('');
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  const handleSeparate = useCallback(async () => {
    if (!filePath.trim()) return;
    setStatus('separating');
    setError('');
    setSuggestions([]);
    setNarrative('');
    try {
      const resp = await separateStems(filePath);
      setTaskId(resp.task_id);
      if (resp.stems && resp.stems.length > 0) {
        setStems(resp.stems);
        setStatus('ready');
      }
    } catch (err) {
      setError((err as Error).message);
      setStatus('error');
    }
  }, [filePath]);

  // Poll for results if task is async
  useEffect(() => {
    if (!taskId || status === 'ready' || status === 'error') return;
    const interval = setInterval(async () => {
      try {
        const resp = await getStemResults(taskId);
        if (resp.stems && resp.stems.length > 0) {
          setStems(resp.stems);
          setStatus('ready');
        }
      } catch {
        // keep polling
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [taskId, status]);

  const handleGetSuggestions = useCallback(async () => {
    if (!taskId) return;
    setLoadingSuggestions(true);
    try {
      const resp = await getStemMixSuggestions(taskId);
      setSuggestions(resp.suggestions);
      setNarrative(resp.narrative);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingSuggestions(false);
    }
  }, [taskId]);

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-orange-500 to-pink-500 flex items-center justify-center">
          <Scissors className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Remix Studio</h1>
          <p className="text-sm text-white/50">
            AI-powered stem separation + intelligent mix suggestions
          </p>
        </div>
      </div>

      {/* Input */}
      <div className="flex gap-3 mb-8">
        <input
          type="text"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          placeholder="Enter audio file path..."
          className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-orange-500/50 transition-colors text-sm"
        />
        <button
          onClick={handleSeparate}
          disabled={!filePath.trim() || status === 'separating'}
          className={cn(
            'px-6 py-3 rounded-xl font-medium text-sm transition-all flex items-center gap-2',
            filePath.trim() && status !== 'separating'
              ? 'bg-gradient-to-r from-orange-500 to-pink-500 text-white hover:shadow-lg hover:shadow-orange-500/25'
              : 'bg-white/5 text-white/20'
          )}
        >
          {status === 'separating' ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Separating...
            </>
          ) : (
            <>
              <Scissors className="h-4 w-4" />
              Separate Stems
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Stems Grid */}
      <AnimatePresence>
        {stems.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-lg font-semibold text-white mb-4">
              Separated Stems
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {stems.map((stem) => (
                <StemCard key={stem.name} stem={stem} />
              ))}
            </div>

            {/* AI Mix Suggestions */}
            <div className="flex items-center gap-3 mb-4">
              <h2 className="text-lg font-semibold text-white">
                AI Mix Suggestions
              </h2>
              <button
                onClick={handleGetSuggestions}
                disabled={loadingSuggestions}
                className="px-4 py-2 rounded-lg bg-violet-500/20 text-violet-400 hover:bg-violet-500/30 text-sm font-medium transition-colors flex items-center gap-2"
              >
                {loadingSuggestions ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Wand2 className="h-3 w-3" />
                )}
                {suggestions.length ? 'Regenerate' : 'Get Suggestions'}
              </button>
            </div>

            {narrative && (
              <div className="mb-6 p-4 rounded-xl bg-violet-500/10 border border-violet-500/20 text-white/80 text-sm leading-relaxed">
                <Lightbulb className="h-4 w-4 text-violet-400 inline mr-2" />
                {narrative}
              </div>
            )}

            {suggestions.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {suggestions.map((sug) => (
                  <SuggestionCard key={sug.stem} suggestion={sug} />
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function StemCard({ stem }: { stem: StemInfo }) {
  const gradient = STEM_COLORS[stem.name.toLowerCase()] ?? STEM_COLORS.other;

  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
      <div className="flex items-center gap-3 mb-3">
        <div
          className={cn(
            'h-10 w-10 rounded-lg bg-gradient-to-br flex items-center justify-center',
            gradient
          )}
        >
          <Music className="h-5 w-5 text-white" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white capitalize">
            {stem.name}
          </p>
          <p className="text-xs text-white/40">
            {(stem.size_bytes / 1024 / 1024).toFixed(1)} MB
            {stem.duration > 0 && ` / ${stem.duration.toFixed(1)}s`}
          </p>
        </div>
      </div>
      {/* Mini waveform placeholder */}
      <div className="h-12 rounded-lg bg-white/5 flex items-center justify-center overflow-hidden">
        <div className="flex gap-px items-end h-8">
          {Array.from({ length: 40 }).map((_, i) => (
            <div
              key={i}
              className={cn('w-1 rounded-full bg-gradient-to-t', gradient)}
              style={{
                height: `${Math.random() * 100}%`,
                opacity: 0.6 + Math.random() * 0.4,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function SuggestionCard({ suggestion }: { suggestion: MixSuggestion }) {
  const gradient =
    STEM_COLORS[suggestion.stem.toLowerCase()] ?? STEM_COLORS.other;

  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
      <div className="flex items-center gap-2 mb-3">
        <div
          className={cn(
            'h-6 w-6 rounded bg-gradient-to-br flex items-center justify-center',
            gradient
          )}
        >
          <Volume2 className="h-3 w-3 text-white" />
        </div>
        <span className="text-sm font-semibold text-white capitalize">
          {suggestion.stem}
        </span>
        <span className="ml-auto text-xs text-white/40">
          {suggestion.gain_db > 0 ? '+' : ''}
          {suggestion.gain_db.toFixed(1)} dB
        </span>
      </div>

      {/* EQ Bars */}
      <div className="flex gap-2 mb-3">
        {Object.entries(suggestion.eq).map(([band, val]) => (
          <div key={band} className="flex-1">
            <div className="h-16 bg-white/5 rounded relative overflow-hidden">
              <div
                className={cn(
                  'absolute bottom-0 left-0 right-0 rounded bg-gradient-to-t',
                  gradient
                )}
                style={{
                  height: `${Math.max(((val + 12) / 24) * 100, 5)}%`,
                  opacity: 0.7,
                }}
              />
            </div>
            <p className="text-[10px] text-white/40 text-center mt-1 uppercase">
              {band}
            </p>
          </div>
        ))}
      </div>

      {/* Effects */}
      <div className="flex flex-wrap gap-1">
        {suggestion.effects.map((fx) => (
          <span
            key={fx}
            className="px-2 py-0.5 rounded-full bg-white/5 text-white/60 text-[10px]"
          >
            {fx}
          </span>
        ))}
      </div>
    </div>
  );
}
