#!/usr/bin/env node

/**
 * Custom MCP Server for assistant-ui Documentation
 * Provides real-time access to assistant-ui docs, examples, and API reference
 *
 * Usage: Add to Kilo Code mcp_settings.json
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const ASSISTANT_UI_DOCS_BASE = 'https://www.assistant-ui.com/docs';

// Comprehensive documentation index
const DOCS_INDEX = {
  runtimes: {
    'external-store': {
      url: `${ASSISTANT_UI_DOCS_BASE}/runtimes/custom/external-store`,
      description: 'Full state control runtime with custom store integration',
      apis: ['useExternalStoreRuntime', 'ExternalStoreAdapter', 'convertMessage'],
    },
    'local': {
      url: `${ASSISTANT_UI_DOCS_BASE}/runtimes/custom/local`,
      description: 'Local-first runtime with built-in state management',
      apis: ['useLocalRuntime', 'LocalRuntimeOptions'],
    },
    'ai-sdk': {
      url: `${ASSISTANT_UI_DOCS_BASE}/runtimes/ai-sdk`,
      description: 'Vercel AI SDK integration runtime',
      apis: ['useAssistantRuntime', 'AssistantRuntimeProvider'],
    },
  },
  components: {
    'thread': {
      url: `${ASSISTANT_UI_DOCS_BASE}/ui/Thread`,
      description: 'Main chat thread component with message list and composer',
      props: ['runtime', 'className', 'components'],
    },
    'thread-list': {
      url: `${ASSISTANT_UI_DOCS_BASE}/ui/ThreadList`,
      description: 'Multi-thread management UI component',
      props: ['threads', 'onThreadSelect', 'onThreadCreate', 'onThreadDelete'],
    },
    'composer': {
      url: `${ASSISTANT_UI_DOCS_BASE}/ui/Composer`,
      description: 'Message input composer with attachments and send button',
      props: ['placeholder', 'onSend', 'allowAttachments'],
    },
  },
  guides: {
    'attachments': {
      url: `${ASSISTANT_UI_DOCS_BASE}/guides/Attachments`,
      description: 'File attachment handling and preview',
    },
    'tools': {
      url: `${ASSISTANT_UI_DOCS_BASE}/guides/Tools`,
      description: 'Tool/function calling integration',
    },
    'streaming': {
      url: `${ASSISTANT_UI_DOCS_BASE}/guides/Streaming`,
      description: 'Streaming response implementation',
    },
  },
};

// Example code templates
const EXAMPLES = {
  zustand: `
// Zustand v5 + ExternalStoreRuntime Integration
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { useExternalStoreRuntime } from '@assistant-ui/react';
import { ThreadMessageLike } from '@assistant-ui/react';

interface ChatStore {
  messages: ThreadMessageLike[];
  isRunning: boolean;
  addMessage: (message: ThreadMessageLike) => void;
  setMessages: (messages: ThreadMessageLike[]) => void;
  setIsRunning: (running: boolean) => void;
}

const useChatStore = create<ChatStore>()(
  immer((set) => ({
    messages: [],
    isRunning: false,
    addMessage: (message) =>
      set((state) => {
        state.messages.push(message);
      }),
    setMessages: (messages) =>
      set((state) => {
        state.messages = messages;
      }),
    setIsRunning: (running) =>
      set((state) => {
        state.isRunning = running;
      }),
  }))
);

function RuntimeProvider({ children }: { children: React.ReactNode }) {
  const { messages, isRunning, setMessages, setIsRunning } = useChatStore();

  const runtime = useExternalStoreRuntime({
    messages,
    isRunning,
    setMessages: (msgs) => setMessages(Array.from(msgs)),
    convertMessage: (msg) => msg,
    onNew: async (message) => {
      // Handle new user message
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ messages: [...messages, message] }),
      });
      // Stream response...
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {children}
    </AssistantRuntimeProvider>
  );
}
`,
  claude: `
// Claude Sonnet 4.5 Streaming Integration
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function* streamClaude(messages: { role: string; content: string }[]) {
  const stream = await anthropic.messages.stream({
    model: 'claude-sonnet-4.5-20250514',
    max_tokens: 8192,
    temperature: 0.7,
    messages: messages.map((msg) => ({
      role: msg.role === 'user' ? 'user' : 'assistant',
      content: msg.content,
    })),
  });

  for await (const chunk of stream) {
    if (chunk.type === 'content_block_delta') {
      yield chunk.delta.text || '';
    }
  }

  const final = await stream.finalMessage();
  return final;
}

// Usage in onNew handler
async function handleNew(message: AppendMessage) {
  setIsRunning(true);

  const assistantMessage: ThreadMessageLike = {
    id: \`msg-\${Date.now()}\`,
    role: 'assistant',
    content: [{ type: 'text', text: '' }],
    createdAt: new Date(),
  };

  addMessage(assistantMessage);

  let fullText = '';
  for await (const chunk of streamClaude([...messages, { role: 'user', content: message.content }])) {
    fullText += chunk;
    updateMessage(assistantMessage.id, {
      ...assistantMessage,
      content: [{ type: 'text', text: fullText }],
    });
  }

  setIsRunning(false);
}
`,
  persistence: `
// IndexedDB Persistence with Compression
import { get, set, del } from 'idb-keyval';
import { compress, decompress } from 'lz-string';

async function saveMessages(threadId: string, messages: ThreadMessageLike[]) {
  const compressed = compress(JSON.stringify(messages));
  await set(\`thread-\${threadId}\`, compressed);
}

async function loadMessages(threadId: string): Promise<ThreadMessageLike[]> {
  const compressed = await get<string>(\`thread-\${threadId}\`);
  if (!compressed) return [];

  const json = decompress(compressed);
  return JSON.parse(json || '[]');
}

// Auto-save on changes
useEffect(() => {
  if (messages.length > 0) {
    saveMessages(currentThreadId, messages);
  }
}, [messages, currentThreadId]);
`,
  fastapi: `
# FastAPI Streaming Endpoint
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from anthropic import AsyncAnthropic
import json
from typing import List, Dict

app = FastAPI()
anthropic = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def stream_response(messages: List[Dict[str, str]]):
    """Stream Claude responses in data stream protocol format"""
    try:
        async with anthropic.messages.stream(
            model="claude-sonnet-4.5-20250514",
            max_tokens=8192,
            messages=messages
        ) as stream:
            # Initial chunk
            yield '0:""\n'

            # Stream text deltas
            async for text in stream.text_stream:
                if text:
                    escaped = json.dumps(text)[1:-1]  # Remove quotes
                    yield f'0:"{escaped}"\n'

            # Finish event
            final_message = await stream.get_final_message()
            finish_data = {
                "type": "finish",
                "usage": {
                    "input_tokens": final_message.usage.input_tokens,
                    "output_tokens": final_message.usage.output_tokens
                }
            }
            yield f'e:{json.dumps(finish_data)}\n'

    except Exception as e:
        error_data = {"type": "error", "error": str(e)}
        yield f'e:{json.dumps(error_data)}\n'

@app.post("/api/assistant/chat")
async def chat_completion(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.messages),
        media_type="text/event-stream"
    )
`,
};

const server = new Server(
  {
    name: 'assistant-ui-docs',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'search_docs',
      description: 'Search assistant-ui documentation by keyword',
      inputSchema: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'Search query (e.g., "ExternalStoreRuntime", "streaming", "attachments")',
          },
        },
        required: ['query'],
      },
    },
    {
      name: 'get_runtime_docs',
      description: 'Get comprehensive documentation for a specific runtime',
      inputSchema: {
        type: 'object',
        properties: {
          runtime: {
            type: 'string',
            enum: ['external-store', 'local', 'ai-sdk'],
            description: 'Runtime type to fetch docs for',
          },
        },
        required: ['runtime'],
      },
    },
    {
      name: 'get_component_docs',
      description: 'Get documentation for a UI component',
      inputSchema: {
        type: 'object',
        properties: {
          component: {
            type: 'string',
            enum: ['thread', 'thread-list', 'composer'],
            description: 'Component name',
          },
        },
        required: ['component'],
      },
    },
    {
      name: 'get_example',
      description: 'Get code example for specific integration',
      inputSchema: {
        type: 'object',
        properties: {
          example: {
            type: 'string',
            enum: ['zustand', 'claude', 'persistence', 'fastapi'],
            description: 'Example type to retrieve',
          },
        },
        required: ['example'],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'search_docs': {
        const query = args.query.toLowerCase();
        const results = [];

        // Search through docs index
        for (const [category, docs] of Object.entries(DOCS_INDEX)) {
          for (const [key, data] of Object.entries(docs)) {
            const searchText = `${key} ${data.description || ''}`.toLowerCase();
            if (searchText.includes(query)) {
              results.push({
                category,
                name: key,
                url: data.url,
                description: data.description,
                apis: data.apis || [],
                props: data.props || [],
              });
            }
          }
        }

        if (results.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: `No documentation found for "${args.query}". Try: "ExternalStoreRuntime", "Thread", "streaming", "attachments"`,
              },
            ],
          };
        }

        return {
          content: [
            {
              type: 'text',
              text: `Found ${results.length} result(s) for "${args.query}":\n\n${JSON.stringify(results, null, 2)}`,
            },
          ],
        };
      }

      case 'get_runtime_docs': {
        const runtime = DOCS_INDEX.runtimes[args.runtime];
        if (!runtime) {
          throw new Error(`Runtime ${args.runtime} not found. Available: external-store, local, ai-sdk`);
        }

        return {
          content: [
            {
              type: 'text',
              text: `# ${args.runtime} Runtime\n\n${runtime.description}\n\n**Documentation URL:** ${runtime.url}\n\n**Key APIs:**\n${runtime.apis.map((api) => `- ${api}`).join('\n')}\n\n**Use Cases:**\n- ${args.runtime === 'external-store' ? 'Full state control with Zustand/Redux/Jotai' : ''}\n- ${args.runtime === 'local' ? 'Simple local-first apps with built-in state' : ''}\n- ${args.runtime === 'ai-sdk' ? 'Vercel AI SDK integration with streaming' : ''}`,
            },
          ],
        };
      }

      case 'get_component_docs': {
        const component = DOCS_INDEX.components[args.component];
        if (!component) {
          throw new Error(`Component ${args.component} not found. Available: thread, thread-list, composer`);
        }

        return {
          content: [
            {
              type: 'text',
              text: `# ${args.component} Component\n\n${component.description}\n\n**Documentation URL:** ${component.url}\n\n**Props:**\n${component.props.map((prop) => `- ${prop}`).join('\n')}\n\n**Example:**\n\`\`\`tsx\nimport { ${args.component === 'thread' ? 'Thread' : args.component === 'thread-list' ? 'ThreadList' : 'Composer'} } from '@assistant-ui/react';\n\n<${args.component === 'thread' ? 'Thread' : args.component === 'thread-list' ? 'ThreadList' : 'Composer'} />\n\`\`\``,
            },
          ],
        };
      }

      case 'get_example': {
        const example = EXAMPLES[args.example];
        if (!example) {
          throw new Error(`Example ${args.example} not found. Available: zustand, claude, persistence, fastapi`);
        }

        return {
          content: [
            {
              type: 'text',
              text: example.trim(),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('assistant-ui MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
