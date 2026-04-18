---
name: agent-pipeline
description: LangGraph 9-node AI agent pipeline with FAISS-backed memory
---

## Agent Pipeline

### Architecture
```
router → analysis → tagging → mixing → quality → recommendations
       → pack_builder → categorizer → micro_timing → aggregator → END
```

### Key Files
- `ai/agents/graph.py` — `build_graph()` builds the StateGraph
- `ai/agents/state.py` — `AudioAnalysisState` TypedDict
- `ai/agents/memory.py` — FAISS-backed AgentMemory

### Adding a New Node
1. Create `ai/agents/<name>_agent.py`
2. Define function accepting and returning `AudioAnalysisState`
3. Register in `build_graph()` with proper edges
4. Use `litellm_router.chat_completion()` for AI calls

### Memory System
- `router_node` injects recalled conversation context
- `aggregator_node` stores completed analyses
- Same FAISS 512-dim CLAP backend as search

### AI Call Pattern
```python
from samplemind.integrations.litellm_router import chat_completion
response = await chat_completion(
    messages=[{"role": "user", "content": prompt}],
    prefer_fast=True,  # Routes to gemini-2.5-flash
)
```

### Celery Integration
Agent tasks run via `core/tasks/agent_tasks.py`.
