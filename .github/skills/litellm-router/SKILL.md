---
name: litellm-router
description: Guide for using the LiteLLM multi-provider AI router. Use when making LLM calls or modifying the AI provider chain.
---

## LiteLLM Router Usage

### Configuration
Located at `src/samplemind/integrations/litellm_router.py`
Fallback chain: Claude → Gemini → GPT → Ollama

### Usage Pattern
```python
from samplemind.integrations.litellm_router import chat_completion

# Default (Claude)
response = await chat_completion(
    messages=[{"role": "user", "content": "Analyze this BPM: 140"}]
)

# Fast mode (Gemini)
response = await chat_completion(
    messages=[{"role": "user", "content": "Quick classification"}],
    prefer_fast=True
)
```

### AI Models (2026-04)
| Provider | Model | Use |
|----------|-------|-----|
| Anthropic | claude-sonnet-4-6 | Primary analysis |
| Google | gemini-2.5-flash | Fast streaming |
| OpenAI | gpt-4o | Agent workflows |
| Ollama | qwen2.5-coder:7b | Offline inference |

### Rules
- Always use `litellm_router.chat_completion()` for new code
- Do NOT use `SampleMindAIManager` — it's deprecated for new features
- Do NOT use old model names like `claude-3-7-sonnet-20250219`
