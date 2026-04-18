'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Package,
  Sparkles,
  Loader2,
  Music,
  Tag,
  Image,
  Copy,
  Check,
  Lightbulb,
} from 'lucide-react';
import {
  getPackSuggestions,
  generatePack,
  type PackSuggestion,
  type GeneratedPack,
  type PackSample,
} from '@/lib/feature-endpoints';
import { cn } from '@/lib/utils';

export default function AutoPacksPage() {
  const [suggestions, setSuggestions] = useState<PackSuggestion[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(true);
  const [generatedPack, setGeneratedPack] = useState<GeneratedPack | null>(null);
  const [generating, setGenerating] = useState(false);
  const [customTheme, setCustomTheme] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadSuggestions();
  }, []);

  const loadSuggestions = useCallback(async () => {
    setLoadingSuggestions(true);
    try {
      const data = await getPackSuggestions();
      setSuggestions(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoadingSuggestions(false);
    }
  }, []);

  const handleGenerate = useCallback(
    async (theme: string) => {
      if (!theme.trim()) return;
      setGenerating(true);
      setError('');
      setGeneratedPack(null);
      try {
        const pack = await generatePack(theme);
        setGeneratedPack(pack);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setGenerating(false);
      }
    },
    []
  );

  return (
    <div className="min-h-screen p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
          <Package className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Auto Packs</h1>
          <p className="text-sm text-white/50">
            AI curates themed sample packs from your library
          </p>
        </div>
      </div>

      {/* Custom Theme Input */}
      <div className="flex gap-3 mb-8">
        <input
          type="text"
          value={customTheme}
          onChange={(e) => setCustomTheme(e.target.value)}
          placeholder="Enter a theme, e.g. 'Dark Ambient Textures'..."
          className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-amber-500/50 text-sm"
          onKeyDown={(e) => {
            if (e.key === 'Enter') handleGenerate(customTheme);
          }}
        />
        <button
          onClick={() => handleGenerate(customTheme)}
          disabled={!customTheme.trim() || generating}
          className={cn(
            'px-6 py-3 rounded-xl font-medium text-sm transition-all flex items-center gap-2',
            customTheme.trim()
              ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:shadow-lg hover:shadow-amber-500/25'
              : 'bg-white/5 text-white/20'
          )}
        >
          {generating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          Generate Pack
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* AI Suggestions */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="h-4 w-4 text-amber-400" />
          <h2 className="text-sm font-semibold text-white/80">
            AI Suggestions for Your Library
          </h2>
        </div>
        {loadingSuggestions ? (
          <div className="flex items-center gap-2 text-white/40 text-sm">
            <Loader2 className="h-4 w-4 animate-spin" />
            Analyzing your library...
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {suggestions.map((sug) => (
              <button
                key={sug.theme}
                onClick={() => handleGenerate(sug.theme)}
                disabled={generating}
                className="text-left p-4 rounded-xl bg-white/5 border border-white/10 hover:border-amber-500/30 hover:bg-white/8 transition-all group"
              >
                <h3 className="text-sm font-semibold text-white group-hover:text-amber-400 transition-colors">
                  {sug.theme}
                </h3>
                <p className="text-xs text-white/40 mt-1 line-clamp-2">
                  {sug.description}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] text-white/30">
                    ~{sug.estimated_samples} samples
                  </span>
                  {sug.genres.length > 0 && (
                    <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 text-[10px]">
                      {sug.genres[0]}
                    </span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Generated Pack */}
      <AnimatePresence>
        {generatedPack && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Pack Header */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/20">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">
                    {generatedPack.name}
                  </h2>
                  <p className="text-sm text-white/60 mt-1">
                    {generatedPack.description}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {generatedPack.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded-full bg-white/10 text-white/60 text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-3xl font-bold text-amber-400">
                    {generatedPack.sample_count}
                  </span>
                  <p className="text-xs text-white/40">samples</p>
                </div>
              </div>

              {/* Cover Art Prompt */}
              {generatedPack.cover_art_prompt && (
                <CopyableField
                  label="Cover Art Prompt"
                  value={generatedPack.cover_art_prompt}
                  icon={<Image className="h-3 w-3" />}
                />
              )}
            </div>

            {/* Samples List */}
            <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
              <h3 className="text-sm font-semibold text-white mb-4">
                Curated Samples
              </h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {generatedPack.samples.map((sample, i) => (
                  <div
                    key={sample.filename}
                    className="flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/8 transition-colors"
                  >
                    <span className="text-xs text-white/30 w-6 text-right tabular-nums">
                      {i + 1}
                    </span>
                    <Music className="h-4 w-4 text-amber-400 flex-shrink-0" />
                    <span className="text-sm text-white/80 truncate flex-1">
                      {sample.filename}
                    </span>
                    {sample.bpm && (
                      <span className="text-xs text-white/40">
                        {sample.bpm} BPM
                      </span>
                    )}
                    {sample.key && (
                      <span className="text-xs text-white/40">{sample.key}</span>
                    )}
                    {sample.similarity_score && (
                      <span className="text-xs text-amber-400 tabular-nums">
                        {(sample.similarity_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function CopyableField({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-4 p-3 rounded-lg bg-black/20 border border-white/10">
      <div className="flex items-center gap-1.5 mb-1">
        {icon}
        <span className="text-[10px] text-white/40 uppercase">{label}</span>
        <button
          onClick={handleCopy}
          className="ml-auto p-1 rounded hover:bg-white/10 transition-colors"
        >
          {copied ? (
            <Check className="h-3 w-3 text-emerald-400" />
          ) : (
            <Copy className="h-3 w-3 text-white/40" />
          )}
        </button>
      </div>
      <p className="text-xs text-white/60 leading-relaxed">{value}</p>
    </div>
  );
}
