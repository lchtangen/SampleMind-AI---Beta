'use client';

import { useMemo, useState, useEffect, useCallback } from 'react';
import { Sparkles, RefreshCw, Music2 } from 'lucide-react';
import { useRecommendations, RecommendationContext, RecommendationMode } from '@/hooks/useRecommendations';
import { useAuthContext } from '@/contexts/AuthContext';
import { useWebSocket } from '@/hooks/useWebSocket';

const MUSIC_KEYS = [
  'C major', 'C minor',
  'C# major', 'C# minor',
  'D major', 'D minor',
  'Eb major', 'Eb minor',
  'E major', 'E minor',
  'F major', 'F minor',
  'F# major', 'F# minor',
  'G major', 'G minor',
  'Ab major', 'Ab minor',
  'A major', 'A minor',
  'Bb major', 'Bb minor',
  'B major', 'B minor',
];

interface RecommendationsPanelProps {
  className?: string;
}

export function RecommendationsPanel({ className }: RecommendationsPanelProps) {
  const {
    context,
    suggestions,
    loading,
    error,
    updateContext,
    refresh,
    recordPreview,
    recordAccept,
    recordSkip,
    applyRealtimeUpdate,
    mode,
    setMode,
  } = useRecommendations();
  const { user } = useAuthContext();

  const handleRealtimeMessage = useCallback((message: { type: string; data?: any }) => {
    if (message.type === 'recommendations_update' && message.data) {
      applyRealtimeUpdate(message.data);
    }
  }, [applyRealtimeUpdate]);

  useWebSocket({
    userId: user?.id ?? 0,
    onMessage: handleRealtimeMessage,
  });
  const [formState, setFormState] = useState<RecommendationContext>({ ...context });
  const moodInput = useMemo(() => (formState.mood_tags || []).join(', '), [formState.mood_tags]);
  const modes: RecommendationMode[] = ['fusion', 'rules'];

  useEffect(() => {
    setFormState({ ...context });
  }, [context]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const sanitized: RecommendationContext = {
      ...formState,
      mood_tags: (formState.mood_tags || []).filter(Boolean),
    };
    await updateContext(sanitized);
  };

  const handleMoodChange = (value: string) => {
    setFormState(prev => ({
      ...prev,
      mood_tags: value
        .split(',')
        .map(tag => tag.trim())
        .filter(Boolean),
    }));
  };

  return (
    <section className={`relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6 ${className ?? ''}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Sparkles className="h-6 w-6 text-[hsl(220,90%,60%)]" />
          <div>
            <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)]">Suggested for You</h3>
            <p className="text-sm text-[hsl(220,10%,65%)]">Fine-tune the vibe and SampleMind will surface matching loops instantly.</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <div className="inline-flex rounded-lg border border-white/10 bg-white/5 p-1">
            {modes.map(option => (
              <button
                key={option}
                type="button"
                onClick={() => setMode(option)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition ${
                  mode === option
                    ? 'bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white shadow-lg shadow-[hsl(220,90%,60%)]/30'
                    : 'text-[hsl(220,10%,70%)] hover:text-[hsl(0,0%,98%)]'
                }`}
              >
                {option === 'fusion' ? 'Fusion' : 'Rules'}
              </button>
            ))}
          </div>
          <button
            onClick={refresh}
            className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 transition text-sm text-[hsl(220,10%,65%)]"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="grid md:grid-cols-4 gap-4 mb-6">
        <label className="flex flex-col">
          <span className="text-xs uppercase tracking-wide text-[hsl(220,10%,65%)] mb-2">Tempo (BPM)</span>
          <input
            type="number"
            min={60}
            max={200}
            placeholder="128"
            value={formState.bpm ?? ''}
            onChange={(event) => setFormState(prev => ({ ...prev, bpm: event.target.value ? Number(event.target.value) : null }))}
            className="rounded-lg bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] px-3 py-2 focus:outline-none focus:border-[hsl(220,90%,60%)]/50"
          />
        </label>

        <label className="flex flex-col">
          <span className="text-xs uppercase tracking-wide text-[hsl(220,10%,65%)] mb-2">Key</span>
          <select
            value={formState.key ?? ''}
            onChange={(event) => setFormState(prev => ({ ...prev, key: event.target.value || null }))}
            className="rounded-lg bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] px-3 py-2 focus:outline-none focus:border-[hsl(220,90%,60%)]/50"
          >
            <option value="">Any key</option>
            {MUSIC_KEYS.map(key => (
              <option key={key} value={key}>{key}</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col md:col-span-2">
          <span className="text-xs uppercase tracking-wide text-[hsl(220,10%,65%)] mb-2">Mood Tags</span>
          <input
            type="text"
            placeholder="uplifting, cinematic"
            value={moodInput}
            onChange={(event) => handleMoodChange(event.target.value)}
            className="rounded-lg bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] px-3 py-2 focus:outline-none focus:border-[hsl(220,90%,60%)]/50"
          />
        </label>

        <button
          type="submit"
          className="md:col-span-4 justify-self-start px-4 py-2 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition"
          disabled={loading}
        >
          Update Preferences
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-4">
        {suggestions.length === 0 && !loading && (
          <div className="col-span-3 text-center text-[hsl(220,10%,65%)]">
            No suggestions yet. Adjust the context above to get personalized picks.
          </div>
        )}

        {suggestions.map((item, index) => (
          <div key={item.audio_id} className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-xl blur-xl group-hover:opacity-80 transition" />
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-5 h-full flex flex-col space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                    <Music2 className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-[hsl(0,0%,98%)] font-semibold">#{item.audio_id}</p>
                    {item.filename && (
                      <p className="text-xs text-[hsl(220,10%,65%)] truncate">{item.filename}</p>
                    )}
                  </div>
                </div>
                {item.source && (
                  <span className="text-[10px] uppercase tracking-wide px-2 py-1 rounded-full bg-white/10 border border-white/10 text-[hsl(220,90%,60%)]">
                    {item.source}
                  </span>
                )}
              </div>

              {item.rationale && (
                <p className="text-xs text-[hsl(220,10%,65%)]">{item.rationale}</p>
              )}

              {item.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {item.tags.slice(0, 4).map(tag => (
                    <span key={tag} className="text-xs px-2 py-1 rounded-full bg-white/10 border border-white/10 text-[hsl(0,0%,98%)]">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {item.score_components && (
                <div className="flex flex-wrap gap-2 text-[10px] text-[hsl(220,10%,65%)]">
                  {Object.entries(item.score_components).map(([key, value]) => (
                    <span key={key} className="px-2 py-1 rounded-full bg-white/5 border border-white/10">
                      {key}: {value.toFixed(2)}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex flex-wrap gap-2 pt-3 mt-auto text-xs">
                <button
                  type="button"
                  onClick={() => recordPreview(item, index)}
                  className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/60 transition text-[hsl(220,10%,80%)]"
                >
                  Preview
                </button>
                <button
                  type="button"
                  onClick={() => recordAccept(item, index)}
                  className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/40 transition"
                >
                  Use Sample
                </button>
                <button
                  type="button"
                  onClick={() => recordSkip(item, index)}
                  className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-red-500/50 hover:text-red-200 transition text-[hsl(220,10%,70%)]"
                >
                  Dismiss
                </button>
              </div>

              <div className="flex items-center justify-between text-xs text-[hsl(220,10%,65%)]">
                <span>Score: {item.score.toFixed(2)}</span>
                {item.tempo && <span>{Math.round(item.tempo)} BPM</span>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
