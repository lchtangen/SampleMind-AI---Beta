import React from 'react';
import { AudioAnalysisPanel } from './AudioAnalysisPanel';
import { AudioAnalysisProvider } from '../../contexts/AudioAnalysisContext';

export const AnalysisLayout: React.FC = () => {
  return (
    <div className="flex-1 flex flex-col h-full">
      <div className="p-6 flex-1 overflow-hidden">
        <div className="h-full bg-cyber-glass-darker/50 rounded-2xl overflow-hidden border border-cyber-primary/10 shadow-2xl">
          <AudioAnalysisProvider>
            <AudioAnalysisPanel />
          </AudioAnalysisProvider>
        </div>
      </div>
    </div>
  );
};
