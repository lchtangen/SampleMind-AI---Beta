/**
 * Chat Primitive Components
 * Composable, unstyled primitives for building AI chat interfaces
 * Inspired by assistant-ui and Radix UI architecture
 */

import { ChatMessage, MessagePart, useChatStore } from '@/stores/chat-store';
import React, { createContext, ReactNode, useContext } from 'react';

// ============================================================================
// Context
// ============================================================================

interface ChatContextValue {
  threadId: string | null;
  isRunning: boolean;
}

const ChatContext = createContext<ChatContextValue | null>(null);

const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('Chat primitives must be used within ChatPrimitive.Root');
  }
  return context;
};

// ============================================================================
// Root Component
// ============================================================================

interface ChatRootProps {
  children: ReactNode;
  className?: string;
}

const ChatRoot: React.FC<ChatRootProps> = ({ children, className }) => {
  const currentThread = useChatStore((state) => state.currentThread);

  const contextValue: ChatContextValue = {
    threadId: currentThread?.id || null,
    isRunning: currentThread?.isRunning || false,
  };

  return (
    <ChatContext.Provider value={contextValue}>
      <div className={className} data-chat-root>
        {children}
      </div>
    </ChatContext.Provider>
  );
};

// ============================================================================
// Messages Component
// ============================================================================

interface MessagesProps {
  className?: string;
  components?: {
    Message?: React.ComponentType<{ message: ChatMessage }>;
    UserMessage?: React.ComponentType<{ message: ChatMessage }>;
    AssistantMessage?: React.ComponentType<{ message: ChatMessage }>;
  };
}

const Messages: React.FC<MessagesProps> = ({ className, components }) => {
  const messages = useChatStore((state) => state.currentThread?.messages || []);

  const MessageComponent = components?.Message;
  const UserMessageComponent = components?.UserMessage;
  const AssistantMessageComponent = components?.AssistantMessage;

  return (
    <div className={className} data-chat-messages>
      {messages.map((message) => {
        if (MessageComponent) {
          return <MessageComponent key={message.id} message={message} />;
        }

        if (message.role === 'user' && UserMessageComponent) {
          return <UserMessageComponent key={message.id} message={message} />;
        }

        if (message.role === 'assistant' && AssistantMessageComponent) {
          return <AssistantMessageComponent key={message.id} message={message} />;
        }

        return (
          <div key={message.id} data-message-role={message.role}>
            {message.parts.map((part, idx) => (
              <div key={idx}>{part.content}</div>
            ))}
          </div>
        );
      })}
    </div>
  );
};

// ============================================================================
// Message Component
// ============================================================================

interface MessageContextValue {
  message: ChatMessage;
}

const MessageContext = createContext<MessageContextValue | null>(null);

const useMessageContext = () => {
  const context = useContext(MessageContext);
  if (!context) {
    throw new Error('Message primitives must be used within MessagePrimitive.Root');
  }
  return context;
};

interface MessageRootProps {
  message: ChatMessage;
  children: ReactNode;
  className?: string;
}

const MessageRoot: React.FC<MessageRootProps> = ({ message, children, className }) => {
  return (
    <MessageContext.Provider value={{ message }}>
      <div
        className={className}
        data-message-id={message.id}
        data-message-role={message.role}
        data-message-status={message.status}
      >
        {children}
      </div>
    </MessageContext.Provider>
  );
};

// ============================================================================
// Message Parts Component
// ============================================================================

interface MessagePartsProps {
  className?: string;
  components?: {
    Text?: React.ComponentType<{ content: string; part: MessagePart }>;
    Audio?: React.ComponentType<{ content: string; part: MessagePart }>;
    Code?: React.ComponentType<{ content: string; part: MessagePart }>;
    ToolCall?: React.ComponentType<{ content: string; part: MessagePart }>;
    ToolResult?: React.ComponentType<{ content: string; part: MessagePart }>;
  };
}

