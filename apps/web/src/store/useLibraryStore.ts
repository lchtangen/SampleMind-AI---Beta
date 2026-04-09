/**
 * useLibraryStore — Zustand slice for the sample library state. (P2-004)
 *
 * Stores the current page of samples, filter state, and selection set.
 * Server fetching is handled separately by TanStack Query / SWR;
 * this store holds UI-level state that needs to persist across navigation.
 */
import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SampleMeta {
  id: string;
  filename: string;
  path: string;
  bpm?: number;
  key?: string;
  energy?: string;
  genre_labels?: string[];
  mood_labels?: string[];
  duration_s?: number;
}

export interface LibraryFilters {
  bpm_min?: number;
  bpm_max?: number;
  key?: string;
  genre?: string;
  mood?: string;
  energy?: string;
  search?: string;
}

interface LibraryState {
  // Data
  samples: SampleMeta[];
  total: number;
  page: number;
  pageSize: number;

  // Filters
  filters: LibraryFilters;

  // Selection
  selectedIds: Set<string>;

  // UI
  viewMode: "grid" | "list";
  sortBy: "filename" | "bpm" | "created_at";
  sortDir: "asc" | "desc";
}

interface LibraryActions {
  setSamples: (samples: SampleMeta[], total: number) => void;
  setPage: (page: number) => void;
  setFilters: (filters: Partial<LibraryFilters>) => void;
  clearFilters: () => void;
  toggleSelection: (id: string) => void;
  selectAll: () => void;
  clearSelection: () => void;
  setViewMode: (mode: "grid" | "list") => void;
  setSortBy: (key: LibraryState["sortBy"], dir?: LibraryState["sortDir"]) => void;
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

const DEFAULT_FILTERS: LibraryFilters = {};

export const useLibraryStore = create<LibraryState & LibraryActions>()(
  devtools(
    persist(
      (set, get) => ({
        // ── Initial state ──────────────────────────────────────────────────
        samples: [],
        total: 0,
        page: 1,
        pageSize: 50,
        filters: DEFAULT_FILTERS,
        selectedIds: new Set<string>(),
        viewMode: "grid",
        sortBy: "filename",
        sortDir: "asc",

        // ── Actions ────────────────────────────────────────────────────────
        setSamples: (samples, total) => set({ samples, total }),

        setPage: (page) => set({ page }),

        setFilters: (incoming) =>
          set((state) => ({
            filters: { ...state.filters, ...incoming },
            page: 1,              // reset to page 1 on filter change
          })),

        clearFilters: () => set({ filters: DEFAULT_FILTERS, page: 1 }),

        toggleSelection: (id) =>
          set((state) => {
            const next = new Set(state.selectedIds);
            if (next.has(id)) {
              next.delete(id);
            } else {
              next.add(id);
            }
            return { selectedIds: next };
          }),

        selectAll: () =>
          set((state) => ({
            selectedIds: new Set(state.samples.map((s) => s.id)),
          })),

        clearSelection: () => set({ selectedIds: new Set<string>() }),

        setViewMode: (mode) => set({ viewMode: mode }),

        setSortBy: (key, dir) =>
          set((state) => ({
            sortBy: key,
            sortDir:
              dir ?? (state.sortBy === key && state.sortDir === "asc" ? "desc" : "asc"),
          })),
      }),
      {
        name: "samplemind-library",
        // Don't persist samples (re-fetched on load); persist UI preferences
        partialize: (state) => ({
          filters: state.filters,
          viewMode: state.viewMode,
          sortBy: state.sortBy,
          sortDir: state.sortDir,
          pageSize: state.pageSize,
        }),
      }
    ),
    { name: "LibraryStore" }
  )
);
