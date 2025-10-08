#!/usr/bin/env node

/**
 * Google AI (Gemini) MCP Server
 * Provides Model Context Protocol interface for Gemini models
 *
 * Model: Gemini 2.5 Pro (Latest stable release)
 * - Best for: Fast audio analysis, genre classification, batch processing
 * - Context Window: 2M tokens (upgraded from 1M)
 * - Reasoning: Advanced multimodal understanding, optimized for speed
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

// Configuration from environment
const API_KEY = process.env.GOOGLE_AI_API_KEY;
const MODEL = process.env.MODEL || 'gemini-2.5-pro'; // Latest: Gemini 2.5 Pro (2M context)
const MAX_TOKENS = parseInt(process.env.MAX_TOKENS || '8192');
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '0.7');

if (!API_KEY) {
  console.error('Error: GOOGLE_AI_API_KEY environment variable is required');
  process.exit(1);
}

// Initialize Google AI client
const genAI = new GoogleGenerativeAI(API_KEY);

// Create MCP server
const server = new Server(
  {
    name: 'google-ai-gemini',
    version: '1.0.0',
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
      const model = genAI.getGenerativeModel({
        model: MODEL,
        generationConfig: {
          maxOutputTokens: MAX_TOKENS,
          temperature: TEMPERATURE,
        }
      });

      const result = await model.generateContent(args.prompt);
      const response = await result.response;
      const text = response.text();

      return {
        content: [
          {
            type: 'text',
            text: text,
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

  if (name === 'analyze_audio') {
    try {
      const model = genAI.getGenerativeModel({ model: MODEL });

      const prompt = `Analyze this audio file for music production insights:
${args.audioPath}

Provide:
1. Genre classification
2. BPM detection
3. Key detection
4. Mood analysis
5. Production recommendations`;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();

      return {
        content: [
          {
            type: 'text',
            text: text,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error analyzing audio: ${error.message}`,
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
        description: 'Generate text completion using Gemini',
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
        name: 'analyze_audio',
        description: 'Analyze audio file for music production insights',
        inputSchema: {
          type: 'object',
          properties: {
            audioPath: {
              type: 'string',
              description: 'Path to the audio file to analyze',
            },
          },
          required: ['audioPath'],
        },
      },
    ],
  };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Google AI (Gemini) MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
