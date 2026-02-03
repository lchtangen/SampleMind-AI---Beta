'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Music, Upload, TrendingUp, Clock, LogOut, User } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useNotification } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoadingSpinner from '@/components/LoadingSpinner';
import { CommandPalette, CommandAction } from '@/components/ui/CommandPalette';
import { BentoGrid } from '@/components/layouts/BentoGrid';
import { DashboardSkeleton } from '@/components/ui/SkeletonLoaders';
import { ThreeJSAudioVisualizer } from '@/components/audio/ThreeJSAudioVisualizer';
import { MusicTheoryCard, MusicTheoryGrid } from '@/components/analysis/MusicTheoryCard';

function DashboardContent() {
  const router = useRouter();
  const { user, logout, loading: authLoading } = useAuthContext();
  const { listAudio, loading: audioLoading } = useAudio();
  const { addNotification } = useNotification();
  const [audioFiles, setAudioFiles] = useState([]);
  const [stats, setStats] = useState({
    totalTracks: 0,
    analyzed: 0,
    processing: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  // WebSocket for real-time updates
  useWebSocket({
    userId: user?.id || 0,
    onMessage: (message) => {
      if (message.type === 'upload_progress' || message.type === 'analysis_status') {
        addNotification('info', message.data.message || 'Update received');
        loadAudioFiles();
      }
    }
  });

  const loadAudioFiles = async () => {
    const result = await listAudio(1, 10);
    if (result.success && result.data) {
      setAudioFiles(result.data.items || []);

      // Calculate stats
      const total = result.data.total || 0;
      const analyzed = result.data.items?.filter((a: any) => a.status === 'completed').length || 0;
      const processing = result.data.items?.filter((a: any) => a.status === 'processing').length || 0;

      setStats({
        totalTracks: total,
        analyzed,
        processing
      });
    }
    setIsLoading(false);
  };

  useEffect(() => {
    if (user) {
      loadAudioFiles();
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    addNotification('success', 'Logged out successfully');
    router.push('/');
  };

  // Command palette actions
  const commands: CommandAction[] = [
    {
      id: 'upload',
      label: 'Upload Audio',
      description: 'Upload new audio files for analysis',
      category: 'action',
      icon: <Upload className="w-4 h-4" />,
      onSelect: () => router.push('/upload'),
      shortcut: 'Ctrl+U',
      keywords: ['upload', 'add', 'file', 'audio'],
    },
    {
      id: 'library',
      label: 'Open Library',
      description: 'Browse your audio library',
      category: 'navigation',
      icon: <Music className="w-4 h-4" />,
      onSelect: () => router.push('/library'),
      shortcut: 'Ctrl+L',
      keywords: ['library', 'browse', 'samples'],
    },
    {
      id: 'dashboard',
      label: 'Dashboard',
      description: 'Return to dashboard',
      category: 'navigation',
      icon: <TrendingUp className="w-4 h-4" />,
      onSelect: () => router.push('/dashboard'),
      keywords: ['home', 'dashboard', 'main'],
    },
  ];

  if (authLoading || audioLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  // Bento grid items
  const bentoItems = [
    {
      id: 'stats-total',
      span: 4 as const,
      height: 'small' as const,
      children: (
        <div className="p-4 h-full flex flex-col justify-center">
          <div className="flex items-center justify-between mb-2">
            <Music className="w-5 h-5 text-cyan-400" />
            <span className="text-2xl font-bold text-cyan-400">{stats.totalTracks}</span>
          </div>
          <p className="text-sm text-slate-400">Total Tracks</p>
        </div>
      ),
    },
    {
      id: 'stats-analyzed',
      span: 4 as const,
      height: 'small' as const,
      children: (
        <div className="p-4 h-full flex flex-col justify-center">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-2xl font-bold text-green-400">{stats.analyzed}</span>
          </div>
          <p className="text-sm text-slate-400">Analyzed</p>
        </div>
      ),
    },
    {
      id: 'stats-processing',
      span: 4 as const,
      height: 'small' as const,
      children: (
        <div className="p-4 h-full flex flex-col justify-center">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-5 h-5 text-magenta-400" />
            <span className="text-2xl font-bold text-magenta-400">{stats.processing}</span>
          </div>
          <p className="text-sm text-slate-400">Processing</p>
        </div>
      ),
    },
    {
      id: 'visualizer',
      span: 8 as const,
      height: 'large' as const,
      children: (
        <Suspense fallback={<div className="p-4 text-slate-400">Loading visualizer...</div>}>
          <ThreeJSAudioVisualizer preset="particles" qualityLevel="high" />
        </Suspense>
      ),
    },
    {
      id: 'music-cards',
      span: 4 as const,
      height: 'large' as const,
      children: (
        <div className="p-4 space-y-3">
          <MusicTheoryCard
            type="tempo"
            value={stats.analyzed > 0 ? '120' : '--'}
            confidence={85}
            subValue="±2"
            isAudioReactive={false}
          />
        </div>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-950 to-black">
      <CommandPalette actions={commands} />

      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-md bg-slate-900/50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold text-slate-100">
                SampleMind AI
              </h1>
            </Link>

            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-cyan-400 font-medium">
                Dashboard
              </Link>
              <Link href="/upload" className="text-slate-400 hover:text-slate-300 transition">
                Upload
              </Link>
              <Link href="/library" className="text-slate-400 hover:text-slate-300 transition">
                Library
              </Link>

              <div className="flex items-center space-x-3 ml-6 pl-6 border-l border-slate-700/50">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-400 text-sm">{user?.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition text-sm"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-4xl font-bold text-slate-100 mb-2">
            Welcome Back, {user?.full_name || user?.email?.split('@')[0] || 'User'}
          </h2>
          <p className="text-slate-400">
            Here&apos;s your audio analysis dashboard with AI insights
          </p>
        </motion.div>

        {/* Bento Grid Dashboard */}
        <BentoGrid items={bentoItems} gap={16} className="mb-8" />

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="relative rounded-xl overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800/40 to-slate-900/40 border border-slate-700/50 rounded-xl backdrop-blur-md" />

          <div className="relative p-6">
            <h3 className="text-2xl font-bold text-slate-100 mb-6">
              Recent Activity
            </h3>

            <div className="space-y-3">
              {audioFiles.length === 0 ? (
                <div className="text-center py-12">
                  <Music className="h-16 w-16 mx-auto mb-4 text-slate-600" />
                  <p className="text-slate-400 mb-4">No audio files yet</p>
                  <Link
                    href="/upload"
                    className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-slate-900 font-medium hover:shadow-lg transition"
                  >
                    <Upload className="h-5 w-5" />
                    <span>Upload Your First Track</span>
                  </Link>
                </div>
              ) : (
                audioFiles.slice(0, 5).map((audio: any, index) => (
                  <motion.div
                    key={audio.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Link
                      href={`/analysis/${audio.id}`}
                      className="flex items-center justify-between p-4 rounded-lg backdrop-blur-sm bg-slate-800/30 border border-slate-700/30 hover:border-cyan-500/50 transition"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                          <Music className="h-5 w-5 text-white" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-200">
                            {audio.filename}
                          </p>
                          <p className="text-sm text-slate-500">
                            {audio.uploaded_at ? new Date(audio.uploaded_at).toLocaleString() : 'Recently'}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          audio.status === 'completed'
                            ? 'bg-green-500/20 text-green-400'
                            : audio.status === 'processing'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-cyan-500/20 text-cyan-400'
                        }`}>
                          {audio.status}
                        </span>
                      </div>
                    </Link>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
