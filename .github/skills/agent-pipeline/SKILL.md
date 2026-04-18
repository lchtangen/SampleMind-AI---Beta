---
name: agent-pipeline
description: Guide for building and modifying the LangGraph multi-agent pipeline. Use when adding nodes, modifying state, or changing agent flow.
---

## LangGraph Agent Pipeline

### Architecture
- **Graph:** `src/samplemind/ai/agents/graph.py` — `build_graph()` with StateGraph
- **State:** `src/samplemind/ai/agents/state.py` — `AudioAnalysisState` TypedDict
- **Memory:** `src/samplemind/ai/agents/memory.py` — FAISS-backed conversation memory

### Current Flow (9 nodes)
```
router → analysis → tagging → mixing → quality → recommendations → pack_builder → categorizer → micro_timing → aggregator → END
```

### Adding a New Node
1. Create `src/samplemind/ai/agents/new_node.py`:
```python
from samplemind.ai.agents.state import AudioAnalysisState

async def new_node(state: AudioAnalysisState) -> AudioAnalysisState:
    # Your logic here
    state["new_field"] = result
    return state
```

2. Add field to `AudioAnalysisState` in `state.py`
3. Register in `build_graph()` in `graph.py`:
```python
graph.add_node("new_node", new_node)
graph.add_edge("previous_node", "new_node")
```

### Memory Integration
- `router_node` injects recalled conversation context via `AgentMemory.recall()`
- `aggregator_node` stores completed analyses via `AgentMemory.store()`
