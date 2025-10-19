import React, { useEffect, useRef, useState } from 'react';
import * as tf from '@tensorflow/tfjs';

type VisualizationMode = 'waveform' | 'spectrum' | 'particles' | 'neural';

interface EnhancedVisualizerProps {
  audioEngine: any; // Replace with proper type
  width?: number;
  height?: number;
  className?: string;
}

export const EnhancedVisualizer: React.FC<EnhancedVisualizerProps> = ({
  audioEngine,
  width = 800,
  height = 300,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mode, setMode] = useState<VisualizationMode>('waveform');
  const animationFrameRef = useRef<number>();
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize visualization
  useEffect(() => {
    if (!canvasRef.current || !audioEngine) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas dimensions
    canvas.width = width;
    canvas.height = height;

    // Visualization loop
    const draw = () => {
      if (!ctx) return;
      
      const analyser = audioEngine.getAnalyser();
      if (!analyser) {
        animationFrameRef.current = requestAnimationFrame(draw);
        return;
      }

      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Draw based on selected mode
      switch (mode) {
        case 'waveform':
          drawWaveform(ctx, analyser, width, height);
          break;
        case 'spectrum':
          drawSpectrum(ctx, analyser, width, height);
          break;
        case 'particles':
          drawParticles(ctx, analyser, width, height);
          break;
        case 'neural':
          drawNeuralNetwork(ctx, analyser, width, height);
          break;
      }

      animationFrameRef.current = requestAnimationFrame(draw);
    };

    // Start animation loop
    animationFrameRef.current = requestAnimationFrame(draw);
    setIsInitialized(true);

    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioEngine, mode, width, height]);

  // Visualization rendering functions
  const drawWaveform = (ctx: CanvasRenderingContext2D, analyser: AnalyserNode, width: number, height: number) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    ctx.lineWidth = 2;
    ctx.strokeStyle = '#00F0FF';
    ctx.beginPath();

    const sliceWidth = (width * 1.0) / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0;
      const y = (v * height) / 2;

      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    ctx.lineTo(width, height / 2);
    ctx.stroke();
  };

  const drawSpectrum = (ctx: CanvasRenderingContext2D, analyser: AnalyserNode, width: number, height: number) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    const barWidth = (width / bufferLength) * 2.5;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
      const barHeight = (dataArray[i] / 255) * height;
      
      // Create gradient for each bar
      const gradient = ctx.createLinearGradient(0, height, 0, height - barHeight);
      gradient.addColorStop(0, '#00F0FF');
      gradient.addColorStop(1, '#7C3AED');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, height - barHeight, barWidth, barHeight);
      
      x += barWidth + 1;
    }
  };

  const drawParticles = (ctx: CanvasRenderingContext2D, analyser: AnalyserNode, width: number, height: number) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    // Clear with semi-transparent black for trail effect
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, width, height);

    const particleCount = 100;
    const segment = Math.floor(bufferLength / particleCount);

    for (let i = 0; i < particleCount; i++) {
      const value = dataArray[i * segment] / 255;
      const x = (i / particleCount) * width;
      const y = height - (value * height);
      const radius = 2 + (value * 8);
      
      // Create radial gradient for particles
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
      gradient.addColorStop(0, 'rgba(124, 58, 237, 0.8)');
      gradient.addColorStop(1, 'rgba(0, 240, 255, 0.2)');
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  };

  const drawNeuralNetwork = (ctx: CanvasRenderingContext2D, analyser: AnalyserNode, width: number, height: number) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteFrequencyData(dataArray);

    // Clear with dark background
    ctx.fillStyle = 'rgba(17, 24, 39, 0.8)';
    ctx.fillRect(0, 0, width, height);

    // Draw neural network connections
    const nodes = 8;
    const layers = 4;
    const nodeRadius = 8;
    const layerSpacing = width / (layers + 1);
    
    // Draw connections
    for (let l = 0; l < layers - 1; l++) {
      const x1 = (l + 1) * layerSpacing;
      const x2 = (l + 2) * layerSpacing;
      
      for (let i = 0; i < nodes; i++) {
        const y1 = ((i + 1) * height) / (nodes + 1);
        
        for (let j = 0; j < nodes; j++) {
          const y2 = ((j + 1) * height) / (nodes + 1);
          const value = dataArray[((l * nodes) + i + j) % bufferLength] / 255;
          
          ctx.strokeStyle = `rgba(0, 240, 255, ${value * 0.3})`;
          ctx.lineWidth = value * 2;
          
          ctx.beginPath();
          ctx.moveTo(x1, y1);
          ctx.quadraticCurveTo(x1 + (x2 - x1) / 2, (y1 + y2) / 2, x2, y2);
          ctx.stroke();
        }
      }
    }
    
    // Draw nodes
    for (let l = 0; l < layers; l++) {
      const x = (l + 1) * layerSpacing;
      
      for (let i = 0; i < nodes; i++) {
        const y = ((i + 1) * height) / (nodes + 1);
        const value = dataArray[((l * nodes) + i) % bufferLength] / 255;
        
        // Node glow
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, nodeRadius * 2);
        gradient.addColorStop(0, `rgba(0, 240, 255, ${value})`);
        gradient.addColorStop(1, 'rgba(0, 240, 255, 0)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius * 2, 0, Math.PI * 2);
        ctx.fill();
        
        // Node core
        ctx.fillStyle = `rgba(0, 240, 255, ${0.5 + (value * 0.5)})`;
        ctx.beginPath();
        ctx.arc(x, y, nodeRadius, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };

  if (!isInitialized) {
    return (
      <div className={`${className} bg-gray-900/50 flex items-center justify-center`} style={{ width, height }}>
        <div className="animate-pulse text-gray-500">Initializing visualization...</div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} style={{ width, height }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full rounded-lg"
      />
      
      {/* Visualization mode selector */}
      <div className="absolute bottom-2 right-2 flex space-x-2">
        {(['waveform', 'spectrum', 'particles', 'neural'] as VisualizationMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              mode === m 
                ? 'bg-cyan-600 text-white' 
                : 'bg-gray-800/70 text-gray-300 hover:bg-gray-700/70'
            }`}
          >
            {m.charAt(0).toUpperCase() + m.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
};

export default EnhancedVisualizer;
