/**
 * @fileoverview Typed endpoint helpers for the SampleMind AI web frontend.
 *
 * Each exported function maps 1-to-1 to a FastAPI route on the Python backend.
 * All functions return typed `Promise`s resolved via {@link apiFetch} or
 * {@link apiUpload} from `@/lib/api-client`.
 *
 * **Route groups:**
 * | Prefix                          | Description                          |
 * |---------------------------------|--------------------------------------|
 * | `GET  /api/v1/analytics/*`      | Plotly chart data & library summary  |
 * | `GET  /api/v1/ai/faiss`         | FAISS semantic text search           |
 * | `POST /api/v1/ai/faiss/audio`   | FAISS audio-to-audio similarity      |
 * | `GET  /api/v1/audio/library`    | Paginated sample library             |
 * | `GET  /api/v1/ai/curate/gaps`   | Library gap analysis report          |
 * | `POST /api/v1/tasks/analyze-agent` | Queue a LangGraph agent task      |
 * | `GET  /api/v1/tasks/:id`        | Poll task status                     |
 * | `ws   /ws/agent/:id`            | Real-time agent progress stream      |
 * | `POST /api/v1/ai/curate/playlist` | AI-generated playlist              |
 *
 * @example
 * ```ts
 * import { getAnalyticsSummary, searchFaiss } from "@/lib/endpoints";
 *
 * const summary = await getAnalyticsSummary();
 * const hits    = await searchFaiss("dark trap kick", 10);
 * ```
 *
 * @module lib/endpoints
 */

import { apiFetch, apiUpload } from "./api-client";

// ---------------------------------------------------------------------------
// Shared response types
// ---------------------------------------------------------------------------

/** Aggregate statistics for the user's sample library. */
export interface LibrarySummary {
  total_samples: number;
  total_duration_s: number;
  avg_bpm: number;
  top_key: string;
  top_genre: string;
  coverage_score: number;
  model_used?: string;
}

/** A single hit returned by the FAISS semantic search index. */
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

/** Wrapper response for a FAISS search query, including result count and index size. */
export interface FAISSSearchResponse {
  query: string;
  results: FAISSSearchResult[];
  total: number;
  index_size: number;
}

/** Generic shape of a Plotly chart payload (data traces + layout). */
export interface PlotlyChart {
  data: unknown[];
  layout: Record<string, unknown>;
}

export interface BpmHistogramResponse extends PlotlyChart {}
export interface KeyHeatmapResponse extends PlotlyChart {}
export interface GenreBreakdownResponse extends PlotlyChart {}
export interface EnergyBreakdownResponse extends PlotlyChart {}

/** A single audio sample record from the library. */
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

/** Paginated response for the audio library listing. */
export interface LibraryResponse {
  samples: SampleEntry[];
  total: number;
  page: number;
  page_size: number;
}

/** AI-generated gap analysis report for the user's library. */
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

/** Status response for a Celery background task. */
export interface TaskQueueResponse {
  task_id: string;
  status: "queued" | "in_progress" | "done" | "error";
}

// ---------------------------------------------------------------------------
// Analytics endpoints  (GET /api/v1/analytics/*)
// ---------------------------------------------------------------------------

/** Fetch the aggregate library summary (total samples, avg BPM, top key, etc.). */
export const getAnalyticsSummary = (): Promise<LibrarySummary> =>
  apiFetch("/api/v1/analytics/summary");

/** Fetch a Plotly BPM histogram chart payload. */
export const getBpmHistogram = (): Promise<BpmHistogramResponse> =>
  apiFetch("/api/v1/analytics/bpm-histogram");

/** Fetch a Plotly key-distribution heatmap chart payload. */
export const getKeyHeatmap = (): Promise<KeyHeatmapResponse> =>
  apiFetch("/api/v1/analytics/key-heatmap");

/** Fetch a Plotly genre-breakdown chart payload. */
export const getGenreBreakdown = (): Promise<GenreBreakdownResponse> =>
  apiFetch("/api/v1/analytics/genre-breakdown");

/** Fetch a Plotly energy-breakdown (pie) chart payload. */
export const getEnergyBreakdown = (): Promise<EnergyBreakdownResponse> =>
  apiFetch("/api/v1/analytics/energy-breakdown");

// ---------------------------------------------------------------------------
// FAISS Semantic Search  (GET /api/v1/ai/faiss)
// ---------------------------------------------------------------------------

/**
 * Run a text-based FAISS semantic search against the CLAP embedding index.
 *
 * @param query - Natural-language search query (e.g. "dark trap kick").
 * @param limit - Maximum number of results to return (default 20).
 */
