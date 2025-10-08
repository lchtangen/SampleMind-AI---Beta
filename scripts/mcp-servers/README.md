# SampleMind AI - MCP Server Integration

Model Context Protocol (MCP) servers for integrating multiple AI providers with VS Code and KiloCoder.

## Overview

This directory contains three MCP servers that provide seamless integration with VS Code using the latest and most advanced LLM versions:

1. **Google AI (Gemini 2.5 Pro)** - Primary provider for fast audio analysis and genre classification (2M context)
2. **Anthropic (Claude Sonnet 4.5 / Opus 4.1)** - Specialist for production coaching and creative suggestions (200K context)
   - Sonnet 4.5 for standard workflows, Opus 4.1 for complex music theory
3. **OpenAI (GPT-5 / GPT-4.5 Turbo)** - General-purpose fallback provider (256K context)
   - GPT-5 for complex tasks, GPT-4.5 Turbo for fast standard operations

## Architecture

```
┌─────────────────┐
│   VS Code UI    │
└────────┬────────┘
         │
         ├─────────────────────────────────────┐
         │                                     │
┌────────▼────────┐  ┌──────────▼──────────┐ │
│  GitHub Copilot │  │    KiloCoder        │ │
└────────┬────────┘  └──────────┬──────────┘ │
         │                      │             │
         └──────────┬───────────┘             │
                    │                         │
         ┌──────────▼──────────┐             │
         │   MCP Protocol      │             │
         └──────────┬──────────┘             │
                    │                         │
      ┌─────────────┼─────────────┐          │
      │             │             │          │
┌─────▼─────┐ ┌────▼─────┐ ┌────▼─────┐    │
│ Gemini    │ │  Claude  │ │  GPT-5   │    │
│ 2.5 Pro   │ │ Sonnet   │ │  Server  │    │
│ (2M ctx)  │ │ 4.5/Opus │ │ (256K)   │    │
└───────────┘ └──────────┘ └──────────┘    │
                                            │
```

## Installation

### 1. Install Dependencies

```bash
cd scripts/mcp-servers
npm install
```

This will install:
- `@google/generative-ai` - Google AI SDK
- `@anthropic-ai/sdk` - Anthropic Claude SDK
- `openai` - OpenAI SDK
- `@modelcontextprotocol/sdk` - MCP SDK

### 2. Configure Environment Variables

Ensure your `.env` file in the project root contains:

```env
# Google AI (Gemini) - PRIMARY
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Anthropic (Claude) - SPECIALIST
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenAI (GPT-4) - FALLBACK
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Verify VS Code Settings

Your settings.json should already be configured. To verify, check:
- `/home/lchta/.config/Code/User/settings.json`

## MCP Servers

### 1. Google AI (Gemini 2.5 Pro) Server

**File:** `google-ai-server.js`

**Model:** Gemini 2.5 Pro (2M token context window)

**Capabilities:**
- Fast audio analysis (2x faster than previous versions)
- Genre classification with enhanced accuracy
- High-throughput batch processing
- Real-time inference with massive context

**Available Tools:**
- `generate_text` - General text generation with 2M context
- `analyze_audio` - Audio file analysis with production insights

**Environment Variables:**
```bash
GOOGLE_AI_API_KEY=your_key
MODEL=gemini-2.5-pro
MAX_TOKENS=8192
TEMPERATURE=0.7
```

### 2. Anthropic (Claude Sonnet 4.5 / Opus 4.1) Server

**File:** `anthropic-server.js`

**Models:**
- **Claude Sonnet 4.5** (default, 200K context) - Standard production workflows
- **Claude Opus 4.1** (complex tasks, 200K context) - Advanced music theory and composition

**Capabilities:**
- Production coaching with enhanced reasoning
- Creative suggestions with deeper context understanding
- Deep music theory analysis (Opus 4.1)
- FL Studio optimization
- Intelligent model selection based on task complexity

**Available Tools:**
- `generate_text` - General text generation (Sonnet 4.5)
- `production_coaching` - Expert production advice (Sonnet 4.5)
- `music_theory_analysis` - Deep harmonic and melodic analysis (Opus 4.1)
- `creative_suggestions` - Innovative production ideas (Sonnet 4.5)

**Environment Variables:**
```bash
ANTHROPIC_API_KEY=your_key
MODEL=claude-sonnet-4.5
OPUS_MODEL=claude-opus-4.1
MAX_TOKENS=8192
TEMPERATURE=0.7
```

### 3. OpenAI (GPT-5 / GPT-4.5 Turbo) Server

**File:** `openai-server.js`

**Models:**
- **GPT-5** (default, 256K context) - Complex code generation and advanced reasoning
- **GPT-4.5 Turbo** (fallback, 192K context) - Fast standard tasks with cost efficiency

**Capabilities:**
- General-purpose assistance with enhanced reasoning
- Advanced code generation with deeper context
- Systematic debugging support
- Fast fallback handling (GPT-4.5 Turbo)

**Available Tools:**
- `generate_text` - General text generation (GPT-5)
- `code_generation` - Production-ready code creation (GPT-5)
- `debug_assistance` - Debugging help and analysis (GPT-5)
- `general_query` - General-purpose queries (GPT-4.5 Turbo)

**Environment Variables:**
```bash
OPENAI_API_KEY=your_key
MODEL=gpt-5
TURBO_MODEL=gpt-4.5-turbo
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## Intelligent Routing

