'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Brain,
  Target,
  Loader2,
  Activity,
  Heart,
  Zap,
  BarChart3,
  AlertCircle,
} from 'lucide-react';
import {
  getTrendAnalysis,
  getGapAnalysis,
  type TrendAnalysis,
  type GapAnalysis,
  type TrendItem,
  type TrendForecast,
} from '@/lib/feature-endpoints';
import { cn } from '@/lib/utils';

type Tab = 'trends' | 'gaps';

export default function TrendsPage() {
  const [tab, setTab] = useState<Tab>('trends');
  const [trends, setTrends] = useState<TrendAnalysis | null>(null);
  const [gaps, setGaps] = useState<GapAnalysis | null>(null);
  const [loadingTrends, setLoadingTrends] = useState(true);
  const [loadingGaps, setLoadingGaps] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTrends();
  }, []);

  useEffect(() => {
    if (tab === 'gaps' && !gaps) loadGaps();
  }, [tab]);

  const loadTrends = async () => {
    setLoadingTrends(true);
    try {
      const data = await getTrendAnalysis(true);
      setTrends(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingTrends(false);
    }
  };

  const loadGaps = async () => {
    setLoadingGaps(true);
    try {
      const data = await getGapAnalysis();
      setGaps(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingGaps(false);
    }
  };

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-fuchsia-500 to-purple-600 flex items-center justify-center">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Trends & Gaps</h1>
            <p className="text-sm text-white/50">
              Library analytics, trend forecasts, and gap detection
            </p>
          </div>
        </div>

        {trends && (
          <div className="text-right">
            <span className="text-2xl font-bold text-white">
              {trends.library_size}
            </span>
            <p className="text-xs text-white/40">samples indexed</p>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-white/5 w-fit mb-8">
        {(['trends', 'gaps'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              'px-5 py-2 rounded-lg text-sm font-medium transition-all capitalize',
              tab === t
                ? 'bg-white/10 text-white'
                : 'text-white/40 hover:text-white/70'
            )}
          >
            {t === 'trends' ? (
              <span className="flex items-center gap-1.5">
                <BarChart3 className="h-3.5 w-3.5" />
                Trends
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <Target className="h-3.5 w-3.5" />
                Gap Analysis
              </span>
            )}
          </button>
        ))}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Trends Tab */}
      {tab === 'trends' && (
        <>
          {loadingTrends ? (
            <LoadingState text="Analyzing trends..." />
          ) : (
            trends && (
              <div className="space-y-8">
                {/* Distribution Charts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <DistributionCard
                    title="BPM Distribution"
                    icon={<Zap className="h-4 w-4 text-fuchsia-400" />}
                    items={trends.bpm_trends}
                    color="fuchsia"
                  />
                  <DistributionCard
                    title="Key Distribution"
                    icon={<Activity className="h-4 w-4 text-violet-400" />}
                    items={trends.key_trends}
                    color="violet"
                  />
                  <DistributionCard
                    title="Genre Distribution"
                    icon={<BarChart3 className="h-4 w-4 text-cyan-400" />}
                    items={trends.genre_trends}
                    color="cyan"
                  />
                  <DistributionCard
                    title="Mood Distribution"
                    icon={<Heart className="h-4 w-4 text-pink-400" />}
                    items={trends.mood_trends}
                    color="pink"
                  />
                </div>

                {/* Energy */}
                {trends.energy_distribution.length > 0 && (
                  <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                      <Zap className="h-4 w-4 text-amber-400" />
                      Energy Distribution
                    </h3>
                    <div className="flex gap-3">
                      {trends.energy_distribution.map((item) => (
                        <div
                          key={item.value}
                          className="flex-1 text-center p-3 rounded-xl bg-white/5"
                        >
                          <div className="text-lg font-bold text-white">
                            {item.percentage}%
                          </div>
                          <div className="text-xs text-white/40 capitalize">
                            {item.value}
                          </div>
                          <div className="text-[10px] text-white/30">
                            {item.count} samples
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Forecasts */}
                {trends.forecasts.length > 0 && (
                  <div className="p-6 rounded-2xl bg-gradient-to-br from-fuchsia-500/10 to-purple-500/10 border border-fuchsia-500/20">
                    <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
                      <Brain className="h-4 w-4 text-fuchsia-400" />
                      AI Forecasts
                    </h3>
                    <div className="space-y-4">
                      {trends.forecasts.map((f, i) => (
                        <ForecastCard key={i} forecast={f} index={i} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          )}
        </>
      )}

      {/* Gaps Tab */}
      {tab === 'gaps' && (
        <>
          {loadingGaps ? (
            <LoadingState text="Scanning library gaps..." />
          ) : (
            gaps && (
              <div className="space-y-6">
                {/* Health Score */}
                <div className="flex items-center gap-6 p-6 rounded-2xl bg-white/5 border border-white/10">
                  <div className="relative h-20 w-20">
                    <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
                      <circle
                        cx="50" cy="50" r="40"
                        stroke="rgba(255,255,255,0.1)" strokeWidth="8" fill="none"
                      />
                      <circle
                        cx="50" cy="50" r="40"
                        stroke={
                          gaps.library_health_score >= 70
                            ? '#10b981'
                            : gaps.library_health_score >= 40
                              ? '#f59e0b'
                              : '#ef4444'
                        }
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${(gaps.library_health_score / 100) * 251.2} 251.2`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xl font-bold text-white">
                        {Math.round(gaps.library_health_score)}
                      </span>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-white">
                      Library Health
                    </h2>
                    <p className="text-sm text-white/50 max-w-md">
                      {gaps.ai_summary}
                    </p>
                  </div>
                </div>

                {/* Gap Items */}
                {gaps.gaps.length > 0 ? (
                  <div className="space-y-3">
                    {gaps.gaps.map((gap, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        className="p-4 rounded-xl bg-white/5 border border-white/10 flex items-start gap-4"
                      >
                        <div
                          className={cn(
                            'h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0',
                            gap.severity === 'high'
                              ? 'bg-red-500/20'
                              : gap.severity === 'medium'
                                ? 'bg-amber-500/20'
                                : 'bg-blue-500/20'
                          )}
                        >
                          <AlertCircle
                            className={cn(
                              'h-4 w-4',
                              gap.severity === 'high'
                                ? 'text-red-400'
                                : gap.severity === 'medium'
                                  ? 'text-amber-400'
                                  : 'text-blue-400'
                            )}
                          />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">
                            {gap.gap}
                          </p>
                          <p className="text-xs text-white/50 mt-1">
                            {gap.recommendation}
                          </p>
                        </div>
                        <span className="text-xs text-white/30 uppercase">
                          {gap.category}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 rounded-xl bg-white/5 border border-white/10 text-center">
                    <Target className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
                    <p className="text-sm text-white/60">
                      No significant gaps detected. Your library is well-balanced!
                    </p>
                  </div>
                )}
              </div>
            )
          )}
        </>
      )}
    </div>
  );
}

function DistributionCard({
  title,
  icon,
  items,
  color,
}: {
  title: string;
  icon: React.ReactNode;
  items: TrendItem[];
  color: string;
}) {
  if (items.length === 0) return null;

  const maxPct = Math.max(...items.map((i) => i.percentage));

  return (
    <div className="p-5 rounded-2xl bg-white/5 border border-white/10">
      <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
        {icon}
        {title}
      </h3>
      <div className="space-y-2">
        {items.slice(0, 8).map((item) => (
          <div key={item.value} className="flex items-center gap-3">
            <span className="text-xs text-white/50 w-28 truncate">
              {item.value}
            </span>
            <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full',
                  `bg-${color}-500`
                )}
                style={{
                  width: `${(item.percentage / maxPct) * 100}%`,
                  backgroundColor:
                    color === 'fuchsia'
                      ? '#d946ef'
                      : color === 'violet'
                        ? '#8b5cf6'
                        : color === 'cyan'
                          ? '#06b6d4'
                          : '#ec4899',
                }}
              />
            </div>
            <span className="text-xs text-white/40 w-12 text-right tabular-nums">
              {item.percentage}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ForecastCard({
  forecast,
  index,
}: {
  forecast: TrendForecast;
  index: number;
}) {
  return (
    <div className="p-4 rounded-xl bg-white/5 border border-white/5">
      <div className="flex items-start justify-between mb-2">
        <p className="text-sm font-medium text-white">{forecast.prediction}</p>
        <span
          className={cn(
            'px-2 py-0.5 rounded-full text-[10px] font-medium',
            forecast.confidence >= 0.7
              ? 'bg-emerald-500/20 text-emerald-400'
              : forecast.confidence >= 0.4
                ? 'bg-amber-500/20 text-amber-400'
                : 'bg-white/10 text-white/50'
          )}
        >
          {(forecast.confidence * 100).toFixed(0)}% confidence
        </span>
      </div>
      <p className="text-xs text-white/50">{forecast.rationale}</p>
      <p className="text-[10px] text-white/30 mt-1">{forecast.timeframe}</p>
    </div>
  );
}

function LoadingState({ text }: { text: string }) {
  return (
    <div className="flex items-center justify-center py-20 gap-3">
      <Loader2 className="h-6 w-6 text-fuchsia-400 animate-spin" />
      <span className="text-white/50">{text}</span>
    </div>
  );
}
