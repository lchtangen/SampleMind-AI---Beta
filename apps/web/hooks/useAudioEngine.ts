import { useState, useEffect, useRef, useCallback } from 'react';
import { NeurologicAudioEngine } from '@samplemind-ai/audio-engine';

export const useAudioEngine = () => {
  const [audioEngine, setAudioEngine] = useState<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTrack, setCurrentTrack] = useState<{
    id: string;
    name: string;
    url: string;
    duration: number;
  } | null>(null);
  
  const animationFrameRef = useRef<number>();
  const audioContextRef = useRef<AudioContext | null>(null);
  
  // Initialize audio engine
  useEffect(() => {
    const init = async () => {
      try {
        const engine = new NeurologicAudioEngine();
        await engine.initialize();
        setAudioEngine(engine);
        setIsInitialized(true);
        
        // Set up event listeners
        engine.on('playbackStarted', () => setIsPlaying(true));
        engine.on('playbackStopped', () => setIsPlaying(false));
        engine.on('playbackEnded', () => {
          setIsPlaying(false);
          setCurrentTime(0);
        });
        
        // Set initial volume
        const maybeSetVolume = (engine as any).setVolume;
        if (typeof maybeSetVolume === 'function') {
          maybeSetVolume.call(engine, volume);
        }
        
      } catch (error) {
        console.error('Failed to initialize audio engine:', error);
      }
    };
    
    init();
    
    return () => {
      if (audioEngine) {
        audioEngine.dispose();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);
  
  // Update current time when playing
  useEffect(() => {
    if (!isPlaying) return;
    
    let lastTime = performance.now();
    
    const updateTime = () => {
      const now = performance.now();
      const delta = (now - lastTime) / 1000; // Convert to seconds
      lastTime = now;
      
      setCurrentTime(prev => {
        const newTime = prev + delta;
        if (newTime >= duration) {
          setIsPlaying(false);
          return 0;
        }
        return newTime;
      });
      
      animationFrameRef.current = requestAnimationFrame(updateTime);
    };
    
    animationFrameRef.current = requestAnimationFrame(updateTime);
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isPlaying, duration]);
  
  // Load audio file
  const loadAudio = useCallback(async (url: string, trackInfo: { id: string; name: string }) => {
    if (!audioEngine) return;
    
    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioEngine.loadAudio(arrayBuffer);
      
      setCurrentTrack({
        ...trackInfo,
        url,
        duration: audioBuffer.duration
      });
      
      setDuration(audioBuffer.duration);
      setCurrentTime(0);
      
      return audioBuffer;
    } catch (error) {
      console.error('Error loading audio:', error);
      throw error;
    }
  }, [audioEngine]);
  
  // Play/pause toggle
  const togglePlayPause = useCallback(async () => {
    if (!audioEngine) return;
    
    if (isPlaying) {
      if (typeof audioEngine.pause === 'function') {
      audioEngine.pause();
      } else if (typeof audioEngine.stop === 'function') {
        audioEngine.stop();
      }
    } else if (typeof audioEngine.play === 'function') {
      await audioEngine.play();
    }
  }, [audioEngine, isPlaying]);
  
  // Seek to position
  const seek = useCallback((time: number) => {
    if (!audioEngine) return;
    
    const newTime = Math.max(0, Math.min(time, duration));
    if (typeof audioEngine.seek === 'function') {
    audioEngine.seek(newTime);
    }
    setCurrentTime(newTime);
  }, [audioEngine, duration]);
  
  // Set volume
  const setVolumeLevel = useCallback((level: number) => {
    if (!audioEngine) return;
    
    const newVolume = Math.max(0, Math.min(1, level));
    if (typeof audioEngine.setVolume === 'function') {
    audioEngine.setVolume(newVolume);
    }
    setVolume(newVolume);
    
    if (isMuted && newVolume > 0) {
      setIsMuted(false);
    } else if (newVolume === 0) {
      setIsMuted(true);
    }
  }, [audioEngine, isMuted]);
  
  // Toggle mute
  const toggleMute = useCallback(() => {
    if (!audioEngine) return;
    
    if (isMuted) {
      if (typeof audioEngine.setVolume === 'function') {
      audioEngine.setVolume(volume || 0.8);
      }
      setIsMuted(false);
    } else {
      if (typeof audioEngine.setVolume === 'function') {
      audioEngine.setVolume(0);
      }
      setIsMuted(true);
    }
  }, [audioEngine, isMuted, volume]);
  
  // Get audio data for visualization
  const getAudioData = useCallback(() => {
    if (!audioEngine) return new Uint8Array(0);
    
    try {
      if (typeof audioEngine.getFrequencyData === 'function') {
      return audioEngine.getFrequencyData();
      }
      return new Uint8Array(0);
    } catch (error) {
      console.error('Error getting audio data:', error);
      return new Uint8Array(0);
    }
  }, [audioEngine]);
  
  return {
    // State
    isInitialized,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    currentTrack,
    
    // Actions
    loadAudio,
    togglePlayPause,
    seek,
    setVolume: setVolumeLevel,
    toggleMute,
    getAudioData,
    
    // Direct engine access (use with caution)
    audioEngine,
  };
};