export const searchFaiss = (
  query: string,
  limit = 20
): Promise<FAISSSearchResponse> =>
  apiFetch(`/api/v1/ai/faiss?q=${encodeURIComponent(query)}&limit=${limit}`);

/**
 * Upload an audio file for FAISS audio-to-audio similarity search.
 *
 * @param file - The audio `File` blob to search against.
 */
export const searchFaissAudio = (file: File): Promise<FAISSSearchResponse> => {
  const form = new FormData();
  form.append("file", file);
  return apiUpload("/api/v1/ai/faiss/audio", form);
};

// ---------------------------------------------------------------------------
// Library  (GET /api/v1/library or /api/v1/collections)
// ---------------------------------------------------------------------------

/**
 * Fetch a paginated list of samples from the user's library.
 *
 * @param page     - 1-based page number.
 * @param pageSize - Number of samples per page (default 50).
 * @param filters  - Optional BPM range, key, or genre filter.
 */
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

/** Fetch the AI-generated library gap analysis report. */
export const getCurationGaps = (): Promise<GapReportResponse> =>
  apiFetch("/api/v1/ai/curate/gaps");

// ---------------------------------------------------------------------------
// Agent tasks  (POST /api/v1/tasks/analyze-agent + WebSocket progress)
// ---------------------------------------------------------------------------

/** Request body to queue a LangGraph agent analysis task. */
export interface AgentAnalysisRequest {
  file_path: string;
  analysis_level?: "basic" | "standard" | "detailed" | "professional";
}

/** Response when an agent task has been successfully queued. */
export interface AgentTaskResponse {
  task_id: string;
  status: string;
  file_path: string;
}

/** Real-time progress message received over the agent WebSocket. */
export interface AgentProgressUpdate {
  task_id: string;
  stage: string;
  pct: number;
  message?: string;
}

/**
 * Queue a LangGraph agent analysis task on the backend (Celery).
 *
 * @param request - The file path and analysis level to process.
 */
export const queueAnalysisAgent = (
  request: AgentAnalysisRequest
): Promise<AgentTaskResponse> =>
  apiFetch("/api/v1/tasks/analyze-agent", {
    method: "POST",
    body: JSON.stringify(request),
  });

/**
 * Poll the current status of a background Celery task.
 *
 * @param taskId - The UUID returned by {@link queueAnalysisAgent}.
 */
export const getTaskStatus = (
  taskId: string
): Promise<TaskQueueResponse> =>
  apiFetch(`/api/v1/tasks/${taskId}`);

/**
 * Open WebSocket for real-time agent task progress
 * @example
 * ```typescript
 * const ws = openAgentProgressWebSocket("task-123", (update) => {
 *   console.log(`Progress: ${update.pct}% - ${update.stage}`);
 * });
 * ```
 */
export const openAgentProgressWebSocket = (
  taskId: string,
  onUpdate: (update: AgentProgressUpdate) => void,
  onError?: (error: Error) => void
): WebSocket => {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const wsUrl = `${protocol}//${new URL(baseUrl).host}/ws/agent/${taskId}`;

  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    try {
      const update = JSON.parse(event.data) as AgentProgressUpdate;
      onUpdate(update);
    } catch (err) {
      console.error("Failed to parse WebSocket message:", err);
    }
  };

  ws.onerror = (event) => {
    const error = new Error(`WebSocket error: ${event.type}`);
    onError?.(error);
  };

  return ws;
};

// ---------------------------------------------------------------------------
// Playlist & Curation (POST /api/v1/ai/curate/playlist)
// ---------------------------------------------------------------------------

/** Parameters for AI-generated playlist creation. */
export interface PlaylistRequest {
  mood?: string;
  energy_arc?: "build" | "plateau" | "decline" | "mixed";
  duration_minutes?: number;
  genre?: string;
  bpm_range?: [number, number];
}

/** A single sample positioned within a generated playlist. */
export interface PlaylistSample {
  id: string;
  filename: string;
  bpm: number;
  energy: number;
  position_in_arc: number;
}

/** Response payload for a generated playlist, including total duration. */
export interface PlaylistResponse {
  samples: PlaylistSample[];
  total_duration_ms: number;
  average_energy: number;
}

/**
 * Request the backend to generate an AI-curated playlist.
 *
 * @param request - Mood, energy arc, duration, genre, and BPM constraints.
 */
export const generatePlaylist = (
  request: PlaylistRequest
): Promise<PlaylistResponse> =>
  apiFetch("/api/v1/ai/curate/playlist", {
    method: "POST",
    body: JSON.stringify(request),
  });
