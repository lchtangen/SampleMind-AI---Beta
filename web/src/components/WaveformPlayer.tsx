/**
 * Waveform Visualization Component
 *
 * Interactive audio waveform player using Wavesurfer.js
 */

import { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import type { AudioFile } from '../store/appStore';

interface WaveformPlayerProps {
  audioFile: AudioFile;
  onReady?: () => void;
  onPlay?: () => void;
  onPause?: () => void;
  onFinish?: () => void;
  height?: number;
  waveColor?: string;
  progressColor?: string;
}

export default function WaveformPlayer({
  audioFile,
  onReady,
  onPlay,
  onPause,
  onFinish,
  height = 128,
  waveColor = '#94a3b8',
  progressColor = '#6366f1',
}: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.75);

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current) return;

    // Create WaveSurfer instance
    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor,
      progressColor,
      height,
      normalize: true,
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      cursorWidth: 1,
      cursorColor: '#6366f1',
    });

    // Load audio
    wavesurfer.load(audioFile.path);

    // Event listeners
    wavesurfer.on('ready', () => {
      setDuration(wavesurfer.getDuration());
      if (onReady) onReady();
    });

    wavesurfer.on('play', () => {
      setIsPlaying(true);
      if (onPlay) onPlay();
    });

    wavesurfer.on('pause', () => {
      setIsPlaying(false);
      if (onPause) onPause();
    });

    wavesurfer.on('finish', () => {
      setIsPlaying(false);
      if (onFinish) onFinish();
    });

    wavesurfer.on('audioprocess', () => {
      setCurrentTime(wavesurfer.getCurrentTime());
    });

    wavesurferRef.current = wavesurfer;

    // Cleanup
    return () => {
      wavesurfer.destroy();
    };
  }, [audioFile, height, waveColor, progressColor, onReady, onPlay, onPause, onFinish]);

  // Volume control
  useEffect(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.setVolume(volume);
    }
  }, [volume]);

  const togglePlayPause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  const stop = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.stop();
      setIsPlaying(false);
      setCurrentTime(0);
    }
  };

  const skipForward = (seconds: number = 5) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.skip(seconds);
    }
  };

  const skipBackward = (seconds: number = 5) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.skip(-seconds);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="waveform-player">
      <div className="waveform-header">
        <h3>{audioFile.name}</h3>
        {audioFile.analyzed && audioFile.analysis && (
          <div className="waveform-meta">
            <span>{audioFile.analysis.tempo.toFixed(0)} BPM</span>
            <span>{audioFile.analysis.key}</span>
          </div>
        )}
      </div>

      {/* Waveform Container */}
      <div ref={containerRef} className="waveform-container" />

      {/* Playback Controls */}
      <div className="waveform-controls">
        <div className="playback-buttons">
          <button
            className="control-btn"
            onClick={() => skipBackward(5)}
            title="Skip backward 5s"
          >
            ⏪
          </button>

          <button
            className="control-btn play-pause"
            onClick={togglePlayPause}
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? '⏸' : '▶'}
          </button>

          <button className="control-btn" onClick={stop} title="Stop">
            ⏹
          </button>

          <button
            className="control-btn"
            onClick={() => skipForward(5)}
            title="Skip forward 5s"
          >
            ⏩
          </button>
        </div>

        <div className="time-display">
          <span>{formatTime(currentTime)}</span>
          <span>/</span>
          <span>{formatTime(duration)}</span>
        </div>

        <div className="volume-control">
          <span className="volume-icon">🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="volume-slider"
          />
          <span className="volume-value">{Math.round(volume * 100)}%</span>
        </div>
      </div>
    </div>
  );
}
