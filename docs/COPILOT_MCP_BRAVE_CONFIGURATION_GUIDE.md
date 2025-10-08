# 🚀 Complete MCP Server Configuration Guide for VS Code GitHub Copilot & Kilo Code

**Version:** 1.0.0 Phoenix Beta  
**Last Updated:** October 6, 2025  
**Total MCP Servers:** 29 (14 Core + 15 Extended)  
**Status:** Production-Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture Diagram](#architecture-diagram)
4. [Core Configuration](#core-configuration)
5. [29 MCP Servers Reference](#29-mcp-servers-reference)
6. [API Key Management](#api-key-management)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Performance Optimization](#performance-optimization)
10. [Security Best Practices](#security-best-practices)

---

## 🎯 Overview

This guide provides complete setup and configuration for integrating **29 MCP (Model Context Protocol) servers** with VS Code GitHub Copilot and Kilo Code for the SampleMind AI project.

### What You Get

✅ **Search & Documentation** - Brave Search, Context7, Memory persistence  
✅ **Audio/ML Specialized** - Custom audio analysis, Python environment, AI providers  
✅ **Database & Storage** - MongoDB, Redis, PostgreSQL, SQLite, Google Drive  
✅ **Cloud & DevOps** - AWS, Docker, Kubernetes orchestration  
✅ **Productivity** - Slack, Linear, Notion, Sentry, Stripe  
✅ **Development** - Sequential thinking, browser automation, code execution  

### System Requirements

- **VS Code:** 1.85.0 or later
- **GitHub Copilot:** Active subscription (Pro or Business)
- **Node.js:** 18.0.0 or later (for npx MCP servers)
- **Python:** 3.11+ (for custom Python MCP servers)
- **Git:** 2.40.0 or later

---

## ⚡ Quick Start

### 1. Clone and Setup

```bash
cd ~/Projects/Samplemind-AI

# Install Node.js dependencies for MCP servers
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-memory
npm install -g @upstash/context7-mcp

# Verify installations
npx -y @modelcontextprotocol/server-brave-search --version
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env and add your keys (see API Key Management section)
```

### 3. Reload VS Code

```
Press: Ctrl+Shift+P (Windows/Linux) or Cmd+Shift+P (Mac)
Type: Developer: Reload Window
```

### 4. Verify MCP Servers

Open GitHub Copilot Chat (`Ctrl+Alt+I`) and test:

```
@memory store: SampleMind AI uses 29 MCP servers for enhanced development
@brave-search latest librosa audio analysis techniques
@sequentialthinking plan a new feature for audio genre classification
```

---

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph VSCode[VS Code Environment]
        Copilot[GitHub Copilot Agent Mode]
        Settings[.vscode/settings.json]
        Instructions[.github/copilot-instructions.md]
        Prompts[.github/copilot-prompts]
    end
    
    subgraph MCPCore[Core MCP Servers - 3]
        Sequential[Sequential Thinking]
        Filesystem[Filesystem Access]
        Codegen[Code Generation]
    end
    
    subgraph MCPSearch[Search & Docs - 3]
        Brave[Brave Search]
        Memory[Memory Persistence]
        Context7[Context7 Docs]
    end
    
    subgraph MCPCode[Code & Collab - 3]
        Git[Git Repository]
        Puppeteer[Browser Automation]
        GitHub[GitHub Integration]
    end
    
    subgraph MCPExec[Execution - 2]
        E2B[E2B Sandbox]
        N8N[N8N Workflows]
    end
    
    subgraph MCPCustom[SampleMind Custom - 5]
        Audio[Audio Analysis]
        PyEnv[Python Environment]
        MongoDB[MongoDB]
        Redis[Redis Cache]
        AIProvider[AI Providers]
    end
    
    subgraph MCPDatabase[Database - 3]
        Postgres[PostgreSQL]
        SQLite[SQLite]
        GDrive[Google Drive]
    end
    
    subgraph MCPCloud[Cloud & DevOps - 3]
        AWS[AWS Infrastructure]
        Docker[Docker Containers]
        K8s[Kubernetes]
    end
    
    subgraph MCPProd[Productivity - 6]
        Slack[Slack]
        Linear[Linear]
        Notion[Notion]
        Sentry[Sentry]
        Stripe[Stripe]
        Time[Time Utils]
    end
    
    subgraph MCPUtils[Utilities - 2]
        Fetch[HTTP Fetch]
        Everything[File Search]
    end
    
    Copilot --> Settings
    Copilot --> Instructions
    Copilot --> Prompts
    
    Copilot --> MCPCore
    Copilot --> MCPSearch
    Copilot --> MCPCode
    Copilot --> MCPExec
    Copilot --> MCPCustom
    Copilot --> MCPDatabase
    Copilot --> MCPCloud
    Copilot --> MCPProd
    Copilot --> MCPUtils
    
    style Copilot fill:#8b5cf6,stroke:#6d28d9,color:#fff
    style Brave fill:#fb923c,stroke:#ea580c,color:#fff
    style Memory fill:#10b981,stroke:#059669,color:#fff
    style Audio fill:#ef4444,stroke:#dc2626,color:#fff
```

---

## 🔧 Core Configuration

### VS Code Settings (`.vscode/settings.json`)

All 29 MCP servers are configured in your `.vscode/settings.json` file under the `github.copilot.chat.mcpServers` section. Key configuration aspects:

**Timeout Settings:**
- Simple operations: 10000-15000ms
- Moderate complexity: 15000-20000ms
- Heavy processing: 25000-30000ms

**Environment Variables:**
- All sensitive credentials use `${env:VAR_NAME}` syntax
- Never hardcode API keys in settings
- Load from `.env` file at runtime

**Agent Mode Optimization:**
```json
"github.copilot.advanced": {
  "temperature": 0.1,
  "maxTokens": 4000,
  "internalAgent": "gpt-4o"
},
"github.copilot.chat.mcpSettings": {
  "toolCallingMode": "reliable",
  "parallelToolCalls": true,
  "autoRetry": true,
  "maxRetries": 3
}
```

### Custom Instructions

Located in `.github/copilot-instructions.md`, this file provides:
- Project context and tech stack overview
- Core development standards
- 29 MCP server capabilities and usage
- Common workflow examples
- Reference to extended documentation

---

## 📚 29 MCP Servers Reference

### Category 1: Core Development (3 Servers)

#### 1. Sequential Thinking
**Purpose:** Step-by-step problem solving with dynamic thought adjustment

**Configuration:**
```json
"sequentialthinking": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
  "alwaysAllow": ["sequentialthinking"],
  "timeout": 30000
}
```

**Capabilities:**
- Break down complex problems into sequential steps
- Revise previous thoughts as understanding deepens
- Branch into alternative approaches
- Generate and verify solution hypotheses

**Usage Example:**
```
@sequentialthinking Plan how to implement real-time audio streaming with WebSocket and waveform visualization
```

#### 2. Filesystem Access
**Purpose:** Read/write files in workspace directories

**Servers:**
- `samplemind-src` - Source code access
- `samplemind-tests` - Test files access
- `samplemind-docs` - Documentation access

**Capabilities:**
- Read file contents with line numbers
- List directory structures
- Search file patterns
- Access multiple directories

**Usage Example:**
```
@samplemind-src Read the audio processing module and suggest optimizations
```

#### 3. Codegen
**Purpose:** Code scaffolding and generation

**Configuration:**
```json
"codegen": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/codegen-sh/codegen-sdk.git#egg=codegen-mcp-server&subdirectory=codegen-examples/examples/codegen-mcp-server", "codegen-mcp-server"],
  "timeout": 30000
}
```

**Capabilities:**
- Generate boilerplate code
- Create file structures
- Scaffold API endpoints
- Generate test files

---

### Category 2: Search & Documentation (3 Servers)

#### 4. Brave Search
**Purpose:** Web, local, and news search for latest information

**Setup:**
1. Sign up at [brave.com/search/api](https://brave.com/search/api)
2. Choose "Data for AI" plan (free: 2,000 queries/month)
3. Generate API key from dashboard
4. Add to `.env`: `BRAVE_API_KEY=your_key_here`

**Capabilities:**
- **Web Search:** General queries, documentation, tutorials
- **Local Search:** Businesses, places, points of interest
- **News Search:** Latest developments, announcements

**Usage Examples:**
```
@brave-search latest FastAPI 0.118 async performance improvements
@brave-search best practices for torch.compile() optimization 2025
@brave-search music production studios near San Francisco
```

**Rate Limits:**
- Free tier: 2,000 queries/month
- Pro tier: 15,000 queries/month ($5)
- Ultra tier: 100,000 queries/month ($20)

#### 5. Memory Persistence
**Purpose:** Store and retrieve context across chat sessions

**Configuration:**
```json
"memory": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "timeout": 10000
}
```

**Capabilities:**
- Create entities (users, projects, concepts)
- Define relations between entities
- Add observations to entities
- Search knowledge graph
- Persistent context across sessions

**Usage Examples:**
```
@memory store: SampleMind AI tech stack includes FastAPI, React 19, librosa, MongoDB
@memory create entity: Genre Classifier Model with type: ML_Model
@memory add relation: Genre Classifier uses sentence-transformers
@memory search: What AI providers does SampleMind use?
```

#### 6. Context7 Documentation
**Purpose:** Up-to-date library documentation with 1M+ code snippets

**Configuration:**
```json
"context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp"],
  "timeout": 15000
}
```

**Capabilities:**
- Resolve library names to Context7 IDs
- Fetch latest documentation
- Get code examples and snippets
- Search specific topics within libraries

**Usage Examples:**
```
@context7 get librosa documentation for tempo detection
@context7 search FastAPI WebSocket implementation examples
@context7 find React 19 useFormState hook documentation
```

---

### Category 3: Code & Collaboration (3 Servers)

#### 7. Git MCP (GitHub Repository)
**Purpose:** Direct integration with SampleMind-AI-Beta repository

**Configuration:**
```json
"git-mcp": {
  "command": "npx",
  "args": ["-y", "mcp-remote@0.1.29", "https://gitmcp.io/lchtangen/SampleMind-AI---Beta"],
  "timeout": 20000
}
```

**Capabilities:**
- Fetch repository documentation
- Search code across repository
- Access issues and pull requests
- Search within docs semantically

**Usage Examples:**
```
@git-mcp fetch documentation about audio processing architecture
@git-mcp search code for BPM detection implementation
@git-mcp find issues related to performance optimization
```

#### 8. Puppeteer (Browser Automation)
**Purpose:** Automated browser testing and web scraping

**Configuration:**
```json
"puppeteer": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
  "timeout": 30000
}
```

**Capabilities:**
- Navigate to URLs and take screenshots
- Click elements and fill forms
- Execute JavaScript in browser context
- Capture console logs
- Test responsive designs

**Usage Examples:**
```
@puppeteer navigate to http://localhost:3000 and take screenshot
@puppeteer click the upload button and test audio file upload
@puppeteer evaluate JavaScript to check if wavesurfer is loaded
```

#### 9. GitHub Integration
**Purpose:** Via git-mcp, access GitHub features

**Capabilities:**
- List repository issues
- Search code patterns
- Access pull requests
- Review commit history

---

### Category 4: Execution & Testing (2 Servers)

#### 10. E2B Secure Sandbox
**Purpose:** Execute Python code in isolated environment

**Configuration:**
```json
"e2b": {
  "command": "npx",
  "args": ["-y", "@e2b/mcp-server"],
  "timeout": 30000
}
```

**Capabilities:**
- Run Python code securely
- Test audio processing functions
- Validate ML model inference
- Execute data transformations

**Usage Examples:**
```
@e2b run this librosa code to detect BPM
@e2b test genre classification with sample audio features
@e2b validate torch model inference performance
```

#### 11. N8N Workflow Automation
**Purpose:** Automate workflows with 525+ integrations

**Configuration:**
```json
"n8n-mcp": {
  "command": "npx",
  "args": ["-y", "n8n-mcp@2.12.2"],
  "timeout": 20000
}
```

**Capabilities:**
- Access 525 n8n node types
- List AI-optimized tools (263 available)
- Get node documentation and examples
- Validate workflow configurations
- Search nodes by capability

**Usage Examples:**
```
@n8n-mcp list nodes for HTTP API integration
@n8n-mcp get documentation for Slack node
@n8n-mcp search nodes related to audio processing
@n8n-mcp get template for database sync workflow
```

---

### Category 5: SampleMind AI Custom (5 Servers)

#### 12. SampleMind Audio MCP
**Purpose:** Custom audio analysis for BPM, key, genre detection

**Configuration:**
```json
"samplemind-audio": {
  "command": "python3",
  "args": ["${workspaceFolder}/tools/mcp-servers/samplemind_audio_mcp.py"],
  "env": {"PYTHONPATH": "${workspaceFolder}/src"},
  "timeout": 30000
}
```

**Capabilities:**
- BPM detection with confidence scoring
- Musical key identification
- Genre classification (20+ genres)
- Mood analysis (energy, valence, acousticness)
- Spectral feature extraction

**Implementation:** See `tools/mcp-servers/samplemind_audio_mcp.py`

**Usage Examples:**
```
@samplemind-audio analyze BPM and key of uploaded track.wav
@samplemind-audio classify genre with confidence scores
@samplemind-audio extract MFCC features for ML training
```

#### 13. Python Environment MCP
**Purpose:** Access ML models, librosa, torch operations

**Configuration:**
```json
"python-env": {
  "command": "python3",
  "args": ["${workspaceFolder}/tools/mcp-servers/python_env_mcp.py"],
  "env": {"PYTHONPATH": "${workspaceFolder}/src"},
  "timeout": 20000
}
```

**Capabilities:**
- List installed packages and versions
- Test ML model inference
- Execute torch operations with GPU
- Run librosa audio analysis
- Check Python environment status

**Usage Examples:**
```
@python-env list all ML-related packages
@python-env test genre classifier model inference
@python-env check if CUDA is available for torch
```

#### 14. MongoDB MCP
**Purpose:** Database queries and audio metadata management

**Configuration:**
```json
"mongodb-mcp": {
  "command": "python3",
  "args": ["${workspaceFolder}/tools/mcp-servers/mongodb_mcp.py"],
  "env": {
    "PYTHONPATH": "${workspaceFolder}/src",
    "MONGODB_URL": "${env:MONGODB_URL}"
  },
  "timeout": 15000
}
```

**Capabilities:**
- Query audio file metadata
- Aggregate analysis results
- Update document fields
- Create indexes for performance
- Monitor collection stats

**Usage Examples:**
```
@mongodb-mcp find all audio files with BPM between 120-130
@mongodb-mcp get audio metadata for file_id abc123
@mongodb-mcp count files by genre category
```

#### 15. Redis MCP
**Purpose:** Cache management and performance monitoring

**Configuration:**
```json
"redis-mcp": {
  "command": "python3",
  "args": ["${workspaceFolder}/tools/mcp-servers/redis_mcp.py"],
  "env": {
    "PYTHONPATH": "${workspaceFolder}/src",
    "REDIS_URL": "${env:REDIS_URL}"
  },
  "timeout": 10000
}
```

**Capabilities:**
- Get/set cache values
- Monitor cache hit rates
- List cached keys by pattern
- Check Redis memory usage
- Clear cache by pattern

**Usage Examples:**
```
@redis-mcp get cache hit rate for audio analysis
@redis-mcp list all cached analysis results
@redis-mcp check Redis memory usage and stats
```

#### 16. AI Provider MCP
**Purpose:** Direct Gemini, Claude, OpenAI integration

**Configuration:**
```json
"ai-provider": {
  "command": "python3",
  "args": ["${workspaceFolder}/tools/mcp-servers/ai_provider_mcp.py"],
  "env": {
    "PYTHONPATH": "${workspaceFolder}/src",
    "GOOGLE_AI_API_KEY": "${env:GOOGLE_AI_API_KEY}",
    "ANTHROPIC_API_KEY": "${env:ANTHROPIC_API_KEY}",
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  },
  "timeout": 30000
}
```

**Capabilities:**
- Generate text with specific AI providers
- Compare responses across providers
- Route queries to optimal provider
- Test provider availability
- Monitor API usage and costs

**Usage Examples:**
```
@ai-provider using Gemini, analyze this audio description
@ai-provider using Claude, give creative production suggestions
@ai-provider compare genre classification across all providers
```

---

## ⚙️ API Key Management

### Required API Keys

Create a `.env` file in project root with these variables:

```bash
# Brave Search API
BRAVE_API_KEY=your_brave_api_key_here

