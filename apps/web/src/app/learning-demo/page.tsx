'use client';

import { useState, useEffect } from 'react';
import { NeurologicAudioEngine } from '@samplemind-ai/audio-engine';
import { NeuroplasticLearning } from '@samplemind-ai/audio-engine';
import { LearningVisualizer } from '@samplemind-ai/audio-engine';
import { useAudioLearning } from '@samplemind-ai/audio-engine';

// Icons (you may need to install @heroicons/react or similar)
const PlayIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const PauseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default function LearningDemo() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [styleVector, setStyleVector] = useState<number[]>([]);
  
  // Initialize audio and learning engines
  const {
    isInitialized: isAudioInitialized,
    isPlaying,
    isLearning,
    error,
    toggleAudio,
    getStyleVector,
    predictNextPattern,
    learningEngine
  } = useAudioLearning();

  // Update style vector periodically
  useEffect(() => {
    if (!isAudioInitialized || !learningEngine) return;

    const updateStyleVector = async () => {
      const vector = await getStyleVector();
      if (vector) {
        setStyleVector(vector[0] || []);
      }
    };

    const interval = setInterval(updateStyleVector, 1000);
    updateStyleVector(); // Initial update

    return () => clearInterval(interval);
  }, [isAudioInitialized, learningEngine, getStyleVector]);

  // Handle prediction
  const handlePredict = async () => {
    try {
      const nextPattern = await predictNextPattern();
      setPrediction(nextPattern);
    } catch (err) {
      console.error('Prediction error:', err);
    }
  };

  // Show loading state
  if (!isAudioInitialized) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p>Initializing audio engine...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="bg-red-900/50 border border-red-500 text-red-200 p-6 rounded-lg max-w-md">
          <h2 className="text-xl font-bold mb-2">Error Initializing Audio</h2>
          <p className="mb-4">{error}</p>
          <p className="text-sm text-red-300">Please check your browser permissions and try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
          SampleMind AI - Neural Learning Demo
        </h1>
        <p className="text-gray-400 mt-2">
          Experience adaptive AI learning from your audio patterns
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Controls */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <h2 className="text-xl font-semibold mb-4 text-cyan-400">Audio Controls</h2>
          
          <div className="space-y-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleAudio}
                className={`p-3 rounded-full ${isPlaying ? 'bg-red-500 hover:bg-red-600' : 'bg-cyan-600 hover:bg-cyan-700'} transition-colors`}
                aria-label={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <PauseIcon /> : <PlayIcon />}
              </button>
              <div>
                <p className="font-medium">{isPlaying ? 'Listening...' : 'Paused'}</p>
                <p className="text-sm text-gray-400">
                  {isLearning ? 'Analyzing patterns...' : 'Ready to learn'}
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-700">
              <h3 className="text-lg font-medium mb-3">Neural Network</h3>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span>Learning Progress</span>
                  <span className="font-mono">
                    {styleVector.length > 0 ? 'Active' : 'Awaiting data'}
                  </span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 transition-all duration-500"
                    style={{ width: `${Math.min(100, styleVector.length * 10)}%` }}
                  ></div>
                </div>
                <button
                  onClick={handlePredict}
                  className="w-full mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-sm font-medium"
                  disabled={styleVector.length === 0}
                >
                  Predict Next Pattern
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Middle Panel - Visualization */}
        <div className="lg:col-span-2 bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700/50">
          <h2 className="text-xl font-semibold mb-4 text-cyan-400">Style Vector Visualization</h2>
          <div className="h-64 mb-6">
            <LearningVisualizer
              neuroplasticLearning={learningEngine!}
              width={800}
              height={256}
              className="w-full h-full"
            />
          </div>
          
          {prediction && (
            <div className="mt-6 p-4 bg-gray-700/50 rounded-lg border border-cyan-500/30">
              <h3 className="text-lg font-medium text-cyan-400 mb-2">Predicted Pattern</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400">BPM</p>
                  <p className="text-2xl font-mono">{prediction.bpm.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Key/Scale</p>
                  <p className="text-2xl font-mono">{prediction.key} {prediction.scale}</p>
                </div>
                <div className="col-span-2">
                  <p className="text-sm text-gray-400 mb-1">Rhythm Pattern</p>
                  <div className="flex space-x-2">
                    {prediction.rhythmPattern.map((val: number, i: number) => (
                      <div 
                        key={i}
                        className="h-8 flex-1 bg-gradient-to-b from-cyan-500 to-purple-600 rounded"
                        style={{ opacity: 0.2 + (val * 0.8) }}
                        title={`${Math.round(val * 100)}%`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-900/80 backdrop-blur-sm border-t border-gray-800 p-3 text-sm text-gray-400 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isLearning ? 'bg-yellow-400 animate-pulse' : 'bg-green-500'}`}></div>
          <span>{isLearning ? 'Learning...' : 'Ready'}</span>
        </div>
        <div className="text-xs font-mono">
          v0.1.0-alpha • Neural Audio Engine
        </div>
      </div>
    </div>
  );
}
