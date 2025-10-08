/**
 * SampleMind AI - ExternalStoreRuntime Provider with Claude Sonnet 4.5
 * Production-ready assistant-ui integration
 */

import { useChatStore } from '@/stores/advanced-chat-store';
import {
    AssistantRuntimeProvider,
    useExternalStoreRuntime,
    type AppendMessage,
    type ThreadMessageLike,
} from '@assistant-ui/react';
import { useCallback } from 'react';
import { useShallow } from 'zustand/shallow';

// Backend API endpoint
const API_ENDPOINT = '/api/assistant/chat';

// ============================================================================
// Runtime Provider Component
// ============================================================================

export function SampleMindRuntimeProvider({ children }: { children: React.ReactNode }) {
  // Get store state with useShallow to prevent unnecessary re-renders
  const { messages, isRunning, addMessage, setMessages, setIsRunning } = useChatStore(
    useShallow((state) => ({
      messages: state.messages,
      isRunning: state.isRunning,
      addMessage: state.addMessage,
      setMessages: state.setMessages,
      setIsRunning: state.setIsRunning,
    }))
  );

  // ============================================================================
  // Handler: New Message (User Input)
  // ============================================================================

  const handleNew = useCallback(
    async (message: AppendMessage) => {
      // Add user message
      const userMessage: ThreadMessageLike = {
        role: 'user',
        content: message.content,
        id: `msg-${Date.now()}`,
        createdAt: new Date(),
      };
      addMessage(userMessage);

      // Start AI response
      setIsRunning(true);

      try {
        // Prepare messages for API
        const apiMessages = [...messages, userMessage].map((msg) => ({
          role: msg.role,
          content: Array.isArray(msg.content)
            ? msg.content
                .filter((part) => part.type === 'text')
                .map((part) => part.text)
                .join('\n')
            : msg.content,
        }));

        // Call Claude API with streaming
        const response = await fetch(API_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: apiMessages,
            model: 'claude-sonnet-4.5-20250514',
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        if (!response.body) {
          throw new Error('Response body is null');
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantText = '';
        const assistantId = `msg-${Date.now()}-assistant`;

        // Create initial assistant message
        const assistantMessage: ThreadMessageLike = {
          role: 'assistant',
          content: [{ type: 'text', text: '' }],
          id: assistantId,
          createdAt: new Date(),
        };
        addMessage(assistantMessage);

        // Stream response chunks
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('0:"')) {
              // Text delta
              const text = line.slice(3, -1); // Remove 0:" and trailing "
              assistantText += text.replace(/\\n/g, '\n').replace(/\\"/g, '"');

              // Update message in store
              const updatedMessages = messages
                .concat([userMessage])
                .concat([assistantMessage])
                .map((msg) =>
                  msg.id === assistantId
                    ? {
                        ...msg,
                        content: [{ type: 'text' as const, text: assistantText }],
                      }
                    : msg
                );
              setMessages(updatedMessages as ThreadMessageLike[]);
            } else if (line.startsWith('e:')) {
              // Event (finish or error)
              const eventData = JSON.parse(line.slice(2));
              if (eventData.type === 'finish') {
                console.log('Stream finished:', eventData.usage);
              } else if (eventData.type === 'error') {
                console.error('Stream error:', eventData.error);
                throw new Error(eventData.error);
              }
            }
          }
        }
      } catch (error) {
        console.error('AI response error:', error);

        // Add error message
        addMessage({
          role: 'assistant',
          content: [
            {
              type: 'text',
              text: `❌ Error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
            },
          ],
          id: `msg-${Date.now()}-error`,
          createdAt: new Date(),
        });
      } finally {
        setIsRunning(false);
      }
    },
    [messages, addMessage, setMessages, setIsRunning]
  );

  // ============================================================================
  // Handler: Edit Message
  // ============================================================================

  const handleEdit = useCallback(
    async (message: AppendMessage) => {
      const index = messages.findIndex((m) => m.id === message.parentId);
      if (index === -1) return;

      // Keep messages up to the parent
      const newMessages = messages.slice(0, index + 1);

      // Add edited message
      const editedMessage: ThreadMessageLike = {
        role: 'user',
        content: message.content,
        id: `msg-${Date.now()}-edit`,
        createdAt: new Date(),
      };
      newMessages.push(editedMessage);
      setMessages(newMessages);

      // Regenerate AI response
      setIsRunning(true);

      try {
        const apiMessages = newMessages.map((msg) => ({
          role: msg.role,
          content: Array.isArray(msg.content)
            ? msg.content
                .filter((part) => part.type === 'text')
                .map((part) => part.text)
                .join('\n')
            : msg.content,
        }));

        const response = await fetch(API_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: apiMessages,
            model: 'claude-sonnet-4.5-20250514',
            stream: false,
          }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();

        newMessages.push({
          role: 'assistant',
          content: [{ type: 'text', text: data.content }],
          id: `msg-${Date.now()}-assistant`,
          createdAt: new Date(),
        });
        setMessages(newMessages);
      } catch (error) {
        console.error('Edit regeneration error:', error);
      } finally {
        setIsRunning(false);
      }
    },
    [messages, setMessages, setIsRunning]
  );

  // ============================================================================
  // Handler: Reload Message
  // ============================================================================

  const handleReload = useCallback(
    async (parentId: string | null) => {
      const index = parentId ? messages.findIndex((m) => m.id === parentId) : messages.length - 1;
      const historyMessages = messages.slice(0, index + 1);

      setIsRunning(true);

      try {
        const apiMessages = historyMessages.map((msg) => ({
          role: msg.role,
          content: Array.isArray(msg.content)
            ? msg.content
                .filter((part) => part.type === 'text')
                .map((part) => part.text)
                .join('\n')
            : msg.content,
        }));

        const response = await fetch(API_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: apiMessages,
            model: 'claude-sonnet-4.5-20250514',
            stream: false,
          }),
        });

        if (!response.ok) {
          throw new Error(`API error: ${response.statusText}`);
        }

        const data = await response.json();

        setMessages([
          ...historyMessages,
          {
            role: 'assistant',
            content: [{ type: 'text', text: data.content }],
            id: `msg-${Date.now()}-reload`,
            createdAt: new Date(),
          },
        ]);
      } catch (error) {
        console.error('Reload error:', error);
      } finally {
        setIsRunning(false);
      }
    },
    [messages, setMessages, setIsRunning]
  );

  // ============================================================================
  // Create Runtime
  // ============================================================================

  const runtime = useExternalStoreRuntime({
    messages,
    isRunning,
    setMessages: (msgs) => setMessages(Array.from(msgs)),
    convertMessage: (msg) => msg, // Already in ThreadMessageLike format
    onNew: handleNew,
    onEdit: handleEdit,
    onReload: handleReload,
  });

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>;
}
