/**
 * Library Page
 *
 * Browse and manage your audio file library
 */

import { useState } from 'react';
import { Search, Filter, Music, Play, Trash2, Download, MoreVertical } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';

export default function Library() {
  const { audioFiles, selectFile, removeAudioFile } = useAppStore((state) => ({
    audioFiles: state.audioFiles,
    selectFile: state.selectFile,
    removeAudioFile: state.removeAudioFile,
  }));

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'analyzed' | 'pending'>('all');

  const filteredFiles = audioFiles.filter((file) => {
    const matchesSearch = file.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filterType === 'all' ||
      (filterType === 'analyzed' && file.analyzed) ||
      (filterType === 'pending' && !file.analyzed);
    return matchesSearch && matchesFilter;
  });

  const stats = {
    total: audioFiles.length,
    analyzed: audioFiles.filter((f) => f.analyzed).length,
    pending: audioFiles.filter((f) => !f.analyzed).length,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text">Audio Library</h1>
        <p className="mt-2 text-slate-400">Browse and manage your audio collection</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card
          className={cn(
            'cursor-pointer border-2 p-4 transition-all',
            filterType === 'all'
              ? 'border-cyan-500 bg-cyan-500/10'
              : 'border-white/10 bg-slate-800/50 hover:border-purple-500/50'
          )}
          onClick={() => setFilterType('all')}
        >
          <div className="text-sm text-slate-400">Total Files</div>
          <div className="mt-1 text-2xl font-bold text-white">{stats.total}</div>
        </Card>

        <Card
          className={cn(
            'cursor-pointer border-2 p-4 transition-all',
            filterType === 'analyzed'
              ? 'border-green-500 bg-green-500/10'
              : 'border-white/10 bg-slate-800/50 hover:border-green-500/50'
          )}
          onClick={() => setFilterType('analyzed')}
        >
          <div className="text-sm text-slate-400">Analyzed</div>
          <div className="mt-1 text-2xl font-bold text-white">{stats.analyzed}</div>
        </Card>

        <Card
          className={cn(
            'cursor-pointer border-2 p-4 transition-all',
            filterType === 'pending'
              ? 'border-yellow-500 bg-yellow-500/10'
              : 'border-white/10 bg-slate-800/50 hover:border-yellow-500/50'
          )}
          onClick={() => setFilterType('pending')}
        >
          <div className="text-sm text-slate-400">Pending</div>
          <div className="mt-1 text-2xl font-bold text-white">{stats.pending}</div>
        </Card>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-white/10 bg-slate-800/50 pl-10 text-white placeholder:text-slate-500"
          />
        </div>
        <Button variant="outline" className="border-white/10 text-slate-400">
          <Filter className="mr-2 h-4 w-4" />
          More Filters
        </Button>
      </div>

      {/* File Grid */}
      {filteredFiles.length === 0 ? (
        <Card className="border-white/10 bg-slate-800/50 p-12">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-700/50">
              <Music className="h-8 w-8 text-slate-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                {searchQuery ? 'No files found' : 'No audio files yet'}
              </h3>
              <p className="mt-1 text-sm text-slate-400">
                {searchQuery ? 'Try a different search term' : 'Upload your first file to get started'}
              </p>
            </div>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredFiles.map((file) => (
            <Card
              key={file.id}
              className="group border-white/10 bg-slate-800/50 p-4 transition-all hover:border-purple-500/50 hover:bg-slate-800/70"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="truncate font-semibold text-white group-hover:text-purple-400">
                    {file.name}
                  </h4>
                  <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                    <span>{file.duration.toFixed(2)}s</span>
                    <span>•</span>
                    <span>{(file.size / 1024 / 1024).toFixed(2)}MB</span>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-400 hover:text-white"
                    >
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="bg-slate-800 border-white/10">
                    <DropdownMenuItem
                      className="text-slate-300 hover:bg-white/10"
                      onClick={() => selectFile(file.id)}
                    >
                      <Play className="mr-2 h-4 w-4" />
                      Play
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-slate-300 hover:bg-white/10">
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      className="text-red-400 hover:bg-red-500/10"
                      onClick={() => removeAudioFile(file.id)}
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* File Metadata */}
              <div className="mt-4 flex flex-wrap gap-2">
                {file.analyzed ? (
                  <>
                    <Badge className="bg-green-500/10 text-green-400">Analyzed</Badge>
                    {file.analysis?.genre && (
                      <Badge variant="secondary">{file.analysis.genre}</Badge>
                    )}
                    {file.analysis?.tempo && (
                      <Badge variant="secondary">{file.analysis.tempo} BPM</Badge>
                    )}
                  </>
                ) : (
                  <Badge className="bg-yellow-500/10 text-yellow-400">Pending</Badge>
                )}
              </div>

              {/* Action Buttons */}
              <div className="mt-4 flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 border-purple-500/50 text-purple-400 hover:bg-purple-500/10"
                  onClick={() => selectFile(file.id)}
                >
                  <Play className="mr-1 h-3 w-3" />
                  Play
                </Button>
                {!file.analyzed && (
                  <Button
                    size="sm"
                    className="flex-1 bg-gradient-to-r from-purple-500 to-cyan-500"
                  >
                    Analyze
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
