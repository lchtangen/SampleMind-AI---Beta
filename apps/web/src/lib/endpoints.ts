/**
 * SampleMind AI — Typed endpoint helpers
 *
 * Each function maps to a FastAPI route.  All return typed Promises.
 * Import from "@/lib/endpoints" in page/component files.
 */

import { apiFetch, apiUpload } from "./api-client";

// ---------------------------------------------------------------------------
// Shared response types
// ---------------------------------------------------------------------------

export interface LibrarySummary {
  total_samples: number;
  total_duration_s: number;
  avg_bpm: number;
  top_key: string;
  top_genre: string;
  coverage_score: number;
  model_used?: string;
}

export interface FAISSSearchResult {
  index_id: number;
  path: string;
  filename: string;
  score: number;
  metadata: {
    bpm?: number;
    key?: string;
    energy?: string;
    genre_labels?: string[];
    mood_labels?: string[];
  };
}

export interface FAISSSearchResponse {
  query: string;
  results: FAISSSearchResult[];
  total: number;
  index_size: number;
}

export interface PlotlyChart {
  data: unknown[];
  layout: Record<string, unknown>;
}

export interface BpmHistogramResponse extends PlotlyChart {}
export interface KeyHeatmapResponse extends PlotlyChart {}
export interface GenreBreakdownResponse extends PlotlyChart {}
export interface EnergyBreakdownResponse extends PlotlyChart {}

export interface SampleEntry {
  id: string;
  filename: string;
  path: string;
  bpm?: number;
  key?: string;
  energy?: string;
  genre_labels?: string[];
  mood_labels?: string[];
  duration_s?: number;
  created_at?: string;
}

export interface LibraryResponse {
  samples: SampleEntry[];
  total: number;
  page: number;
  page_size: number;
}

export interface GapReportResponse {
  total_samples: number;
  coverage_score: number;
  gap_count: number;
  critical_gaps: number;
  moderate_gaps: number;
  suggestions: string[];
  summary: string;
  model_used: string;
}

export interface TaskQueueResponse {
  task_id: string;
  status: "queued" | "in_progress" | "done" | "error";
}

// ---------------------------------------------------------------------------
// Analytics endpoints  (GET /api/v1/analytics/*)
// ---------------------------------------------------------------------------

export const getAnalyticsSummary = (): Promise<LibrarySummary> =>
  apiFetch("/api/v1/analytics/summary");

export const getBpmHistogram = (): Promise<BpmHistogramResponse> =>
  apiFetch("/api/v1/analytics/bpm-histogram");

export const getKeyHeatmap = (): Promise<KeyHeatmapResponse> =>
  apiFetch("/api/v1/analytics/key-heatmap");

export const getGenreBreakdown = (): Promise<GenreBreakdownResponse> =>
  apiFetch("/api/v1/analytics/genre-breakdown");

export const getEnergyBreakdown = (): Promise<EnergyBreakdownResponse> =>
  apiFetch("/api/v1/analytics/energy-breakdown");

// ---------------------------------------------------------------------------
// FAISS Semantic Search  (GET /api/v1/ai/faiss)
// ---------------------------------------------------------------------------

export const searchFaiss = (
  query: string,
  limit = 20
): Promise<FAISSSearchResponse> =>
  apiFetch(`/api/v1/ai/faiss?q=${encodeURIComponent(query)}&limit=${limit}`);

export const searchFaissAudio = (file: File): Promise<FAISSSearchResponse> => {
  const form = new FormData();
  form.append("file", file);
  return apiUpload("/api/v1/ai/faiss/audio", form);
};

// ---------------------------------------------------------------------------
// Library  (GET /api/v1/library or /api/v1/collections)
// ---------------------------------------------------------------------------

export const getLibrarySamples = (
  page = 1,
  pageSize = 50,
  filters?: { bpm_min?: number; bpm_max?: number; key?: string; genre?: string }
): Promise<LibraryResponse> => {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
    ...(filters?.bpm_min !== undefined && {
      bpm_min: String(filters.bpm_min),
    }),
    ...(filters?.bpm_max !== undefined && {
      bpm_max: String(filters.bpm_max),
    }),
    ...(filters?.key && { key: filters.key }),
    ...(filters?.genre && { genre: filters.genre }),
  });
  return apiFetch(`/api/v1/audio/library?${params}`);
};

// ---------------------------------------------------------------------------
// Curation  (GET /api/v1/ai/curate/*)
// ---------------------------------------------------------------------------

export const getCurationGaps = (): Promise<GapReportResponse> =>
  apiFetch("/api/v1/ai/curate/gaps");

// ---------------------------------------------------------------------------
// Agent tasks  (POST /api/v1/tasks/analyze-agent)
// ---------------------------------------------------------------------------

export const queueAnalysisAgent = (
  filePath: string
): Promise<TaskQueueResponse> =>
  apiFetch("/api/v1/tasks/analyze-agent", {
    method: "POST",
    body: JSON.stringify({ file_path: filePath }),
  });