# AI Providers (Already configured)
GOOGLE_AI_API_KEY=your_google_ai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key

# Database URLs
MONGODB_URL=mongodb://localhost:27017/samplemind
REDIS_URL=redis://localhost:6379/0

# Cloud Services (Optional)
POSTGRES_URL=postgresql://user:pass@localhost:5432/samplemind
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1

# Collaboration Tools (Optional)
SLACK_BOT_TOKEN=xoxb-your-token
LINEAR_API_KEY=lin_api_your_key
NOTION_API_KEY=secret_your_key
SENTRY_DSN=https://your-sentry-dsn
STRIPE_SECRET_KEY=sk_test_your_key
```

### Security Best Practices

1. **Never commit `.env` to version control**
   - Add `.env` to `.gitignore` (already done)
   - Use `.env.example` as template

2. **Use environment-specific keys**
   - Development: Use test/sandbox keys
   - Production: Use live keys with restrictions

3. **Rotate keys regularly**
   - Set expiration reminders (90 days)
   - Revoke unused keys immediately

4. **Scope permissions minimally**
   - Only grant required API scopes
   - Use read-only keys when possible

5. **Monitor API usage**
   - Set up billing alerts
   - Track unusual activity patterns

---

## 🎯 Usage Examples

### Example 1: Complete Audio Analysis Workflow

```
Step 1: Upload and Analyze
@samplemind-audio analyze BPM, key, and genre of track.wav

