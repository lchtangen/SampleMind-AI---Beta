"""
SampleMind AI — Multi-Agent Orchestration System (Phase 15 / v3.0)

Uses LangGraph ^0.2 to coordinate specialized agents for audio analysis,
tagging, mixing recommendations, and sample pack building.

Entry point:
    from samplemind.ai.agents import run_analysis_pipeline, AudioAnalysisState
"""

from samplemind.ai.agents.graph import build_graph, run_analysis_pipeline
from samplemind.ai.agents.state import AudioAnalysisState

__all__ = ["run_analysis_pipeline", "build_graph", "AudioAnalysisState"]
