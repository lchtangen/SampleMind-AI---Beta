/**
 * SampleMind AI — New feature endpoint helpers
 *
 * Typed wrappers for Copilot, Remix, Graph, Reference, Auto Packs, and Trends APIs.
 */

import { apiFetch } from './api-client';

const BASE_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

// ── Copilot Chat (SSE streaming) ─────────────────────────────────────────────

export interface CopilotMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface CopilotChatRequest {
  messages: CopilotMessage[];
  context?: Record<string, unknown>;
  prefer_fast?: boolean;
}

export interface CopilotContextResponse {
  context_analysis: string;
  model_used: string;
}

/**
 * Stream copilot chat via SSE. Returns an async iterator of text chunks.
 */
export async function* streamCopilotChat(
  body: CopilotChatRequest,
  signal?: AbortSignal
): AsyncGenerator<string> {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('samplemind_token')
    : null;

  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}/api/v1/copilot/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    throw new Error(`Copilot error ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        yield data;
      }
    }
  }
}

export async function analyzeCopilotContext(
  context: Record<string, unknown>
): Promise<CopilotContextResponse> {
  return apiFetch('/api/v1/copilot/analyze-context', {
    method: 'POST',
    body: JSON.stringify({ context }),
  });
}

// ── Remix Studio ─────────────────────────────────────────────────────────────

export interface StemInfo {
  name: string;
  filename: string;
  size_bytes: number;
  duration: number;
  url: string;
}

export interface SeparateResponse {
  task_id: string;
  status: string;
  stems?: StemInfo[];
}

export interface MixSuggestion {
  stem: string;
  eq: { low: number; mid: number; high: number };
  effects: string[];
  gain_db: number;
  pan: number;
}

export interface MixSuggestResponse {
  suggestions: MixSuggestion[];
  narrative: string;
  model_used: string;
}

export async function separateStems(
  filePath: string,
  model?: string
): Promise<SeparateResponse> {
  return apiFetch('/api/v1/remix/separate', {
    method: 'POST',
    body: JSON.stringify({ file_path: filePath, model: model ?? 'htdemucs_6s' }),
  });
}

export async function getStemResults(taskId: string): Promise<SeparateResponse> {
  return apiFetch(`/api/v1/remix/${taskId}/stems`);
}

export async function getStemMixSuggestions(
  taskId: string,
  style?: string
): Promise<MixSuggestResponse> {
  return apiFetch(`/api/v1/remix/${taskId}/suggest-mix`, {
    method: 'POST',
    body: JSON.stringify({ style }),
  });
}

// ── Sonic Graph ──────────────────────────────────────────────────────────────

export interface GraphNode {
  id: string;
  filename: string;
  bpm: number | null;
  key: string | null;
  energy: string | null;
  genre: string[];
  mood: string[];
  x: number;
  y: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

export interface SonicMapResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  clusters: Array<{ label: string; node_ids: string[]; count: number }>;
}

export async function getSonicMap(
  limit?: number,
  threshold?: number
): Promise<SonicMapResponse> {
  const params = new URLSearchParams();
  if (limit) params.set('limit', String(limit));
  if (threshold) params.set('similarity_threshold', String(threshold));
  return apiFetch(`/api/v1/graph/sonic-map?${params}`);
}

export async function getCluster(
  sampleId: string,
  topK?: number
): Promise<{
  source: { filename: string; bpm: number | null; key: string | null; energy: string | null };
  similar: Array<{ filename: string; score: number; bpm?: number; key?: string; genre?: string[] }>;
  total: number;
}> {
  const params = topK ? `?top_k=${topK}` : '';
  return apiFetch(`/api/v1/graph/cluster/${encodeURIComponent(sampleId)}${params}`);
}

// ── Mix Reference ────────────────────────────────────────────────────────────

export interface FrequencyBand {
  name: string;
  range_hz: string;
  mix_db: number;
  reference_db: number;
  difference_db: number;
}

export interface CompareResponse {
  mix_lufs: number;
  reference_lufs: number;
  lufs_difference: number;
  dynamic_range_mix: number;
  dynamic_range_reference: number;
  frequency_bands: FrequencyBand[];
  ai_recommendations: string[];
  overall_score: number;
  model_used: string;
}

export async function compareMix(
  mixPath: string,
  referencePath: string
): Promise<CompareResponse> {
  return apiFetch('/api/v1/reference/compare', {
    method: 'POST',
    body: JSON.stringify({ mix_path: mixPath, reference_path: referencePath }),
  });
}

// ── Auto Packs ───────────────────────────────────────────────────────────────

export interface PackSuggestion {
  theme: string;
  description: string;
  estimated_samples: number;
  moods: string[];
  genres: string[];
}

export interface PackSample {
  filename: string;
  bpm: number | null;
  key: string | null;
  energy: string | null;
  genre: string[];
  similarity_score: number | null;
}

export interface GeneratedPack {
  name: string;
  description: string;
  tags: string[];
  samples: PackSample[];
  sample_count: number;
  cover_art_prompt: string;
  status: string;
}

export async function getPackSuggestions(): Promise<PackSuggestion[]> {
  return apiFetch('/api/v1/autopacks/suggestions');
}

export async function generatePack(
  theme: string,
  maxSamples?: number,
  targetMood?: string,
  targetEnergy?: string
): Promise<GeneratedPack> {
  return apiFetch('/api/v1/autopacks/generate', {
    method: 'POST',
    body: JSON.stringify({
      theme,
      max_samples: maxSamples ?? 25,
      target_mood: targetMood,
      target_energy: targetEnergy,
    }),
  });
}

// ── Trends ───────────────────────────────────────────────────────────────────

export interface TrendItem {
  category: string;
  value: string;
  count: number;
  percentage: number;
  direction: string;
  confidence: number;
}

export interface TrendForecast {
  prediction: string;
  rationale: string;
  confidence: number;
  timeframe: string;
}

export interface TrendAnalysis {
  generated_at: string;
  library_size: number;
  bpm_trends: TrendItem[];
  key_trends: TrendItem[];
  genre_trends: TrendItem[];
  mood_trends: TrendItem[];
  energy_distribution: TrendItem[];
  forecasts: TrendForecast[];
}

export interface GapItem {
  category: string;
  gap: string;
  severity: string;
  recommendation: string;
  sample_count_needed: number;
}

export interface GapAnalysis {
  total_gaps: number;
  gaps: GapItem[];
  library_health_score: number;
  ai_summary: string;
}

export async function getTrendAnalysis(
  includeForecasts?: boolean
): Promise<TrendAnalysis> {
  const params = includeForecasts === false ? '?include_forecasts=false' : '';
  return apiFetch(`/api/v1/trends/analysis${params}`);
}

export async function getGapAnalysis(): Promise<GapAnalysis> {
  return apiFetch('/api/v1/trends/gaps');
}
