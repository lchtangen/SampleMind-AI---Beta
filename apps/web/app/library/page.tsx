'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  Search,
  Filter,
  Grid3x3,
  List,
  Download,
  Trash2,
  Play,
  Loader2,
  ChevronDown,
} from 'lucide-react';
import { useAudio } from '@/hooks/useAudio';
import LoadingSpinner from '@/components/LoadingSpinner';

interface AudioFile {
  file_id: string;
  filename: string;
  duration: number;
  format: string;
  file_size: number;
  upload_time: string;
  status?: string;
}

interface FilterState {
  search: string;
  status: 'all' | 'analyzed' | 'processing' | 'error';
  sortBy: 'recent' | 'name' | 'duration' | 'size';
  viewMode: 'grid' | 'list';
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
};

export default function LibraryPage() {
  const { listAudio, deleteAudio } = useAudio();
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    status: 'all',
    sortBy: 'recent',
    viewMode: 'grid',
  });
  const [showFilters, setShowFilters] = useState(false);

  // Load audio files
  useEffect(() => {
    const loadFiles = async () => {
      try {
        setLoading(true);
        const files = await listAudio(page, pageSize);
        setAudioFiles(files);
      } catch (error) {
        console.error('Failed to load audio files:', error);
      } finally {
        setLoading(false);
      }
    };

    loadFiles();
  }, [page, pageSize, listAudio]);

  // Filter and sort files
  const filteredFiles = useMemo(() => {
    let result = [...audioFiles];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      result = result.filter(file =>
        file.filename.toLowerCase().includes(searchLower)
      );
    }

    // Status filter
    if (filters.status !== 'all') {
      result = result.filter(file => file.status === filters.status);
    }

    // Sort
    switch (filters.sortBy) {
      case 'name':
        result.sort((a, b) => a.filename.localeCompare(b.filename));
        break;
      case 'duration':
        result.sort((a, b) => b.duration - a.duration);
        break;
      case 'size':
        result.sort((a, b) => b.file_size - a.file_size);
        break;
      case 'recent':
      default:
        result.sort((a, b) =>
          new Date(b.upload_time).getTime() - new Date(a.upload_time).getTime()
        );
    }

    return result;
  }, [audioFiles, filters]);

  const handleDelete = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    setDeleting(fileId);
    try {
      await deleteAudio(fileId);
      setAudioFiles(audioFiles.filter(f => f.file_id !== fileId));
    } catch (error) {
      console.error('Failed to delete file:', error);
    } finally {
      setDeleting(null);
    }
  };

  if (loading && audioFiles.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Library</h1>
          <p className="text-slate-400">
            {filteredFiles.length} sample{filteredFiles.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Controls */}
        <div className="mb-8 space-y-4">
          {/* Top Bar */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search samples..."
                value={filters.search}
                onChange={(e) => {
                  setFilters({ ...filters, search: e.target.value });
                  setPage(1);
                }}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>

            {/* View Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setFilters({ ...filters, viewMode: 'grid' })}
                className={`p-2 rounded-lg transition-colors ${
                  filters.viewMode === 'grid'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700/50 text-slate-400 hover:text-white'
                }`}
              >
                <Grid3x3 className="w-5 h-5" />
              </button>
              <button
                onClick={() => setFilters({ ...filters, viewMode: 'list' })}
                className={`p-2 rounded-lg transition-colors ${
                  filters.viewMode === 'list'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700/50 text-slate-400 hover:text-white'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-slate-300 hover:text-white hover:border-slate-500 transition-colors"
            >
              <Filter className="w-4 h-4" />
              Filters
              <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="p-4 rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => {
                      setFilters({ ...filters, status: e.target.value as any });
                      setPage(1);
                    }}
                    className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                  >
                    <option value="all">All Files</option>
                    <option value="analyzed">Analyzed</option>
                    <option value="processing">Processing</option>
                    <option value="error">Error</option>
                  </select>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Sort By
                  </label>
                  <select
                    value={filters.sortBy}
                    onChange={(e) => {
                      setFilters({ ...filters, sortBy: e.target.value as any });
                    }}
                    className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600 text-white focus:outline-none focus:border-blue-500/50"
                  >
                    <option value="recent">Most Recent</option>
                    <option value="name">Name (A-Z)</option>
                    <option value="duration">Duration</option>
                    <option value="size">File Size</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Empty State */}
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400 mb-4">
              {audioFiles.length === 0
                ? 'No samples yet. Upload one to get started!'
                : 'No samples match your filters.'}
            </p>
          </div>
        ) : (
          <>
            {/* Grid View */}
            {filters.viewMode === 'grid' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredFiles.map((file) => (
                  <div
                    key={file.file_id}
                    className="group relative rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 hover:border-slate-600 transition-all duration-300 overflow-hidden hover:shadow-lg hover:shadow-blue-500/10"
                  >
                    {/* Background gradient on hover */}
                    <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                    <div className="relative p-4 h-full flex flex-col">
                      {/* File Icon & Status */}
                      <div className="mb-4">
                        <div className="w-12 h-12 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 transition-colors mb-3">
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M9 3h6v6h6v12H3V3h6zm0-2H3a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V9l-8-8z" />
                          </svg>
                        </div>

                        {file.status && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                            file.status === 'analyzed'
                              ? 'bg-green-500/10 text-green-300'
                              : file.status === 'processing'
                              ? 'bg-blue-500/10 text-blue-300'
                              : 'bg-red-500/10 text-red-300'
                          }`}>
                            {file.status === 'processing' && <Loader2 className="w-3 h-3 mr-1 animate-spin" />}
                            {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                          </span>
                        )}
                      </div>

                      {/* File Info */}
                      <h3 className="text-sm font-semibold text-white mb-2 line-clamp-2 group-hover:text-blue-400 transition-colors">
                        {file.filename}
                      </h3>

                      <p className="text-xs text-slate-500 mb-4 flex-1">
                        <div>{formatFileSize(file.file_size)}</div>
                        <div>{formatDuration(file.duration)}</div>
                      </p>

                      {/* Actions */}
                      <div className="flex gap-2 pt-4 border-t border-slate-700">
                        <button className="flex-1 flex items-center justify-center gap-1 px-2 py-2 rounded text-xs text-blue-400 hover:bg-blue-500/10 transition-colors">
                          <Play className="w-3 h-3" />
                          Play
                        </button>
                        <button className="flex-1 flex items-center justify-center gap-1 px-2 py-2 rounded text-xs text-slate-400 hover:bg-slate-700 transition-colors">
                          <Download className="w-3 h-3" />
                          Download
                        </button>
                        <button
                          onClick={() => handleDelete(file.file_id)}
                          disabled={deleting === file.file_id}
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-2 rounded text-xs text-red-400 hover:bg-red-500/10 disabled:opacity-50 transition-colors"
                        >
                          {deleting === file.file_id ? (
                            <Loader2 className="w-3 h-3 animate-spin" />
                          ) : (
                            <Trash2 className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              /* List View */
              <div className="rounded-lg bg-slate-800/50 backdrop-blur border border-slate-700/50 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b border-slate-700 bg-slate-900/50">
                      <tr>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                          Filename
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                          Size
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                          Duration
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-slate-300">
                          Uploaded
                        </th>
                        <th className="px-6 py-3 text-right text-sm font-semibold text-slate-300">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {filteredFiles.map((file) => (
                        <tr key={file.file_id} className="hover:bg-slate-700/20 transition-colors">
                          <td className="px-6 py-4 text-sm text-white font-medium truncate">
                            {file.filename}
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-400">
                            {formatFileSize(file.file_size)}
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-400">
                            {formatDuration(file.duration)}
                          </td>
                          <td className="px-6 py-4 text-sm">
                            {file.status && (
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                                file.status === 'analyzed'
                                  ? 'bg-green-500/10 text-green-300'
                                  : file.status === 'processing'
                                  ? 'bg-blue-500/10 text-blue-300'
                                  : 'bg-red-500/10 text-red-300'
                              }`}>
                                {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-400">
                            {new Date(file.upload_time).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 text-right text-sm">
                            <div className="flex gap-2 justify-end">
                              <button className="p-1 text-slate-400 hover:text-blue-400 transition-colors">
                                <Play className="w-4 h-4" />
                              </button>
                              <button className="p-1 text-slate-400 hover:text-blue-400 transition-colors">
                                <Download className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleDelete(file.file_id)}
                                disabled={deleting === file.file_id}
                                className="p-1 text-slate-400 hover:text-red-400 disabled:opacity-50 transition-colors"
                              >
                                {deleting === file.file_id ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Trash2 className="w-4 h-4" />
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

        {/* Pagination */}
        {audioFiles.length > 0 && (
          <div className="mt-8 flex justify-between items-center">
            <p className="text-sm text-slate-400">
              Page {page} • Showing {filteredFiles.length} of {audioFiles.length}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:text-white disabled:opacity-50 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                className="px-4 py-2 rounded-lg border border-slate-600 text-slate-300 hover:text-white transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
