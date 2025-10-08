# 🛠️ AI Tool Calling Best Practices - Avoiding Degraded Performance

## 🎯 Overview

This guide explains how to prevent **degraded tool calling performance** when using AI agents with OpenAI, Anthropic Claude, and Google Gemini in your codebase.

## ⚠️ Common Causes of Degraded Tool Calling

### 1. **High Temperature Settings**
- **Problem**: Temperature > 0.3 causes unreliable function calls
- **Solution**: Keep temperature ≤ 0.2 (preferably 0.1) for tool calling
- **Our Implementation**:
  ```python
  TaskType.TOOL_CALLING: {
      "temperature": 0.1,  # ✅ Optimal for reliability
  }
  ```

### 2. **Streaming Enabled for Tool Calls**
- **Problem**: Streaming degrades structured output reliability
- **Solution**: Disable streaming for tool calling tasks
- **Our Implementation**:
  ```python
  TaskType.TOOL_CALLING: {
      "streaming": StreamingMode.DISABLED,  # ✅ Critical
  }
  ```

### 3. **Wrong Model Selection**
- **Problem**: Older/experimental models have poor tool support
- **Solution**: Use latest stable models with tool calling support

### 4. **Missing Tool Declarations**
- **Problem**: Not properly declaring tools to the API
- **Solution**: Use provider-specific tool declaration formats

### 5. **Insufficient Context Window**
- **Problem**: Tool responses get truncated
- **Solution**: Ensure adequate `max_tokens` for tool responses (≥1000)

---

## 🚀 Recommended Models (October 2025)

### OpenAI
```python
"gpt-4o"              # ✅ Best tool calling support
"gpt-4o-mini"         # ⚠️ Good for simple tools, cheaper
"gpt-3.5-turbo"       # ❌ Deprecated for tools
```

### Anthropic Claude
```python
"claude-3-5-sonnet-20241022"  # ✅ Excellent (best reasoning)
"claude-3-opus-20240229"      # ✅ Good (most powerful)
"claude-3-haiku-20240307"     # ⚠️ Fast but less reliable
```

### Google Gemini
```python
"gemini-2.5-pro"          # ✅ Best for production
"gemini-2.0-flash-exp"    # ⚠️ Fast but experimental
"gemini-1.5-pro"          # ✅ Stable fallback
```

---

## 🔧 Implementation Guide

### Using Our Optimization Function

```python
from samplemind.ai import (
    Provider, 
    build_gemini_request,
    optimize_for_tool_calling
)

# 1. Build base request
tools = [
    {
        "name": "analyze_audio",
        "description": "Analyze audio file for genre and BPM",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            }
        }
    }
]

payload = build_gemini_request(
    messages=[{"role": "user", "content": "Analyze this track"}],
    task_type=TaskType.TOOL_CALLING,
    tools=tools  # ✅ Tool declarations added
)

# 2. Optimize for tool calling
payload = optimize_for_tool_calling(
    provider=Provider.GEMINI,
    payload=payload,
    num_tools=len(tools)
)
```

### Provider-Specific Examples

#### OpenAI
```python
from samplemind.ai import build_openai_request, TaskType

payload = build_openai_request(
    messages=[{"role": "user", "content": "Extract BPM"}],
    task_type=TaskType.TOOL_CALLING,
    functions=[{
        "name": "extract_bpm",
        "description": "Extract BPM from audio",
        "parameters": {
            "type": "object",
            "properties": {
                "bpm": {"type": "number"},
                "confidence": {"type": "number"}
            }
        }
    }],
    parallel_tool_calls=True  # ✅ Enable for multi-tool requests
)
```

#### Anthropic Claude
```python
from samplemind.ai import build_anthropic_request, TaskType

payload = build_anthropic_request(
    messages=[{"role": "user", "content": "Classify genre"}],
    task_type=TaskType.TOOL_CALLING,
    enable_prompt_caching=True  # ✅ Save 60-90% on costs
)
```

