'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Radar,
  Upload,
  Loader2,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Minus,
  CheckCircle,
  AlertTriangle,
} from 'lucide-react';
import {
  compareMix,
  type CompareResponse,
  type FrequencyBand,
} from '@/lib/feature-endpoints';
import { cn } from '@/lib/utils';

export default function ReferencePage() {
  const [mixPath, setMixPath] = useState('');
  const [refPath, setRefPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState('');

  const handleCompare = async () => {
    if (!mixPath.trim() || !refPath.trim()) return;
    setLoading(true);
    setError('');
    try {
      const resp = await compareMix(mixPath, refPath);
      setResult(resp);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
          <Radar className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Mix Reference</h1>
          <p className="text-sm text-white/50">
            Compare your mix against a reference track for professional results
          </p>
        </div>
      </div>

      {/* Input: Two file paths */}
      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end mb-8">
        <div>
          <label className="text-xs text-white/50 mb-1 block">Your Mix</label>
          <input
            type="text"
            value={mixPath}
            onChange={(e) => setMixPath(e.target.value)}
            placeholder="Path to your mix..."
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 text-sm"
          />
        </div>
        <ArrowRight className="h-5 w-5 text-white/20 hidden md:block mb-3" />
        <div>
          <label className="text-xs text-white/50 mb-1 block">
            Reference Track
          </label>
          <input
            type="text"
            value={refPath}
            onChange={(e) => setRefPath(e.target.value)}
            placeholder="Path to reference..."
            className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 text-sm"
          />
        </div>
      </div>

      <button
        onClick={handleCompare}
        disabled={!mixPath.trim() || !refPath.trim() || loading}
        className={cn(
          'px-6 py-3 rounded-xl font-medium text-sm transition-all flex items-center gap-2 mb-8',
          mixPath.trim() && refPath.trim()
            ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white hover:shadow-lg hover:shadow-emerald-500/25'
            : 'bg-white/5 text-white/20'
        )}
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Radar className="h-4 w-4" />
            Compare
          </>
        )}
      </button>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Score */}
            <div className="flex items-center gap-6 p-6 rounded-2xl bg-white/5 border border-white/10">
              <div className="relative h-24 w-24">
                <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke={
                      result.overall_score >= 80
                        ? '#10b981'
                        : result.overall_score >= 50
                          ? '#f59e0b'
                          : '#ef4444'
                    }
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${(result.overall_score / 100) * 251.2} 251.2`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-white">
                    {Math.round(result.overall_score)}
                  </span>
                </div>
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Match Score</h2>
                <p className="text-sm text-white/50">
                  {result.overall_score >= 80
                    ? 'Excellent match — professional quality'
                    : result.overall_score >= 50
                      ? 'Good match — some adjustments needed'
                      : 'Significant differences detected'}
                </p>
              </div>
            </div>

            {/* Loudness Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard
                label="LUFS Difference"
                value={`${result.lufs_difference > 0 ? '+' : ''}${result.lufs_difference}`}
                sub={`Mix: ${result.mix_lufs} / Ref: ${result.reference_lufs}`}
                ok={Math.abs(result.lufs_difference) < 2}
              />
              <StatCard
                label="Dynamic Range (Mix)"
                value={`${result.dynamic_range_mix} dB`}
                sub={`Reference: ${result.dynamic_range_reference} dB`}
                ok={Math.abs(result.dynamic_range_mix - result.dynamic_range_reference) < 3}
              />
              <StatCard
                label="Frequency Bands"
                value={`${result.frequency_bands.filter((b) => Math.abs(b.difference_db) < 3).length}/${result.frequency_bands.length}`}
                sub="within tolerance"
                ok={
                  result.frequency_bands.filter((b) => Math.abs(b.difference_db) < 3)
                    .length >= 5
                }
              />
            </div>

            {/* Frequency Band Comparison */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
              <h3 className="text-sm font-semibold text-white mb-4">
                Frequency Comparison
              </h3>
              <div className="space-y-3">
                {result.frequency_bands.map((band) => (
                  <FrequencyBar key={band.range_hz} band={band} />
                ))}
              </div>
            </div>

            {/* AI Recommendations */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
              <h3 className="text-sm font-semibold text-white mb-4">
                AI Recommendations
              </h3>
              <div className="space-y-3">
                {result.ai_recommendations.map((rec, i) => (
                  <div
                    key={i}
                    className="flex gap-3 p-3 rounded-lg bg-white/5"
                  >
                    <span className="h-5 w-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                      {i + 1}
                    </span>
                    <p className="text-sm text-white/70">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  ok,
}: {
  label: string;
  value: string;
  sub: string;
  ok: boolean;
}) {
  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/10">
      <div className="flex items-center gap-2 mb-1">
        {ok ? (
          <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
        ) : (
          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
        )}
        <span className="text-xs text-white/50">{label}</span>
      </div>
      <p className="text-xl font-bold text-white">{value}</p>
      <p className="text-xs text-white/40">{sub}</p>
    </div>
  );
}

function FrequencyBar({ band }: { band: FrequencyBand }) {
  const maxDb = 60;
  const mixWidth = Math.max(((band.mix_db + maxDb) / maxDb) * 100, 2);
  const refWidth = Math.max(((band.reference_db + maxDb) / maxDb) * 100, 2);
  const diff = band.difference_db;

  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-white/50 w-32 truncate">{band.name}</span>
      <div className="flex-1 space-y-1">
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400"
            style={{ width: `${Math.min(mixWidth, 100)}%` }}
          />
        </div>
        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-white/30 to-white/20"
            style={{ width: `${Math.min(refWidth, 100)}%` }}
          />
        </div>
      </div>
      <span
        className={cn(
          'text-xs font-mono w-16 text-right',
          Math.abs(diff) < 3
            ? 'text-emerald-400'
            : Math.abs(diff) < 6
              ? 'text-amber-400'
              : 'text-red-400'
        )}
      >
        {diff > 0 ? '+' : ''}
        {diff.toFixed(1)} dB
      </span>
    </div>
  );
}
