import { useEffect, useRef, useState } from 'react';
import { NeurologicAudioEngine } from '../core/NeurologicAudioEngine';
import { NeuroplasticLearning } from '../core/NeuroplasticLearning';

export const useAudioLearning = () => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLearning, setIsLearning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const audioEngineRef = useRef<any>(null);
  const learningEngineRef = useRef<NeuroplasticLearning | null>(null);
  const analysisIntervalRef = useRef<number | null>(null);

  // Initialize audio and learning engines
  useEffect(() => {
    const init = async () => {
      try {
        // Initialize audio engine
        const audioEngine = new NeurologicAudioEngine();
        await audioEngine.initialize();
        
        // Initialize learning engine
        const learningEngine = new NeuroplasticLearning();
        
        // Set up event listeners for learning engine
        learningEngine.on('trainingStart', () => setIsLearning(true));
        learningEngine.on('trainingComplete', () => setIsLearning(false));
        
        // Store references
        audioEngineRef.current = audioEngine;
        learningEngineRef.current = learningEngine;
        
        setIsInitialized(true);
        
        // Start audio analysis
        startAnalysis(audioEngine, learningEngine);
      } catch (err) {
        console.error('Initialization error:', err);
        setError('Failed to initialize audio system');
      }
    };

    init();

    // Cleanup
    return () => {
      if (analysisIntervalRef.current) {
        window.clearInterval(analysisIntervalRef.current);
      }
      
      if (audioEngineRef.current && typeof audioEngineRef.current.dispose === 'function') {
        audioEngineRef.current.dispose();
      }
    };
  }, []);

  // Start analyzing audio and learning patterns
  const startAnalysis = (audioEngine: any, learningEngine: NeuroplasticLearning) => {
    if (analysisIntervalRef.current) {
      window.clearInterval(analysisIntervalRef.current);
    }

    // Analyze audio every 2 seconds
    analysisIntervalRef.current = window.setInterval(async () => {
      try {
        if (!audioEngine || !audioEngine.isPlaying) return;
        
        // Get current audio analysis
        const analysis = typeof audioEngine.getCurrentAnalysis === 'function'
          ? audioEngine.getCurrentAnalysis()
          : {
              bpm: 0,
              spectralCentroid: 0,
              beatHistogram: [0, 0, 0, 0],
            };
        
        // Add pattern to learning engine
        learningEngine.addPattern({
          bpm: analysis.bpm || 120,
          key: 'C', // This would come from key detection
          scale: 'minor', // This would come from scale detection
          timbreProfile: analysis.spectralCentroid ? [analysis.spectralCentroid] : [0],
          rhythmPattern: analysis.beatHistogram || [0, 0, 0, 0]
        });
      } catch (err) {
        console.error('Analysis error:', err);
      }
    }, 2000);
  };

  // Start/stop audio processing
  const toggleAudio = async () => {
    if (!audioEngineRef.current) return;
    
    try {
      const engine = audioEngineRef.current;
      if (!engine) {
        return;
      }

      if (engine.isPlaying && typeof engine.stop === 'function') {
        await engine.stop();
      } else if (typeof engine.start === 'function') {
        await engine.start();
      } else if (typeof engine.play === 'function') {
        await engine.play();
      }
    } catch (err) {
      console.error('Audio control error:', err);
      setError('Failed to control audio playback');
    }
  };

  // Get current style vector
  const getStyleVector = async () => {
    if (!learningEngineRef.current) return null;
    return await learningEngineRef.current.getStyleVector();
  };

  // Predict next pattern
  const predictNextPattern = async () => {
    if (!learningEngineRef.current || !audioEngineRef.current) return null;
    
    const analysisSource = audioEngineRef.current.getCurrentAnalysis &&
      typeof audioEngineRef.current.getCurrentAnalysis === 'function'
        ? audioEngineRef.current.getCurrentAnalysis()
        : {
            bpm: 120,
            spectralCentroid: 0,
            beatHistogram: [0, 0, 0, 0],
          };
    
    return await learningEngineRef.current.predictNextPattern({
      bpm: analysisSource.bpm || 120,
      key: 'C',
      scale: 'minor',
      timbreProfile: analysisSource.spectralCentroid ? [analysisSource.spectralCentroid] : [0],
      rhythmPattern: analysisSource.beatHistogram || [0, 0, 0, 0]
    });
  };

  return {
    isInitialized,
    isPlaying: audioEngineRef.current?.isPlaying || false,
    isLearning,
    error,
    toggleAudio,
    getStyleVector,
    predictNextPattern,
    audioEngine: audioEngineRef.current,
    learningEngine: learningEngineRef.current
  };
};

export default useAudioLearning;
