# 🚀 MCP Servers for GitHub Copilot in VS Code - Setup Guide

## 📋 Overview

This guide shows you how to use **Model Context Protocol (MCP) servers** with GitHub Copilot Chat in VS Code for enhanced AI agent capabilities in your development workflow.

---

## ✅ Current MCP Configuration

Your current setup in `.kilocode/mcp.json`:

```json
{
  "mcpServers": {
    "sequentialthinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "alwaysAllow": ["sequentialthinking"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/lchta/Projects"]
    },
    "codegen": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/codegen-sh/codegen-sdk.git#egg=codegen-mcp-server&subdirectory=codegen-examples/examples/codegen-mcp-server",
        "codegen-mcp-server"
      ]
    }
  }
}
```

### What Each Server Does:

1. **🧠 Sequential Thinking** - Helps AI break down complex problems step-by-step
2. **📁 Filesystem** - Provides file system access across your Projects directory
3. **💻 Codegen** - Assists with code generation and scaffolding

---

## 🔧 VS Code Configuration for MCP

### Step 1: Configure MCP in VS Code Settings

Create or update `.vscode/settings.json` in your workspace:

```json
{
  "github.copilot.chat.mcpServers": {
    "sequentialthinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "alwaysAllow": ["sequentialthinking"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    },
    "samplemind-project": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}/src",
        "${workspaceFolder}/tests",
        "${workspaceFolder}/docs"
      ]
    },
    "python-env": {
      "command": "python3",
      "args": ["-m", "mcp.server.stdio"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

---

## 🎯 Recommended MCP Servers for SampleMind AI

### 1. **GitHub MCP Server** (Access GitHub Issues, PRs, Code)

```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
  }
}
```

**Usage in Copilot Chat:**
- "@github list issues in lchtangen/samplemind-ai-v2-phoenix"
- "@github create issue: Bug in audio processing"
- "@github search code: TaskType.TOOL_CALLING"

### 2. **Memory Server** (Persistent Context)

```json
"memory": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"]
}
```

**Usage:**
- "@memory store: SampleMind uses Gemini, Claude, and OpenAI"
- "@memory recall: What AI providers does SampleMind use?"

### 3. **Brave Search** (Web Search for Latest Info)

```json
"brave-search": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": {
    "BRAVE_API_KEY": "${env:BRAVE_API_KEY}"
  }
}
```

**Usage:**
- "@brave-search latest Gemini 2.5 Pro features"
- "@brave-search best practices for tool calling with Claude"

### 4. **Python Environment Inspector**

Create a custom MCP server for your Python environment:

```json
"python-inspector": {
  "command": "${workspaceFolder}/tools/mcp_python_inspector.py"
}
```

### 5. **Database Inspector** (MongoDB/Redis)

```json
"database": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-mongodb"],
  "env": {
    "MONGODB_URI": "mongodb://localhost:27017/samplemind"
  }
}
```

---

## 🚫 Preventing Degraded Tool Calling with MCP

### Critical Configuration

Add this to your VS Code settings to prevent degraded performance:

```json
{
  "github.copilot.advanced": {
    "temperature": 0.1,
    "maxTokens": 4000,
    "modelId": "gpt-4o",  // or "claude-3.5-sonnet"
    "streaming": false
  },
  "github.copilot.chat.mcpSettings": {
    "toolCallingMode": "reliable",
    "parallelToolCalls": true,
    "autoRetry": true,
    "maxRetries": 3
  }
}
```

### MCP Server Reliability Settings

```json
{
  "github.copilot.chat.mcpServers": {
    "your-server": {
      "command": "...",
      "timeout": 30000,  // 30 seconds
      "retryAttempts": 3,
      "retryDelay": 1000  // 1 second
    }
  }
}
```

---

## 📝 How to Use MCP in Copilot Chat

### Basic Usage

1. **Open Copilot Chat**: `Ctrl+Alt+I` (Windows/Linux) or `Cmd+Option+I` (Mac)

2. **Use @ mentions to invoke MCP servers**:
   ```
   @sequentialthinking How should I refactor the audio processing pipeline?
   
   @filesystem Read src/samplemind/ai/providers.py and explain the tool calling flow
   
   @github List all open issues tagged with "performance"
   ```

3. **Chain multiple MCP servers**:
   ```
   @filesystem Read the AI provider code
   @sequentialthinking Break down how to add a new AI provider
   @codegen Generate the boilerplate for a new provider
   ```

### Advanced Usage

**Context-Aware Coding:**
```
@workspace @samplemind-project
I need to add support for a new AI provider called "Mistral". 
Use @sequentialthinking to plan the implementation, 
then @filesystem to find similar implementations,
finally @codegen to scaffold the new code.
```

**Debugging with MCP:**
```
@filesystem Read tests/unit/test_api_key_manager.py
@github Search for similar test failures in issues
@sequentialthinking Analyze why this test might be failing
```

**Documentation with MCP:**
```
@filesystem Read all files in src/samplemind/ai/
@sequentialthinking Create a comprehensive architecture diagram
Generate markdown documentation for the AI module
```

---

## 🔥 Custom MCP Server for SampleMind AI

Create a custom MCP server specific to your project:

### `tools/samplemind_mcp_server.py`

```python
#!/usr/bin/env python3
"""
SampleMind AI Custom MCP Server
Provides project-specific tools for Copilot Chat
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List

class SampleMindMCPServer:
    """Custom MCP server for SampleMind AI project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
    
    async def list_ai_providers(self) -> List[str]:
        """List all configured AI providers"""
        providers_file = self.project_root / "src/samplemind/ai/router.py"
        # Parse and return provider names
        return ["OpenAI", "Anthropic", "Google Gemini", "Ollama"]
    
    async def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider"""
        # Read from providers.py
        return {
            "name": provider,
            "temperature": 0.1,
            "max_tokens": 1000,
            "streaming": False
        }
    
    async def analyze_tool_calling_usage(self) -> Dict[str, Any]:
        """Analyze how tool calling is used in the codebase"""
        # Scan codebase for tool calling patterns
        return {
            "total_tool_calls": 42,
            "providers_with_tools": ["OpenAI", "Claude", "Gemini"],
            "common_patterns": [
                "audio_analysis",
                "genre_classification",
                "production_tips"
            ]
        }
    
    async def suggest_optimization(self, file_path: str) -> List[str]:
        """Suggest optimizations for a specific file"""
        return [
            "Consider using async/await for I/O operations",
            "Add type hints for better IDE support",
            "Implement caching for expensive operations"
        ]

async def main():
    """MCP server main loop"""
    server = SampleMindMCPServer()
    
    # MCP protocol implementation
    while True:
        try:
            # Read JSON-RPC request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, input)
            request = json.loads(line)
            
            method = request.get("method")
            params = request.get("params", {})
            
            # Route to appropriate handler
            if method == "list_ai_providers":
                result = await server.list_ai_providers()
            elif method == "get_provider_config":
                result = await server.get_provider_config(params["provider"])
            elif method == "analyze_tool_calling":
                result = await server.analyze_tool_calling_usage()
            elif method == "suggest_optimization":
                result = await server.suggest_optimization(params["file_path"])
            else:
                result = {"error": f"Unknown method: {method}"}
            
            # Send JSON-RPC response to stdout
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result
            }
            print(json.dumps(response))
            
        except EOFError:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"message": str(e)}
            }
            print(json.dumps(error_response))

if __name__ == "__main__":
    asyncio.run(main())
```

### Add to VS Code Settings

```json
{
  "github.copilot.chat.mcpServers": {
    "samplemind": {
      "command": "python3",
      "args": ["${workspaceFolder}/tools/samplemind_mcp_server.py"]
    }
  }
}
```

### Usage

```
@samplemind list_ai_providers
@samplemind get_provider_config OpenAI
@samplemind analyze_tool_calling
@samplemind suggest_optimization src/samplemind/ai/providers.py
```

---

## 🎯 Best Practices

### 1. **MCP Server Hygiene**
- ✅ Keep MCP servers lightweight and fast
- ✅ Use timeouts to prevent hanging
- ✅ Implement retry logic for reliability
- ✅ Log all MCP interactions for debugging

### 2. **Tool Calling Reliability**
- ✅ Set temperature ≤ 0.2 for Copilot Chat
- ✅ Disable streaming when using MCP tools
- ✅ Use `alwaysAllow` for trusted tools
- ✅ Test MCP servers independently first

### 3. **Performance Optimization**
- ✅ Cache MCP server responses when possible
- ✅ Use connection pooling for database MCP servers
- ✅ Implement request deduplication
- ✅ Monitor MCP server resource usage

### 4. **Security**
- ✅ Never expose API keys in MCP config (use env vars)
- ✅ Limit filesystem access scope
- ✅ Validate all MCP server inputs
- ✅ Use `alwaysAllow` only for safe operations

---

## 🐛 Troubleshooting

### MCP Server Not Working

1. **Check VS Code Output Panel**:
   - View → Output → Select "GitHub Copilot Chat"
   - Look for MCP server errors

2. **Test MCP Server Manually**:
   ```bash
   # Test sequential thinking
   echo '{"jsonrpc":"2.0","method":"think","params":{"prompt":"test"},"id":1}' | npx -y @modelcontextprotocol/server-sequential-thinking
   ```

3. **Verify Configuration**:
   ```bash
   # Check if npx/uvx is available
   which npx
   which uvx
   
   # Test filesystem access
   ls -la /home/lchta/Projects
   ```

### Degraded Performance

1. **Check Copilot Settings**:
   ```json
   {
     "github.copilot.advanced.temperature": 0.1,
     "github.copilot.chat.mcpSettings.toolCallingMode": "reliable"
   }
   ```

2. **Monitor MCP Server Logs**:
   ```bash
   # Enable debug logging
   export DEBUG=mcp:*
   ```

3. **Reduce MCP Server Count**:
   - Disable unused servers
   - Use only essential tools

---

## 📚 Recommended MCP Servers for AI Development

### Essential (Install These First)

1. **Sequential Thinking** ✅ (Already installed)
   ```bash
   npx -y @modelcontextprotocol/server-sequential-thinking
   ```

2. **Filesystem** ✅ (Already installed)
   ```bash
   npx -y @modelcontextprotocol/server-filesystem
   ```

3. **GitHub**
   ```bash
   npx -y @modelcontextprotocol/server-github
   ```

### Advanced (Optional)

4. **Memory** (Persistent context)
   ```bash
   npx -y @modelcontextprotocol/server-memory
   ```

5. **Brave Search** (Web search)
   ```bash
   npx -y @modelcontextprotocol/server-brave-search
   ```

6. **PostgreSQL** (Database)
   ```bash
   npx -y @modelcontextprotocol/server-postgres
   ```

---

## 🚀 Quick Start

### 1. Update VS Code Settings

```bash
# Create or update .vscode/settings.json
cat > .vscode/settings.json << 'EOF'
{
  "github.copilot.chat.mcpServers": {
    "sequentialthinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "alwaysAllow": ["sequentialthinking"]
    },
    "samplemind-fs": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${workspaceFolder}/src",
        "${workspaceFolder}/tests"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    }
  },
  "github.copilot.advanced": {
    "temperature": 0.1,
    "maxTokens": 4000
  }
}
EOF
```

### 2. Reload VS Code

```
Ctrl+Shift+P → Developer: Reload Window
```

### 3. Test in Copilot Chat

```
@sequentialthinking Plan how to add a new AI provider

@samplemind-fs Read src/samplemind/ai/providers.py

@github List issues with label:enhancement
```

---

## 📊 Summary

### What You Have Now
✅ Sequential thinking MCP server  
✅ Filesystem access MCP server  
✅ Codegen MCP server  

### What to Add
🔲 GitHub MCP server (for issue/PR management)  
🔲 Memory MCP server (for persistent context)  
🔲 Custom SampleMind MCP server (project-specific tools)  

### Configuration for Reliability
✅ Temperature ≤ 0.2  
✅ Streaming disabled for tools  
✅ Retry logic enabled  
✅ Proper error handling  

---

**Ready to use MCP in VS Code Copilot Chat!** 🎉

Open Copilot Chat (`Ctrl+Alt+I`) and try:
```
@sequentialthinking How can I optimize the AI tool calling in my codebase?
```
