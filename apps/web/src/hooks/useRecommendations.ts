/**
 * Hook for interacting with recommendation API
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { RecommendationAPI } from '@/lib/api-client';
import { buildTelemetryEvent, sendRecommendationTelemetry, RecommendationTelemetryEventType } from '@/lib/telemetry';

export interface RecommendationContext {
  bpm?: number | null;
  key?: string | null;
  mode?: string | null;
  mood_tags?: string[];
  genre?: string | null;
  energy?: number | null;
  target_embedding?: number[] | null;
}

export interface RecommendationItem {
  audio_id: number;
  filename?: string | null;
  score: number;
  rationale?: string | null;
  tags: string[];
  tempo?: number | null;
  source?: string | null;
  score_components?: Record<string, number> | null;
}

export type RecommendationMode = 'fusion' | 'rules';

export interface RecommendationRealtimePayload {
  context?: RecommendationContext;
  suggestions?: RecommendationItem[];
  mode?: RecommendationMode;
}

export interface RecommendationState {
  context: RecommendationContext;
  suggestions: RecommendationItem[];
  loading: boolean;
  error: string | null;
  mode: RecommendationMode;
}

const DEFAULT_CONTEXT: RecommendationContext = {
  bpm: null,
  key: null,
  mode: null,
  mood_tags: [],
  genre: null,
  energy: null,
  target_embedding: null,
};

const DEFAULT_MODE: RecommendationMode = (process.env.NEXT_PUBLIC_RECOMMENDATION_MODE as RecommendationMode) || 'fusion';

export function useRecommendations(topK = 6) {
  const [state, setState] = useState<RecommendationState>({
    context: DEFAULT_CONTEXT,
    suggestions: [],
    loading: false,
    error: null,
    mode: DEFAULT_MODE,
  });

  const generateSessionId = () => {
    const globalCrypto = typeof globalThis !== 'undefined' ? (globalThis.crypto as { randomUUID?: () => string } | undefined) : undefined;
    if (globalCrypto && typeof globalCrypto.randomUUID === 'function') {
      return globalCrypto.randomUUID();
    }
    return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  };

  const telemetrySessionRef = useRef<string>(generateSessionId());
  const viewedRef = useRef<Set<number>>(new Set());

  const applyRealtimeUpdate = useCallback((payload: RecommendationRealtimePayload) => {
    if (!payload) {
      return;
    }
    viewedRef.current = new Set();
    setState(prev => ({
      ...prev,
      context: payload.context ?? prev.context,
      suggestions: payload.suggestions ?? prev.suggestions,
      loading: false,
      error: null,
      mode: payload.mode ?? prev.mode,
    }));
  }, []);

  const fetchSuggestions = useCallback(async (contextOverride?: RecommendationContext, modeOverride?: RecommendationMode) => {
    const activeMode = modeOverride ?? state.mode;
    setState(prev => ({ ...prev, loading: true, error: null, mode: activeMode }));
    try {
      const response = await RecommendationAPI.getTop(topK, activeMode);
      setState(prev => ({
        ...prev,
        context: response?.context ?? contextOverride ?? prev.context,
        suggestions: response?.suggestions ?? [],
        loading: false,
        mode: (response?.mode as RecommendationMode) || activeMode,
      }));
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Failed to fetch recommendations',
      }));
    }
  }, [state.mode, topK]);

  useEffect(() => {
    fetchSuggestions();
  }, [fetchSuggestions]);

  useEffect(() => {
    const viewed = viewedRef.current;
    const payloads = state.suggestions
      .map((item, index) => ({ item, index }))
      .filter(({ item }) => !viewed.has(item.audio_id))
      .map(({ item, index }) => {
        viewed.add(item.audio_id);
        return buildTelemetryEvent('view', item, index, {
          context: {
            bpm: state.context.bpm,
            key: state.context.key,
            genre: state.context.genre,
            mood_tags: state.context.mood_tags,
            mode: state.mode,
          },
        });
      });

    if (payloads.length) {
      sendRecommendationTelemetry(payloads, telemetrySessionRef.current);
    }
  }, [state.suggestions, state.context]);

  const recordTelemetry = useCallback((
    type: RecommendationTelemetryEventType,
    item: RecommendationItem,
    rank?: number,
    metadata?: Record<string, unknown>,
  ) => {
    const contextMetadata = {
      context: {
        bpm: state.context.bpm,
        key: state.context.key,
        genre: state.context.genre,
        mood_tags: state.context.mood_tags,
        mode: state.mode,
      },
      ...metadata,
    };

    sendRecommendationTelemetry(
      [buildTelemetryEvent(type, item, rank, contextMetadata)],
      telemetrySessionRef.current,
    );
  }, [state.context, state.mode]);

  const recordPreview = useCallback((item: RecommendationItem, rank?: number) => {
    recordTelemetry('preview', item, rank, { action: 'preview' });
  }, [recordTelemetry]);

  const recordAccept = useCallback((item: RecommendationItem, rank?: number) => {
    recordTelemetry('accept', item, rank, { action: 'accept' });
  }, [recordTelemetry]);

  const recordSkip = useCallback((item: RecommendationItem, rank?: number) => {
    recordTelemetry('skip', item, rank, { action: 'skip' });
  }, [recordTelemetry]);

  const updateContext = useCallback(async (partial: RecommendationContext) => {
    const nextContext: RecommendationContext = {
      ...state.context,
      ...partial,
      mood_tags: partial.mood_tags ?? state.context.mood_tags ?? [],
    };

    setState(prev => ({ ...prev, context: nextContext, loading: true }));

    try {
      await RecommendationAPI.updateContext({
        bpm: nextContext.bpm ?? null,
        key: nextContext.key ?? null,
        mode: nextContext.mode ?? null,
        mood_tags: nextContext.mood_tags ?? [],
        genre: nextContext.genre ?? null,
        energy: nextContext.energy ?? null,
        target_embedding: nextContext.target_embedding ?? null,
      });
      viewedRef.current = new Set();
      return { success: true };
    } catch (error: any) {
      const message = error.message || 'Failed to update context';
      setState(prev => ({ ...prev, error: message, loading: false }));
      return { success: false, error: message };
    }
  }, [state.context]);

  const setMode = useCallback(async (mode: RecommendationMode) => {
    setState(prev => ({ ...prev, mode, loading: true, context: { ...prev.context, mode }, error: null }));
    await fetchSuggestions(undefined, mode);
  }, [fetchSuggestions]);

  const refresh = useCallback(async () => {
    await fetchSuggestions();
  }, [fetchSuggestions]);

  return {
    ...state,
    updateContext,
    refresh,
    recordPreview,
    recordAccept,
    recordSkip,
    applyRealtimeUpdate,
    setMode,
  };
}
