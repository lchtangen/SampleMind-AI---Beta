---
applyTo: "src/samplemind/integrations/**/*.py"
---

# Integrations Instructions

- LiteLLM Router: `integrations/litellm_router.py` — unified fallback chain: Claude → Gemini → GPT → Ollama
  - Pattern: `await chat_completion(messages=[...], prefer_fast=True)`
  - `prefer_fast=True` routes to gemini-2.5-flash
- Supabase: `integrations/supabase_client.py` — Auth (email/magic link/JWT) + user sync
- Realtime Sync: `integrations/realtime_sync.py` — Supabase Realtime multi-device library sync
- AI models (2026-04): claude-sonnet-4-6, gpt-4o, gemini-2.5-flash, qwen2.5-coder:7b
- Do NOT use old model names like `claude-3-7-sonnet-20250219`
- Do NOT use `SampleMindAIManager` for new features — use `litellm_router` instead
- Ollama runs at `http://localhost:11434` for offline inference
