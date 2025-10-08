/**
 * AnalysisDisplay Component
 *
 * Display AI-powered audio analysis results with visualizations
 */

import { TrendingUp, Music, Zap, Target, Star, BarChart3 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { AudioAnalysis } from '@/store/appStore';
import { cn } from '@/lib/utils';

interface AnalysisDisplayProps {
  result: AudioAnalysis;
  isLoading?: boolean;
}

export function AnalysisDisplay({ result, isLoading = false }: AnalysisDisplayProps) {
  if (isLoading) {
    return (
      <Card className="border-white/10 bg-slate-800/50 p-8">
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
          <p className="text-sm text-slate-400">Analyzing audio...</p>
        </div>
      </Card>
    );
  }

  const metrics = [
    { label: 'Energy', value: result.energy || 0, icon: Zap, color: 'cyan' },
    { label: 'Danceability', value: result.danceability || 0, icon: Music, color: 'purple' },
    { label: 'Acousticness', value: result.acousticness || 0, icon: Target, color: 'blue' },
    { label: 'Instrumentalness', value: result.instrumentalness || 0, icon: Star, color: 'indigo' },
    { label: 'Valence', value: result.valence || 0, icon: TrendingUp, color: 'violet' },
  ];

  return (
    <div className="space-y-6">
      {/* Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-white/10 bg-gradient-to-br from-purple-500/10 to-blue-500/10 p-6">
          <div className="mb-2 text-sm text-slate-400">Genre</div>
          <div className="text-2xl font-bold gradient-text">{result.genre || 'Unknown'}</div>
        </Card>

        <Card className="border-white/10 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 p-6">
          <div className="mb-2 text-sm text-slate-400">Mood</div>
          <div className="text-2xl font-bold text-white">{result.mood || 'Unknown'}</div>
        </Card>

        <Card className="border-white/10 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 p-6">
          <div className="mb-2 text-sm text-slate-400">Tempo</div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{result.tempo}</span>
            <span className="text-sm text-slate-400">BPM</span>
          </div>
        </Card>
      </div>

      {/* Detailed Analysis */}
      <Tabs defaultValue="metrics" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-slate-800/50">
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
        </TabsList>

        <TabsContent value="metrics" className="space-y-4">
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <div className="mb-6 flex items-center gap-3">
              <BarChart3 className="h-5 w-5 text-cyan-400" />
              <h3 className="text-lg font-semibold text-white">Audio Characteristics</h3>
            </div>

            <div className="space-y-6">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                const percentage = metric.value * 100;

                return (
                  <div key={metric.label} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Icon className={cn(
                          'h-4 w-4',
                          metric.color === 'cyan' && 'text-cyan-400',
                          metric.color === 'purple' && 'text-purple-400',
                          metric.color === 'blue' && 'text-blue-400',
                          metric.color === 'indigo' && 'text-indigo-400',
                          metric.color === 'violet' && 'text-violet-400'
                        )} />
                        <span className="text-sm font-medium text-white">{metric.label}</span>
                      </div>
                      <Badge
                        className={cn(
                          'text-xs',
                          percentage >= 70 && 'bg-green-500/10 text-green-400',
                          percentage >= 40 && percentage < 70 && 'bg-yellow-500/10 text-yellow-400',
                          percentage < 40 && 'bg-red-500/10 text-red-400'
                        )}
                      >
                        {percentage.toFixed(0)}%
                      </Badge>
                    </div>
                    <Progress value={percentage} className="h-2" />
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Key Information */}
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <div className="mb-1 text-sm text-slate-400">Musical Key</div>
                <div className="text-xl font-semibold text-white">{result.key}</div>
              </div>
              <div>
                <div className="mb-1 text-sm text-slate-400">Time Signature</div>
                <div className="text-xl font-semibold text-white">4/4</div>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="summary">
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-cyan-500">
                <Star className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">AI Analysis Summary</h3>
                <p className="text-xs text-slate-400">Powered by advanced AI models</p>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-slate-300">
              {result.summary || 'No summary available.'}
            </p>
          </Card>
        </TabsContent>

        <TabsContent value="suggestions" className="space-y-3">
          {(result.suggestions || []).map((suggestion, index) => (
            <Card
              key={index}
              className="border-white/10 bg-slate-800/50 p-4 transition-all hover:bg-slate-800/70"
            >
              <div className="flex gap-3">
                <div className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-cyan-500 text-xs font-bold text-white">
                  {index + 1}
                </div>
                <p className="text-sm text-slate-300">{suggestion}</p>
              </div>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}