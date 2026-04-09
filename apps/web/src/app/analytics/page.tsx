"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getBpmHistogram,
  getEnergyBreakdown,
  getGenreBreakdown,
  getKeyHeatmap,
  getAnalyticsSummary,
  LibrarySummary,
  PlotlyChart,
} from "@/lib/endpoints";

// ---------------------------------------------------------------------------
// Plotly chart renderer (loads Plotly from CDN once, then renders via
// window.Plotly.newPlot so we avoid a heavy npm dependency)
// ---------------------------------------------------------------------------

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Plotly?: any;
  }
}

let plotlyLoaded = false;

function loadPlotly(): Promise<void> {
  if (plotlyLoaded || window.Plotly) {
    plotlyLoaded = true;
    return Promise.resolve();
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://cdn.plot.ly/plotly-2.27.0.min.js";
    script.onload = () => { plotlyLoaded = true; resolve(); };
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

interface PlotProps {
  chart: PlotlyChart | null;
  title: string;
  loading: boolean;
  error?: string | null;
}

function PlotPanel({ chart, title, loading, error }: PlotProps) {
  const divRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chart || !divRef.current) return;
    loadPlotly().then(() => {
      if (!divRef.current || !window.Plotly) return;
      window.Plotly.newPlot(
        divRef.current,
        chart.data,
        {
          ...chart.layout,
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(0,0,0,0)",
          font: { color: "rgba(255,255,255,0.7)", family: "inherit" },
          margin: { t: 40, l: 40, r: 20, b: 40 },
        },
        { responsive: true, displayModeBar: false }
      );
    });
  }, [chart]);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-white/50">
        {title}
      </h3>

      {loading && (
        <div className="flex h-48 items-center justify-center text-white/30 text-sm animate-pulse">
          Loading…
        </div>
      )}

      {error && !loading && (
        <div className="flex h-48 items-center justify-center text-red-400 text-sm">
          {error}
        </div>
      )}

      {!loading && !error && chart && (
        <div ref={divRef} className="h-64 w-full" />
      )}

      {!loading && !error && !chart && (
        <div className="flex h-48 items-center justify-center text-white/20 text-sm">
          No data
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Summary stat card
// ---------------------------------------------------------------------------
function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 text-center">
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="mt-1 text-xs text-white/50">{label}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function AnalyticsPage() {
  const [summary, setSummary] = useState<LibrarySummary | null>(null);
  const [bpmChart, setBpmChart] = useState<PlotlyChart | null>(null);
  const [keyChart, setKeyChart] = useState<PlotlyChart | null>(null);
  const [genreChart, setGenreChart] = useState<PlotlyChart | null>(null);
  const [energyChart, setEnergyChart] = useState<PlotlyChart | null>(null);
  const [loading, setLoading] = useState(true);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    const newErrors: Record<string, string> = {};

    await Promise.all([
      getAnalyticsSummary().then(setSummary).catch((e: Error) => { newErrors.summary = e.message; }),
      getBpmHistogram().then(setBpmChart).catch((e: Error) => { newErrors.bpm = e.message; }),
      getKeyHeatmap().then(setKeyChart).catch((e: Error) => { newErrors.key = e.message; }),
      getGenreBreakdown().then(setGenreChart).catch((e: Error) => { newErrors.genre = e.message; }),
      getEnergyBreakdown().then(setEnergyChart).catch((e: Error) => { newErrors.energy = e.message; }),
    ]);

    setErrors(newErrors);
    setLoading(false);
  }, []);

  // Initial fetch
  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Auto-refresh every 30 s
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchAll, 30_000);
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [autoRefresh, fetchAll]);

  return (
    <div className="mx-auto max-w-5xl space-y-8 px-4 py-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
          <p className="mt-1 text-sm text-white/50">
            Library distribution across BPM, key, genre, and energy.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-white/50">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="accent-purple-500"
            />
            Auto-refresh (30 s)
          </label>
          <button
            onClick={fetchAll}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-sm text-white/70 hover:bg-white/10 transition-colors"
          >
            ↻ Refresh
          </button>
        </div>
      </div>

      {/* Summary stats row */}
      {summary && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          <StatCard label="Total Samples" value={summary.total_samples.toLocaleString()} />
          <StatCard label="Avg BPM" value={summary.avg_bpm?.toFixed(1) ?? "—"} />
          <StatCard label="Top Key" value={summary.top_key ?? "—"} />
          <StatCard label="Top Genre" value={summary.top_genre ?? "—"} />
          <StatCard label="Coverage" value={`${summary.coverage_score ?? 0}%`} />
          <StatCard
            label="Duration"
            value={
              summary.total_duration_s
                ? `${(summary.total_duration_s / 3600).toFixed(1)} h`
                : "—"
            }
          />
        </div>
      )}

      {/* Charts 2-column grid */}
      <div className="grid gap-4 md:grid-cols-2">
        <PlotPanel
          title="BPM Distribution"
          chart={bpmChart}
          loading={loading}
          error={errors.bpm}
        />
        <PlotPanel
          title="Key / Mode Heatmap"
          chart={keyChart}
          loading={loading}
          error={errors.key}
        />
        <PlotPanel
          title="Genre Breakdown"
          chart={genreChart}
          loading={loading}
          error={errors.genre}
        />
        <PlotPanel
          title="Energy Levels"
          chart={energyChart}
          loading={loading}
          error={errors.energy}
        />
      </div>
    </div>
  );
}
