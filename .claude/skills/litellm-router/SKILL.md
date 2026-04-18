---
name: litellm-router
description: LiteLLM multi-provider AI router with Claude→Gemini→GPT→Ollama fallback
---

## LiteLLM Router

### Location
`src/samplemind/integrations/litellm_router.py`

### Fallback Chain
1. **Claude** (claude-sonnet-4-6) — Primary analysis + curation
2. **Gemini** (gemini-2.5-flash) — Fast streaming
3. **GPT** (gpt-4o) — Agent workflows
4. **Ollama** (qwen2.5-coder:7b @ localhost:11434) — Offline inference

### Usage
```python
from samplemind.integrations.litellm_router import chat_completion

# Standard call (routes to Claude first)
response = await chat_completion(
    messages=[{"role": "user", "content": "Analyze this audio"}],
)

# Fast call (routes to Gemini)
response = await chat_completion(
    messages=[{"role": "user", "content": "Quick tag this sample"}],
    prefer_fast=True,
)
```

### Rules
- **Always** use `litellm_router.chat_completion()` — never direct SDK calls
- Do NOT use old model names like `claude-3-7-sonnet-20250219`
- Do NOT use `SampleMindAIManager` for new features
- `prefer_fast=True` routes to gemini-2.5-flash for speed
