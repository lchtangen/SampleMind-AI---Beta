'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  Music,
  Search,
  Filter,
  Trash2,
  LogOut,
  User,
  RefreshCcw,
  PlayCircle,
} from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoadingSpinner from '@/components/LoadingSpinner';
import { useAuthContext } from '@/contexts/AuthContext';
import { useAudio } from '@/hooks/useAudio';
import { useNotification } from '@/contexts/NotificationContext';
import { useWebSocket } from '@/hooks/useWebSocket';

interface LibraryTrack {
  id: number;
  filename: string;
  duration?: number | null;
  format: string;
  uploaded_at: string;
  has_analysis?: boolean;
}

function LibraryContent() {
  const router = useRouter();
  const { user, logout } = useAuthContext();
  const { listAudio, deleteAudio, loading } = useAudio();
  const { addNotification } = useNotification();

  const [tracks, setTracks] = useState<LibraryTrack[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'analyzed' | 'processing'>('all');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchTracks = useCallback(async () => {
    setIsRefreshing(true);
    const result = await listAudio(1, 100);
    if (result.success && result.data) {
      setTracks(result.data.items ?? []);
    } else {
      addNotification('error', result.error || 'Unable to load library');
    }
    setIsRefreshing(false);
  }, [listAudio, addNotification]);

  useEffect(() => {
    fetchTracks();
  }, [fetchTracks]);

  useWebSocket({
    userId: user?.id ?? 0,
    onMessage: (message) => {
      if (['upload_progress', 'analysis_status'].includes(message.type)) {
        fetchTracks();
      }
    },
  });

  const formatDuration = (seconds?: number | null) => {
    if (!seconds || Number.isNaN(seconds)) return '—';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (iso: string) => {
    const date = new Date(iso);
    return date.toLocaleString();
  };

  const getStatus = (track: LibraryTrack) => (track.has_analysis ? 'analyzed' : 'processing');

  const filteredTracks = useMemo(() => {
    return tracks.filter((track) => {
      const matchesSearch = track.filename.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = filterStatus === 'all' || getStatus(track) === filterStatus;
      return matchesSearch && matchesFilter;
    });
  }, [tracks, searchQuery, filterStatus]);

  const handleDelete = async (track: LibraryTrack) => {
    const result = await deleteAudio(track.id);
    if (result.success) {
      addNotification('success', `${track.filename} removed from your library`);
      fetchTracks();
    } else {
      addNotification('error', result.error || 'Failed to remove track');
    }
  };

  const handleLogout = async () => {
    await logout();
    addNotification('success', 'Logged out successfully');
    router.push('/');
  };

  const isLoadingState = (loading && tracks.length === 0) || (isRefreshing && tracks.length === 0);

  if (isLoadingState) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[hsl(220,15%,8%)] to-[hsl(220,12%,12%)] flex items-center justify-center">
        <LoadingSpinner size="lg" text="Loading your library..." />
      </div>
    );
  }

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
            
            <nav className="flex items-center space-x-6">
              <Link href="/dashboard" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Dashboard
              </Link>
              <Link href="/upload" className="text-[hsl(220,10%,65%)] hover:text-[hsl(0,0%,98%)] transition">
                Upload
              </Link>
              <Link href="/library" className="text-[hsl(220,90%,60%)] font-medium">
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

      <main className="container mx-auto px-6 py-8">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-8">
          <div>
            <h2 className="text-4xl font-bold text-[hsl(0,0%,98%)] mb-2">
              Music Library
            </h2>
            <p className="text-[hsl(220,10%,65%)]">
              {filteredTracks.length} track{filteredTracks.length === 1 ? '' : 's'} available
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/upload"
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition text-center"
          >
            Upload New
          </Link>
            <button
              onClick={fetchTracks}
              className="flex items-center justify-center space-x-2 px-6 py-3 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/40 transition"
              disabled={isRefreshing}
            >
              <RefreshCcw className={`h-4 w-4 text-[hsl(220,10%,65%)] ${isRefreshing ? 'animate-spin' : ''}`} />
              <span className="text-[hsl(220,10%,65%)]">Refresh</span>
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4 mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
            <input
              type="text"
              placeholder="Search tracks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-md bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] placeholder-[hsl(220,10%,65%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition"
            />
          </div>

          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as typeof filterStatus)}
              className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-md bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition appearance-none cursor-pointer"
            >
              <option value="all">All Status</option>
              <option value="analyzed">Analyzed</option>
              <option value="processing">Processing</option>
            </select>
          </div>
        </div>

        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/5 to-[hsl(270,85%,65%)]/5 rounded-xl blur-2xl"></div>
          
          <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl overflow-hidden">
            {filteredTracks.length === 0 ? (
              <div className="py-16 text-center">
                <Music className="h-16 w-16 mx-auto mb-4 text-[hsl(220,10%,65%)] opacity-60" />
                <p className="text-[hsl(220,10%,65%)] mb-4">No audio files match your filters yet.</p>
                <Link
                  href="/upload"
                  className="inline-flex items-center space-x-2 px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg transition"
                >
                  <PlayCircle className="h-5 w-5" />
                  <span>Upload your first track</span>
                </Link>
              </div>
            ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Track</th>
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Duration</th>
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Format</th>
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Uploaded</th>
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Status</th>
                      <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTracks.map((track) => (
                      <tr key={track.id} className="border-b border-white/5 last:border-b-0">
                      <td className="p-4">
                        <div className="flex items-center space-x-3">
                            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center">
                              <Music className="h-5 w-5 text-white" />
                            </div>
                            <div>
                              <p className="font-medium text-[hsl(0,0%,98%)]">{track.filename}</p>
                              <p className="text-xs text-[hsl(220,10%,65%)]">ID: {track.id}</p>
                          </div>
                        </div>
                      </td>
                        <td className="p-4 text-[hsl(0,0%,98%)]">{formatDuration(track.duration ?? undefined)}</td>
                        <td className="p-4 text-[hsl(0,0%,98%)] uppercase">{track.format}</td>
                        <td className="p-4 text-[hsl(220,10%,65%)]">{formatDate(track.uploaded_at)}</td>
                      <td className="p-4">
                          <span
                            className={`px-3 py-1 rounded-full text-sm font-medium ${
                              getStatus(track) === 'analyzed'
                            ? 'bg-[hsl(180,95%,55%)]/20 text-[hsl(180,95%,55%)]'
                                : 'bg-[hsl(320,90%,60%)]/20 text-[hsl(320,90%,60%)]'
                            }`}
                          >
                            {getStatus(track)}
                        </span>
                      </td>
                      <td className="p-4">
                          <div className="flex items-center space-x-3">
                            <Link
                              href={`/analysis/${track.id}`}
                              className="text-[hsl(220,90%,60%)] hover:text-[hsl(270,85%,65%)] transition text-sm"
                            >
                              View
                            </Link>
                            <button
                              onClick={() => handleDelete(track)}
                              className="text-red-400 hover:text-red-300 transition"
                              title="Remove from library"
                            >
                              <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function LibraryPage() {
  return (
    <ProtectedRoute>
      <LibraryContent />
    </ProtectedRoute>
  );
}
