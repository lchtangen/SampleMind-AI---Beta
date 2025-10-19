'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { 
  Music, ArrowLeft, Play, Pause, Download, Share2, 
  Activity, TrendingUp, Zap, Disc, Volume2, Clock
} from 'lucide-react';

interface AnalysisData {
  audio_id: number;
  filename: string;
  status: string;
  features: {
    tempo: number;
    key: string;
    time_signature: string;
    duration: number;
    loudness: number;
    energy: number;
    danceability: number;
    valence: number;
    spectral_centroid: number;
    zero_crossing_rate: number;
  };
  ai_analysis: {
    genre: string[];
    mood: string[];
    instruments: string[];
    tags: string[];
    similarity_score: number;
    description: string;
  };
  analyzed_at: string;
}

export default function AnalysisPage() {
  const params = useParams();
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Fetch from API
    // Mock data for now
    setTimeout(() => {
      setAnalysis({
        audio_id: Number(params.id),
        filename: 'Summer Vibes.mp3',
        status: 'completed',
        features: {
          tempo: 128.5,
          key: 'C major',
          time_signature: '4/4',
          duration: 245,
          loudness: -12.5,
          energy: 0.75,
          danceability: 0.82,
          valence: 0.68,
          spectral_centroid: 1500.5,
          zero_crossing_rate: 0.08
        },
        ai_analysis: {
          genre: ['Electronic', 'House', 'Dance'],
          mood: ['Energetic', 'Uplifting', 'Happy'],
          instruments: ['Synthesizer', 'Drums', 'Bass', 'Vocals'],
          tags: ['Summer', 'Festival', 'Club', 'Party', 'Upbeat'],
          similarity_score: 0.85,
          description: 'An energetic electronic dance track with uplifting melodies and a driving beat. Perfect for summer festivals and club settings. Features prominent synthesizer leads, punchy drums, and infectious grooves that encourage movement.'
        },
        analyzed_at: '2025-10-19T20:00:00Z'
      });
      setLoading(false);
    }, 500);
  }, [params.id]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getEnergyColor = (value: number): string => {
    if (value >= 0.7) return 'from-[hsl(320,90%,60%)] to-[hsl(270,85%,65%)]';
    if (value >= 0.4) return 'from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)]';
    return 'from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)]';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-16 w-16 animate-spin rounded-full border-4 border-solid border-[hsl(220,90%,60%)] border-r-transparent mb-4"></div>
          <p className="text-[hsl(0,0%,98%)]">Loading analysis...</p>
        </div>
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)]">
      {/* Header */}
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
            
            <Link
              href="/library"
              className="flex items-center space-x-2 text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Library</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Track Header */}
          <div className="relative mb-8">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-2xl blur-3xl"></div>
            
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-8">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-6">
                  <div className="h-24 w-24 rounded-xl bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center flex-shrink-0">
                    <Music className="h-12 w-12 text-white" />
                  </div>
                  
                  <div>
                    <h2 className="text-3xl font-bold text-[hsl(0,0%,98%)] mb-2">
                      {analysis.filename}
                    </h2>
                    <div className="flex items-center space-x-4 text-[hsl(220,10%,65%)]">
                      <span>{formatDuration(analysis.features.duration)}</span>
                      <span>•</span>
                      <span>{analysis.features.tempo.toFixed(1)} BPM</span>
                      <span>•</span>
                      <span>{analysis.features.key}</span>
                    </div>
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
                  
                  <button className="h-14 w-14 rounded-xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition">
                    <Download className="h-5 w-5 text-[hsl(220,10%,65%)]" />
                  </button>
                  
                  <button className="h-14 w-14 rounded-xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition">
                    <Share2 className="h-5 w-5 text-[hsl(220,10%,65%)]" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Audio Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Tempo */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-xl blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(320,90%,60%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <Activity className="h-8 w-8 text-[hsl(320,90%,60%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {analysis.features.tempo.toFixed(1)}
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Tempo (BPM)</h3>
              </div>
            </div>

            {/* Energy */}
            <div className="relative group">
              <div className={`absolute inset-0 bg-gradient-to-r ${getEnergyColor(analysis.features.energy)}/20 rounded-xl blur-xl`}></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(220,90%,60%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <Zap className="h-8 w-8 text-[hsl(220,90%,60%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {(analysis.features.energy * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Energy</h3>
                <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className={`h-full bg-gradient-to-r ${getEnergyColor(analysis.features.energy)}`}
                    style={{ width: `${analysis.features.energy * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Danceability */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(180,95%,55%)]/20 to-[hsl(220,90%,60%)]/20 rounded-xl blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(180,95%,55%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <Disc className="h-8 w-8 text-[hsl(180,95%,55%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {(analysis.features.danceability * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Danceability</h3>
                <div className="mt-2 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)]"
                    style={{ width: `${analysis.features.danceability * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Loudness */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-xl blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(220,90%,60%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <Volume2 className="h-8 w-8 text-[hsl(270,85%,65%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {analysis.features.loudness.toFixed(1)}
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Loudness (dB)</h3>
              </div>
            </div>

            {/* Duration */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 rounded-xl blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(320,90%,60%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <Clock className="h-8 w-8 text-[hsl(320,90%,60%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {formatDuration(analysis.features.duration)}
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Duration</h3>
              </div>
            </div>

            {/* Valence */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(180,95%,55%)]/20 to-[hsl(220,90%,60%)]/20 rounded-xl blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(180,95%,55%)]/50 transition">
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="h-8 w-8 text-[hsl(180,95%,55%)]" />
                  <span className="text-3xl font-bold text-[hsl(0,0%,98%)]">
                    {(analysis.features.valence * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="text-[hsl(220,10%,65%)] font-medium">Positivity</h3>
              </div>
            </div>
          </div>

          {/* AI Analysis Section */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Genre & Mood */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-xl blur-2xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-4">
                  Genre & Mood
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-[hsl(220,10%,65%)] mb-2">Genres</p>
                    <div className="flex flex-wrap gap-2">
                      {analysis.ai_analysis.genre.map((genre, idx) => (
                        <span 
                          key={idx}
                          className="px-3 py-1 rounded-full bg-gradient-to-r from-[hsl(220,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 border border-[hsl(220,90%,60%)]/30 text-[hsl(220,90%,60%)] text-sm font-medium"
                        >
                          {genre}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm text-[hsl(220,10%,65%)] mb-2">Mood</p>
                    <div className="flex flex-wrap gap-2">
                      {analysis.ai_analysis.mood.map((mood, idx) => (
                        <span 
                          key={idx}
                          className="px-3 py-1 rounded-full bg-gradient-to-r from-[hsl(180,95%,55%)]/20 to-[hsl(220,90%,60%)]/20 border border-[hsl(180,95%,55%)]/30 text-[hsl(180,95%,55%)] text-sm font-medium"
                        >
                          {mood}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Instruments & Tags */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-xl blur-2xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-4">
                  Instruments & Tags
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-[hsl(220,10%,65%)] mb-2">Instruments</p>
                    <div className="flex flex-wrap gap-2">
                      {analysis.ai_analysis.instruments.map((instrument, idx) => (
                        <span 
                          key={idx}
                          className="px-3 py-1 rounded-full bg-gradient-to-r from-[hsl(320,90%,60%)]/20 to-[hsl(270,85%,65%)]/20 border border-[hsl(320,90%,60%)]/30 text-[hsl(320,90%,60%)] text-sm font-medium"
                        >
                          {instrument}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm text-[hsl(220,10%,65%)] mb-2">Tags</p>
                    <div className="flex flex-wrap gap-2">
                      {analysis.ai_analysis.tags.map((tag, idx) => (
                        <span 
                          key={idx}
                          className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[hsl(220,10%,65%)] text-sm"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Description */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-xl blur-2xl"></div>
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-4">
                AI Analysis
              </h3>
              <p className="text-[hsl(220,10%,65%)] leading-relaxed">
                {analysis.ai_analysis.description}
              </p>
              
              <div className="mt-6 flex items-center justify-between p-4 rounded-lg bg-white/5">
                <span className="text-[hsl(220,10%,65%)]">Confidence Score</span>
                <span className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                  {(analysis.ai_analysis.similarity_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
