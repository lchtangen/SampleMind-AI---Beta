---
applyTo: "src/samplemind/ai/agents/**/*.py"
---

# LangGraph Agent Pipeline Instructions

- Graph definition: `ai/agents/graph.py` — `build_graph()` builds the StateGraph
- State: `ai/agents/state.py` — `AudioAnalysisState` TypedDict with `conversation_history` field
- 9 nodes: router → analysis → tagging → mixing → quality → recommendations → pack_builder → categorizer → micro_timing → aggregator → END
- Memory: `ai/agents/memory.py` — FAISS-backed AgentMemory (P3-014)
  - router_node injects recalled conversation context
  - aggregator_node stores completed analyses
- AI calls: Use `litellm_router.chat_completion()` — NOT direct anthropic/openai SDK calls
- Each node is a separate file: `analysis_agent.py`, `tagging_agent.py`, `mixing_agent.py`, etc.
- Nodes must accept and return `AudioAnalysisState` dict
- New nodes must be registered in `build_graph()` with proper edges
- Agent tasks run via Celery: `core/tasks/agent_tasks.py`
