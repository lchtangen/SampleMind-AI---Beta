/**
 * SampleMind AI - Advanced ExternalStoreRuntime Setup
 * Production-ready integration with assistant-ui, Zustand v5, IndexedDB, and Claude Sonnet 4.5
 */

import type { ThreadMessageLike } from '@assistant-ui/react';
import { del as idbDel, entries as idbEntries, get as idbGet, set as idbSet } from 'idb-keyval';
import LZString from 'lz-string';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// ============================================================================
// Types & Interfaces
// ============================================================================

export interface Thread {
  id: string;
  title: string;
  archived: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  // Current thread state
  messages: ThreadMessageLike[];
  isRunning: boolean;
  currentThreadId: string;

  // Thread management
  threads: Map<string, Thread>;

  // assistant-ui integration methods
  addMessage: (message: ThreadMessageLike) => void;
  setMessages: (messages: ThreadMessageLike[]) => void;
  setIsRunning: (isRunning: boolean) => void;
  updateMessage: (id: string, updates: Partial<ThreadMessageLike>) => void;

  // Multi-thread management
  switchThread: (threadId: string) => Promise<void>;
  createThread: (title?: string) => string;
  renameThread: (threadId: string, newTitle: string) => void;
  archiveThread: (threadId: string) => void;
  unarchiveThread: (threadId: string) => void;
  deleteThread: (threadId: string) => Promise<void>;

  // Persistence
  saveToIndexedDB: () => Promise<void>;
  loadFromIndexedDB: (threadId: string) => Promise<void>;
  loadAllThreads: () => Promise<void>;
  clearOldMessages: (daysToKeep?: number) => Promise<void>;
}

// ============================================================================
// Storage Keys
// ============================================================================

const THREAD_LIST_KEY = 'samplemind-thread-list';
const threadMessagesKey = (threadId: string) => `samplemind-thread-${threadId}`;
const threadMetadataKey = (threadId: string) => `samplemind-thread-meta-${threadId}`;

// ============================================================================
// Zustand Store with Advanced Persistence
// ============================================================================

