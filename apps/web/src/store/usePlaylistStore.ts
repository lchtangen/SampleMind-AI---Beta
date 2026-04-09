/**
 * usePlaylistStore — Zustand slice for AI playlist generation state. (P2-004)
 *
 * Tracks active playlists, generation history, and the currently playing
 * playlist item. Server mutations happen in generate/page.tsx components;
 * this store keeps the client-side playlist state across route changes.
 */
import { create } from "zustand";
import { devtools } from "zustand/middleware";

// ---------------------------------------------------------------------------
// Types (mirrors backend PlaylistResponse schema)
// ---------------------------------------------------------------------------

export interface PlaylistSampleItem {
  filename: string;
  path: string;
  bpm?: number;
  key?: string;
  energy?: string;
  duration_s?: number;
}

export interface GeneratedPlaylist {
  name: string;
  mood: string;
  energy_arc: string;
  duration_s: number;
  sample_count: number;
  samples: PlaylistSampleItem[];
  narrative: string;
  model_used: string;
  generated_at: number;   // Date.now() timestamp
}

export type GenerationStatus =
  | "idle"
  | "queuing"
  | "running"
  | "done"
  | "error";

interface PlaylistState {
  // Active playlist
  currentPlaylist: GeneratedPlaylist | null;
  currentSampleIndex: number;

  // Generation progress
  status: GenerationStatus;
  stage: string;
  progressPct: number;
  errorMessage: string | null;

  // History (up to 10 playlists)
  history: GeneratedPlaylist[];
}

interface PlaylistActions {
  setPlaylist: (pl: GeneratedPlaylist) => void;
  clearPlaylist: () => void;
  setCurrentSample: (index: number) => void;
  nextSample: () => void;
  prevSample: () => void;
  setStatus: (status: GenerationStatus, stage?: string, pct?: number) => void;
  setError: (msg: string) => void;
  clearError: () => void;
  clearHistory: () => void;
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

const MAX_HISTORY = 10;

export const usePlaylistStore = create<PlaylistState & PlaylistActions>()(
  devtools(
    (set, get) => ({
      // ── Initial state ────────────────────────────────────────────────────
      currentPlaylist: null,
      currentSampleIndex: 0,
      status: "idle",
      stage: "",
      progressPct: 0,
      errorMessage: null,
      history: [],

      // ── Actions ──────────────────────────────────────────────────────────
      setPlaylist: (pl) =>
        set((state) => {
          const newHistory = [pl, ...state.history].slice(0, MAX_HISTORY);
          return {
            currentPlaylist: pl,
            currentSampleIndex: 0,
            status: "done",
            progressPct: 100,
            errorMessage: null,
            history: newHistory,
          };
        }),

      clearPlaylist: () =>
        set({
          currentPlaylist: null,
          currentSampleIndex: 0,
          status: "idle",
          stage: "",
          progressPct: 0,
          errorMessage: null,
        }),

      setCurrentSample: (index) =>
        set((state) => {
          if (!state.currentPlaylist) return {};
          const clamped = Math.max(
            0,
            Math.min(index, state.currentPlaylist.samples.length - 1)
          );
          return { currentSampleIndex: clamped };
        }),

      nextSample: () =>
        set((state) => {
          if (!state.currentPlaylist) return {};
          const next = Math.min(
            state.currentSampleIndex + 1,
            state.currentPlaylist.samples.length - 1
          );
          return { currentSampleIndex: next };
        }),

      prevSample: () =>
        set((state) => ({
          currentSampleIndex: Math.max(0, state.currentSampleIndex - 1),
        })),

      setStatus: (status, stage = "", pct = 0) =>
        set({ status, stage, progressPct: pct }),

      setError: (msg) =>
        set({ status: "error", errorMessage: msg, progressPct: 0 }),

      clearError: () => set({ errorMessage: null, status: "idle" }),

      clearHistory: () => set({ history: [] }),
    }),
    { name: "PlaylistStore" }
  )
);
