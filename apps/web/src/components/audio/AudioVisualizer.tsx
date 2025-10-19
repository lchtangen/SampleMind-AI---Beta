import React, { useEffect, useRef, useCallback } from 'react';
import { cn } from '../../lib/utils';

interface AudioVisualizerProps {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  className?: string;
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  isPlaying,
  currentTime,
  duration,
  className,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();
  const analyserData = useRef<Uint8Array>(new Uint8Array(0));
  
  // Mock data for visualization when audio engine is not connected
  const getMockData = useCallback(() => {
    const data = new Uint8Array(128);
    for (let i = 0; i < data.length; i++) {
      // Create a more interesting wave pattern
      const value = Math.sin(i / 10 + Date.now() / 500) * 50 + 50;
      data[i] = Math.min(255, Math.max(0, value));
    }
    return data;
  }, []);

  const draw = useCallback(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(0, 240, 255, 0.1)');
    gradient.addColorStop(1, 'rgba(0, 240, 255, 0.01)');
    
    // Draw waveform
    ctx.beginPath();
    const sliceWidth = (width * 1.0) / analyserData.current.length;
    let x = 0;
    
    // Draw the main waveform
    for (let i = 0; i < analyserData.current.length; i++) {
      const v = analyserData.current[i] / 255.0;
      const y = v * height;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      x += sliceWidth;
    }
    
    // Create gradient for the stroke
    const strokeGradient = ctx.createLinearGradient(0, 0, width, 0);
    strokeGradient.addColorStop(0, '#00f0ff');
    strokeGradient.addColorStop(0.5, '#ff00ff');
    strokeGradient.addColorStop(1, '#00ffcc');
    
    // Draw the line
    ctx.strokeStyle = strokeGradient;
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Draw the fill
    ctx.lineTo(width, height);
    ctx.lineTo(0, height);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // Draw time indicator
    if (duration > 0) {
      const progress = currentTime / duration;
      const progressX = progress * width;
      
      // Draw progress line
      ctx.beginPath();
      ctx.moveTo(progressX, 0);
      ctx.lineTo(progressX, height);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
      ctx.lineWidth = 1;
      ctx.stroke();
      
      // Draw glow effect
      const glowGradient = ctx.createRadialGradient(
        progressX, height / 2, 0,
        progressX, height / 2, 100
      );
      glowGradient.addColorStop(0, 'rgba(0, 240, 255, 0.3)');
      glowGradient.addColorStop(1, 'rgba(0, 240, 255, 0)');
      
      ctx.fillStyle = glowGradient;
      ctx.fillRect(0, 0, width, height);
    }
    
    // Request next frame if playing
    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(draw);
      
      // Update analyzer data with mock data when not connected to audio engine
      analyserData.current = getMockData();
    }
  }, [currentTime, duration, isPlaying, getMockData]);
  
  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current) {
        const container = canvasRef.current.parentElement;
        if (container) {
          const rect = container.getBoundingClientRect();
          canvasRef.current.width = rect.width;
          canvasRef.current.height = rect.height;
        }
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  // Start/stop animation
  useEffect(() => {
    if (isPlaying) {
      animationFrameRef.current = requestAnimationFrame(draw);
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, draw]);
  
  return (
    <div className={cn('relative w-full h-full', className)}>
      <canvas
        ref={canvasRef}
        className="w-full h-full"
      />
      
      {/* Time indicators */}
      <div className="absolute bottom-2 left-2 text-xs text-cyber-primary/70">
        {formatTime(currentTime)}
      </div>
      <div className="absolute bottom-2 right-2 text-xs text-cyber-primary/70">
        {formatTime(duration)}
      </div>
      
      {/* Playhead indicator */}
      {isPlaying && (
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-cyber-primary/50"
          style={{
            left: `${(currentTime / Math.max(1, duration)) * 100}%`,
            boxShadow: '0 0 10px 2px rgba(0, 240, 255, 0.7)',
          }}
        />
      )}
    </div>
  );
};

// Helper function to format time (seconds to MM:SS)
function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}