export const useChatStore = create<ChatState>()(
  immer(
    devtools(
      (set, get) => ({
        // Initial state
        messages: [],
        isRunning: false,
        currentThreadId: 'default',
        threads: new Map([
          ['default', {
            id: 'default',
            title: 'New Chat',
            archived: false,
            createdAt: new Date(),
            updatedAt: new Date(),
          }],
        ]),

        // ====================================================================
        // assistant-ui Integration Methods
        // ====================================================================

        addMessage: (message) =>
          set((state) => {
            state.messages.push(message);
            state.threads.get(state.currentThreadId)!.updatedAt = new Date();
            get().saveToIndexedDB();
          }),

        setMessages: (messages) =>
          set((state) => {
            state.messages = messages;
            state.threads.get(state.currentThreadId)!.updatedAt = new Date();
            get().saveToIndexedDB();
          }),

        setIsRunning: (isRunning) =>
          set((state) => {
            state.isRunning = isRunning;
          }),

        updateMessage: (id, updates) =>
          set((state) => {
            const index = state.messages.findIndex((m) => m.id === id);
            if (index !== -1) {
              Object.assign(state.messages[index], updates);
              get().saveToIndexedDB();
            }
          }),

        // ====================================================================
        // Multi-Thread Management
        // ====================================================================

        switchThread: async (threadId) => {
          const { threads, currentThreadId } = get();

          if (threadId === currentThreadId) return;

          // Save current thread before switching
          await get().saveToIndexedDB();

          // Load new thread
          await get().loadFromIndexedDB(threadId);

          set((state) => {
            state.currentThreadId = threadId;
          });
        },

        createThread: (title = 'New Chat') => {
          const newId = `thread-${Date.now()}`;
          const newThread: Thread = {
            id: newId,
            title,
            archived: false,
            createdAt: new Date(),
            updatedAt: new Date(),
          };

          set((state) => {
            state.threads.set(newId, newThread);
          });

          // Save thread list to IndexedDB
          idbSet(THREAD_LIST_KEY, Array.from(get().threads.values()));

          return newId;
        },

        renameThread: (threadId, newTitle) => {
          set((state) => {
            const thread = state.threads.get(threadId);
            if (thread) {
              thread.title = newTitle;
              thread.updatedAt = new Date();
            }
          });

          // Save thread metadata
          const thread = get().threads.get(threadId);
          if (thread) {
            idbSet(threadMetadataKey(threadId), thread);
            idbSet(THREAD_LIST_KEY, Array.from(get().threads.values()));
          }
        },

        archiveThread: (threadId) => {
          set((state) => {
            const thread = state.threads.get(threadId);
            if (thread) {
              thread.archived = true;
              thread.updatedAt = new Date();
            }
          });

          const thread = get().threads.get(threadId);
          if (thread) {
            idbSet(threadMetadataKey(threadId), thread);
            idbSet(THREAD_LIST_KEY, Array.from(get().threads.values()));
          }
        },

        unarchiveThread: (threadId) => {
          set((state) => {
            const thread = state.threads.get(threadId);
            if (thread) {
              thread.archived = false;
              thread.updatedAt = new Date();
            }
          });

          const thread = get().threads.get(threadId);
          if (thread) {
            idbSet(threadMetadataKey(threadId), thread);
            idbSet(THREAD_LIST_KEY, Array.from(get().threads.values()));
          }
        },

        deleteThread: async (threadId) => {
          if (threadId === 'default') {
            console.warn('Cannot delete default thread');
            return;
          }

          // Delete from IndexedDB
          await idbDel(threadMessagesKey(threadId));
          await idbDel(threadMetadataKey(threadId));

          set((state) => {
            state.threads.delete(threadId);

            // Switch to default if deleting current thread
            if (state.currentThreadId === threadId) {
              state.currentThreadId = 'default';
              state.messages = [];
            }
          });

          // Update thread list
          await idbSet(THREAD_LIST_KEY, Array.from(get().threads.values()));

          // Load default thread if we switched to it
          if (get().currentThreadId === 'default') {
            await get().loadFromIndexedDB('default');
          }
        },

        // ====================================================================
        // Persistence with IndexedDB & Compression
        // ====================================================================

        saveToIndexedDB: async () => {
          const { currentThreadId, messages, threads } = get();

          try {
            // Compress messages for storage efficiency
            const messagesJSON = JSON.stringify(messages);
            const compressed = LZString.compressToUTF16(messagesJSON);

            // Save messages
            await idbSet(threadMessagesKey(currentThreadId), {
              messages,
              compressed,
              timestamp: Date.now(),
            });

            // Update thread metadata
            const thread = threads.get(currentThreadId);
            if (thread) {
              thread.updatedAt = new Date();
              await idbSet(threadMetadataKey(currentThreadId), thread);
            }

            // Save thread list
            await idbSet(THREAD_LIST_KEY, Array.from(threads.values()));
          } catch (error) {
            console.error('Failed to save to IndexedDB:', error);
          }
        },

        loadFromIndexedDB: async (threadId) => {
          try {
            const threadData = await idbGet<{
              messages: ThreadMessageLike[];
              compressed: string;
              timestamp: number;
            }>(threadMessagesKey(threadId));

            if (threadData) {
              set((state) => {
                state.messages = threadData.messages || [];
              });
            } else {
              // No saved data, initialize empty
              set((state) => {
                state.messages = [];
              });
            }
          } catch (error) {
            console.error('Failed to load from IndexedDB:', error);
            set((state) => {
              state.messages = [];
            });
          }
        },

        loadAllThreads: async () => {
          try {
            const savedThreads = await idbGet<Thread[]>(THREAD_LIST_KEY);

            if (savedThreads && savedThreads.length > 0) {
              set((state) => {
                state.threads = new Map(savedThreads.map((t) => [t.id, t]));
              });
            }
          } catch (error) {
            console.error('Failed to load threads:', error);
          }
        },

        clearOldMessages: async (daysToKeep = 30) => {
          try {
            const cutoffDate = Date.now() - daysToKeep * 24 * 60 * 60 * 1000;
            const allEntries = await idbEntries();

            for (const [key, value] of allEntries) {
              if (
                typeof key === 'string' &&
                key.startsWith('samplemind-thread-') &&
                typeof value === 'object' &&
                value !== null &&
                'timestamp' in value &&
                typeof value.timestamp === 'number' &&
                value.timestamp < cutoffDate
              ) {
                await idbDel(key);
              }
            }
          } catch (error) {
            console.error('Failed to clear old messages:', error);
          }
        },
      }),
      {
        name: 'SampleMind-Chat-Store',
        enabled: process.env.NODE_ENV === 'development',
      }
    )
  )
);

// ============================================================================
// Initialization
// ============================================================================

// Load all threads on first render
useChatStore.getState().loadAllThreads().then(() => {
  // Load current thread messages
  const currentThreadId = useChatStore.getState().currentThreadId;
  useChatStore.getState().loadFromIndexedDB(currentThreadId);
});

// Auto-cleanup old messages every 24 hours
if (typeof window !== 'undefined') {
  setInterval(() => {
    useChatStore.getState().clearOldMessages(30);
  }, 24 * 60 * 60 * 1000);
}