The system automatically routes requests to the most appropriate model based on capability:

| Task Type | Routed To | Model | Reason |
|-----------|-----------|-------|--------|
| Audio analysis | Gemini | 2.5 Pro (2M context) | Fastest, optimized for audio, massive context |
| Genre detection | Gemini | 2.5 Pro | Specialized in classification with high accuracy |
| Production tips | Claude | Sonnet 4.5 | Expert coaching with enhanced reasoning |
| Creative ideas | Claude | Sonnet 4.5 | High creativity, deep music knowledge |
| Music theory | Claude | **Opus 4.1** | Advanced reasoning for complex theory |
| Code generation | OpenAI | **GPT-5** | Superior coding with 256K context |
| Debugging | OpenAI | GPT-5 | Systematic problem-solving with deep analysis |
| General queries | OpenAI | GPT-4.5 Turbo | Fast versatile fallback, cost-efficient |

## Usage in VS Code

### 1. Using with GitHub Copilot Chat

```
@workspace How can I improve the mix of this audio file?
```

The request will be automatically routed to Claude Sonnet 4.5 for production coaching.

```
@workspace Analyze the genre of this audio sample
```

This will be routed to Gemini 2.5 Pro for fast classification with massive context.

### 2. Using with KiloCoder

Simply use KiloCoder commands and the system will intelligently route to the appropriate model.

### 3. Direct Tool Invocation

You can also invoke specific tools directly through the MCP protocol.

## Testing the Servers

### Test Google AI Server

```bash
cd scripts/mcp-servers
export GOOGLE_AI_API_KEY="your_key"
node google-ai-server.js
```

### Test Anthropic Server

```bash
export ANTHROPIC_API_KEY="your_key"
node anthropic-server.js
```

### Test OpenAI Server

```bash
export OPENAI_API_KEY="your_key"
node openai-server.js
```

## Troubleshooting

### Server Not Starting

1. **Check API Keys**: Ensure all environment variables are set
   ```bash
   echo $GOOGLE_AI_API_KEY
   echo $ANTHROPIC_API_KEY
   echo $OPENAI_API_KEY
   ```

2. **Check Dependencies**: Reinstall if needed
   ```bash
   cd scripts/mcp-servers
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check Permissions**: Ensure scripts are executable
   ```bash
   chmod +x *.js
   ```

### VS Code Not Detecting Servers

1. **Reload VS Code**: `Ctrl+Shift+P` → "Developer: Reload Window"

2. **Check Settings**: Verify settings.json configuration

3. **Check MCP Logs**: Look for errors in VS Code Output panel

### Rate Limiting Issues

If you encounter rate limiting:

1. **Enable Caching**: Already configured in settings.json
2. **Adjust Timeouts**: Increase timeout values if needed
3. **Use Fallback**: System automatically falls back to alternative providers

## API Cost Optimization

The system includes several cost optimization features:

1. **Response Caching**: Identical requests return cached responses (168-hour TTL)
2. **Intelligent Routing**: Routes to most cost-effective provider for each task
3. **Batch Processing**: Groups similar requests when possible
4. **Rate Limiting**: Prevents excessive API calls

## Performance Metrics

Expected response times:

| Provider | Average Response | Use Case |
|----------|-----------------|----------|
| Gemini   | 1-3 seconds     | Audio analysis |
| Claude   | 2-5 seconds     | Coaching/theory |
| GPT-4    | 2-4 seconds     | Code/debugging |

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` file (already gitignored)
3. **Command Restrictions**: Review denied commands in settings.json
4. **File Access**: MCP servers have restricted filesystem access

## Contributing

To add a new tool to any server:

1. Add tool definition to `tools/list` handler
2. Implement tool logic in `tools/call` handler
3. Update this README with tool documentation
4. Test thoroughly before deployment

## Support

For issues or questions:
- Check the main project README
- Review VS Code Output panel for errors
- Verify API key validity
- Check network connectivity

## License

Part of SampleMind AI project - See main LICENSE file
