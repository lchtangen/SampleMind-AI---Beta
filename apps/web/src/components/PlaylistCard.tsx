"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Types (matching FastAPI PlaylistResponse)
// ---------------------------------------------------------------------------
export interface PlaylistSampleItem {
  filename: string;
  path: string;
  bpm?: number;
  key?: string;
  energy?: string;
  duration_s?: number;
}

export interface CuratedPlaylist {
  name: string;
  mood: string;
  energy_arc: string;
  duration_s: number;
  sample_count: number;
  samples: PlaylistSampleItem[];
  narrative: string;
  model_used: string;
}

// ---------------------------------------------------------------------------
// Energy badge colour
// ---------------------------------------------------------------------------
const ENERGY_COLOUR: Record<string, string> = {
  low: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  mid: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
  high: "bg-red-500/20 text-red-300 border-red-500/30",
};

// ---------------------------------------------------------------------------
// Single sample row
// ---------------------------------------------------------------------------
function SampleRow({
  sample,
  index,
}: {
  sample: PlaylistSampleItem;
  index: number;
}) {
  const energyClass =
    ENERGY_COLOUR[sample.energy ?? "mid"] ?? ENERGY_COLOUR["mid"];
  return (
    <div className="flex items-center gap-3 rounded-lg border border-white/5 bg-white/3 px-4 py-2.5 text-sm">
      <span className="w-5 shrink-0 text-right text-xs text-white/30 font-mono">
        {index + 1}
      </span>
      <span className="flex-1 truncate font-medium text-white/80">
        {sample.filename}
      </span>
      <div className="flex shrink-0 items-center gap-2">
        {sample.bpm !== undefined && (
          <span className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs text-white/50">
            {Math.round(sample.bpm)} BPM
          </span>
        )}
        {sample.key && (
          <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 text-xs text-purple-300">
            {sample.key}
          </span>
        )}
        {sample.energy && (
          <span
            className={`rounded-full border px-2 py-0.5 text-xs capitalize ${energyClass}`}
          >
            {sample.energy}
          </span>
        )}
        {sample.duration_s !== undefined && (
          <span className="w-10 text-right text-xs text-white/30">
            {sample.duration_s.toFixed(0)}s
          </span>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main PlaylistCard component
// ---------------------------------------------------------------------------
interface PlaylistCardProps {
  playlist: CuratedPlaylist;
  onReset?: () => void;
}

export default function PlaylistCard({ playlist, onReset }: PlaylistCardProps) {
  const [expanded, setExpanded] = useState(false);
  const minutes = Math.floor(playlist.duration_s / 60);
  const seconds = Math.round(playlist.duration_s % 60);
  const shownSamples = expanded ? playlist.samples : playlist.samples.slice(0, 5);

  return (
    <div className="space-y-4 rounded-2xl border border-white/10 bg-white/3 p-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">{playlist.name}</h2>
          <p className="mt-1 text-sm text-white/50">
            {playlist.mood} · {playlist.energy_arc} arc ·{" "}
            {minutes}m {seconds}s · {playlist.sample_count} samples
          </p>
        </div>
        <div className="flex gap-2">
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/40">
            {playlist.model_used}
          </span>
          {onReset && (
            <button
              onClick={onReset}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/40 hover:border-white/20 hover:text-white/70 transition-colors"
            >
              New playlist
            </button>
          )}
        </div>
      </div>

      {/* Narrative */}
      {playlist.narrative && (
        <div className="rounded-xl border border-purple-500/20 bg-purple-500/5 px-4 py-3 text-sm leading-relaxed text-white/70 italic">
          &ldquo;{playlist.narrative}&rdquo;
        </div>
      )}

      {/* Sample list */}
      <div className="space-y-1.5">
        {shownSamples.map((s, i) => (
          <SampleRow key={s.path ?? i} sample={s} index={i} />
        ))}
      </div>

      {/* Expand toggle */}
      {playlist.samples.length > 5 && (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="w-full rounded-lg border border-white/10 py-2 text-xs text-white/40 hover:border-white/20 hover:text-white/60 transition-colors"
        >
          {expanded
            ? "Show less"
            : `Show all ${playlist.samples.length} samples`}
        </button>
      )}
    </div>
  );
}
