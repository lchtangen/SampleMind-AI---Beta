import React, { useState, useEffect, useCallback } from 'react';
import { Play, Pause, Volume2, VolumeX, SkipBack, SkipForward, RotateCcw, RotateCw } from 'lucide-react';
import { Slider } from '../ui/slider';
import { Button } from '../ui/button';
import { cn } from '../../lib/utils';

interface AudioControlsProps {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  onPlayPause: () => void;
  onVolumeChange: (volume: number) => void;
  onSeek: (time: number) => void;
  className?: string;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  isPlaying,
  currentTime,
  duration,
  volume,
  onPlayPause,
  onVolumeChange,
  onSeek,
  className,
}) => {
  const [isMuted, setIsMuted] = useState(false);
  const [scrubberValue, setScrubberValue] = useState(0);
  const [isScrubbing, setIsScrubbing] = useState(false);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  
  // Update scrubber value when currentTime changes (unless user is scrubbing)
  useEffect(() => {
    if (!isScrubbing && !isNaN(duration) && duration > 0) {
      setScrubberValue((currentTime / duration) * 100);
    }
  }, [currentTime, duration, isScrubbing]);
  
  // Toggle mute
  const toggleMute = () => {
    if (isMuted) {
      onVolumeChange(volume || 0.8); // Restore to previous volume or default
    } else {
      onVolumeChange(0);
    }
    setIsMuted(!isMuted);
  };
  
  // Handle volume change
  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0] / 100;
    onVolumeChange(newVolume);
    if (newVolume === 0) {
      setIsMuted(true);
    } else if (isMuted) {
      setIsMuted(false);
    }
  };
  
  // Handle seek
  const handleSeek = (value: number[]) => {
    const newValue = value[0];
    setScrubberValue(newValue);
    onSeek((newValue / 100) * duration);
  };
  
  // Format time (MM:SS)
  const formatTime = (timeInSeconds: number): string => {
    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = Math.floor(timeInSeconds % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };
  
  // Skip forward/backward
  const skip = (seconds: number) => {
    const newTime = Math.max(0, Math.min(currentTime + seconds, duration));
    onSeek(newTime);
  };
  
  return (
    <div className={cn('w-full', className)}>
      {/* Progress bar */}
      <div className="flex items-center gap-3 mb-2">
        <span className="text-xs text-cyber-primary/70 w-10 text-right">
          {formatTime(currentTime)}
        </span>
        
        <div className="flex-1 relative group">
          <Slider
            value={[scrubberValue]}
            min={0}
            max={100}
            step={0.1}
            onValueChange={(value) => {
              setIsScrubbing(true);
              setScrubberValue(value[0]);
            }}
            onValueCommit={handleSeek}
            onPointerDown={() => setIsScrubbing(true)}
            onPointerUp={() => setIsScrubbing(false)}
            className="h-1.5 cursor-pointer"
            trackClassName="bg-cyber-primary/20"
            rangeClassName="bg-cyber-primary"
            thumbClassName="h-4 w-4 border-2 border-cyber-primary bg-cyber-darker hover:bg-cyber-primary transition-all"
          />
          
          {/* Hover time indicator */}
          <div className="absolute -top-8 left-0 right-0 h-6 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="absolute -translate-x-1/2 px-2 py-1 text-xs bg-cyber-glass-darker border border-cyber-primary/20 rounded-md whitespace-nowrap">
              {formatTime((scrubberValue / 100) * duration)}
            </div>
          </div>
        </div>
        
        <span className="text-xs text-cyber-primary/70 w-10">
          {formatTime(duration)}
        </span>
      </div>
      
      {/* Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleMute}
            className="text-cyber-primary hover:bg-cyber-primary/10 hover:text-cyber-highlight"
          >
            {isMuted || volume === 0 ? (
              <VolumeX className="h-5 w-5" />
            ) : (
              <Volume2 className="h-5 w-5" />
            )}
          </Button>
          
          <div className="relative">
            <Button
              variant="ghost"
              size="icon"
              onMouseEnter={() => setShowVolumeSlider(true)}
              onMouseLeave={() => setShowVolumeSlider(false)}
              className="text-cyber-primary hover:bg-cyber-primary/10 hover:text-cyber-highlight"
            >
              <Volume2 className="h-5 w-5" />
            </Button>
            
            {showVolumeSlider && (
              <div 
                className="absolute bottom-full left-0 mb-2 p-2 bg-cyber-glass-darker/90 backdrop-blur-md rounded-lg shadow-lg border border-cyber-primary/20"
                onMouseEnter={() => setShowVolumeSlider(true)}
                onMouseLeave={() => setShowVolumeSlider(false)}
              >
                <Slider
                  orientation="vertical"
                  value={[isMuted ? 0 : volume * 100]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(value) => handleVolumeChange(value)}
                  className="h-24 w-2"
                  trackClassName="bg-cyber-primary/20"
                  rangeClassName="bg-cyber-primary"
                  thumbClassName="h-3 w-3 border-2 border-cyber-primary bg-cyber-darker hover:bg-cyber-primary transition-all"
                />
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => skip(-5)}
            className="text-cyber-primary hover:bg-cyber-primary/10 hover:text-cyber-highlight"
          >
            <RotateCcw className="h-5 w-5" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={onPlayPause}
            className={cn(
              'h-12 w-12 rounded-full',
              'bg-cyber-primary/10 hover:bg-cyber-primary/20',
              'text-cyber-primary hover:text-cyber-highlight',
              'transition-all duration-200',
              'shadow-cyber-glow hover:shadow-cyber-glow-hover',
              'group relative overflow-hidden',
              'after:absolute after:inset-0 after:bg-cyber-primary/10 after:opacity-0 hover:after:opacity-100',
              'after:transition-opacity after:duration-300'
            )}
          >
            {isPlaying ? (
              <Pause className="h-6 w-6 fill-current" />
            ) : (
              <Play className="h-6 w-6 fill-current ml-0.5" />
            )}
            
            {/* Animated rings */}
            <span className="absolute inset-0 rounded-full border-2 border-cyber-primary/30 group-hover:border-cyber-primary/50 transition-all duration-500 animate-ping-slow opacity-0 group-hover:opacity-100" />
            <span className="absolute inset-0 rounded-full border-2 border-cyber-primary/20 group-hover:border-cyber-primary/40 transition-all duration-700 animate-ping-slow opacity-0 group-hover:opacity-100" />
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            onClick={() => skip(5)}
            className="text-cyber-primary hover:bg-cyber-primary/10 hover:text-cyber-highlight"
          >
            <RotateCw className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="w-24">
          {/* Placeholder for additional controls */}
        </div>
      </div>
    </div>
  );
};
