import React, { useEffect, useState } from 'react';
import { Toaster } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { AudioVisualizer } from './components/audio/AudioVisualizer';
import { AudioControls } from './components/audio/AudioControls';
import { Sidebar } from './components/navigation/Sidebar';
import { TopBar } from './components/navigation/TopBar';
import { NeurologicAudioEngine } from '@samplemind-ai/audio-engine';
import { useAudioEngine } from './hooks/useAudioEngine';
import { cn } from './lib/utils';

// Initialize audio engine
const audioEngine = new NeurologicAudioEngine();

export default function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Initialize audio engine
  useEffect(() => {
    const init = async () => {
      try {
        await audioEngine.initialize();
        setIsInitialized(true);
        
        // Set up event listeners
        audioEngine.on('playbackStarted', () => setIsPlaying(true));
        audioEngine.on('playbackStopped', () => setIsPlaying(false));
        audioEngine.on('playbackEnded', () => setIsPlaying(false));
        
        // Load a sample audio file (replace with actual audio loading)
        // await audioEngine.loadAudio('/path/to/sample.mp3');
        
      } catch (error) {
        console.error('Failed to initialize audio engine:', error);
      }
    };

    init();

    return () => {
      audioEngine.dispose();
    };
  }, []);

  // Update current time
  useEffect(() => {
    let animationFrameId: number;
    
    const updateTime = () => {
      // Update current time for visualization
      // This is a simplified version - in a real app, you'd get this from the audio engine
      if (isPlaying) {
        setCurrentTime(prev => {
          const newTime = prev + 0.1;
          return newTime > duration ? 0 : newTime;
        });
      }
      animationFrameId = requestAnimationFrame(updateTime);
    };
    
    if (isPlaying) {
      animationFrameId = requestAnimationFrame(updateTime);
    }
    
    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [isPlaying, duration]);

  const handlePlayPause = () => {
    if (!isInitialized) return;
    
    if (isPlaying) {
      audioEngine.stop();
    } else {
      // In a real app, you'd have an audio buffer loaded
      // audioEngine.play(buffer);
      setIsPlaying(true);
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    // Update volume in audio engine
    // audioEngine.setVolume(newVolume);
  };

  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-cyber-darker text-cyber-primary">
        <div className="text-center">
          <div className="text-4xl font-bold mb-4 animate-pulse">SAMPLEMIND AI</div>
          <div className="text-cyber-highlight">Initializing audio engine...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-cyber-darker text-cyber-primary overflow-hidden">
      <TopBar 
        isSidebarOpen={isSidebarOpen} 
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} 
      />
      
      <div className="flex flex-1 overflow-hidden">
        <AnimatePresence>
          {isSidebarOpen && (
            <motion.div
              initial={{ x: -300, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -300, opacity: 0 }}
              transition={{ type: 'spring', damping: 30 }}
              className="w-64 bg-cyber-glass-dark backdrop-blur-lg border-r border-cyber-primary/20 flex-shrink-0 h-full overflow-y-auto"
            >
              <Sidebar />
            </motion.div>
          )}
        </AnimatePresence>
        
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Main workspace area */}
          <div className="flex-1 p-6 overflow-auto">
            <div className={cn(
              'glass-panel p-6 rounded-xl h-full',
              'bg-cyber-glass-dark/50 backdrop-blur-md',
              'border border-cyber-primary/20',
              'shadow-cyber-glow'
            )}>
              <h1 className="text-2xl font-bold mb-6 text-cyber-primary">
                Welcome to <span className="text-cyber-accent">SampleMind AI</span>
              </h1>
              
              {/* Audio visualization */}
              <div className="h-48 mb-6">
                <AudioVisualizer 
                  isPlaying={isPlaying} 
                  currentTime={currentTime} 
                  duration={duration} 
                />
              </div>
              
              {/* Sample content */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((item) => (
                  <div 
                    key={item}
                    className={cn(
                      'p-4 rounded-lg transition-all duration-300',
                      'bg-cyber-glass-dark/30 backdrop-blur-sm',
                      'border border-cyber-primary/10 hover:border-cyber-primary/30',
                      'hover:shadow-cyber-glow-hover',
                      'cursor-pointer'
                    )}
                  >
                    <div className="font-medium text-cyber-highlight">Sample Track {item}</div>
                    <div className="text-sm text-cyber-primary/70">00:30 • 120 BPM • C Minor</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Audio controls */}
          <div className={cn(
            'border-t border-cyber-primary/10',
            'bg-cyber-glass-darker/80 backdrop-blur-lg',
            'p-4'
          )}>
            <AudioControls
              isPlaying={isPlaying}
              currentTime={currentTime}
              duration={duration}
              volume={volume}
              onPlayPause={handlePlayPause}
              onVolumeChange={handleVolumeChange}
              onSeek={(time) => setCurrentTime(time)}
            />
          </div>
        </main>
      </div>
      
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: 'rgba(10, 10, 20, 0.9)',
            border: '1px solid rgba(0, 240, 255, 0.2)',
            backdropFilter: 'blur(10px)',
          },
        }}
      />
    </div>
  );
}
