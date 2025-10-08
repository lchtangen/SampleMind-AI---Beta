#!/usr/bin/env node

/**
 * Anthropic (Claude) MCP Server
 * Provides Model Context Protocol interface for Claude models
 * Specialized in production coaching, creative suggestions, and music theory
 *
 * Models:
 * - Claude Sonnet 4.5 (Default): Best for standard production workflows, mixing advice, creative suggestions
 *   Context: 200K tokens, Fast responses, Excellent music production knowledge
 * - Claude Opus 4.1 (Complex): Best for deep music theory analysis, complex arrangements, advanced composition
 *   Context: 200K tokens, Highest quality reasoning, Superior creative capabilities
 */

const Anthropic = require('@anthropic-ai/sdk');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

// Configuration from environment
const API_KEY = process.env.ANTHROPIC_API_KEY;
// Use Sonnet 4.5 for standard tasks, Opus 4.1 for complex reasoning
const MODEL = process.env.MODEL || 'claude-4-sonnet-20250514'; // Latest: Claude Sonnet 4.5 (Oct 2025)
const OPUS_MODEL = 'claude-4-opus-20250514'; // For complex music theory and composition
const MAX_TOKENS = parseInt(process.env.MAX_TOKENS || '8192');
const TEMPERATURE = parseFloat(process.env.TEMPERATURE || '0.7');

if (!API_KEY) {
  console.error('Error: ANTHROPIC_API_KEY environment variable is required');
  process.exit(1);
}

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: API_KEY,
});

// Create MCP server
const server = new Server(
  {
    name: 'anthropic-claude',
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

// Helper function to select appropriate model based on task complexity
function selectModel(taskType) {
  // Use Opus 4.1 for complex reasoning tasks
  const complexTasks = ['music_theory_analysis', 'advanced_composition', 'complex_arrangement'];
  return complexTasks.includes(taskType) ? OPUS_MODEL : MODEL;
}

// Tool: Generate text completion
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'generate_text') {
    try {
      const message = await anthropic.messages.create({
        model: MODEL, // Use Sonnet 4.5 for standard text generation
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
            text: message.content[0].text,
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

  if (name === 'production_coaching') {
    try {
      const prompt = `As an expert music producer and FL Studio specialist, provide detailed production coaching for this audio:

${args.audioPath || 'Audio file provided'}
${args.context || ''}

Focus on:
1. Mix quality and balance
2. Sound design recommendations
3. Arrangement improvements
4. Genre-specific production techniques
5. FL Studio workflow optimization tips
6. Creative enhancement suggestions

Provide actionable, specific advice that a producer can immediately implement.`;

      const message = await anthropic.messages.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: TEMPERATURE,
        messages: [
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
            text: message.content[0].text,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error providing coaching: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === 'music_theory_analysis') {
    try {
      const prompt = `As a music theory expert, analyze this audio for:

${args.audioPath || 'Audio file provided'}
${args.context || ''}

Provide detailed analysis of:
1. Harmonic progression and chord analysis
2. Melodic contour and intervals
3. Rhythmic patterns and time signatures
4. Scales and modes used
5. Tension and resolution points
6. Suggestions for harmonic development
7. Modal interchange opportunities

Present the analysis in a clear, educational format.`;

      const message = await anthropic.messages.create({
        model: OPUS_MODEL, // Use Opus 4.1 for complex music theory analysis
        max_tokens: MAX_TOKENS,
        temperature: TEMPERATURE,
        messages: [
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
            text: message.content[0].text,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error analyzing music theory: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  if (name === 'creative_suggestions') {
    try {
      const prompt = `As a creative music production consultant, provide innovative suggestions for:

${args.audioPath || 'Audio file provided'}
${args.style || 'the current production'}
${args.context || ''}

Generate creative ideas for:
1. Unique sound design elements
2. Unconventional arrangement approaches
3. Genre-bending fusion ideas
4. Experimental processing techniques
5. Mood and atmosphere enhancements
6. Surprise elements and ear candy
7. Bridge and transition ideas

Be bold and inspiring while remaining practical.`;

      const message = await anthropic.messages.create({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        temperature: 0.9, // Higher temperature for creativity
        messages: [
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
            text: message.content[0].text,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error generating creative suggestions: ${error.message}`,
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
        description: 'Generate text completion using Claude',
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
        name: 'production_coaching',
        description: 'Get expert production coaching and FL Studio optimization tips',
        inputSchema: {
          type: 'object',
          properties: {
            audioPath: {
              type: 'string',
              description: 'Path to the audio file',
            },
            context: {
              type: 'string',
              description: 'Additional context about the production',
            },
          },
        },
      },
      {
        name: 'music_theory_analysis',
        description: 'Deep music theory analysis with educational insights',
        inputSchema: {
          type: 'object',
          properties: {
            audioPath: {
              type: 'string',
              description: 'Path to the audio file',
            },
            context: {
              type: 'string',
              description: 'Additional context',
            },
          },
        },
      },
      {
        name: 'creative_suggestions',
        description: 'Get innovative creative suggestions for production',
        inputSchema: {
          type: 'object',
          properties: {
            audioPath: {
              type: 'string',
              description: 'Path to the audio file',
            },
            style: {
              type: 'string',
              description: 'Desired style or genre',
            },
            context: {
              type: 'string',
              description: 'Additional context',
            },
          },
        },
      },
    ],
  };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Anthropic (Claude) MCP server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
