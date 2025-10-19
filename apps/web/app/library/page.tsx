'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Music, Search, Filter, Play, Pause, Download, Trash2, MoreVertical } from 'lucide-react';

interface AudioTrack {
  id: number;
  filename: string;
  duration: number;
  format: string;
  uploadedAt: string;
  status: 'analyzed' | 'processing' | 'failed';
  features?: {
    tempo: number;
    key: string;
    energy: number;
  };
}

export default function LibraryPage() {
  const [tracks, setTracks] = useState<AudioTrack[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [playingId, setPlayingId] = useState<number | null>(null);

  useEffect(() => {
    // TODO: Fetch from API
    // Mock data for now
    setTracks([
      {
        id: 1,
        filename: 'Summer Vibes.mp3',
        duration: 245,
        format: 'mp3',
        uploadedAt: '2025-10-19T10:00:00Z',
        status: 'analyzed',
        features: { tempo: 128, key: 'C major', energy: 0.75 }
      },
      {
        id: 2,
        filename: 'Deep Bass Loop.wav',
        duration: 120,
        format: 'wav',
        uploadedAt: '2025-10-19T09:30:00Z',
        status: 'analyzed',
        features: { tempo: 85, key: 'D minor', energy: 0.62 }
      },
      {
        id: 3,
        filename: 'Vocal Take 01.flac',
        duration: 180,
        format: 'flac',
        uploadedAt: '2025-10-18T15:20:00Z',
        status: 'processing'
      },
      {
        id: 4,
        filename: 'Ambient Pad.aiff',
        duration: 300,
        format: 'aiff',
        uploadedAt: '2025-10-18T14:00:00Z',
        status: 'analyzed',
        features: { tempo: 90, key: 'A minor', energy: 0.45 }
      }
    ]);
  }, []);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 24) {
      return `${diffHours} hours ago`;
    } else {
      const diffDays = Math.floor(diffHours / 24);
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    }
  };

  const filteredTracks = tracks.filter(track => {
    const matchesSearch = track.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterStatus === 'all' || track.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

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
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Title & Stats */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-4xl font-bold text-[hsl(0,0%,98%)] mb-2">
              Music Library
            </h2>
            <p className="text-[hsl(220,10%,65%)]">
              {filteredTracks.length} track{filteredTracks.length !== 1 ? 's' : ''} found
            </p>
          </div>
          
          <Link
            href="/upload"
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition"
          >
            Upload New
          </Link>
        </div>

        {/* Search & Filter */}
        <div className="grid md:grid-cols-2 gap-4 mb-6">
          {/* Search */}
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

          {/* Filter */}
          <div className="relative">
            <Filter className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[hsl(220,10%,65%)]" />
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-lg backdrop-blur-md bg-white/5 border border-white/10 text-[hsl(0,0%,98%)] focus:outline-none focus:border-[hsl(220,90%,60%)]/50 transition appearance-none cursor-pointer"
            >
              <option value="all">All Status</option>
              <option value="analyzed">Analyzed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>

        {/* Tracks Table */}
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-[hsl(220,90%,60%)]/5 to-[hsl(270,85%,65%)]/5 rounded-xl blur-2xl"></div>
          
          <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Track
                    </th>
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Duration
                    </th>
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Tempo
                    </th>
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Key
                    </th>
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Status
                    </th>
                    <th className="text-left p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Uploaded
                    </th>
                    <th className="text-right p-4 text-[hsl(220,10%,65%)] font-medium text-sm">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTracks.map((track) => (
                    <tr
                      key={track.id}
                      className="border-b border-white/5 hover:bg-white/5 transition"
                    >
                      <td className="p-4">
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => setPlayingId(playingId === track.id ? null : track.id)}
                            className="h-10 w-10 rounded-lg bg-gradient-to-br from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] flex items-center justify-center hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition flex-shrink-0"
                          >
                            {playingId === track.id ? (
                              <Pause className="h-5 w-5 text-white" />
                            ) : (
                              <Play className="h-5 w-5 text-white" />
                            )}
                          </button>
                          
                          <div className="min-w-0">
                            <p className="font-medium text-[hsl(0,0%,98%)] truncate">
                              {track.filename}
                            </p>
                            <p className="text-sm text-[hsl(220,10%,65%)] uppercase">
                              {track.format}
                            </p>
                          </div>
                        </div>
                      </td>
                      
                      <td className="p-4">
                        <span className="text-[hsl(0,0%,98%)]">
                          {formatDuration(track.duration)}
                        </span>
                      </td>
                      
                      <td className="p-4">
                        <span className="text-[hsl(0,0%,98%)]">
                          {track.features ? `${track.features.tempo} BPM` : '-'}
                        </span>
                      </td>
                      
                      <td className="p-4">
                        <span className="text-[hsl(0,0%,98%)]">
                          {track.features?.key || '-'}
                        </span>
                      </td>
                      
                      <td className="p-4">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          track.status === 'analyzed'
                            ? 'bg-[hsl(180,95%,55%)]/20 text-[hsl(180,95%,55%)]'
                            : track.status === 'processing'
                            ? 'bg-[hsl(320,90%,60%)]/20 text-[hsl(320,90%,60%)]'
                            : 'bg-red-500/20 text-red-400'
                        }`}>
                          {track.status}
                        </span>
                      </td>
                      
                      <td className="p-4">
                        <span className="text-[hsl(220,10%,65%)] text-sm">
                          {formatDate(track.uploadedAt)}
                        </span>
                      </td>
                      
                      <td className="p-4">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition">
                            <Download className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                          </button>
                          <button className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(320,90%,60%)]/50 hover:bg-[hsl(320,90%,60%)]/10 flex items-center justify-center transition">
                            <Trash2 className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                          </button>
                          <button className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 hover:border-[hsl(220,90%,60%)]/50 flex items-center justify-center transition">
                            <MoreVertical className="h-4 w-4 text-[hsl(220,10%,65%)]" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Empty State */}
        {filteredTracks.length === 0 && (
          <div className="text-center py-12">
            <Music className="h-16 w-16 mx-auto mb-4 text-[hsl(220,10%,65%)]" />
            <h3 className="text-xl font-bold text-[hsl(0,0%,98%)] mb-2">
              No tracks found
            </h3>
            <p className="text-[hsl(220,10%,65%)] mb-6">
              {searchQuery || filterStatus !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Upload your first audio file to get started'}
            </p>
            {!searchQuery && filterStatus === 'all' && (
              <Link
                href="/upload"
                className="inline-flex px-6 py-3 rounded-lg bg-gradient-to-r from-[hsl(220,90%,60%)] to-[hsl(270,85%,65%)] text-white font-medium hover:shadow-lg hover:shadow-[hsl(220,90%,60%)]/50 transition"
              >
                Upload Files
              </Link>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