const MessageParts: React.FC<MessagePartsProps> = ({ className, components }) => {
  const { message } = useMessageContext();

  return (
    <div className={className} data-message-parts>
      {message.parts.map((part, idx) => {
        const Component = components?.[
          part.type.charAt(0).toUpperCase() +
          part.type.slice(1).replace(/-./g, (m) => m[1].toUpperCase()) as keyof typeof components
        ];

        if (Component) {
          return <Component key={idx} content={part.content} part={part} />;
        }

        return (
          <div key={idx} data-part-type={part.type}>
            {part.content}
          </div>
        );
      })}
    </div>
  );
};

// ============================================================================
// Composer Component
// ============================================================================

interface ComposerRootProps {
  children: ReactNode;
  className?: string;
  onSubmit?: (content: string) => void;
}

const ComposerRoot: React.FC<ComposerRootProps> = ({ children, className, onSubmit }) => {
  const sendMessage = useChatStore((state) => state.sendMessage);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const content = formData.get('message') as string;

    if (content.trim()) {
      if (onSubmit) {
        onSubmit(content);
      } else {
        sendMessage(content);
      }
      e.currentTarget.reset();
    }
  };

  return (
    <form onSubmit={handleSubmit} className={className} data-composer-root>
      {children}
    </form>
  );
};

interface ComposerInputProps {
  className?: string;
  placeholder?: string;
  disabled?: boolean;
}

const ComposerInput: React.FC<ComposerInputProps> = ({
  className,
  placeholder = 'Type a message...',
  disabled
}) => {
  const isStreaming = useChatStore((state) => state.isStreaming);

  return (
    <input
      name="message"
      type="text"
      className={className}
      placeholder={placeholder}
      disabled={disabled || isStreaming}
      data-composer-input
      autoComplete="off"
    />
  );
};

interface ComposerSendProps {
  className?: string;
  children?: ReactNode;
  disabled?: boolean;
}

const ComposerSend: React.FC<ComposerSendProps> = ({ className, children, disabled }) => {
  const isStreaming = useChatStore((state) => state.isStreaming);

  return (
    <button
      type="submit"
      className={className}
      disabled={disabled || isStreaming}
      data-composer-send
    >
      {children || 'Send'}
    </button>
  );
};

// ============================================================================
// Thread Switcher Components
// ============================================================================

interface ThreadListProps {
  className?: string;
  children?: ReactNode;
}

const ThreadList: React.FC<ThreadListProps> = ({ className, children }) => {
  const threads = useChatStore((state) => state.threads);

  if (children) {
    return <div className={className} data-thread-list>{children}</div>;
  }

  return (
    <div className={className} data-thread-list>
      {threads.map((thread) => (
        <div key={thread.id} data-thread-id={thread.id}>
          {thread.title}
        </div>
      ))}
    </div>
  );
};

interface ThreadItemProps {
  threadId: string;
  className?: string;
  children?: ReactNode;
}

const ThreadItem: React.FC<ThreadItemProps> = ({ threadId, className, children }) => {
  const selectThread = useChatStore((state) => state.selectThread);
  const currentThread = useChatStore((state) => state.currentThread);
  const isActive = currentThread?.id === threadId;

  return (
    <div
      className={className}
      data-thread-id={threadId}
      data-active={isActive}
      onClick={() => selectThread(threadId)}
    >
      {children}
    </div>
  );
};

// ============================================================================
// Conditional Rendering Components
// ============================================================================

interface IfProps {
  condition: boolean;
  children: ReactNode;
}

const If: React.FC<IfProps> = ({ condition, children }) => {
  return condition ? <>{children}</> : null;
};

const Empty: React.FC<{ children: ReactNode; className?: string }> = ({ children, className }) => {
  const messages = useChatStore((state) => state.currentThread?.messages || []);

  return messages.length === 0 ? (
    <div className={className} data-chat-empty>
      {children}
    </div>
  ) : null;
};

// ============================================================================
// Exports
// ============================================================================

export const ChatPrimitive = {
  Root: ChatRoot,
  Messages,
  Empty,
  If,
};

export const MessagePrimitive = {
  Root: MessageRoot,
  Parts: MessageParts,
};

export const ComposerPrimitive = {
  Root: ComposerRoot,
  Input: ComposerInput,
  Send: ComposerSend,
};

export const ThreadPrimitive = {
  List: ThreadList,
  Item: ThreadItem,
};
