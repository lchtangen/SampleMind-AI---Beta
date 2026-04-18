'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Square,
  Trash2,
  Bot,
  User,
  Sparkles,
  Loader2,
} from 'lucide-react';
import { useCopilotChat, type ChatMessage } from '@/hooks/useCopilotChat';
import { cn } from '@/lib/utils';

export default function CopilotPage() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { messages, isLoading, sendMessage, stopStreaming, clearChat } =
    useCopilotChat({ preferFast: false });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const suggestions = [
    'Find dark trap kicks above 140 BPM',
    'Analyze the frequency spectrum of my latest upload',
    'Create a chill lo-fi playlist from my library',
    'What samples are similar to my favorite 808?',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Audio Copilot</h1>
            <p className="text-xs text-white/50">
              AI-powered music production assistant
            </p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="p-2 rounded-lg text-white/40 hover:text-white/80 hover:bg-white/5 transition-colors"
          title="Clear chat"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4 scrollbar-thin scrollbar-thumb-white/10">
        {messages.length === 0 && (
          <EmptyState suggestions={suggestions} onSelect={(s) => sendMessage(s)} />
        )}

        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="relative mt-2">
        <div className="flex items-end gap-2 p-3 rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl focus-within:border-violet-500/50 transition-colors">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your samples, search your library, get mixing advice..."
            rows={1}
            className="flex-1 bg-transparent text-white placeholder:text-white/30 resize-none focus:outline-none text-sm max-h-32"
            style={{
              height: 'auto',
              minHeight: '1.5rem',
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 128) + 'px';
            }}
          />
          {isLoading ? (
            <button
              type="button"
              onClick={stopStreaming}
              className="p-2 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
            >
              <Square className="h-4 w-4" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className={cn(
                'p-2 rounded-xl transition-all',
                input.trim()
                  ? 'bg-violet-500 text-white hover:bg-violet-400 shadow-lg shadow-violet-500/25'
                  : 'bg-white/5 text-white/20'
              )}
            >
              <Send className="h-4 w-4" />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className={cn('flex gap-3', isUser ? 'justify-end' : 'justify-start')}
    >
      {!isUser && (
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500/20 to-cyan-500/20 border border-white/10 flex items-center justify-center flex-shrink-0">
          <Sparkles className="h-4 w-4 text-violet-400" />
        </div>
      )}

      <div
        className={cn(
          'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
          isUser
            ? 'bg-violet-500/20 border border-violet-500/30 text-white'
            : 'bg-white/5 border border-white/10 text-white/90'
        )}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        {message.isStreaming && (
          <span className="inline-block w-2 h-4 bg-violet-400 animate-pulse ml-0.5 rounded-sm" />
        )}
      </div>

      {isUser && (
        <div className="h-8 w-8 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center flex-shrink-0">
          <User className="h-4 w-4 text-white/70" />
        </div>
      )}
    </motion.div>
  );
}

function EmptyState({
  suggestions,
  onSelect,
}: {
  suggestions: string[];
  onSelect: (s: string) => void;
}) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-16">
      <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 border border-white/10 flex items-center justify-center mb-6">
        <Bot className="h-8 w-8 text-violet-400" />
      </div>
      <h2 className="text-xl font-bold text-white mb-2">Audio Copilot</h2>
      <p className="text-white/50 text-sm mb-8 text-center max-w-md">
        Your AI-powered music production assistant. Search samples, analyze audio,
        get mixing advice, and curate playlists — all through natural conversation.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg w-full">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => onSelect(s)}
            className="text-left px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-white/70 text-sm hover:bg-white/10 hover:text-white hover:border-violet-500/30 transition-all"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
