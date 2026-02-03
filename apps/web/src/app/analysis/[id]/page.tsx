'use client';

import { useState, useEffect, useCallback, type ReactNode, Suspense } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
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
import { BentoGrid } from '@/components/layouts/BentoGrid';
import { AdvancedWaveform } from '@/components/audio/AdvancedWaveform';
import { MusicTheoryCard } from '@/components/analysis/MusicTheoryCard';
import { AIConfidenceMeter } from '@/components/analysis/AIConfidenceMeter';
import { AnalysisProgress } from '@/components/analysis/AnalysisProgress';
import { AnalysisDetailSkeleton } from '@/components/ui/SkeletonLoaders';

// Lazy load heavy 3D component
const ThreeJSAudioVisualizer = dynamic(() =>
  import('@/components/audio/ThreeJSAudioVisualizer').then(mod => ({
    default: mod.ThreeJSAudioVisualizer
  })),
  { ssr: false }
);

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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black">
        <header className="border-b border-slate-700/50 backdrop-blur-md bg-slate-900/50">
          <div className="container mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <Link href="/" className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                  <span className="text-white font-bold text-xl">SM</span>
                </div>
                <h1 className="text-2xl font-bold text-slate-100">SampleMind AI</h1>
              </Link>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-6 py-8">
          <AnalysisDetailSkeleton />
        </main>
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

  // Bento grid items for comprehensive analysis display
  const analysisItems = [
    {
      id: 'header',
      span: 12 as const,
      height: 'auto' as const,
      children: (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative rounded-xl overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />
          <div className="relative p-6 md:p-8">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
              <div className="flex items-start space-x-6">
                <div className="h-20 w-20 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                  <Music className="h-10 w-10 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl font-bold text-slate-100 mb-2">{analysis.filename}</h2>
                  <div className="flex flex-wrap items-center gap-3 text-slate-400 text-sm">
                    <span>{formatDuration(features?.duration)}</span>
                    <span>•</span>
                    <span>{features?.tempo ? `${features.tempo.toFixed(1)} BPM` : 'Tempo N/A'}</span>
                    <span>•</span>
                    <span>{features?.key || 'Key N/A'}</span>
                  </div>
                  <p className="mt-3 text-sm text-slate-500">
                    {new Date(analysis.uploaded_at).toLocaleString()} • {analysis.status}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="h-12 w-12 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center hover:shadow-lg hover:shadow-cyan-500/50 transition"
                >
                  {isPlaying ? (
                    <Pause className="h-6 w-6 text-white" />
                  ) : (
                    <Play className="h-6 w-6 text-white ml-1" />
                  )}
                </button>
                <button
                  onClick={handleReanalyze}
                  disabled={isAnalyzing}
                  className="h-12 w-12 rounded-lg backdrop-blur-sm bg-slate-700/30 border border-slate-600 hover:border-cyan-500/50 flex items-center justify-center transition disabled:opacity-50"
                >
                  <RefreshCcw className={`h-5 w-5 text-slate-400 ${isAnalyzing ? 'animate-spin' : ''}`} />
                </button>
                <button className="h-12 w-12 rounded-lg backdrop-blur-sm bg-slate-700/30 border border-slate-600 hover:border-cyan-500/50 flex items-center justify-center transition">
                  <Download className="h-5 w-5 text-slate-400" />
                </button>
                <button className="h-12 w-12 rounded-lg backdrop-blur-sm bg-slate-700/30 border border-slate-600 hover:border-cyan-500/50 flex items-center justify-center transition">
                  <Share2 className="h-5 w-5 text-slate-400" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      ),
    },
    {
      id: 'waveform',
      span: 12 as const,
      height: 'large' as const,
      children: (
        <Suspense fallback={<div className="p-4 text-slate-400">Loading waveform...</div>}>
          <AdvancedWaveform />
        </Suspense>
      ),
    },
    {
      id: 'visualizer',
      span: 8 as const,
      height: 'large' as const,
      children: (
        <Suspense fallback={<div className="p-4 text-slate-400">Loading visualizer...</div>}>
          <ThreeJSAudioVisualizer preset="waves" qualityLevel="high" />
        </Suspense>
      ),
    },
    {
      id: 'confidence',
      span: 4 as const,
      height: 'large' as const,
      children: (
        <div className="p-4 space-y-4">
          <h3 className="text-lg font-semibold text-slate-100">Analysis Quality</h3>
          <AIConfidenceMeter
            value={analysis.status === 'completed' ? 92 : 65}
            confidence={analysis.status === 'completed' ? 92 : 65}
            description={analysis.status === 'completed' ? 'Complete' : 'In Progress'}
          />
        </div>
      ),
    },
    {
      id: 'tempo',
      span: 4 as const,
      height: 'medium' as const,
      children: (
        <div className="p-4">
          <MusicTheoryCard
            type="tempo"
            value={features?.tempo ? `${features.tempo.toFixed(0)}` : '--'}
            confidence={85}
            subValue={features?.tempo ? '±2' : undefined}
            isAudioReactive={false}
          />
        </div>
      ),
    },
    {
      id: 'key',
      span: 4 as const,
      height: 'medium' as const,
      children: (
        <div className="p-4">
          <MusicTheoryCard
            type="key"
            value={features?.key || '--'}
            confidence={88}
            isAudioReactive={false}
          />
        </div>
      ),
    },
    {
      id: 'mood',
      span: 4 as const,
      height: 'medium' as const,
      children: (
        <div className="p-4">
          <MusicTheoryCard
            type="mood"
            value={aiAnalysis?.mood?.[0] || '--'}
            confidence={82}
            isAudioReactive={false}
          />
        </div>
      ),
    },
    {
      id: 'progress',
      span: 12 as const,
      height: 'medium' as const,
      children: analysis.status !== 'completed' ? (
        <AnalysisProgress
          stages={[
            { name: 'Upload', status: 'completed' },
            { name: 'Feature Extraction', status: 'completed' },
            { name: 'Neural Embedding', status: 'in-progress' },
            { name: 'AI Tagging', status: 'pending' },
            { name: 'Similarity Search', status: 'pending' },
          ]}
          overallProgress={60}
        />
      ) : (
        <div className="p-4 text-center text-slate-400">✓ Analysis Complete</div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black">
      <header className="border-b border-slate-700/50 backdrop-blur-md bg-slate-900/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-slate-100">SampleMind AI</h1>
            </Link>
            <Link
              href="/library"
              className="flex items-center space-x-2 text-slate-400 hover:text-slate-300 transition"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Library</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <BentoGrid items={analysisItems} gap={16} />

        {aiAnalysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8 grid lg:grid-cols-2 gap-6"
          >
            <div className="relative rounded-xl overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />
              <div className="relative p-6">
                <h3 className="text-xl font-bold text-slate-100 mb-4">AI Summary</h3>
                <p className="text-slate-400 leading-relaxed">
                  {aiAnalysis.description || 'AI description will appear once analysis completes.'}
                </p>
              </div>
            </div>

            <div className="relative rounded-xl overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />
              <div className="relative p-6">
                <h3 className="text-xl font-bold text-slate-100 mb-4">Highlights</h3>
                <div className="grid grid-cols-2 gap-4">
                  <TagList label="Genres" items={aiAnalysis.genre} />
                  <TagList label="Mood" items={aiAnalysis.mood} />
                  <TagList label="Instruments" items={aiAnalysis.instruments} />
                  <TagList label="Tags" items={aiAnalysis.tags} />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
}

function TagList({ label, items }: { label: string; items?: string[] }) {
  if (!items || items.length === 0) {
    return (
      <div>
        <h4 className="text-slate-400 uppercase text-xs mb-2 tracking-wide font-semibold">{label}</h4>
        <p className="text-slate-500 text-sm">—</p>
      </div>
    );
  }

  return (
    <div>
      <h4 className="text-slate-400 uppercase text-xs mb-2 tracking-wide font-semibold">{label}</h4>
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <span
            key={item}
            className="px-2.5 py-1 rounded-full text-xs bg-slate-700/50 border border-slate-600 text-slate-200 hover:border-cyan-500/50 transition"
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
