"""
Micro-Timing Agent — LangGraph Node

Analyzes micro-timing characteristics (swing, pocket, ghost notes, human
feel, groove DNA) using MicroTimingAnalyzer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


def micro_timing_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    LangGraph node: micro-timing analysis.

    Reads file_path from state, runs MicroTimingAnalyzer, and returns
    the micro-timing results dict.
    """
    file_path = state.get("file_path", "")
    messages = list(state.get("messages", []))
    errors = list(state.get("errors", []))

    if not file_path or not Path(file_path).exists():
        errors.append("micro_timing: file_path missing or not found")
        return {
            "micro_timing": None,
            "errors": errors,
            "current_stage": "micro_timing",
            "progress_pct": 85,
        }

    try:
        from samplemind.core.analysis.micro_timing_analyzer import (
            MicroTimingAnalyzer,
        )

        analyzer = MicroTimingAnalyzer()

        # Load audio
        try:
            import librosa

            y, sr = librosa.load(file_path, sr=22050, mono=True)
        except ImportError:
            logger.warning("librosa unavailable — skipping micro-timing")
            return {
                "micro_timing": None,
                "errors": errors + ["micro_timing: librosa not available"],
                "current_stage": "micro_timing",
                "progress_pct": 85,
            }

        # Use BPM from prior analysis if available
        bpm = None
        features = state.get("audio_features", {})
        if features and "bpm" in features:
            bpm = features["bpm"]

        result = analyzer.analyze(y, sr, bpm=bpm)

        messages.append(
            f"⏱️ Micro-timing: {result.swing.style} feel, "
            f"human score {result.human_feel_score:.0%}, "
            f"pocket {result.pocket.feel}"
        )

        return {
            "micro_timing": result.to_dict(),
            "messages": messages,
            "current_stage": "micro_timing",
            "progress_pct": 85,
        }

    except Exception as exc:
        logger.error("MicroTimingAgent failed: %s", exc)
        errors.append(f"micro_timing: {exc}")
        return {
            "micro_timing": None,
            "errors": errors,
            "current_stage": "micro_timing",
            "progress_pct": 85,
        }
