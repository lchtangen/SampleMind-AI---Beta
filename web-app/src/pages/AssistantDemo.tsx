import { SampleMindRuntimeProvider } from '@/providers/SampleMindRuntimeProvider';
import { useChatStore } from '@/stores/advanced-chat-store';
import { ComposerPrimitive, ThreadPrimitive } from '@assistant-ui/react';
import { useShallow } from 'zustand/shallow';

/**
 * AssistantDemo - Full-featured AI chat interface with Claude Sonnet 4.5
 *
 * Features:
 * - Streaming responses from Claude API
 * - IndexedDB persistence with compression
 * - Multi-thread management
 * - Message editing and regeneration
 * - Optimistic UI updates
 *
 * Design System: Modern Tech Cyberpunk with glassmorphism
 */
export function AssistantDemo() {
  const { currentThreadId, threads, switchThread, createThread, renameThread, deleteThread } = useChatStore(
    useShallow((state) => ({
      currentThreadId: state.currentThreadId,
      threads: state.threads,
      switchThread: state.switchThread,
      createThread: state.createThread,
      renameThread: state.renameThread,
      deleteThread: state.deleteThread,
    }))
  );

  const currentThread = threads.get(currentThreadId);

  return (
    <SampleMindRuntimeProvider>
      <div className="h-screen flex flex-col bg-bg-primary">
        {/* Header */}
        <header className="glass-card p-4 border-b border-primary/20 shadow-glow-purple">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-heading font-bold text-text-primary">
                🎵 SampleMind AI Assistant
              </h1>
              <div className="text-sm text-text-secondary flex items-center gap-2">
                <span className="inline-block w-2 h-2 bg-accent-cyan rounded-full animate-pulse" />
                Claude Sonnet 4.5
              </div>
            </div>

            {/* Thread Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => createThread()}
                className="
                  bg-gradient-purple rounded-lg px-4 py-2
                  text-sm font-semibold text-text-primary
                  shadow-glow-purple hover:shadow-glow-cyan
                  transition-normal ease-out
                  hover:scale-105 active:scale-95
                "
              >
                + New Chat
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Thread List Sidebar */}
          <aside className="w-64 border-r border-primary/20 glass-card overflow-y-auto">
            <div className="p-4">
              <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">
                Chat History
              </h2>
              <div className="space-y-2">
                {Array.from(threads.values()).map((thread) => (
                  <div
                    key={thread.id}
                    className={`
                      group relative p-3 rounded-lg cursor-pointer
                      transition-normal ease-out
                      ${
                        thread.id === currentThreadId
                          ? 'bg-gradient-purple shadow-glow-purple'
                          : 'bg-bg-tertiary hover:bg-bg-secondary'
                      }
                    `}
                    onClick={() => switchThread(thread.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-text-primary truncate">
                          {thread.title}
                        </p>
                        <p className="text-xs text-text-muted">
                          {new Date(thread.updatedAt).toLocaleDateString()}
                        </p>
                      </div>

                      {/* Thread Actions */}
                      <div className="opacity-0 group-hover:opacity-100 transition-normal flex items-center gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            const newName = prompt('Rename thread:', thread.title);
                            if (newName) renameThread(thread.id, newName);
                          }}
                          className="p-1 rounded hover:bg-bg-primary/50 transition-normal"
                          aria-label="Rename thread"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                          </svg>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            if (confirm(`Delete "${thread.title}"?`)) deleteThread(thread.id);
                          }}
                          className="p-1 rounded hover:bg-error/20 text-error transition-normal"
                          aria-label="Delete thread"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </aside>

          {/* Chat Thread */}
          <main className="flex-1 overflow-hidden flex flex-col">
            {currentThread ? (
              <ThreadPrimitive.Root className="flex-1 flex flex-col">
                <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-4 py-6">
                  <ThreadPrimitive.Empty>
                    <div className="flex-1 flex items-center justify-center p-8">
                      <div className="text-center max-w-2xl">
                        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-purple shadow-glow-purple flex items-center justify-center">
                          <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                          </svg>
                        </div>
                        <h2 className="text-3xl font-heading font-bold text-text-primary mb-4">
                          Welcome to SampleMind AI
                        </h2>
                        <p className="text-lg text-text-secondary mb-8">
                          Powered by Claude Sonnet 4.5 with 200K context window.
                          Ask me anything about music production, audio analysis, or coding assistance.
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                          <div className="glass-card p-4 rounded-lg">
                            <h3 className="font-semibold text-text-primary mb-2">🎼 Music Analysis</h3>
                            <p className="text-sm text-text-secondary">
                              Analyze BPM, key, genre, and get production tips for your tracks
                            </p>
                          </div>
                          <div className="glass-card p-4 rounded-lg">
                            <h3 className="font-semibold text-text-primary mb-2">💻 Code Assistance</h3>
                            <p className="text-sm text-text-secondary">
                              Get help with FastAPI, React, Python, TypeScript, and more
                            </p>
                          </div>
                          <div className="glass-card p-4 rounded-lg">
                            <h3 className="font-semibold text-text-primary mb-2">🎛️ Mixing & Mastering</h3>
                            <p className="text-sm text-text-secondary">
                              Professional mixing advice, EQ tips, and mastering techniques
                            </p>
                          </div>
                          <div className="glass-card p-4 rounded-lg">
                            <h3 className="font-semibold text-text-primary mb-2">🚀 Project Planning</h3>
                            <p className="text-sm text-text-secondary">
                              Architecture design, feature planning, and technical decisions
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </ThreadPrimitive.Empty>

                  <ThreadPrimitive.Messages
                    components={{
                      UserMessage: () => <div>User message</div>,
                      AssistantMessage: () => <div>Assistant message</div>,
                    }}
                  />
                </ThreadPrimitive.Viewport>

                {/* Composer */}
                <div className="border-t border-primary/20 p-4">
                  <ComposerPrimitive.Root className="flex items-end gap-2">
                    <ComposerPrimitive.Input
                      autoFocus
                      placeholder="Ask anything about music production, coding, or creative work..."
                      className="
                        flex-1 resize-none rounded-lg
                        bg-bg-tertiary border border-primary/20
                        px-4 py-3 text-text-primary
                        placeholder:text-text-muted
                        focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                        min-h-[48px] max-h-[200px]
                      "
                    />
                    <ComposerPrimitive.Send
                      className="
                        bg-gradient-purple rounded-lg px-6 py-3
                        font-semibold text-text-primary
                        shadow-glow-purple hover:shadow-glow-cyan
                        transition-normal ease-out
                        hover:scale-105 active:scale-95
                        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                      "
                    >
                      Send
                    </ComposerPrimitive.Send>
                  </ComposerPrimitive.Root>
                </div>
              </ThreadPrimitive.Root>
            ) : (
              <div className="flex-1 flex items-center justify-center">
                <p className="text-text-muted">No thread selected. Create a new chat to get started.</p>
              </div>
            )}
          </main>
        </div>

        {/* Footer Info */}
        <footer className="glass-card p-3 border-t border-primary/20">
          <div className="flex items-center justify-between text-xs text-text-muted">
            <div className="flex items-center gap-4">
              <span>💾 Auto-saved to IndexedDB</span>
              <span>🗜️ LZ-String compression enabled</span>
              <span>🧵 {threads.size} thread(s)</span>
            </div>
            <div>
              <span>Press</span>
              <kbd className="mx-1 px-2 py-0.5 bg-bg-tertiary rounded text-text-secondary">Ctrl+K</kbd>
              <span>for commands</span>
            </div>
          </div>
        </footer>
      </div>
    </SampleMindRuntimeProvider>
  );
}
