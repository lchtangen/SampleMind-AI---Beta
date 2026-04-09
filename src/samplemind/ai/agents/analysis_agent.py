"""
AnalysisAgent — Orchestrates AudioEngine + Claude for comprehensive music analysis.

Uses Claude (claude-sonnet-4-6) with tool_use to drive the audio engine,
then synthesizes the raw features into a structured analysis report.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


def analysis_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Run core audio analysis.

    1. Loads audio features via AudioEngine (cached).
    2. Sends features to Claude with tool_use for deep interpretation.
    3. Returns structured analysis result.
    """
    file_path = state.get("file_path", "")
    if not file_path:
        return {"errors": state.get("errors", []) + ["AnalysisAgent: no file_path"]}

    updates: Dict[str, Any] = {
        "current_stage": "analysis",
        "progress_pct": 10,
        "messages": state.get("messages", []) + ["🔬 Analyzing audio features…"],
    }

    try:
        # ── Step 1: Extract audio features ─────────────────────────────────
        from samplemind.core.engine.audio_engine import AnalysisLevel, AudioEngine

        engine = AudioEngine()
        features = engine.analyze_file(file_path, level=AnalysisLevel.STANDARD)
        features_dict = {
            "bpm": features.bpm,
            "key": features.key,
            "scale": features.scale,
            "duration": features.duration,
            "sample_rate": features.sample_rate,
            "rms_energy": features.rms_energy,
            "spectral_centroid": features.spectral_centroid,
            "spectral_bandwidth": features.spectral_bandwidth,
            "zero_crossing_rate": features.zero_crossing_rate,
            "mfcc_mean": features.mfcc_mean[:5] if features.mfcc_mean is not None else [],
        }
        updates["audio_features"] = features_dict
        updates["duration"] = features.duration
        updates["sample_rate"] = features.sample_rate
        updates["progress_pct"] = 25

    except Exception as exc:
        logger.warning("AudioEngine analysis failed: %s", exc)
        features_dict = state.get("audio_features", {})
        updates["errors"] = state.get("errors", []) + [f"AudioEngine: {exc}"]

    analysis_depth = state.get("analysis_depth", "standard")

    try:
        if analysis_depth == "deep":
            # ── Step 2a: Deep mode — Claude tool_use loop ──────────────────
            from samplemind.ai.agents.tool_use import run_tool_use_loop
            from pathlib import Path

            system_prompt = (
                "You are an expert music production AI. You have access to SampleMind "
                "tools that analyse audio files. Use the tools to gather data, then "
                "synthesise a comprehensive, structured analysis report in JSON with keys: "
                "summary, detailed_analysis, production_tips, creative_ideas, "
                "fl_studio_recommendations, harmonic_analysis, confidence_score."
            )
            user_prompt = (
                f"Analyse the audio sample at: {file_path}\n\n"
                f"Pre-extracted features: {json.dumps(features_dict, indent=2)}\n\n"
                "Use the tag_sample and get_recommendations tools to enrich the analysis, "
                "then provide your full structured report."
            )
            tool_result = run_tool_use_loop(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model="claude-sonnet-4-6",
                max_tokens=4096,
            )
            updates["analysis_result"] = {
                "summary": tool_result["text"][:500] if tool_result["text"] else "Deep analysis complete",
                "detailed_analysis": tool_result["text"],
                "provider": "claude-sonnet-4-6 (tool_use)",
                "tokens": sum(
                    len(json.dumps(tc)) for tc in tool_result.get("tool_calls", [])
                ),
                "tool_calls": tool_result.get("tool_calls", []),
            }
            updates["tool_calls"] = tool_result.get("tool_calls", [])

        else:
            # ── Step 2b: Standard/quick mode — direct AI manager call ──────
            from samplemind.integrations.ai_manager import AnalysisType, SampleMindAIManager
            import asyncio

            mgr = SampleMindAIManager()
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(
                    mgr.analyze_music(
                        audio_features=features_dict,
                        analysis_type=AnalysisType.COMPREHENSIVE_ANALYSIS,
                        user_context={"file": file_path},
                    )
                )
            finally:
                loop.close()

            if result:
                updates["analysis_result"] = {
                    "summary": result.summary,
                    "detailed_analysis": result.detailed_analysis,
                    "provider": result.provider_used,
                    "tokens": result.tokens_used,
                }

        updates["progress_pct"] = 40
        updates["messages"] = state.get("messages", []) + ["✅ Analysis complete"]

    except Exception as exc:
        logger.error("Claude analysis failed: %s", exc)
        updates["errors"] = updates.get("errors", state.get("errors", [])) + [
            f"ClaudeAnalysis: {exc}"
        ]
        updates["analysis_result"] = {
            "summary": "Audio analysis completed (AI unavailable)",
            "detailed_analysis": str(features_dict),
            "provider": "fallback",
        }

    return updates
