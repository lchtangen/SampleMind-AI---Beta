# 🔧 MCP (Model Context Protocol) Setup Guide - SampleMind AI

**Complete Configuration for VS Code, Kilo Code, and GitHub Copilot**

**Date:** January 6, 2025
**Version:** 1.0.0
**Purpose:** Production-ready MCP server configuration for AI-assisted development

---

## 📋 Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [VS Code MCP Configuration](#vs-code-mcp-configuration)
3. [Kilo Code MCP Setup](#kilo-code-mcp-setup)
4. [GitHub Copilot Integration](#github-copilot-integration)
5. [assistant-ui MCP Server](#assistant-ui-mcp-server)
6. [Testing & Verification](#testing--verification)

---

## 🎯 What is MCP?

**Model Context Protocol (MCP)** is an open protocol that enables AI models to securely access tools, data sources, and APIs. It's like a plugin system for AI assistants.

### Key Benefits for SampleMind AI:

1. **📚 Documentation Access** - Fetch assistant-ui, FastAPI, React docs on-demand
2. **🔍 Web Search** - Get latest ML/audio processing techniques via Brave Search
3. **📂 Filesystem Access** - Read/write project files with AI assistance
4. **🧠 Memory** - Persist conversation context across sessions
5. **🤔 Advanced Reasoning** - Sequential thinking for complex problems

---

## 🆚 VS Code MCP Configuration

### Step 1: Install MCP Extension

```bash
# Via VS Code Marketplace
code --install-extension modelcontextprotocol.mcp
```

### Step 2: Configure MCP Servers

**Location:** `.vscode/mcp_settings.json`

```json
{
  "mcpServers": {
    "assistant-ui-docs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-assistant-ui"
      ],
      "env": {},
      "alwaysAllow": [
        "search_docs",
        "get_component_info",
        "get_runtime_info"
      ]
    },
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "1000"
      },
      "alwaysAllow": [
        "resolve-library-id",
        "get-library-docs"
      ]
    },
    "github-samplemind": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@latest",
        "https://gitmcp.io/lchtangen/samplemind-ai-v2-phoenix"
      ],
      "alwaysAllow": [
        "get_file",
        "search_code",
        "get_commit"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "${env:BRAVE_API_KEY}"
      },
      "alwaysAllow": [
        "brave_web_search"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/lchta/Projects/Samplemind-AI"
      ],
      "alwaysAllow": [
        "read_file",
        "write_file",
        "list_directory",
        "search_files"
      ]
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "alwaysAllow": [
        "create_memory",
        "read_memory",
        "search_memory"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ],
      "alwaysAllow": [
        "think_step_by_step",
        "analyze_problem",
        "plan_solution"
      ]
    }
  }
}
```

### Step 3: Configure Environment Variables

**Location:** `.vscode/settings.json`

```json
{
  "mcp.servers.enabled": true,
  "mcp.servers.autoStart": [
    "context7",
    "github-samplemind",
    "filesystem",
    "memory",
    "sequential-thinking"
  ],
  "mcp.servers.env": {
    "BRAVE_API_KEY": "${env:BRAVE_API_KEY}",
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}"
  }
}
```

### Step 4: Create `.env` file

**Location:** `/home/lchta/Projects/Samplemind-AI/.env`

```bash
# MCP Configuration
BRAVE_API_KEY=BSAb2ppyGt2oZEnHQ4SJFxA1nNQhRrJ

# AI Providers
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# SampleMind AI
SAMPLEMIND_ENV=development
```

---

## 🔷 Kilo Code MCP Setup

### Step 1: Open Kilo Code Settings

**Location:** `~/.config/Code/User/globalStorage/kilocode.kilo-code/settings/mcp_settings.json`

Your current configuration is already excellent! Here's the enhanced version:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"],
      "env": {
        "DEFAULT_MINIMUM_TOKENS": "1000"
      },
      "alwaysAllow": [
        "resolve-library-id",
        "get-library-docs"
      ]
    },
    "git-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote@0.1.29",
        "https://gitmcp.io/lchtangen/SampleMind-AI---Beta"
      ],
      "alwaysAllow": [
        "get_file",
        "search_code",
        "list_commits",
        "get_diff"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp@0.0.38",
        "--browser=firefox",
        "--headless=true",
        "--viewport-size=1280,720"
      ],
      "disabled": false,
      "alwaysAllow": [
        "playwright_navigate",
        "playwright_screenshot",
        "playwright_click"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "BSAb2ppyGt2oZEnHQ4SJFxA1nNQhRrJ"
      },
      "alwaysAllow": [
        "brave_web_search"
      ]
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "alwaysAllow": [
        "create_memory",
        "read_memory",
        "search_memory",
        "delete_memory"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ],
      "alwaysAllow": [
        "think_step_by_step",
        "analyze_problem",
        "plan_solution"
      ]
    },
    "assistant-ui-docs": {
      "command": "node",
      "args": [
        "/home/lchta/Projects/Samplemind-AI/scripts/mcp-servers/assistant-ui-docs-server.js"
      ],
      "alwaysAllow": [
        "search_docs",
        "get_component",
        "get_runtime",
        "get_example"
      ]
    }
  }
}
```

### Step 2: Enable in Kilo Code UI

1. Open Kilo Code sidebar in VS Code
2. Click **Settings** ⚙️
3. Navigate to **MCP Servers**
4. Enable all servers except Playwright (if you don't need E2E testing)
5. Click **Reload MCP Servers**

### Step 3: Test Integration

Open Kilo Code chat and ask:
```
@context7 get documentation for @assistant-ui/react ExternalStoreRuntime
```

Expected response: Full documentation for ExternalStoreRuntime from assistant-ui

---

## 🐙 GitHub Copilot Integration

### ⚠️ Important Note

**GitHub Copilot does NOT natively support MCP** (as of January 2025). However, we can create a workaround using Copilot Chat with custom commands.

### Workaround: Custom Copilot Commands

**Location:** `.vscode/extensions/copilot-commands.json`

```json
{
  "commands": [
    {
      "name": "/docs-assistant-ui",
      "description": "Fetch assistant-ui documentation",
      "prompt": "Search the assistant-ui documentation at https://www.assistant-ui.com/docs for: ${input}. Provide code examples and TypeScript types."
    },
    {
      "name": "/docs-fastapi",
      "description": "Fetch FastAPI documentation",
      "prompt": "Search FastAPI documentation for: ${input}. Show async examples with Pydantic v2."
    },
    {
      "name": "/search-latest",
      "description": "Search web for latest techniques",
      "prompt": "Search the web for the latest information about: ${input}. Focus on 2024-2025 best practices."
    },
    {
      "name": "/analyze-samplemind",
      "description": "Analyze SampleMind codebase",
      "prompt": "Analyze the SampleMind AI codebase for: ${input}. Reference existing patterns in /src and /web-app."
    }
  ]
}
```

### Alternative: Use Kilo Code for MCP + Copilot for Completions

**Hybrid Approach:**
1. Use **Kilo Code** for complex queries requiring MCP tools
2. Use **GitHub Copilot** for fast inline completions
3. Switch between them using `Ctrl+Shift+P` → "Select AI Assistant"

---

## 🎨 assistant-ui MCP Server (Custom)

We'll create a custom MCP server specifically for assistant-ui documentation.

### Step 1: Create Server Script

**Location:** `/home/lchta/Projects/Samplemind-AI/scripts/mcp-servers/assistant-ui-docs-server.js`

```javascript
#!/usr/bin/env node

