"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { FAISSSearchResult, searchFaiss, searchFaissAudio } from "@/lib/endpoints";
import SearchResultCard from "@/components/SearchResultCard";

// ---------------------------------------------------------------------------
// Debounce helper
// ---------------------------------------------------------------------------
function useDebounce<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------
export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<FAISSSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [indexSize, setIndexSize] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const debouncedQuery = useDebounce(query, 300);

  // Text search
  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setResults([]);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    searchFaiss(debouncedQuery, 20)
      .then((res) => {
        setResults(res.results);
        setTotal(res.total);
        setIndexSize(res.index_size);
      })
      .catch((err) => setError(err.message ?? "Search failed"))
      .finally(() => setLoading(false));
  }, [debouncedQuery]);

  // Audio file search
  const handleAudioSearch = useCallback(async (file: File) => {
    setAudioFile(file);
    setLoading(true);
    setError(null);
    try {
      const res = await searchFaissAudio(file);
      setResults(res.results);
      setTotal(res.total);
      setIndexSize(res.index_size);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Audio search failed");
    } finally {
      setLoading(false);
    }
  }, []);

  // Drag-and-drop
  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleAudioSearch(file);
    },
    [handleAudioSearch]
  );

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleAudioSearch(file);
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="mx-auto max-w-3xl space-y-8 px-4 py-10">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Semantic Search</h1>
        <p className="mt-1 text-sm text-white/50">
          Describe a sound in natural language, or drop an audio file to find
          similar samples using CLAP embeddings.
        </p>
        {indexSize > 0 && (
          <p className="mt-1 text-xs text-white/30">
            Index contains {indexSize.toLocaleString()} samples
          </p>
        )}
      </div>

      {/* Text input */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "dark trap kick with sub" or "chill ambient pad"'
          className="w-full rounded-xl border border-white/10 bg-white/5 px-5 py-3.5 text-white placeholder-white/30 outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
        />
        {loading && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 text-sm animate-pulse">
            Searching…
          </span>
        )}
      </div>

      {/* Audio drop zone */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => fileInputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && fileInputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed py-8 text-sm transition-colors ${
          dragging
            ? "border-purple-400 bg-purple-500/10 text-purple-300"
            : "border-white/20 text-white/40 hover:border-white/40 hover:text-white/60"
        }`}
      >
        <span className="text-2xl">🎵</span>
        {audioFile
          ? <span className="font-medium text-white/70">{audioFile.name}</span>
          : <span>Drop an audio file here, or click to browse</span>}
        <span className="text-xs text-white/30">WAV · MP3 · FLAC · OGG</span>
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          className="sr-only"
          onChange={onFileChange}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs text-white/40">
            {total} result{total !== 1 ? "s" : ""} found
          </p>
          {results.map((r, i) => (
            <SearchResultCard key={r.index_id} result={r} rank={i + 1} />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && query.trim() && results.length === 0 && (
        <div className="flex flex-col items-center gap-3 py-16 text-white/30">
          <span className="text-4xl">🔍</span>
          <p className="text-sm">No results found for &quot;{query}&quot;</p>
          <p className="text-xs">
            Try rebuilding the index:{" "}
            <code className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-white/50">
              samplemind index rebuild ~/samples/
            </code>
          </p>
        </div>
      )}

      {/* Intro state */}
      {!query.trim() && !audioFile && !loading && (
        <div className="flex flex-col items-center gap-3 py-16 text-white/20">
          <span className="text-4xl">🎛️</span>
          <p className="text-sm">Start typing to search your sample library</p>
        </div>
      )}
    </div>
  );
}
