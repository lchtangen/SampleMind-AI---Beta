import React, { useState, useRef, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useAudioAnalysis } from '../../contexts/AudioAnalysisContext';
import { AudioAnalysisVisualizer } from '../../components/audio/AudioAnalysisVisualizer';
import { Button } from '../../components/ui/button';
import { Loader2, Upload, X, Music, RotateCw } from 'lucide-react';
import { cn } from '../../lib/utils';

export const AudioAnalysisPanel: React.FC = () => {
  const { analyzeAudio, isAnalyzing, analysis, error } = useAudioAnalysis();
  const [audioBuffer, setAudioBuffer] = useState<AudioBuffer | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    try {
      // Create audio context
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      
      // Read file as array buffer
      const arrayBuffer = await file.arrayBuffer();
      
      // Decode audio data
      const buffer = await audioContext.decodeAudioData(arrayBuffer);
      
      // Set audio buffer and URL
      setAudioBuffer(buffer);
      setAudioUrl(URL.createObjectURL(file));
      
      // Start analysis
      await analyzeAudio(buffer);
      
    } catch (err) {
      console.error('Error processing audio file:', err);
    }
  }, [analyzeAudio]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.ogg', '.m4a']
    },
    maxFiles: 1,
    disabled: isAnalyzing
  });
  
  const clearAnalysis = () => {
    setAudioBuffer(null);
    setAudioUrl(null);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-cyber-primary">Audio Analysis</h2>
        {audioBuffer && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAnalysis}
            className="text-cyber-primary/70 hover:text-cyber-primary hover:bg-cyber-primary/10"
          >
            <X className="h-4 w-4 mr-1" />
            Clear
          </Button>
        )}
      </div>
      
      {!audioBuffer ? (
        <div
          {...getRootProps()}
          className={cn(
            'flex-1 flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl',
            'border-cyber-primary/30 hover:border-cyber-primary/60',
            'bg-cyber-glass-dark/30 hover:bg-cyber-glass-dark/50',
            'transition-all duration-200 cursor-pointer',
            isDragActive && 'border-cyber-primary/80 bg-cyber-glass-dark/60'
          )}
        >
          <input {...getInputProps()} />
          <div className="text-center">
            <Upload className="h-12 w-12 mx-auto mb-4 text-cyber-primary/60" />
            <p className="text-cyber-primary/80 mb-1">
              {isDragActive ? 'Drop the audio file here' : 'Drag & drop an audio file, or click to select'}
            </p>
            <p className="text-sm text-cyber-primary/50">
              Supports MP3, WAV, OGG, M4A (max 50MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col">
          {/* Audio Player */}
          <div className={cn(
            'mb-6 p-4 rounded-lg',
            'bg-cyber-glass-dark/30 border border-cyber-primary/20',
            'flex items-center space-x-4'
          )}>
            <div className="flex-shrink-0 w-12 h-12 rounded-lg bg-cyber-primary/10 flex items-center justify-center">
              <Music className="h-6 w-6 text-cyber-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-cyber-primary truncate">
                {audioUrl?.split('/').pop() || 'Audio File'}
              </p>
              <p className="text-xs text-cyber-primary/60">
                {audioBuffer ? `${(audioBuffer.duration / 60).toFixed(2)} min` : '--:--'}
              </p>
            </div>
            <audio
              ref={audioRef}
              src={audioUrl || ''}
              controls
              className="flex-1 max-w-md h-10"
            />
          </div>
          
          {/* Analysis Results */}
          <div className="flex-1 overflow-hidden">
            {isAnalyzing ? (
              <div className="h-full flex flex-col items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-cyber-primary mb-4" />
                <p className="text-cyber-primary/80">Analyzing audio...</p>
                <p className="text-sm text-cyber-primary/50 mt-2">This may take a few moments</p>
              </div>
            ) : error ? (
              <div className="h-full flex flex-col items-center justify-center p-8 text-center">
                <div className="bg-cyber-error/10 text-cyber-error p-4 rounded-lg max-w-md">
                  <p className="font-medium">Analysis Failed</p>
                  <p className="text-sm mt-1">{error.message}</p>
                </div>
                <Button
                  variant="outline"
                  className="mt-6 border-cyber-primary/20 text-cyber-primary hover:bg-cyber-primary/10"
                  onClick={() => audioBuffer && analyzeAudio(audioBuffer)}
                >
                  <RotateCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </div>
            ) : analysis ? (
              <div className="h-full">
                <AudioAnalysisVisualizer 
                  analysis={analysis} 
                  className="h-full min-h-[400px]"
                />
                
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <StatCard 
                    label="Energy" 
                    value={analysis.energy} 
                    color="#00f0ff"
                  />
                  <StatCard 
                    label="Danceability" 
                    value={analysis.danceability} 
                    color="#ff00ff"
                  />
                  <StatCard 
                    label="Valence" 
                    value={analysis.valence} 
                    color="#00ffcc"
                  />
                  <StatCard 
                    label="Arousal" 
                    value={analysis.arousal} 
                    color="#ffcc00"
                  />
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: number; color: string }> = ({ 
  label, 
  value, 
  color 
}) => {
  const percentage = Math.round(value * 100);
  
  return (
    <div className={cn(
      'p-4 rounded-lg',
      'bg-cyber-glass-dark/30 border border-cyber-primary/10',
      'transition-all duration-200 hover:border-cyber-primary/30',
      'group'
    )}>
      <div className="flex justify-between items-start mb-2">
        <span className="text-sm font-medium text-cyber-primary/70">
          {label}
        </span>
        <span 
          className="text-sm font-bold"
          style={{ color }}
        >
          {percentage}%
        </span>
      </div>
      <div className="h-2 bg-cyber-primary/10 rounded-full overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-500"
          style={{
            width: `${percentage}%`,
            background: `linear-gradient(90deg, ${color}77, ${color}ff)`,
            boxShadow: `0 0 8px ${color}80`
          }}
        />
      </div>
    </div>
  );
};
