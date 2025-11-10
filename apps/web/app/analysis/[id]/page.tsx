'use client';

import { useState, useEffect, useCallback, type ReactNode } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  Music,
  ArrowLeft,
  Play,
  Pause,
  Download,
  Share2,
  Activity,
  TrendingUp,
  Zap,
  Disc,
  Volume2,
  Clock,
  RefreshCcw,
} from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useNotification } from '@/contexts/NotificationContext';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AudioFeatures {
  tempo?: number;
  key?: string;
  time_signature?: string;
  duration?: number;
  loudness?: number;
  energy?: number;
  danceability?: number;
  valence?: number;
  spectral_centroid?: number;
  zero_crossing_rate?: number;
}

interface AIAnalysis {
  genre?: string[];
  mood?: string[];
  instruments?: string[];
  tags?: string[];
  similarity_score?: number;
  description?: string;
}

interface AudioDetail {
  id: number;
  filename: string;
  file_size: number;
  format: string;
  duration?: number | null;
  sample_rate?: number | null;
  channels?: number | null;
  uploaded_at: string;
  status: string;
  features?: AudioFeatures | null;
  ai_analysis?: AIAnalysis | null;
}

function AnalysisContent() {
  const params = useParams<{ id: string }>();
  const audioId = Number(params.id);
  const { user } = useAuthContext();
  const { getAudio, analyzeAudio } = useAudio();
  const { addNotification } = useNotification();

  const [analysis, setAnalysis] = useState<AudioDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const fetchAnalysis = useCallback(async () => {
    if (Number.isNaN(audioId)) {
      setAnalysis(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    const result = await getAudio(audioId);
    if (result.success && result.data) {
      setAnalysis(result.data as AudioDetail);
    } else {
      addNotification('error', result.error || 'Unable to load analysis');
      setAnalysis(null);
    }
    setIsLoading(false);
  }, [audioId, getAudio, addNotification]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  useWebSocket({
    userId: user?.id ?? 0,
    onMessage: (message) => {
      if (message.type === 'analysis_status') {
        if (!message.data || message.data.audio_id === audioId || message.data.id === audioId) {
          fetchAnalysis();
        }
      }
    },
  });

  const handleReanalyze = async () => {
    if (!analysis) return;
    setIsAnalyzing(true);
    const result = await analyzeAudio(analysis.id);
    if (result.success) {
      addNotification('info', 'Analysis started, results will update shortly.');
      fetchAnalysis();
    } else {
      addNotification('error', result.error || 'Failed to trigger analysis');
    }
    setIsAnalyzing(false);
  };

  const formatDuration = (seconds?: number | null) => {
    if (!seconds || Number.isNaN(seconds)) return '—';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading analysis..." />
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[hsl(0,0%,98%)] text-xl mb-4">Analysis not found</p>
          <Link href="/library" className="text-[hsl(220,90%,60%)] hover:underline">
            Back to Library
          </Link>
        </div>
      </div>
    );
  }

  const { features, ai_analysis: aiAnalysis } = analysis;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)]">
      <header className="border-b border-white/10 backdrop-blur-md bg-black/20">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                SampleMind AI
              </h1>
            </Link>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleReanalyze}
                disabled={isAnalyzing}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 transition text-sm text-[hsl(220,10%,65%)] disabled:opacity-50"
              >
                <RefreshCcw className={`h-4 w-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
                <span>{isAnalyzing ? 'Re-analyzing…' : 'Re-run Analysis'}</span>
              </button>
              <Link
                href="/library"
                className="flex items-center space-x-2 text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Library</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="relative mb-8">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-2xl blur-3xl"></div>

            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                <div className="flex items-start space-x-6">
                  <div className="h-24 w-24 rounded-xl bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center flex-shrink-0">
                    <Music className="h-12 w-12 text-white" />
                  </div>

                  <div>
                    <h2 className="text-3xl font-bold text-[hsl(0,0%,98%)] mb-2">
                      {analysis.filename}
                    </h2>
                    <div className="flex flex-wrap items-center gap-3 text-[hsl(220,10%,65%)]">
                      <span>{formatDuration(features?.duration)}</span>
                      <span>•</span>
                      <span>{features?.tempo ? `${features.tempo.toFixed(1)} BPM` : 'Tempo N/A'}</span>
                      <span>•</span>
                      <span>{features?.key || 'Key N/A'}</span>
                    </div>
                    <p className="mt-3 text-sm text-[hsl(220,10%,65%)]">
                      Uploaded {new Date(analysis.uploaded_at).toLocaleString()} • Status: {analysis.status}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="h-14 w-14 rounded-xl bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition"
                  >
                    {isPlaying ? (
                      <Pause className="h-6 w-6 text-white" />
                    ) : (
                      <Play className="h-6 w-6 text-white ml-1" />
                    )}
                  </button>

                  <button className="h-14 w-14 rounded-xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition" title="Download">
                    <Download className="h-5 w-5 text-[hsl(220,10%,65%)]" />
                  </button>

                  <button className="h-14 w-14 rounded-xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition" title="Share">
                    <Share2 className="h-5 w-5 text-[hsl(220,10%,65%)]" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <FeatureCard
              title="Tempo"
              icon={<Activity className="h-8 w-8 text-[hsl(320,90%,60%)]" />}
              value={features?.tempo ? `${features.tempo.toFixed(1)} BPM` : 'N/A'}
            />
            <FeatureCard
              title="Energy"
              icon={<Zap className="h-8 w-8 text-[hsl(220,90%,60%)]" />}
              value={features?.energy ? `${Math.round(features.energy * 100)}%` : 'N/A'}
            />
            <FeatureCard
              title="Key"
              icon={<Disc className="h-8 w-8 text-[hsl(270,85%,65%)]" />}
              value={features?.key || 'N/A'}
            />
            <FeatureCard
              title="Danceability"
              icon={<TrendingUp className="h-8 w-8 text-[hsl(180,95%,55%)]" />}
              value={features?.danceability ? `${Math.round(features.danceability * 100)}%` : 'N/A'}
            />
            <FeatureCard
              title="Loudness"
              icon={<Volume2 className="h-8 w-8 text-[hsl(320,90%,60%)]" />}
              value={features?.loudness ? `${features.loudness.toFixed(1)} dB` : 'N/A'}
            />
            <FeatureCard
              title="Duration"
              icon={<Clock className="h-8 w-8 text-[hsl(220,90%,60%)]" />}
              value={formatDuration(features?.duration)}
            />
          </div>

          {aiAnalysis && (
            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-2xl blur-2xl"></div>
                <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)] mb-4">AI Summary</h3>
                  <p className="text-[hsl(220,10%,65%)] leading-relaxed">
                    {aiAnalysis.description || 'AI description will appear here once analysis completes.'}
                  </p>
                </div>
              </div>

              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-2xl blur-2xl"></div>
                <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)] mb-4">Highlights</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <TagList label="Genres" items={aiAnalysis.genre} />
                    <TagList label="Mood" items={aiAnalysis.mood} />
                    <TagList label="Instruments" items={aiAnalysis.instruments} />
                    <TagList label="Tags" items={aiAnalysis.tags} />
                  </div>
                  {aiAnalysis.similarity_score !== undefined && (
                    <p className="mt-4 text-[hsl(220,10%,65%)]">Similarity Score: {(aiAnalysis.similarity_score * 100).toFixed(0)}%</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function FeatureCard({
  title,
  icon,
  value,
}: {
  title: string;
  icon: ReactNode;
  value: string;
}) {
  return (
    <div className="relative group">
      <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-xl opacity-20 group-hover:opacity-30 transition blur-xl"></div>
      <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(320,90%,60%)]/50 transition">
        <div className="flex items-center justify-between mb-4">
          <div className="h-12 w-12 rounded-lg bg-white/10 flex items-center justify-center">
            {icon}
          </div>
        </div>
        <h3 className="text-[hsl(220,10%,65%)] font-medium mb-2">{title}</h3>
        <p className="text-2xl font-bold text-[hsl(0,0%,98%)]">{value}</p>
      </div>
    </div>
  );
}

function TagList({ label, items }: { label: string; items?: string[] }) {
  if (!items || items.length === 0) {
    return (
      <div>
        <h4 className="text-[hsl(220,10%,65%)] uppercase text-xs mb-2 tracking-wide">{label}</h4>
        <p className="text-[hsl(220,10%,65%)] text-sm">—</p>
      </div>
    );
  }

  return (
    <div>
      <h4 className="text-[hsl(220,10%,65%)] uppercase text-xs mb-2 tracking-wide">{label}</h4>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className="px-2 py-1 rounded-full text-xs bg-white/10 border border-white/10 text-[hsl(0,0%,98%)]"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function AnalysisPage() {
  return (
    <ProtectedRoute>
      <AnalysisContent />
    </ProtectedRoute>
  );
}
