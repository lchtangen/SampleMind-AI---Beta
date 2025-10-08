/**
 * WaveformPlayer Component
 * 
 * Professional audio waveform player using WaveSurfer.js
 * Features: Real-time visualization, zoom, regions, playback controls
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface WaveformPlayerProps {
  audioUrl: string;
  title?: string;
  artist?: string;
  onReady?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  className?: string;
}

export function WaveformPlayer({
  audioUrl,
  title = 'Untitled Track',
  artist,
  onReady,
  onPlay,
  onPause,
  onFinish,
  className,
}: WaveformPlayerProps) {
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.75);
  const [isMuted, setIsMuted] = useState(false);
  const [zoom, setZoom] = useState(1);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!waveformRef.current) return;

    const wavesurfer = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: 'rgb(148, 163, 184)', // slate-400
      progressColor: 'rgb(6, 182, 212)', // cyan-500
      cursorColor: 'rgb(167, 139, 250)', // violet-400
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 100,
      normalize: true,
    });

    wavesurferRef.current = wavesurfer;

    // Load audio
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on('ready', () => {
      setIsLoading(false);
      setDuration(wavesurfer.getDuration());
      wavesurfer.setVolume(volume);
      onReady?.();
    });

    wavesurfer.on('play', () => {
      setIsPlaying(true);
      onPlay?.();
    });

    wavesurfer.on('pause', () => {
      setIsPlaying(false);
      onPause?.();
    });

    wavesurfer.on('finish', () => {
      setIsPlaying(false);
      onFinish?.();
    });

    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('interaction', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    // Cleanup
    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, onReady, onPlay, onPause, onFinish, volume]);

  // Playback controls
  const togglePlayPause = useCallback(() => {
    wavesurferRef.current?.playPause();
  }, []);

  const skipBackward = useCallback(() => {
    const current = wavesurferRef.current?.getCurrentTime() || 0;
    wavesurferRef.current?.setTime(Math.max(0, current - 5));
  }, []);

  const skipForward = useCallback(() => {
    const current = wavesurferRef.current?.getCurrentTime() || 0;
    const duration = wavesurferRef.current?.getDuration() || 0;
    wavesurferRef.current?.setTime(Math.min(duration, current + 5));
  }, []);

  const toggleMute = useCallback(() => {
    if (!wavesurferRef.current) return;
    
    if (isMuted) {
      wavesurferRef.current.setVolume(volume);
      setIsMuted(false);
    } else {
      wavesurferRef.current.setVolume(0);
      setIsMuted(true);
    }
  }, [isMuted, volume]);

  const handleVolumeChange = useCallback((newVolume: number) => {
    setVolume(newVolume);
    wavesurferRef.current?.setVolume(newVolume);
    if (newVolume > 0 && isMuted) {
      setIsMuted(false);
    }
  }, [isMuted]);

  const handleZoomIn = useCallback(() => {
    const newZoom = Math.min(zoom + 10, 100);
    setZoom(newZoom);
    wavesurferRef.current?.zoom(newZoom);
  }, [zoom]);

  const handleZoomOut = useCallback(() => {
    const newZoom = Math.max(zoom - 10, 1);
    setZoom(newZoom);
    wavesurferRef.current?.zoom(newZoom);
  }, [zoom]);

  // Format time (seconds to MM:SS)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className={cn('border-white/10 bg-slate-800/50 p-6', className)}>
      {/* Track Info */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-white">{title}</h3>
          {artist && <p className="text-sm text-slate-400">{artist}</p>}
        </div>
        
        {/* Zoom Controls */}
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleZoomOut}
            disabled={zoom <= 1}
            className="h-8 w-8 text-slate-400 hover:text-white"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleZoomIn}
            disabled={zoom >= 100}
            className="h-8 w-8 text-slate-400 hover:text-white"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Waveform */}
      <div className="relative mb-4 overflow-hidden rounded-lg bg-slate-900/50 p-4">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-2">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
              <p className="text-sm text-slate-400">Loading audio...</p>
            </div>
          </div>
        )}
        <div ref={waveformRef} className="w-full" />
      </div>

      {/* Time Display */}
      <div className="mb-3 flex items-center justify-between text-sm text-slate-400">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        {/* Playback Controls */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={skipBackward}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
          >
            <SkipBack className="h-5 w-5" />
          </Button>

          <Button
            size="icon"
            onClick={togglePlayPause}
            disabled={isLoading}
            className="h-12 w-12 bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40"
          >
            {isPlaying ? (
              <Pause className="h-6 w-6" />
            ) : (
              <Play className="h-6 w-6 ml-0.5" />
            )}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={skipForward}
            disabled={isLoading}
            className="text-slate-400 hover:text-white"
          >
            <SkipForward className="h-5 w-5" />
          </Button>
        </div>

        {/* Volume Control */}
        <div className="flex flex-1 items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleMute}
            className="text-slate-400 hover:text-white"
          >
            {isMuted || volume === 0 ? (
              <VolumeX className="h-5 w-5" />
            ) : (
              <Volume2 className="h-5 w-5" />
            )}
          </Button>

          <div className="relative flex-1 max-w-32">
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={isMuted ? 0 : volume}
              onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
              className="w-full cursor-pointer appearance-none bg-transparent [&::-webkit-slider-runnable-track]:h-1 [&::-webkit-slider-runnable-track]:rounded-full [&::-webkit-slider-runnable-track]:bg-slate-700 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-500"
            />
          </div>
        </div>

        {/* Progress Indicator */}
        <div className="text-xs text-slate-500">
          {duration > 0 && `${Math.round((currentTime / duration) * 100)}%`}
        </div>
      </div>
    </Card>
  );
}