/**
 * AI Chat Store
 * Zustand store for managing AI chat state with DevTools
 * Based on assistant-ui architecture pattern
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export type MessageRole = 'user' | 'assistant' | 'system';
export type MessageStatus = 'sending' | 'sent' | 'error' | 'streaming';

export interface MessagePart {
  type: 'text' | 'audio' | 'code' | 'tool-call' | 'tool-result';
  content: string;
  metadata?: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  parts: MessagePart[];
  status: MessageStatus;
  timestamp: Date;
  metadata?: {
    model?: string;
    tokens?: number;
    duration?: number;
  };
}

export interface Thread {
  id: string;
  title: string;
  messages: ChatMessage[];
  isRunning: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  // Current thread
  currentThread: Thread | null;
  threads: Thread[];

  // UI State
  isStreaming: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  createThread: (title?: string) => void;
  selectThread: (threadId: string) => void;
  sendMessage: (content: string, parts?: MessagePart[]) => void;
  appendMessagePart: (messageId: string, part: MessagePart) => void;
  updateMessageStatus: (messageId: string, status: MessageStatus) => void;
  deleteThread: (threadId: string) => void;
  clearError: () => void;
  resetChat: () => void;
}

const createEmptyThread = (title?: string): Thread => ({
  id: crypto.randomUUID(),
  title: title || 'New Chat',
  messages: [],
  isRunning: false,
  createdAt: new Date(),
  updatedAt: new Date(),
});

export const useChatStore = create<ChatState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        currentThread: null,
        threads: [],
        isStreaming: false,
        isLoading: false,
        error: null,

        // Create new thread
        createThread: (title) => {
          const newThread = createEmptyThread(title);
          set((state) => ({
            threads: [newThread, ...state.threads],
            currentThread: newThread,
          }), false, 'createThread');
        },

        // Select existing thread
        selectThread: (threadId) => {
          const thread = get().threads.find((t) => t.id === threadId);
          if (thread) {
            set({ currentThread: thread }, false, 'selectThread');
          }
        },

        // Send message
        sendMessage: (content, parts = []) => {
          const { currentThread } = get();

          if (!currentThread) {
            get().createThread();
            return get().sendMessage(content, parts);
          }

          const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'user',
            parts: parts.length > 0 ? parts : [{ type: 'text', content }],
            status: 'sent',
            timestamp: new Date(),
          };

          const assistantMessage: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            parts: [],
            status: 'streaming',
            timestamp: new Date(),
          };

          set((state) => ({
            currentThread: state.currentThread ? {
              ...state.currentThread,
              messages: [...state.currentThread.messages, userMessage, assistantMessage],
              isRunning: true,
              updatedAt: new Date(),
            } : state.currentThread,
            isStreaming: true,
          }), false, 'sendMessage');
        },

        // Append message part (for streaming)
        appendMessagePart: (messageId, part) => {
          set((state) => {
            if (!state.currentThread) return state;

            const updatedMessages = state.currentThread.messages.map((msg) =>
              msg.id === messageId
                ? { ...msg, parts: [...msg.parts, part] }
                : msg
            );

            return {
              currentThread: {
                ...state.currentThread,
                messages: updatedMessages,
                updatedAt: new Date(),
              },
            };
          }, false, 'appendMessagePart');
        },

        // Update message status
        updateMessageStatus: (messageId, status) => {
          set((state) => {
            if (!state.currentThread) return state;

            const updatedMessages = state.currentThread.messages.map((msg) =>
              msg.id === messageId ? { ...msg, status } : msg
            );

            const isRunning = updatedMessages.some((msg) => msg.status === 'streaming');

            return {
              currentThread: {
                ...state.currentThread,
                messages: updatedMessages,
                isRunning,
                updatedAt: new Date(),
              },
              isStreaming: isRunning,
            };
          }, false, 'updateMessageStatus');
        },

        // Delete thread
        deleteThread: (threadId) => {
          set((state) => {
            const filteredThreads = state.threads.filter((t) => t.id !== threadId);
            const newCurrentThread = state.currentThread?.id === threadId
              ? filteredThreads[0] || null
              : state.currentThread;

            return {
              threads: filteredThreads,
              currentThread: newCurrentThread,
            };
          }, false, 'deleteThread');
        },

        // Clear error
        clearError: () => set({ error: null }, false, 'clearError'),

        // Reset entire chat
        resetChat: () => set({
          currentThread: null,
          threads: [],
          isStreaming: false,
          isLoading: false,
          error: null,
        }, false, 'resetChat'),
      }),
      {
        name: 'samplemind-chat-storage',
        partialize: (state) => ({
          threads: state.threads,
          currentThread: state.currentThread,
        }),
      }
    )
  )
);

// Selectors for optimized re-renders
export const useChatMessages = () => useChatStore((state) => state.currentThread?.messages || []);
export const useIsStreaming = () => useChatStore((state) => state.isStreaming);
export const useCurrentThread = () => useChatStore((state) => state.currentThread);
export const useThreads = () => useChatStore((state) => state.threads);
