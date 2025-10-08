/**
 * Dashboard Page
 *
 * Modern dashboard with stats, recent files, and quick actions
 */

import { TrendingUp, Music, Sparkles, Activity, Upload, Wand2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';

export default function Dashboard() {
  const audioFiles = useAppStore((state) => state.audioFiles);
  const generations = useAppStore((state) => state.generations);
  const streamingSession = useAppStore((state) => state.streamingSession);

  const stats = {
    totalFiles: audioFiles.length,
    analyzedFiles: audioFiles.filter((f) => f.analyzed).length,
    totalGenerations: generations.length,
    activeStreams: streamingSession?.active ? 1 : 0,
  };

  const statCards = [
    {
      title: 'Audio Files',
      value: stats.totalFiles,
      subtitle: `${stats.analyzedFiles} analyzed`,
      icon: Music,
      color: 'purple',
      trend: '+12%',
    },
    {
      title: 'AI Generations',
      value: stats.totalGenerations,
      subtitle: 'Music tracks created',
      icon: Sparkles,
      color: 'cyan',
      trend: '+23%',
    },
    {
      title: 'Active Streams',
      value: stats.activeStreams,
      subtitle: 'Real-time analysis',
      icon: Activity,
      color: 'blue',
      trend: '—',
    },
    {
      title: 'This Week',
      value: '47',
      subtitle: 'Total analyses',
      icon: TrendingUp,
      color: 'indigo',
      trend: '+8%',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text">Dashboard</h1>
        <p className="mt-2 text-slate-400">Welcome back to SampleMind AI</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card
              key={stat.title}
              className="border-white/10 bg-slate-800/50 p-6 transition-all hover:bg-slate-800/70"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">{stat.title}</p>
                  <p className="mt-2 text-3xl font-bold text-white">{stat.value}</p>
                  <p className="mt-1 text-xs text-slate-500">{stat.subtitle}</p>
                </div>
                <div
                  className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-lg',
                    stat.color === 'purple' && 'bg-purple-500/10',
                    stat.color === 'cyan' && 'bg-cyan-500/10',
                    stat.color === 'blue' && 'bg-blue-500/10',
                    stat.color === 'indigo' && 'bg-indigo-500/10'
                  )}
                >
                  <Icon
                    className={cn(
                      'h-6 w-6',
                      stat.color === 'purple' && 'text-purple-400',
                      stat.color === 'cyan' && 'text-cyan-400',
                      stat.color === 'blue' && 'text-blue-400',
                      stat.color === 'indigo' && 'text-indigo-400'
                    )}
                  />
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <Badge
                  className={cn(
                    'text-xs',
                    stat.trend.startsWith('+') && 'bg-green-500/10 text-green-400',
                    stat.trend === '—' && 'bg-slate-500/10 text-slate-400'
                  )}
                >
                  {stat.trend}
                </Badge>
                <span className="text-xs text-slate-500">vs last week</span>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <Card className="border-white/10 bg-gradient-to-r from-purple-500/10 via-blue-500/10 to-cyan-500/10 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white">Quick Actions</h3>
            <p className="text-sm text-slate-400">Get started with your audio analysis</p>
          </div>
          <div className="flex gap-3">
            <Link to="/analyze">
              <Button className="bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40">
                <Upload className="mr-2 h-4 w-4" />
                Upload Audio
              </Button>
            </Link>
            <Link to="/generate">
              <Button variant="outline" className="border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10">
                <Wand2 className="mr-2 h-4 w-4" />
                Generate Music
              </Button>
            </Link>
          </div>
        </div>
      </Card>

      {/* Recent Files */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">Recent Files</h2>
          <Link to="/library">
            <Button variant="ghost" className="text-slate-400 hover:text-white">
              View All
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {audioFiles.length === 0 ? (
          <Card className="border-white/10 bg-slate-800/50 p-12">
            <div className="flex flex-col items-center gap-4 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-700/50">
                <Music className="h-8 w-8 text-slate-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">No audio files yet</h3>
                <p className="mt-1 text-sm text-slate-400">
                  Upload your first file to get started with AI-powered analysis
                </p>
              </div>
              <Link to="/analyze">
                <Button className="mt-2 bg-gradient-to-r from-purple-500 to-cyan-500">
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Your First File
                </Button>
              </Link>
            </div>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {audioFiles.slice(0, 6).map((file) => (
              <Card
                key={file.id}
                className="group cursor-pointer border-white/10 bg-slate-800/50 p-4 transition-all hover:border-purple-500/50 hover:bg-slate-800/70"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="truncate font-semibold text-white group-hover:text-purple-400">
                      {file.name}
                    </h4>
                    <p className="mt-1 text-xs text-slate-400">
                      Duration: {file.duration.toFixed(2)}s
                    </p>
                  </div>
                  {file.analyzed ? (
                    <Badge className="bg-green-500/10 text-green-400">
                      Analyzed
                    </Badge>
                  ) : (
                    <Badge className="bg-yellow-500/10 text-yellow-400">
                      Pending
                    </Badge>
                  )}
                </div>
                {file.analyzed && file.analysis && (
                  <div className="mt-3 flex gap-2">
                    <Badge variant="secondary" className="text-xs">
                      {file.analysis.genre}
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {file.analysis.tempo} BPM
                    </Badge>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