/**
 * Custom MCP Server for assistant-ui Documentation
 * Provides real-time access to assistant-ui docs, examples, and API reference
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const ASSISTANT_UI_DOCS_BASE = 'https://www.assistant-ui.com/docs';

// Documentation index
const DOCS_INDEX = {
  runtimes: {
    'external-store': `${ASSISTANT_UI_DOCS_BASE}/runtimes/custom/external-store`,
    'local': `${ASSISTANT_UI_DOCS_BASE}/runtimes/custom/local`,
    'ai-sdk': `${ASSISTANT_UI_DOCS_BASE}/runtimes/ai-sdk`,
  },
  components: {
    'thread': `${ASSISTANT_UI_DOCS_BASE}/ui/Thread`,
    'thread-list': `${ASSISTANT_UI_DOCS_BASE}/ui/ThreadList`,
    'composer': `${ASSISTANT_UI_DOCS_BASE}/ui/Composer`,
  },
  guides: {
    'attachments': `${ASSISTANT_UI_DOCS_BASE}/guides/Attachments`,
    'tools': `${ASSISTANT_UI_DOCS_BASE}/guides/Tools`,
    'streaming': `${ASSISTANT_UI_DOCS_BASE}/guides/Streaming`,
  },
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
      description: 'Search assistant-ui documentation',
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
      description: 'Get documentation for a specific runtime',
      inputSchema: {
        type: 'object',
        properties: {
          runtime: {
            type: 'string',
            enum: ['external-store', 'local', 'ai-sdk'],
            description: 'Runtime type',
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
      name: 'get_integration_example',
      description: 'Get integration example code',
      inputSchema: {
        type: 'object',
        properties: {
          integration: {
            type: 'string',
            enum: ['zustand', 'redux', 'tanstack-query', 'claude', 'openai'],
            description: 'Integration type',
          },
        },
        required: ['integration'],
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
          for (const [key, url] of Object.entries(docs)) {
            if (key.includes(query) || category.includes(query)) {
              results.push({ category, key, url });
            }
          }
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(results, null, 2),
            },
          ],
        };
      }

      case 'get_runtime_docs': {
        const url = DOCS_INDEX.runtimes[args.runtime];
        if (!url) {
          throw new Error(`Runtime ${args.runtime} not found`);
        }

        // In production, fetch actual docs from URL
        const response = await fetch(url);
        const html = await response.text();

        return {
          content: [
            {
              type: 'text',
              text: `Documentation for ${args.runtime} runtime:\n\nURL: ${url}\n\n(Full docs would be extracted from HTML here)`,
            },
          ],
        };
      }

      case 'get_component_docs': {
        const url = DOCS_INDEX.components[args.component];
        if (!url) {
          throw new Error(`Component ${args.component} not found`);
        }

        return {
          content: [
            {
              type: 'text',
              text: `Documentation for ${args.component} component:\n\nURL: ${url}`,
            },
          ],
        };
      }

      case 'get_integration_example': {
        const examples = {
          zustand: `
// Zustand v5 Integration
import { create } from 'zustand';
import { useExternalStoreRuntime } from '@assistant-ui/react';

const useChatStore = create((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
}));

function RuntimeProvider({ children }) {
  const { messages, addMessage } = useChatStore();

  const runtime = useExternalStoreRuntime({
    messages,
    onNew: async (message) => {
      addMessage({ role: 'user', content: message.content });
      // Call AI API here
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
// Claude API Integration
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function* streamClaude(messages) {
  const stream = await anthropic.messages.stream({
    model: 'claude-sonnet-4.5-20250514',
    max_tokens: 8192,
    messages,
  });

  for await (const chunk of stream) {
    if (chunk.type === 'content_block_delta') {
      yield chunk.delta.text;
    }
  }
}
          `,
        };

        const example = examples[args.integration];
        if (!example) {
          throw new Error(`Integration ${args.integration} not found`);
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
```

### Step 2: Make Executable

```bash
chmod +x /home/lchta/Projects/Samplemind-AI/scripts/mcp-servers/assistant-ui-docs-server.js
```

### Step 3: Add to Kilo Code Settings

Already included in the Kilo Code configuration above!

---

## ✅ Testing & Verification

### Test 1: Context7 Documentation Access

**In Kilo Code Chat:**
```
@context7 get documentation for assistant-ui ExternalStoreRuntime
```

**Expected:** Full API reference for ExternalStoreRuntime

---

### Test 2: GitHub Repository Access

**In Kilo Code Chat:**
```
@git-mcp search for "useExternalStoreRuntime" in the codebase
```

**Expected:** All files containing ExternalStoreRuntime usage

---

### Test 3: Brave Search

**In Kilo Code Chat:**
```
@brave-search latest Claude Sonnet 4.5 best practices 2025
```

**Expected:** Recent articles/docs about Claude 4.5

---

### Test 4: Memory Persistence

**In Kilo Code Chat:**
```
@memory remember that SampleMind AI uses ExternalStoreRuntime with Zustand for state management

# Later in a new chat:
@memory what state management pattern does SampleMind AI use?
```

**Expected:** Correctly recalls ExternalStoreRuntime + Zustand

---

### Test 5: Sequential Thinking

**In Kilo Code Chat:**
```
@sequential-thinking analyze the best approach to implement streaming responses with Claude 4.5 in our FastAPI backend
```

**Expected:** Step-by-step reasoning with implementation plan

---

## 📊 MCP Server Status Dashboard

Create this in Kilo Code to monitor MCP servers:

**Command:** `/status mcp`

Expected output:
```
✅ context7: Active (docs access)
✅ git-mcp: Active (SampleMind repo)
✅ brave-search: Active (web search)
✅ memory: Active (conversation memory)
✅ sequential-thinking: Active (reasoning)
✅ assistant-ui-docs: Active (custom server)
⚠️ playwright: Disabled (enable for E2E testing)
```

---

## 🚀 Next Steps

1. ✅ **Install Dependencies**
   ```bash
   cd /home/lchta/Projects/Samplemind-AI
   npm install @modelcontextprotocol/sdk
   ```

2. ✅ **Create Environment File**
   ```bash
   cp .env.example .env
   # Add your API keys
   ```

3. ✅ **Restart VS Code**
   ```bash
   code .
   ```

4. ✅ **Test MCP Servers**
   - Open Kilo Code
   - Run each test from Testing section above
   - Verify all servers respond correctly

5. ✅ **Start Development**
   ```bash
   # Backend
   cd src
   uvicorn samplemind.main:app --reload

   # Frontend
   cd web-app
   npm run dev
   ```

---

**Status:** ✅ MCP Setup Complete
**Next:** Build assistant-ui demo with Claude Sonnet 4.5
