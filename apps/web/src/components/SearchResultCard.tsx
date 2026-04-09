"use client";

import { FAISSSearchResult } from "@/lib/endpoints";

interface Props {
  result: FAISSSearchResult;
  rank: number;
}

/** Colour-codes the similarity score bar: green ≥ 0.7, yellow ≥ 0.4, red < 0.4 */
function scoreColour(score: number): string {
  if (score >= 0.7) return "bg-green-500";
  if (score >= 0.4) return "bg-yellow-400";
  return "bg-red-400";
}

export default function SearchResultCard({ result, rank }: Props) {
  const pct = Math.round(result.score * 100);
  const bpm = result.metadata?.bpm;
  const key = result.metadata?.key;
  const energy = result.metadata?.energy;
  const genres = result.metadata?.genre_labels ?? [];
  const moods = result.metadata?.mood_labels ?? [];

  return (
    <div className="flex items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition-colors">
      {/* Rank badge */}
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white/10 text-xs font-bold text-white/60">
        {rank}
      </span>

      {/* Main content */}
      <div className="min-w-0 flex-1 space-y-2">
        {/* Filename */}
        <p
          className="truncate font-medium text-white"
          title={result.path}
        >
          {result.filename}
        </p>

        {/* Score bar */}
        <div className="flex items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/10">
            <div
              className={`h-full rounded-full ${scoreColour(result.score)}`}
              style={{ width: `${pct}%` }}
            />
          </div>
          <span className="w-10 text-right text-xs text-white/50">
            {pct}%
          </span>
        </div>

        {/* Metadata badges */}
        <div className="flex flex-wrap gap-1.5 text-xs">
          {bpm !== undefined && (
            <Badge label={`${bpm.toFixed(0)} BPM`} colour="purple" />
          )}
          {key && <Badge label={key} colour="blue" />}
          {energy && <Badge label={energy} colour="orange" />}
          {genres.slice(0, 3).map((g) => (
            <Badge key={g} label={g} colour="teal" />
          ))}
          {moods.slice(0, 2).map((m) => (
            <Badge key={m} label={m} colour="pink" />
          ))}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Internal Badge helper
// ---------------------------------------------------------------------------

type BadgeColour = "purple" | "blue" | "orange" | "teal" | "pink";

const COLOUR_MAP: Record<BadgeColour, string> = {
  purple: "bg-purple-500/20 text-purple-300",
  blue: "bg-blue-500/20 text-blue-300",
  orange: "bg-orange-500/20 text-orange-300",
  teal: "bg-teal-500/20 text-teal-300",
  pink: "bg-pink-500/20 text-pink-300",
};

function Badge({ label, colour }: { label: string; colour: BadgeColour }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 font-medium ${COLOUR_MAP[colour]}`}
    >
      {label}
    </span>
  );
}