Step 2: Store Results
@mongodb-mcp save analysis results to database with file_id

Step 3: Cache for Performance
@redis-mcp cache analysis with 1-hour TTL

Step 4: Generate Recommendations
@ai-provider using Claude, generate mixing tips based on analysis

Step 5: Notify Team
@slack send analysis summary to #production channel
```

### Example 2: Debug Performance Issue

```
Step 1: Check Error Logs
@sentry search for audio processing errors in last 24 hours

Step 2: Analyze Cache Performance
@redis-mcp get cache hit rate for audio endpoints

Step 3: Check Database Performance
@mongodb-mcp analyze slow queries and missing indexes

Step 4: Research Optimizations
@brave-search latest librosa performance optimization techniques 2025

Step 5: Plan Solution
@sequentialthinking create optimization strategy with benchmarks
```

### Example 3: Deploy New ML Model

```
Step 1: Train Model
@python-env train genre classifier on /data/genres dataset

Step 2: Test in Sandbox
@e2b validate model inference with test samples

Step 3: Build Container
@docker build image with new model and dependencies

Step 4: Deploy to Kubernetes
@kubernetes update deployment with rolling update strategy

Step 5: Monitor Performance
@sentry track model inference latency and error rates
```

---

## 🐛 Troubleshooting

### Issue: MCP Server Not Responding

**Symptoms:**
- Tool calls timeout after 30 seconds
- No response from @mention
- "Server connection failed" errors

**Solutions:**

1. **Check Node.js/Python installation:**
   ```bash
   node --version  # Should be 18.0.0+
   python3 --version  # Should be 3.11+
   ```

2. **Verify package installation:**
   ```bash
   npx -y @modelcontextprotocol/server-brave-search --help
   ```

3. **Check VS Code Output:**
   - Open Output panel: View → Output
   - Select "GitHub Copilot Chat" from dropdown
   - Look for connection errors or stack traces

4. **Reload VS Code window:**
   ```
   Ctrl+Shift+P → Developer: Reload Window
   ```

### Issue: API Key Authentication Failed

**Symptoms:**
- "Invalid API key" errors
- 401 Unauthorized responses
- Authentication failures

**Solutions:**

1. **Verify `.env` file exists and has correct keys:**
   ```bash
   cat .env | grep BRAVE_API_KEY
   ```

2. **Check for extra spaces or newlines:**
   ```bash
   # Remove any whitespace
   sed -i 's/[[:space:]]*$//' .env
   ```

3. **Regenerate API key:**
   - Visit provider dashboard
   - Revoke old key
   - Generate new key
   - Update `.env` file

4. **Check key permissions:**
   - Ensure required scopes are granted
   - Verify key is not expired

### Issue: Slow MCP Response Times

**Symptoms:**
- Tools take >10 seconds to respond
- Frequent timeouts
- Poor user experience

**Solutions:**

1. **Increase timeout values in settings.json:**
   ```json
   "your-server": {
     "timeout": 45000  // Increase from 30000
   }
   ```

2. **Check network connectivity:**
   ```bash
   ping api.brave.com
   curl -I https://api.openai.com/v1/models
   ```

3. **Optimize database queries:**
   - Add indexes for frequent queries
   - Use projection to limit fields
   - Implement query caching

4. **Monitor system resources:**
   ```bash
   # Check CPU/memory usage
   top
   # Check disk I/O
   iostat
   ```

### Issue: Custom Python MCP Servers Not Working

**Symptoms:**
- `samplemind-audio` not responding
- Python import errors
- Module not found errors

**Solutions:**

1. **Verify PYTHONPATH is set:**
   ```bash
   echo $PYTHONPATH
   # Should include /home/lchta/Projects/Samplemind-AI/src
   ```

2. **Check Python dependencies:**
   ```bash
   pip list | grep librosa
   pip list | grep torch
   ```

3. **Test MCP server manually:**
   ```bash
   python3 tools/mcp-servers/samplemind_audio_mcp.py
   ```

4. **Check file permissions:**
   ```bash
   chmod +x tools/mcp-servers/*.py
   ```

---

## ⚡ Performance Optimization

### Backend MCP Servers

1. **Use Connection Pooling**
   - MongoDB: `maxPoolSize=100, minPoolSize=10`
   - Redis: Connection pool with max 50 connections
   - PostgreSQL: pgbouncer for connection management

2. **Implement Caching**
   - Cache frequent queries in Redis
   - Set appropriate TTL (1 hour for analysis, 24 hours for metadata)
   - Use cache warming for predictable queries

3. **Optimize Timeouts**
   - Set realistic timeouts based on operation complexity
   - Implement exponential backoff for retries
   - Use circuit breakers for failing services

### Frontend Integration

1. **Debounce MCP Calls**
   - Wait 300ms before sending search queries
   - Batch multiple requests when possible
   - Cancel in-flight requests on new input

2. **Show Loading States**
   - Display progress indicators
   - Provide estimated wait times
   - Allow user cancellation

3. **Handle Errors Gracefully**
   - Show user-friendly error messages
   - Provide retry options
   - Fallback to alternative providers

---

## 🔒 Security Best Practices

### 1. API Key Protection

```bash
# ✅ Good: Use environment variables
BRAVE_API_KEY=${env:BRAVE_API_KEY}

# ❌ Bad: Hardcode keys
BRAVE_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxx
```

### 2. Scope Limitations

- **Brave Search:** Read-only, no admin access needed
- **GitHub:** repo scope only, no delete permissions
- **Slack:** channels:read, chat:write only
- **Linear:** issue:read, issue:write (no admin)

### 3. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from redis import Redis
from datetime import datetime, timedelta

async def rate_limit(user_id: str, limit: int = 60, window: int = 60):
    """Allow 'limit' requests per 'window' seconds"""
    redis = Redis()
    key = f"rate_limit:{user_id}"
    count = redis.incr(key)
    
    if count == 1:
        redis.expire(key, window)
    
    if count > limit:
        raise HTTPException(429, "Rate limit exceeded")
```

### 4. Audit Logging

Log all MCP server interactions:

```python
import structlog

logger = structlog.get_logger()

async def log_mcp_call(
    server: str,
    method: str,
    user_id: str,
    duration_ms: float
):
    logger.info(
        "mcp_call",
        server=server,
        method=method,
        user_id=user_id,
        duration_ms=duration_ms,
        timestamp=datetime.utcnow().isoformat()
    )
```

### 5. Data Encryption

- Use HTTPS for all external API calls
- Encrypt sensitive data at rest
- Use TLS 1.3 for database connections
- Implement field-level encryption for PII

---

## 📊 Monitoring & Analytics

### Key Metrics to Track

1. **MCP Server Health**
   - Uptime percentage (target: 99.9%)
   - Average response time (target: <500ms)
   - Error rate (target: <0.1%)

2. **API Usage**
   - Requests per hour/day/month
   - Cost per provider
   - Rate limit violations

3. **Performance**
   - P50, P95, P99 latencies
   - Cache hit rates
   - Database query times

### Monitoring Tools

```json
// Configure Sentry for error tracking
"sentry": {
  "command": "npx",
  "args": ["-y", "mcp-sentry@0.1.0"],
  "env": {
    "SENTRY_DSN": "${env:SENTRY_DSN}"
  }
}
```

---

## 🚀 Next Steps

1. **Complete API Key Setup**
   - Obtain Brave Search API key
   - Configure optional service keys (Slack, Linear, etc.)

2. **Test Each MCP Server**
   - Run verification script (see below)
   - Test sample queries
   - Monitor response times

3. **Customize for Your Workflow**
   - Create additional prompt files in `.github/copilot-prompts/`
   - Add project-specific MCP servers
   - Optimize timeout values based on usage

4. **Monitor and Optimize**
   - Track MCP server performance
   - Adjust caching strategies
   - Optimize database queries

---

## 🔗 Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/copilot)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Brave Search API Docs](https://brave.com/search/api/docs)
- [SampleMind AI Architecture](./KILO_CODE_MASTER_PROMPT.md)

---

**Version:** 1.0.0 Phoenix Beta  
**Status:** Production-Ready  
**Last Updated:** October 6, 2025  
**Total MCP Servers:** 29

**Let's build the future of AI-powered music production! 🎵✨**
