#!/usr/bin/env node

/**
 * OpenAI (GPT-5) MCP Server
 * Provides Model Context Protocol interface for OpenAI models
 * General-purpose fallback provider for code generation and debugging
 *
 * Models:
 * - GPT-5 (Default): Latest flagship model with superior reasoning and coding capabilities
 *   Context: 256K tokens (2x increase), Best for complex code generation
 * - GPT-4.5 Turbo (Fallback): Fast, cost-effective for standard tasks
 *   Context: 192K tokens, Excellent code quality, 50% faster than GPT-4
 */

const OpenAI = require('openai');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

// Configuration from environment
const API_KEY = process.env.OPENAI_API_KEY;
const MODEL = process.env.MODEL || 'gpt-5'; // Latest: GPT-5 with 256K context
const TURBO_MODEL = 'gpt-4.5-turbo'; // Fast fallback: GPT-4.5 Turbo
const MAX_TOKENS = parseInt(process.env.MAX_TOKENS || '4096');
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '0.7');

if (!API_KEY) {
  console.error('Error: OPENAI_API_KEY environment variable is required');
  process.exit(1);
}

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: API_KEY,
});

// Create MCP server
const server = new Server(
  {
    name: 'openai-gpt5', // Updated to reflect GPT-5
    version: '2.0.0', // Bumped version for major model upgrade
  },
  {
    capabilities: {
      tools: {},
      prompts: {},
      resources: {},
    },
  }
);

// Tool: Generate text completion
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'generate_text') {
    try {
      const completion = await openai.chat.completions.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: TEMPERATURE,
        messages: [
          {
            role: 'user',
            content: args.prompt,
          },
        ],
      });

      return {
        content: [
          {
            type: 'text',
            text: completion.choices[0].message.content,
          },
        ],
      };
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
  }

  if (name === 'code_generation') {
    try {
      const prompt = `Generate high-quality, production-ready code for:

${args.description}

Requirements:
- Language: ${args.language || 'Python'}
- Follow best practices and design patterns
- Include error handling
- Add comprehensive documentation
- Write clean, maintainable code
${args.additionalRequirements || ''}

Provide the complete, working code.`;

      const completion = await openai.chat.completions.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: 0.3, // Lower temperature for code
        messages: [
          {
            role: 'system',
            content: 'You are an expert software engineer who writes clean, efficient, well-documented code.',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      return {
        content: [
          {
            type: 'text',
            text: completion.choices[0].message.content,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error generating code: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === 'debug_assistance') {
    try {
      const prompt = `Help debug this issue:

Problem Description:
${args.problem}

Code/Context:
${args.code || 'No code provided'}

Error Message:
${args.error || 'No error message'}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Potential fixes with code examples
4. Prevention strategies for similar issues`;

      const completion = await openai.chat.completions.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: TEMPERATURE,
        messages: [
          {
            role: 'system',
            content: 'You are an expert debugger who systematically identifies and resolves software issues.',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      return {
        content: [
          {
            type: 'text',
            text: completion.choices[0].message.content,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error providing debug assistance: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === 'general_query') {
    try {
      const completion = await openai.chat.completions.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: TEMPERATURE,
        messages: [
          {
            role: 'system',
            content: args.systemPrompt || 'You are a helpful AI assistant.',
          },
          {
            role: 'user',
            content: args.query,
          },
        ],
      });

      return {
        content: [
          {
            type: 'text',
            text: completion.choices[0].message.content,
          },
        ],
      };
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
  }

  return {
    content: [
      {
        type: 'text',
        text: `Unknown tool: ${name}`,
      },
    ],
    isError: true,
  };
});

// List available tools
server.setRequestHandler('tools/list', async () => {
  return {
    tools: [
      {
        name: 'generate_text',
        description: 'Generate text completion using GPT-4',
        inputSchema: {
          type: 'object',
          properties: {
            prompt: {
              type: 'string',
              description: 'The prompt to generate text from',
            },
          },
          required: ['prompt'],
        },
      },
      {
        name: 'code_generation',
        description: 'Generate production-ready code with best practices',
        inputSchema: {
          type: 'object',
          properties: {
            description: {
              type: 'string',
              description: 'Description of the code to generate',
            },
            language: {
              type: 'string',
              description: 'Programming language (default: Python)',
            },
            additionalRequirements: {
              type: 'string',
              description: 'Additional requirements or constraints',
            },
          },
          required: ['description'],
        },
      },
      {
        name: 'debug_assistance',
        description: 'Get debugging help and root cause analysis',
        inputSchema: {
          type: 'object',
          properties: {
            problem: {
              type: 'string',
              description: 'Description of the problem',
            },
            code: {
              type: 'string',
              description: 'Relevant code snippet',
            },
            error: {
              type: 'string',
              description: 'Error message or stack trace',
            },
          },
          required: ['problem'],
        },
      },
      {
        name: 'general_query',
        description: 'Handle general-purpose queries and fallback requests',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'The query to process',
            },
            systemPrompt: {
              type: 'string',
              description: 'Optional system prompt to set context',
            },
          },
          required: ['query'],
        },
      },
    ],
  };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('OpenAI (GPT-4) MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
