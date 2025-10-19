import React, { createContext, useContext, useEffect, useState } from 'react';
import { AudioNeuralNetwork, AudioAnalysisResult } from '@samplemind-ai/audio-engine';
import { useAudioEngine } from '../hooks/useAudioEngine';

interface AudioAnalysisContextType {
  isAnalyzing: boolean;
  analysis: AudioAnalysisResult | null;
  analyzeAudio: (audioBuffer: AudioBuffer) => Promise<AudioAnalysisResult>;
  error: Error | null;
}

const AudioAnalysisContext = createContext<AudioAnalysisContextType | undefined>(undefined);

export const AudioAnalysisProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [neuralNetwork, setNeuralNetwork] = useState<AudioNeuralNetwork | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AudioAnalysisResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  
  const { audioEngine } = useAudioEngine();
  
  // Initialize neural network
  useEffect(() => {
    if (!audioEngine) return;
    
    const initNeuralNetwork = async () => {
      try {
        const nn = new AudioNeuralNetwork(audioEngine as any);
        await nn.initialize();
        setNeuralNetwork(nn);
      } catch (err) {
        console.error('Failed to initialize neural network:', err);
        setError(err instanceof Error ? err : new Error('Failed to initialize neural network'));
      }
    };
    
    initNeuralNetwork();
    
    return () => {
      if (neuralNetwork) {
        neuralNetwork.dispose();
      }
    };
  }, [audioEngine]);
  
  // Analyze audio buffer
  const analyzeAudio = async (audioBuffer: AudioBuffer): Promise<AudioAnalysisResult> => {
    if (!neuralNetwork) {
      throw new Error('Neural network not initialized');
    }
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await neuralNetwork.analyzeAudioFeatures(audioBuffer);
      setAnalysis(result);
      return result;
    } catch (err) {
      console.error('Audio analysis failed:', err);
      const error = err instanceof Error ? err : new Error('Audio analysis failed');
      setError(error);
      throw error;
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  return (
    <AudioAnalysisContext.Provider
      value={{
        isAnalyzing,
        analysis,
        analyzeAudio,
        error,
      }}
    >
      {children}
    </AudioAnalysisContext.Provider>
  );
};

export const useAudioAnalysis = (): AudioAnalysisContextType => {
  const context = useContext(AudioAnalysisContext);
  if (context === undefined) {
    throw new Error('useAudioAnalysis must be used within an AudioAnalysisProvider');
  }
  return context;
};
