/**
 * @fileoverview Search result card component for FAISS semantic search results.
 *
 * Renders a single search hit as a compact card showing:
 * - Numeric rank badge
 * - Filename (truncated, with full path tooltip)
 * - Colour-coded similarity score progress bar (green ≥ 70 %, yellow ≥ 40 %, red < 40 %)
 * - Metadata badges — BPM, musical key, energy level, genres, and moods
 *
 * Designed to be rendered inside a results list by the search page.
 *
 * @module components/SearchResultCard
 */

"use client";

import { FAISSSearchResult } from "@/lib/endpoints";

/**
 * Props accepted by {@link SearchResultCard}.
 *
 * @property result - A single FAISS search hit containing filename, score, and metadata.
 * @property rank   - 1-based display rank within the results list.
 */
interface Props {
  result: FAISSSearchResult;
  rank: number;
}

/**
 * Map a FAISS similarity score (0–1) to a Tailwind background colour class.
 *
 * - `≥ 0.7` → green (strong match)
 * - `≥ 0.4` → yellow (moderate match)
 * - `< 0.4` → red (weak match)
 *
 * @param score - Normalised similarity score between 0 and 1.
 * @returns A Tailwind CSS `bg-*` class string.
 */
function scoreColour(score: number): string {
  if (score >= 0.7) return "bg-green-500";
  if (score >= 0.4) return "bg-yellow-400";
  return "bg-red-400";
}

/**
 * Renders a single FAISS search result as a card with rank, score bar, and metadata.
 *
 * @param props
 * @param props.result - The {@link FAISSSearchResult} to display.
 * @param props.rank   - 1-based position in the search results list.
 * @returns A styled card element.
 */
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

/** Allowed colour presets for metadata badges. */
type BadgeColour = "purple" | "blue" | "orange" | "teal" | "pink";

const COLOUR_MAP: Record<BadgeColour, string> = {
  purple: "bg-purple-500/20 text-purple-300",
  blue: "bg-blue-500/20 text-blue-300",
  orange: "bg-orange-500/20 text-orange-300",
  teal: "bg-teal-500/20 text-teal-300",
  pink: "bg-pink-500/20 text-pink-300",
};

/**
 * Small pill badge used to display metadata values (BPM, key, genre, etc.).
 *
 * @param props.label  - Text displayed inside the badge.
 * @param props.colour - Visual colour preset mapped via {@link COLOUR_MAP}.
 */
function Badge({ label, colour }: { label: string; colour: BadgeColour }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 font-medium ${COLOUR_MAP[colour]}`}
    >
      {label}
    </span>
  );
}
