import React, { useEffect, useRef, useState } from 'react';
import * as tf from '@tensorflow/tfjs';
import { NeuroplasticLearning } from '../core/NeuroplasticLearning';

export interface LearningVisualizerProps {
  neuroplasticLearning: NeuroplasticLearning;
  width?: number;
  height?: number;
  className?: string;
}

export const LearningVisualizer: React.FC<LearningVisualizerProps> = ({
  neuroplasticLearning,
  width = 400,
  height = 200,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLearning, setIsLearning] = useState(false);
  const [learningProgress, setLearningProgress] = useState(0);
  const [styleVector, setStyleVector] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const onTrainingStart = () => {
      setIsLearning(true);
      setLearningProgress(0);
    };

    const onTrainingProgress = (data: any) => {
      setLearningProgress(Math.min(100, Math.round((data.epoch / 20) * 100)));
    };

    const onTrainingComplete = async () => {
      setIsLearning(false);
      setLearningProgress(100);
      
      // Update style vector visualization
      const vector = await neuroplasticLearning.getStyleVector();
      if (vector) {
        setStyleVector(vector[0]);
      }
    };

    // Set up event listeners
    neuroplasticLearning.on('trainingStart', onTrainingStart);
    neuroplasticLearning.on('trainingProgress', onTrainingProgress);
    neuroplasticLearning.on('trainingComplete', onTrainingComplete);

    // Initial style vector
    const initStyleVector = async () => {
      try {
        const vector = await neuroplasticLearning.getStyleVector();
        if (vector) {
          setStyleVector(vector[0]);
        }
      } catch (err) {
        console.error('Error getting initial style vector:', err);
        setError('Failed to load style visualization');
      }
    };
    
    initStyleVector();

    // Cleanup
    return () => {
      neuroplasticLearning.off('trainingStart', onTrainingStart);
      neuroplasticLearning.off('trainingProgress', onTrainingProgress);
      neuroplasticLearning.off('trainingComplete', onTrainingComplete);
    };
  }, [neuroplasticLearning]);

  // Draw the style vector visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || styleVector.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const draw = () => {
      // Clear canvas
      ctx.clearRect(0, 0, width, height);
      
      // Draw background
      ctx.fillStyle = 'rgba(17, 24, 39, 0.7)';
      ctx.fillRect(0, 0, width, height);
      
      // Draw grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 1;
      
      // Horizontal grid lines
      for (let y = 0; y <= height; y += height / 4) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      
      // Draw style vector
      const barWidth = width / styleVector.length;
      const maxValue = Math.max(...styleVector.map(Math.abs));
      
      styleVector.forEach((value, i) => {
        const x = i * barWidth;
        const barHeight = (Math.abs(value) / (maxValue || 1)) * (height * 0.8);
        const y = (height - barHeight) / 2;
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, '#00F0FF');
        gradient.addColorStop(1, '#7C3AED');
        
        // Draw bar
        ctx.fillStyle = gradient;
        ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
        
        // Add glow effect
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#00F0FF';
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Draw border
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.strokeRect(x + 2, y, barWidth - 4, barHeight);
        
        // Reset shadow
        ctx.shadowBlur = 0;
      });
      
      // Draw labels
      if (isLearning) {
        ctx.fillStyle = 'white';
        ctx.font = '12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Learning...', width / 2, height / 2);
        
        // Draw progress bar
        const progressWidth = width * 0.8;
        const progressX = (width - progressWidth) / 2;
        const progressY = height * 0.7;
        const progressHeight = 8;
        
        // Background
        ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.fillRect(progressX, progressY, progressWidth, progressHeight);
        
        // Progress
        const progressFillWidth = (learningProgress / 100) * progressWidth;
        const progressGradient = ctx.createLinearGradient(0, progressY, 0, progressY + progressHeight);
        progressGradient.addColorStop(0, '#00F0FF');
        progressGradient.addColorStop(1, '#7C3AED');
        
        ctx.fillStyle = progressGradient;
        ctx.fillRect(progressX, progressY, progressFillWidth, progressHeight);
        
        // Percentage text
        ctx.fillStyle = 'white';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`${learningProgress}%`, width / 2, progressY + progressHeight + 15);
      }
    };
    
    draw();
  }, [styleVector, isLearning, learningProgress, width, height]);

  if (error) {
    return (
      <div className={`bg-gray-900 p-4 rounded-lg text-red-400 ${className}`}>
        Error: {error}
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="w-full h-full rounded-lg border border-gray-700"
      />
      <div className="absolute bottom-2 left-2 text-xs text-gray-400">
        Style Vector
      </div>
      {isLearning && (
        <div className="absolute top-2 right-2 text-xs bg-cyan-500 text-white px-2 py-1 rounded-full">
          LEARNING
        </div>
      )}
    </div>
  );
};

export default LearningVisualizer;