#### Google Gemini
```python
from samplemind.ai import build_gemini_request, TaskType

payload = build_gemini_request(
    messages=[{"role": "user", "content": "Get production tips"}],
    task_type=TaskType.TOOL_CALLING,
    tools=[{
        "name": "get_tips",
        "description": "Get FL Studio production tips",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "genre": {"type": "STRING"}
            }
        }
    }],
    enable_json_mode=True  # ✅ Force structured output
)
```

---

## 📊 Performance Comparison

| Provider | Tool Call Latency | Reliability | Cost per 1M tokens | Best Use Case |
|----------|-------------------|-------------|-------------------|---------------|
| **Ollama** (local) | <50ms | Medium | $0 | Fast, simple tools |
| **Gemini 2.5 Pro** | 200-500ms | High | $0.075 | Balanced speed/quality |
| **Claude 3.5 Sonnet** | 300-800ms | Very High | $3.00 | Complex reasoning |
| **GPT-4o** | 400-900ms | High | $2.50 | Reliable fallback |

---

## ✅ Checklist: Preventing Degraded Tool Calling

- [ ] **Temperature ≤ 0.2** for all tool calling tasks
- [ ] **Streaming disabled** for tool responses
- [ ] **Latest stable models** (not experimental)
- [ ] **Proper tool declarations** in provider-specific format
- [ ] **max_tokens ≥ 1000** for tool responses
- [ ] **Parallel tool calls enabled** (OpenAI) for multi-tool requests
- [ ] **Prompt caching enabled** (Claude) to reduce costs
- [ ] **JSON mode enabled** (Gemini) for structured outputs
- [ ] **Error handling** with fallback providers
- [ ] **Response validation** to catch malformed tool calls

---

## 🧪 Testing Tool Calling

### Quick Test Script

```python
from samplemind.ai import (
    Provider,
    TaskType,
    build_provider_request,
    optimize_for_tool_calling,
    make_ai_request
)

async def test_tool_calling():
    tools = [{
        "name": "test_function",
        "description": "A test function",
        "parameters": {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    }]
    
    for provider in [Provider.OPENAI, Provider.CLAUDE, Provider.GEMINI]:
        print(f"\n🧪 Testing {provider.value}...")
        
        payload = build_provider_request(
            provider=provider,
            messages=[{"role": "user", "content": "Call test_function"}],
            task_type=TaskType.TOOL_CALLING,
            tools=tools
        )
        
        payload = optimize_for_tool_calling(
            provider=provider,
            payload=payload,
            num_tools=len(tools)
        )
        
        response = await make_ai_request(provider, payload)
        print(f"✅ Success: {response}")

# Run test
import asyncio
asyncio.run(test_tool_calling())
```

---

## 🚨 Common Errors and Solutions

### Error: "Tool call format invalid"
**Cause**: Wrong tool declaration format for provider  
**Solution**: Use provider-specific format (OpenAI uses `tools`, Gemini uses `functionDeclarations`)

### Error: "Temperature too high for reliable tool calling"
**Cause**: Temperature > 0.3  
**Solution**: Call `optimize_for_tool_calling()` to auto-fix

### Error: "Context length exceeded"
**Cause**: `max_tokens` too low for tool response  
**Solution**: Set `max_tokens ≥ 1000` or use `optimize_for_tool_calling()`

### Error: "Streaming not supported with tools"
**Cause**: Streaming enabled with tool calls  
**Solution**: Set `streaming=False` or use `TaskType.TOOL_CALLING`

---

## 📚 Additional Resources

- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **Anthropic Claude Tools**: https://docs.anthropic.com/claude/docs/tool-use
- **Google Gemini Function Calling**: https://ai.google.dev/gemini-api/docs/function-calling
- **Our Implementation**: `/src/samplemind/ai/providers.py`

---

## 🎯 Key Takeaways

1. **Use `optimize_for_tool_calling()`** for automatic optimization
2. **Temperature ≤ 0.2** is critical for reliability
3. **Disable streaming** for tool calling tasks
4. **Use latest stable models** with proven tool support
5. **Test thoroughly** across all providers
6. **Monitor performance** and adjust based on use case

---

**Updated**: October 2025  
**Maintainer**: SampleMind AI Team  
**Status**: Production Ready ✅
