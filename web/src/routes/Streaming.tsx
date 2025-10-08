/**
 * Real-time Streaming Page
 *
 * Real-time audio analysis with live visualization
 */

import { useState } from 'react';
import { Radio, Mic, Square, Activity, Zap, TrendingUp, Pause } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useAppStore } from '@/store/appStore';
import { cn } from '@/lib/utils';

export default function Streaming() {
  const { streamingSession, setStreamingSession } = useAppStore((state) => ({
    streamingSession: state.streamingSession,
    setStreamingSession: state.setStreamingSession,
  }));

  const [isStreaming, setIsStreaming] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const handleStartStreaming = () => {
    const newSession = {
      id: `stream-${Date.now()}`,
      active: true,
      connected: true,
    };
    setStreamingSession(newSession);
    setIsStreaming(true);
    setIsPaused(false);
  };

  const handleStopStreaming = () => {
    setStreamingSession(null);
    setIsStreaming(false);
    setIsPaused(false);
  };

  const handleTogglePause = () => {
    setIsPaused(!isPaused);
  };

  // Mock real-time metrics
  const metrics = {
    tempo: 128,
    energy: 0.78,
    pitch: 440,
    volume: 0.65,
    latency: 12,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold gradient-text">Real-time Streaming</h1>
        <p className="mt-2 text-slate-400">
          Analyze audio in real-time with live visualizations
        </p>
      </div>

      {/* Connection Status */}
      <Card className={cn(
        'border-2 p-6 transition-all',
        isStreaming
          ? 'border-green-500 bg-green-500/10'
          : 'border-white/10 bg-slate-800/50'
      )}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={cn(
              'flex h-12 w-12 items-center justify-center rounded-full',
              isStreaming
                ? 'bg-green-500 animate-pulse'
                : 'bg-slate-700'
            )}>
              <Radio className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                {isStreaming ? (isPaused ? 'Paused' : 'Streaming Active') : 'Ready to Stream'}
              </h3>
              <p className="text-sm text-slate-400">
                {isStreaming
                  ? streamingSession?.connected
                    ? `Latency: ${metrics.latency}ms • Connected`
                    : 'Connecting...'
                  : 'Start streaming to begin real-time analysis'}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            {!isStreaming ? (
              <Button
                onClick={handleStartStreaming}
                className="bg-gradient-to-r from-purple-500 to-cyan-500 text-white shadow-lg shadow-purple-500/20"
              >
                <Mic className="mr-2 h-4 w-4" />
                Start Streaming
              </Button>
            ) : (
              <>
                <Button
                  onClick={handleTogglePause}
                  variant="outline"
                  className="border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/10"
                >
                  <Pause className="mr-2 h-4 w-4" />
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                <Button
                  onClick={handleStopStreaming}
                  variant="outline"
                  className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Square className="mr-2 h-4 w-4" />
                  Stop
                </Button>
              </>
            )}
          </div>
        </div>
      </Card>

      {isStreaming && !isPaused && (
        <>
          {/* Real-time Metrics */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card className="border-white/10 bg-slate-800/50 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10">
                  <Activity className="h-5 w-5 text-cyan-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Tempo</p>
                  <p className="text-2xl font-bold text-white">{metrics.tempo}</p>
                  <p className="text-xs text-slate-500">BPM</p>
                </div>
              </div>
            </Card>

            <Card className="border-white/10 bg-slate-800/50 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/10">
                  <Zap className="h-5 w-5 text-purple-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Energy</p>
                  <p className="text-2xl font-bold text-white">
                    {(metrics.energy * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-slate-500">Level</p>
                </div>
              </div>
            </Card>

            <Card className="border-white/10 bg-slate-800/50 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/10">
                  <TrendingUp className="h-5 w-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Pitch</p>
                  <p className="text-2xl font-bold text-white">{metrics.pitch}</p>
                  <p className="text-xs text-slate-500">Hz</p>
                </div>
              </div>
            </Card>

            <Card className="border-white/10 bg-slate-800/50 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10">
                  <Activity className="h-5 w-5 text-indigo-400" />
                </div>
                <div>
                  <p className="text-sm text-slate-400">Volume</p>
                  <p className="text-2xl font-bold text-white">
                    {(metrics.volume * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-slate-500">dB</p>
                </div>
              </div>
            </Card>
          </div>

          {/* Live Visualization */}
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Live Waveform</h3>
            <div className="flex h-48 items-center justify-center rounded-lg bg-slate-900/50">
              <div className="flex h-full items-end justify-center gap-1 px-4">
                {Array.from({ length: 50 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-2 animate-pulse rounded-t-full bg-gradient-to-t from-purple-500 via-blue-500 to-cyan-500"
                    style={{
                      height: `${Math.random() * 100}%`,
                      animationDelay: `${i * 20}ms`,
                    }}
                  />
                ))}
              </div>
            </div>
          </Card>

          {/* Frequency Analysis */}
          <Card className="border-white/10 bg-slate-800/50 p-6">
            <h3 className="mb-4 text-lg font-semibold text-white">Frequency Spectrum</h3>
            <div className="space-y-3">
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-slate-400">Sub Bass (20-60 Hz)</span>
                  <span className="text-cyan-400">45%</span>
                </div>
                <Progress value={45} className="h-2" />
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-slate-400">Bass (60-250 Hz)</span>
                  <span className="text-purple-400">72%</span>
                </div>
                <Progress value={72} className="h-2" />
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-slate-400">Midrange (250-2000 Hz)</span>
                  <span className="text-blue-400">58%</span>
                </div>
                <Progress value={58} className="h-2" />
              </div>
              <div>
                <div className="mb-2 flex justify-between text-sm">
                  <span className="text-slate-400">Treble (2k-20k Hz)</span>
                  <span className="text-indigo-400">67%</span>
                </div>
                <Progress value={67} className="h-2" />
              </div>
            </div>
          </Card>
        </>
      )}

      {/* Information Panel */}
      {!isStreaming && (
        <Card className="border-white/10 bg-slate-800/50 p-8">
          <div className="flex flex-col items-center gap-6 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 to-cyan-500">
              <Radio className="h-10 w-10 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Real-time Audio Analysis</h3>
              <p className="mt-2 text-slate-400">
                Start streaming to see live metrics and visualizations
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-3 text-left w-full max-w-2xl">
              <div className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                <Activity className="mb-2 h-6 w-6 text-cyan-400" />
                <h4 className="font-semibold text-white">Low Latency</h4>
                <p className="mt-1 text-sm text-slate-400">
                  Real-time analysis with {'<'} 20ms latency
                </p>
              </div>
              <div className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                <Zap className="mb-2 h-6 w-6 text-purple-400" />
                <h4 className="font-semibold text-white">Live Metrics</h4>
                <p className="mt-1 text-sm text-slate-400">
                  Tempo, pitch, energy in real-time
                </p>
              </div>
              <div className="rounded-lg border border-white/10 bg-slate-900/50 p-4">
                <TrendingUp className="mb-2 h-6 w-6 text-blue-400" />
                <h4 className="font-semibold text-white">Visualizations</h4>
                <p className="mt-1 text-sm text-slate-400">
                  Waveforms and frequency spectrum
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
