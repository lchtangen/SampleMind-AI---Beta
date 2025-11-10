'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Music, Upload, TrendingUp, Clock, Play, LogOut, User } from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useNotification } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoadingSpinner from '@/components/LoadingSpinner';
import { RecommendationsPanel } from '@/components/RecommendationsPanel';

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

  if (authLoading || audioLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
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
            
            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-[hsl(220,90%,60%)] font-medium">
                Dashboard
              </Link>
              <Link href="/upload" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Upload
              </Link>
              <Link href="/library" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Library
              </Link>
              <Link href="/gallery" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Gallery
              </Link>
              
              <div className="flex items-center space-x-3 ml-6 pl-6 border-l border-white/10">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                  <span className="text-[hsl(220,10%,65%)] text-sm">{user?.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-red-500/50 hover:bg-red-500/10 transition text-sm"
                >
                  <LogOut className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                  <span className="text-[hsl(220,10%,65%)]">Logout</span>
                </button>
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-4xl font-bold text-[hsl(0,0%,98%)] mb-2">
            Welcome Back, {user?.full_name || user?.email?.split('@')[0] || 'User'}
          </h2>
          <p className="text-[hsl(220,10%,65%)]">
            Here&apos;s what&apos;s happening with your music production
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Total Tracks */}
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] rounded-xl opacity-20 group-hover:opacity-30 transition blur-xl"></div>
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(220,90%,60%)]/50 transition">
              <div className="flex items-center justify-between mb-4">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                  <Music className="h-6 w-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                  {stats.totalTracks}
                </span>
              </div>
              <h3 className="text-[hsl(220,10%,65%)] font-medium">Total Tracks</h3>
            </div>
          </div>

          {/* Analyzed */}
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)] rounded-xl opacity-20 group-hover:opacity-30 transition blur-xl"></div>
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(180,95%,55%)]/50 transition">
              <div className="flex items-center justify-between mb-4">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)] flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                  {stats.analyzed}
                </span>
              </div>
              <h3 className="text-[hsl(220,10%,65%)] font-medium">Analyzed</h3>
            </div>
          </div>

          {/* Processing */}
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-[hsl(320,90%,60%)] to-[hsl(270,85%,65%)] rounded-xl opacity-20 group-hover:opacity-30 transition blur-xl"></div>
            <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6 hover:border-[hsl(320,90%,60%)]/50 transition">
              <div className="flex items-center justify-between mb-4">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-[hsl(320,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                  <Clock className="h-6 w-6 text-white animate-pulse" />
                </div>
                <span className="text-2xl font-bold text-[hsl(0,0%,98%)]">
                  {stats.processing}
                </span>
              </div>
              <h3 className="text-[hsl(220,10%,65%)] font-medium">Processing</h3>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link href="/upload" className="group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] rounded-xl opacity-20 group-hover:opacity-40 transition blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-8 hover:border-[hsl(220,90%,60%)]/50 transition text-center">
                <Upload className="h-12 w-12 mx-auto mb-4 text-[hsl(220,90%,60%)]" />
                <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-2">
                  Upload New Track
                </h3>
                <p className="text-[hsl(220,10%,65%)]">
                  Add audio files for AI analysis
                </p>
              </div>
            </div>
          </Link>

          <Link href="/library" className="group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[hsl(180,95%,55%)] to-[hsl(220,90%,60%)] rounded-xl opacity-20 group-hover:opacity-40 transition blur-xl"></div>
              <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-8 hover:border-[hsl(180,95%,55%)]/50 transition text-center">
                <Music className="h-12 w-12 mx-auto mb-4 text-[hsl(180,95%,55%)]" />
                <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-2">
                  Browse Library
                </h3>
                <p className="text-[hsl(220,10%,65%)]">
                  View all your analyzed tracks
                </p>
              </div>
            </div>
          </Link>
        </div>

        <RecommendationsPanel className="mb-8" />

        {/* Recent Activity */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/10 to-[hsl(270,85%,65%)]/10 rounded-xl blur-2xl"></div>
          <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-2xl font-bold text-[hsl(0,0%,98%)] mb-6">
              Recent Activity
            </h3>
            
            <div className="space-y-4">
              {audioFiles.length === 0 ? (
                <div className="text-center py-12">
                  <Music className="h-16 w-16 mx-auto mb-4 text-[hsl(220,10%,65%)] opacity-50" />
                  <p className="text-[hsl(220,10%,65%)] mb-4">No audio files yet</p>
                  <Link
                    href="/upload"
                    className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg transition"
                  >
                    <Upload className="h-5 w-5" />
                    <span>Upload Your First Track</span>
                  </Link>
                </div>
              ) : (
                audioFiles.slice(0, 5).map((audio: any) => (
                  <Link
                    key={audio.id}
                    href={`/analysis/${audio.id}`}
                    className="flex items-center justify-between p-4 rounded-lg backdrop-blur-sm bg-white/5 border border-white/5 hover:border-[hsl(220,90%,60%)]/30 transition"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                        <Music className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-[hsl(0,0%,98%)]">
                          {audio.filename}
                        </p>
                        <p className="text-sm text-[hsl(220,10%,65%)]">
                          {audio.uploaded_at ? new Date(audio.uploaded_at).toLocaleString() : 'Recently'}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        audio.status === 'completed'
                          ? 'bg-[hsl(180,95%,55%)]/20 text-[hsl(180,95%,55%)]'
                          : audio.status === 'processing'
                          ? 'bg-[hsl(320,90%,60%)]/20 text-[hsl(320,90%,60%)]'
                          : 'bg-[hsl(220,90%,60%)]/20 text-[hsl(220,90%,60%)]'
                      }`}>
                        {audio.status}
                      </span>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>
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
