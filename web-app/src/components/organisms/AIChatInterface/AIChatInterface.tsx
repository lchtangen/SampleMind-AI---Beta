/**
 * AI Chat Interface - Cyberpunk/Neon Styled
 * Uses Chat Primitives with SampleMind AI design system
 */

import { ChatPrimitive, ComposerPrimitive, MessagePrimitive } from '@/components/primitives/chat';
import { ChatMessage } from '@/stores/chat-store';
import { motion } from 'framer-motion';
import React from 'react';

// ============================================================================
// Message Components
// ============================================================================

const UserMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  return (
    <MessagePrimitive.Root message={message}>
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-end mb-4"
      >
        <div className="max-w-[80%] rounded-xl bg-gradient-to-br from-primary/20 to-primary/10 border border-primary/30 p-4 shadow-glow-purple">
          <MessagePrimitive.Parts
            components={{
              Text: ({ content }) => (
                <p className="text-text-primary text-base leading-relaxed">
                  {content}
                </p>
              ),
            }}
          />
          <div className="mt-2 flex items-center gap-2 text-xs text-text-muted">
            <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
            {message.status === 'sent' && (
              <svg className="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </div>
        </div>
      </motion.div>
    </MessagePrimitive.Root>
  );
};

const AssistantMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isStreaming = message.status === 'streaming';

  return (
    <MessagePrimitive.Root message={message}>
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex justify-start mb-4"
      >
        <div className="max-w-[80%] rounded-xl glass-card border border-accent-cyan/20 p-4 shadow-glow-cyan">
          <div className="flex items-start gap-3">
            {/* AI Avatar */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent-cyan to-primary flex items-center justify-center shadow-glow-cyan flex-shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>

            {/* Message Content */}
            <div className="flex-1">
              <MessagePrimitive.Parts
                components={{
                  Text: ({ content }) => (
                    <div className="prose prose-invert prose-purple max-w-none">
                      <p className="text-text-primary text-base leading-relaxed m-0">
                        {content}
                      </p>
                    </div>
                  ),
                  Code: ({ content }) => (
                    <pre className="bg-bg-tertiary rounded-lg p-3 overflow-x-auto">
                      <code className="text-accent-cyan text-sm font-code">
                        {content}
                      </code>
                    </pre>
                  ),
                }}
              />

              {isStreaming && (
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-2 h-2 rounded-full bg-accent-cyan"
                        animate={{
                          scale: [1, 1.2, 1],
                          opacity: [0.5, 1, 0.5],
                        }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          delay: i * 0.2,
                        }}
                      />
                    ))}
                  </div>
                  <span className="text-xs text-text-muted">Thinking...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </MessagePrimitive.Root>
  );
};

// ============================================================================
// Empty State
// ============================================================================

const EmptyState: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full py-12">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary to-accent-cyan flex items-center justify-center shadow-glow-purple">
          <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h3 className="text-2xl font-heading font-bold text-text-primary mb-2">
          Start a Conversation
        </h3>
        <p className="text-text-secondary max-w-md">
          Ask me about audio analysis, mixing tips, or production techniques. I'm here to help elevate your music!
        </p>
      </motion.div>
    </div>
  );
};

// ============================================================================
// Main AI Chat Component
// ============================================================================

export const AIChatInterface: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <ChatPrimitive.Root className={`flex flex-col h-full ${className}`}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <ChatPrimitive.Empty>
          <EmptyState />
        </ChatPrimitive.Empty>

        <ChatPrimitive.Messages
          components={{
            UserMessage,
            AssistantMessage,
          }}
        />
      </div>

      {/* Composer Area */}
      <div className="border-t border-border-subtle bg-bg-secondary/50 backdrop-blur-md p-4">
        <ComposerPrimitive.Root className="flex items-end gap-3">
          {/* Input */}
          <div className="flex-1 relative">
            <ComposerPrimitive.Input
              placeholder="Ask about audio analysis, mixing tips, or music theory..."
              className="w-full px-4 py-3 pr-12 rounded-xl bg-bg-tertiary border border-border-subtle text-text-primary placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/50 focus:outline-none transition-normal"
            />

            {/* Attachment Button (placeholder) */}
            <button
              type="button"
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 rounded-lg hover:bg-bg-primary transition-normal text-text-muted hover:text-text-primary"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>
          </div>

          {/* Send Button */}
          <ComposerPrimitive.Send className="px-6 py-3 rounded-xl bg-gradient-to-r from-primary to-accent-cyan text-white font-semibold shadow-glow-purple hover:shadow-glow-cyan transition-normal hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </ComposerPrimitive.Send>
        </ComposerPrimitive.Root>
      </div>
    </ChatPrimitive.Root>
  );
};

export default AIChatInterface;
