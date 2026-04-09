"use client";

import { useRef, useState } from "react";
import PlaylistCard, { CuratedPlaylist } from "@/components/PlaylistCard";
import { apiFetch } from "@/lib/api-client";

// ---------------------------------------------------------------------------
// Selectors
// ---------------------------------------------------------------------------
const MOODS = ["dark", "chill", "euphoric", "tense", "uplifting"] as const;
const ARCS = ["build", "drop", "plateau", "tension"] as const;
type Mood = (typeof MOODS)[number];
type Arc = (typeof ARCS)[number];

const MOOD_EMOJI: Record<Mood, string> = {
  dark: "🌑",
  chill: "🌊",
  euphoric: "✨",
  tense: "⚡",
  uplifting: "🌅",
};

const ARC_DESC: Record<Arc, string> = {
  build: "Low → Mid → High energy",
  drop: "High → Mid → Low energy",
  plateau: "Sustained mid energy",
  tension: "Oscillating build & release",
};

// ---------------------------------------------------------------------------
// Progress bar
// ---------------------------------------------------------------------------
function ProgressBar({ stage, pct }: { stage: string; pct: number }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs text-white/50">
        <span className="capitalize">{stage}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------
export default function GeneratePage() {
  const [mood, setMood] = useState<Mood>("dark");
  const [arc, setArc] = useState<Arc>("build");
  const [duration, setDuration] = useState(30);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<{ stage: string; pct: number } | null>(null);
  const [playlist, setPlaylist] = useState<CuratedPlaylist | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // ---- Generate -------------------------------------------------------
  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setPlaylist(null);
    setProgress({ stage: "starting", pct: 0 });

    try {
      // 1. POST to curate/playlist — this runs synchronously in the API
      const result = await apiFetch<CuratedPlaylist>(
        "/api/v1/ai/curate/playlist",
        {
          method: "POST",
          body: JSON.stringify({
            mood,
            energy_arc: arc,
            duration_minutes: duration,
          }),
        }
      );
      setPlaylist(result);
      setProgress(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Generation failed");
      setProgress(null);
    } finally {
      setLoading(false);
    }
  };

  // ---- Also support queuing via agent task with WS progress ----------
  const handleGenerateWithAgent = async () => {
    setLoading(true);
    setError(null);
    setPlaylist(null);
    setProgress({ stage: "queuing", pct: 2 });

    try {
      // Queue analysis agent — the task will push progress to Redis/WS
      const taskResp = await apiFetch<{ task_id: string; status: string }>(
        "/api/v1/tasks/analyze-agent",
        {
          method: "POST",
          body: JSON.stringify({
            file_path: "/library",   // sentinel: generate from library
            analysis_depth: "standard",
          }),
        }
      );

      // Open WebSocket for progress
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const wsUrl = `${protocol}//${new URL(apiBase).host}/ws/agent/${taskResp.task_id}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onmessage = (ev) => {
        try {
          const update = JSON.parse(ev.data) as {
            stage: string;
            pct: number;
            message?: string;
          };
          setProgress({ stage: update.stage, pct: update.pct });
          if (update.pct >= 100 || update.stage === "error") {
            ws.close();
            wsRef.current = null;
            setLoading(false);
            setProgress(null);
          }
        } catch {}
      };

      ws.onerror = () => {
        setError("WebSocket error — check backend");
        setLoading(false);
        setProgress(null);
      };
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to queue job");
      setLoading(false);
      setProgress(null);
    }
  };

  const handleReset = () => {
    setPlaylist(null);
    setError(null);
    setProgress(null);
    wsRef.current?.close();
  };

  // ---- Render ---------------------------------------------------------
  return (
    <div className="mx-auto max-w-2xl space-y-8 px-4 py-10">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">AI Playlist Generator</h1>
        <p className="mt-1 text-sm text-white/50">
          Curate a mood-driven sample playlist from your library using CLAP
          embeddings + Camelot harmonic scoring.
        </p>
      </div>

      {/* Controls — hidden when showing result */}
      {!playlist && (
        <div className="space-y-6 rounded-2xl border border-white/10 bg-white/3 p-6">
          {/* Mood */}
          <div>
            <label className="mb-3 block text-sm font-medium text-white/70">
              Mood
            </label>
            <div className="flex flex-wrap gap-2">
              {MOODS.map((m) => (
                <button
                  key={m}
                  onClick={() => setMood(m)}
                  className={`flex items-center gap-2 rounded-xl border px-4 py-2 text-sm capitalize transition-all ${
                    mood === m
                      ? "border-purple-500 bg-purple-500/20 text-purple-200"
                      : "border-white/10 bg-white/5 text-white/50 hover:border-white/20 hover:text-white/70"
                  }`}
                >
                  <span>{MOOD_EMOJI[m]}</span>
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Energy arc */}
          <div>
            <label className="mb-3 block text-sm font-medium text-white/70">
              Energy Arc
            </label>
            <div className="grid grid-cols-2 gap-2">
              {ARCS.map((a) => (
                <button
                  key={a}
                  onClick={() => setArc(a)}
                  className={`rounded-xl border px-4 py-3 text-left text-sm transition-all ${
                    arc === a
                      ? "border-indigo-500 bg-indigo-500/20 text-indigo-200"
                      : "border-white/10 bg-white/5 text-white/50 hover:border-white/20 hover:text-white/70"
                  }`}
                >
                  <div className="font-medium capitalize">{a}</div>
                  <div className="mt-0.5 text-xs opacity-60">{ARC_DESC[a]}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="mb-3 flex justify-between text-sm font-medium text-white/70">
              <span>Duration</span>
              <span className="text-white/40">{duration} minutes</span>
            </label>
            <input
              type="range"
              min={1}
              max={120}
              step={5}
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="w-full accent-purple-500"
            />
            <div className="mt-1 flex justify-between text-xs text-white/20">
              <span>1 min</span>
              <span>120 min</span>
            </div>
          </div>

          {/* Generate buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex-1 rounded-xl bg-purple-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Generating…" : "Generate Playlist"}
            </button>
            <button
              onClick={handleGenerateWithAgent}
              disabled={loading}
              title="Queue via LangGraph agent with live progress"
              className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/50 transition-colors hover:border-white/20 hover:text-white/70 disabled:cursor-not-allowed disabled:opacity-40"
            >
              🤖 Agent
            </button>
          </div>

          {/* Progress */}
          {loading && progress && (
            <ProgressBar stage={progress.stage} pct={progress.pct} />
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}{" "}
          <button
            onClick={handleReset}
            className="ml-2 underline underline-offset-2 hover:text-red-200"
          >
            Try again
          </button>
        </div>
      )}

      {/* Result */}
      {playlist && (
        <PlaylistCard playlist={playlist} onReset={handleReset} />
      )}

      {/* Empty state */}
      {!playlist && !loading && !error && (
        <div className="flex flex-col items-center gap-3 py-10 text-white/20">
          <span className="text-5xl">🎛️</span>
          <p className="text-sm">
            Select a mood and arc, then generate your playlist
          </p>
          <p className="text-xs text-white/10">
            Requires{" "}
            <code className="rounded bg-white/10 px-1 text-white/30">
              samplemind index rebuild ~/samples/
            </code>{" "}
            first
          </p>
        </div>
      )}
    </div>
  );
}
