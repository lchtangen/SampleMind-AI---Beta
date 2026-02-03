'use client';

/**
 * ADVANCED WAVEFORM COMPONENT
 * Canvas-based high-performance waveform with zoom, scrubbing, and real-time playhead tracking
 * Features: GPU acceleration, zoom controls, click-to-seek, gradient coloring, responsive design
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface AdvancedWaveformProps {
  audioBuffer?: AudioBuffer;
  audioElement?: HTMLAudioElement;
  className?: string;
  height?: number;
  backgroundColor?: string;
  waveformColor?: string;
  playheadColor?: string;
  onSeek?: (time: number) => void;
  onZoomChange?: (zoomLevel: number) => void;
}

interface CanvasState {
  canvasWidth: number;
  canvasHeight: number;
  zoomLevel: number;
  scrollOffset: number;
  isDragging: boolean;
  isPlayingInternal: boolean;
  playheadPosition: number;
}

/**
 * Advanced Waveform Component with Canvas Rendering
 */
export const AdvancedWaveform: React.FC<AdvancedWaveformProps> = ({
  audioBuffer,
  audioElement,
  className = '',
  height = 150,
  backgroundColor = '#0f172a',
  waveformColor = '#06b6d4',
  playheadColor = '#ec4899',
  onSeek,
  onZoomChange,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [canvasState, setCanvasState] = useState<CanvasState>({
    canvasWidth: 0,
    canvasHeight: height,
    zoomLevel: 1,
    scrollOffset: 0,
    isDragging: false,
    isPlayingInternal: false,
    playheadPosition: 0,
  });

  const [audioDataArray, setAudioDataArray] = useState<Uint8Array | null>(null);
  const [duration, setDuration] = useState(0);
  const animationFrameRef = useRef<number | null>(null);

  // Extract audio data from buffer
  useEffect(() => {
    if (!audioBuffer) return;

    const audioContext = audioBuffer.getChannelData(0);
    const samples = new Uint8Array(audioContext.length);

    for (let i = 0; i < audioContext.length; i++) {
      samples[i] = Math.abs(audioContext[i]) * 255;
    }

    setAudioDataArray(samples);
    setDuration(audioBuffer.duration);
  }, [audioBuffer]);

  // Update canvas size on mount and resize
  useEffect(() => {
    const updateCanvasSize = () => {
      if (!containerRef.current || !canvasRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const newWidth = rect.width;

      canvasRef.current.width = newWidth;
      canvasRef.current.height = height;

      setCanvasState((prev) => ({
        ...prev,
        canvasWidth: newWidth,
        canvasHeight: height,
      }));
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, [height]);

  // Draw waveform on canvas
  const drawWaveform = useCallback(() => {
    if (
      !canvasRef.current ||
      !audioDataArray ||
      canvasState.canvasWidth === 0
    ) {
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Background
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, width, height);

    // Grid lines (time markers)
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)';
    ctx.lineWidth = 1;

    const timelineHeight = 20;
    const markerSpacing = (width / canvasState.zoomLevel) / 4;

    for (let i = 0; i < width; i += markerSpacing) {
      const time = (i / width) * duration * canvasState.zoomLevel;
      const minutes = Math.floor(time / 60);
      const seconds = Math.floor(time % 60);

      ctx.drawImage(
        ctx.canvas,
        i,
        0,
        1,
        height - timelineHeight,
        i,
        timelineHeight,
        1,
        height - timelineHeight
      );

      if (i % (markerSpacing * 4) === 0) {
        ctx.fillStyle = 'rgba(148, 163, 184, 0.3)';
        ctx.font = '10px monospace';
        ctx.fillText(`${minutes}:${seconds.toString().padStart(2, '0')}`, i + 5, 15);
      }
    }

    // Draw waveform
    const samplesPerPixel = Math.ceil(
      (audioDataArray.length / width) * canvasState.zoomLevel
    );
    const middleY = height / 2;
    const amplitude = (height - timelineHeight) / 2 - 5;

    // Gradient for waveform
    const gradient = ctx.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, 'hsl(180, 95%, 55%, 0.3)');
    gradient.addColorStop(0.5, 'hsl(180, 95%, 55%, 0.8)');
    gradient.addColorStop(1, 'hsl(280, 85%, 65%, 0.3)');

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';

    ctx.beginPath();
    ctx.moveTo(0, middleY);

    for (let i = 0; i < width; i++) {
      const sampleIndex = Math.floor(
        ((i / width) * audioDataArray.length) / canvasState.zoomLevel
      );
      const sample = audioDataArray[sampleIndex] || 128;
      const normalized = (sample / 255) * amplitude;

      ctx.lineTo(i, middleY - normalized);
    }

    ctx.stroke();

    // Draw waveform bottom
    ctx.beginPath();
    ctx.moveTo(0, middleY);

    for (let i = 0; i < width; i++) {
      const sampleIndex = Math.floor(
        ((i / width) * audioDataArray.length) / canvasState.zoomLevel
      );
      const sample = audioDataArray[sampleIndex] || 128;
      const normalized = (sample / 255) * amplitude;

      ctx.lineTo(i, middleY + normalized);
    }

    ctx.stroke();

    // Draw center line
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, middleY);
    ctx.lineTo(width, middleY);
    ctx.stroke();

    // Draw playhead
    if (audioElement) {
      const playheadX =
        (audioElement.currentTime / duration) * (width / canvasState.zoomLevel) -
        canvasState.scrollOffset;

      ctx.strokeStyle = playheadColor;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(playheadX, 0);
      ctx.lineTo(playheadX, height);
      ctx.stroke();

      // Playhead circle
      ctx.fillStyle = playheadColor;
      ctx.beginPath();
      ctx.arc(playheadX, 8, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw selection/hover indicator
    if (canvasState.isDragging) {
      ctx.fillStyle = 'rgba(139, 92, 246, 0.1)';
      ctx.fillRect(
        0,
        timelineHeight,
        width,
        height - timelineHeight
      );
    }
  }, [audioDataArray, canvasState, backgroundColor, playheadColor, duration, audioElement]);

  // Animation loop for playhead tracking
  useEffect(() => {
    const update = () => {
      if (audioElement && audioDataArray) {
        drawWaveform();
      }
      animationFrameRef.current = requestAnimationFrame(update);
    };

    animationFrameRef.current = requestAnimationFrame(update);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioElement, audioDataArray, drawWaveform]);

  // Handle canvas click for seeking
  const handleCanvasClick = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (!canvasRef.current || !audioElement) return;

      const rect = canvasRef.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const clickedTime =
        (x / canvasState.canvasWidth) * duration * canvasState.zoomLevel;

      audioElement.currentTime = Math.max(0, Math.min(clickedTime, duration));
      onSeek?.(audioElement.currentTime);
    },
    [canvasState.canvasWidth, canvasState.zoomLevel, duration, audioElement, onSeek]
  );

  // Zoom in
  const handleZoomIn = useCallback(() => {
    setCanvasState((prev) => {
      const newZoom = Math.min(prev.zoomLevel + 0.5, 4);
      onZoomChange?.(newZoom);
      return { ...prev, zoomLevel: newZoom };
    });
  }, [onZoomChange]);

  // Zoom out
  const handleZoomOut = useCallback(() => {
    setCanvasState((prev) => {
      const newZoom = Math.max(prev.zoomLevel - 0.5, 1);
      onZoomChange?.(newZoom);
      return { ...prev, zoomLevel: newZoom };
    });
  }, [onZoomChange]);

  // Reset zoom
  const handleResetZoom = useCallback(() => {
    setCanvasState((prev) => ({
      ...prev,
      zoomLevel: 1,
      scrollOffset: 0,
    }));
    onZoomChange?.(1);
  }, [onZoomChange]);

  // Handle dragging for scrolling zoomed waveform
  const handleMouseDown = useCallback(() => {
    setCanvasState((prev) => ({
      ...prev,
      isDragging: true,
    }));
  }, []);

  const handleMouseUp = useCallback(() => {
    setCanvasState((prev) => ({
      ...prev,
      isDragging: false,
    }));
  }, []);

  const handleMouseMove = useCallback(
    (event: React.MouseEvent<HTMLCanvasElement>) => {
      if (!canvasState.isDragging || canvasState.zoomLevel === 1) return;

      // Handle horizontal scrolling
      const deltaX = event.movementX;
      setCanvasState((prev) => ({
        ...prev,
        scrollOffset: Math.max(
          0,
          prev.scrollOffset - deltaX * canvasState.zoomLevel
        ),
      }));
    },
    [canvasState.isDragging, canvasState.zoomLevel]
  );

  return (
    <div className={`w-full rounded-lg overflow-hidden ${className}`}>
      {/* Waveform canvas */}
      <div
        ref={containerRef}
        className="relative bg-slate-900 border border-slate-700/50 rounded-t-lg overflow-hidden"
        style={{ height: `${height}px` }}
      >
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseMove={handleMouseMove}
          onMouseLeave={() =>
            setCanvasState((prev) => ({ ...prev, isDragging: false }))
          }
          className="w-full cursor-pointer hover:bg-slate-900/80 transition-colors"
          style={{ display: 'block' }}
        />
      </div>

      {/* Controls bar */}
      <motion.div
        className="bg-slate-800/50 border-t border-slate-700/50 px-4 py-3 flex items-center justify-between"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {/* Time display */}
        <div className="text-xs font-mono text-slate-400">
          <span>
            {audioElement
              ? `${Math.floor(audioElement.currentTime / 60)}:${Math.floor(audioElement.currentTime % 60)
                  .toString()
                  .padStart(2, '0')}`
              : '0:00'}
          </span>
          <span className="mx-2 opacity-50">/</span>
          <span>
            {`${Math.floor(duration / 60)}:${Math.floor(duration % 60)
              .toString()
              .padStart(2, '0')}`}
          </span>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={handleZoomOut}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={canvasState.zoomLevel === 1}
            className="p-1.5 rounded-md hover:bg-slate-700/50 disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 hover:text-cyan-400 transition-colors"
            title="Zoom out"
          >
            <ZoomOut size={16} />
          </motion.button>

          <div className="text-xs font-mono text-slate-400 px-2">
            {(canvasState.zoomLevel * 100).toFixed(0)}%
          </div>

          <motion.button
            onClick={handleZoomIn}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={canvasState.zoomLevel >= 4}
            className="p-1.5 rounded-md hover:bg-slate-700/50 disabled:opacity-50 disabled:cursor-not-allowed text-slate-400 hover:text-cyan-400 transition-colors"
            title="Zoom in"
          >
            <ZoomIn size={16} />
          </motion.button>

          <motion.button
            onClick={handleResetZoom}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-1.5 rounded-md hover:bg-slate-700/50 text-slate-400 hover:text-purple-400 transition-colors"
            title="Reset zoom"
          >
            <RotateCcw size={16} />
          </motion.button>
        </div>

        {/* Info */}
        <div className="text-xs text-slate-500">
          Click to seek • Drag to scroll
        </div>
      </motion.div>
    </div>
  );
};

export default AdvancedWaveform;
