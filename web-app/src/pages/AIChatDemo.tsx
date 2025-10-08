/**
 * AI Chat Demo Page
 * Demonstrates the AI Chat Interface with cyberpunk styling
 */

import { AIChatInterface } from '@/components/organisms/AIChatInterface';
import { CyberpunkBackground } from '@/components/effects/CyberpunkBackground';
import { TitleBar } from '@/components/organisms/TitleBar';
import { useChatStore } from '@/stores/chat-store';
import React from 'react';

export const AIChatDemo: React.FC = () => {
  const createThread = useChatStore((state) => state.createThread);
  const currentThread = useChatStore((state) => state.currentThread);

  React.useEffect(() => {
    if (!currentThread) {
      createThread('Audio Production Assistant');
    }
  }, [currentThread, createThread]);

  return (
    <>
      <TitleBar />
      <CyberpunkBackground />
      <div className="min-h-screen p-8 pt-16">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
          <h1 className="text-4xl font-heading font-bold text-text-primary mb-2">
            🎵 SampleMind AI Assistant
          </h1>
          <p className="text-text-secondary">
            Your intelligent music production companion powered by AI
          </p>
        </div>

        {/* Chat Interface */}
        <div className="glass-card rounded-2xl border border-primary/20 shadow-glow-purple overflow-hidden h-[calc(100vh-200px)]">
          <AIChatInterface />
        </div>

        {/* Footer Info */}
        <div className="mt-4 text-center text-sm text-text-muted">
          <p>
            💡 Try asking: "Analyze this audio file" or "Give me mixing tips for vocals"
          </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default AIChatDemo;
