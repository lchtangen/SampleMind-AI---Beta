'use client';

import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward } from 'lucide-react';
import { cn, formatDuration } from '@/lib/utils';
import Button from '../ui/Button';

export interface WaveformVisualizerProps {
  audioUrl: string;
  height?: number;
  waveColor?: string;
  progressColor?: string;
  cursorColor?: string;
  className?: string;
}

const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  audioUrl,
  height = 128,
  waveColor = '#ddd',
  progressColor = '#3b82f6',
  cursorColor = '#1e40af',
  className,
}) => {
  const waveformRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!waveformRef.current) return;

    // Create WaveSurfer instance
    const wavesurfer = WaveSurfer.create({
      container: waveformRef.current,
      waveColor,
      progressColor,
      cursorColor,
      barWidth: 2,
      barRadius: 3,
      cursorWidth: 2,
      height,
      barGap: 1,
      normalize: true,
      backend: 'WebAudio',
    });

    wavesurferRef.current = wavesurfer;

    // Load audio
    wavesurfer.load(audioUrl);

    // Event listeners
    wavesurfer.on('ready', () => {
      setIsLoading(false);
      setDuration(wavesurfer.getDuration());
      wavesurfer.setVolume(volume);
    });

    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('interaction', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurfer.on('finish', () => {
      setIsPlaying(false);
    });

    wavesurfer.on('error', (err: Error) => {
      setError(err.message);
      setIsLoading(false);
    });

    // Cleanup
    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, waveColor, progressColor, cursorColor, height, volume]);

  const handlePlayPause = () => {
    if (!wavesurferRef.current) return;
    
    if (isPlaying) {
      wavesurferRef.current.pause();
    } else {
      wavesurferRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSkipBackward = () => {
    if (!wavesurferRef.current) return;
    const newTime = Math.max(0, currentTime - 5);
    wavesurferRef.current.seekTo(newTime / duration);
  };

  const handleSkipForward = () => {
    if (!wavesurferRef.current) return;
    const newTime = Math.min(duration, currentTime + 5);
    wavesurferRef.current.seekTo(newTime / duration);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (wavesurferRef.current) {
      wavesurferRef.current.setVolume(newVolume);
    }
    if (newVolume === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    if (!wavesurferRef.current) return;
    
    if (isMuted) {
      wavesurferRef.current.setVolume(volume || 0.7);
      setIsMuted(false);
    } else {
      wavesurferRef.current.setVolume(0);
      setIsMuted(true);
    }
  };

  if (error) {
    return (
      <div className={cn('p-6 bg-red-50 border border-red-200 rounded-lg', className)}>
        <p className="text-sm text-red-600">Error loading audio: {error}</p>
      </div>
    );
  }

  return (
    <div className={cn('w-full bg-white rounded-lg border border-gray-200 p-4', className)}>
      {/* Waveform */}
      <div className="mb-4">
        <div
          ref={waveformRef}
          className={cn('w-full', isLoading && 'opacity-50')}
        />
        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        )}
      </div>

      {/* Time Display */}
      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
        <span>{formatDuration(currentTime)}</span>
        <span>{formatDuration(duration)}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSkipBackward}
            disabled={isLoading}
          >
            <SkipBack size={18} />
          </Button>

          <Button
            variant="primary"
            size="md"
            onClick={handlePlayPause}
            disabled={isLoading}
          >
            {isPlaying ? <Pause size={20} /> : <Play size={20} />}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleSkipForward}
            disabled={isLoading}
          >
            <SkipForward size={18} />
          </Button>
        </div>

        {/* Volume Control */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleMute}
            className="text-gray-600 hover:text-gray-900 transition-colors"
            disabled={isLoading}
          >
            {isMuted || volume === 0 ? (
              <VolumeX size={20} />
            ) : (
              <Volume2 size={20} />
            )}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
            disabled={isLoading}
            className="w-24 h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>
      </div>
    </div>
  );
};

export default WaveformVisualizer;
