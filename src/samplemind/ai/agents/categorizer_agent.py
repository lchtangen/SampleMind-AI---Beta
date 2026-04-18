"""
Categorizer Agent — LangGraph Node

Auto-categorizes the audio file using the SmartAutoCategorizer, adding
category, subcategory, character tags, and suggested library path to
the pipeline state.
"""

from __future__ import annotations

import logging
from pathlib import Path

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


def categorizer_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    LangGraph node: auto-categorize the audio file.

    Reads file_path from state, runs SmartAutoCategorizer, and returns
    the categorization dict.
    """
    file_path = state.get("file_path", "")
    messages = list(state.get("messages", []))
    errors = list(state.get("errors", []))

    if not file_path or not Path(file_path).exists():
        errors.append("categorizer: file_path missing or not found")
        return {
            "categorization": None,
            "errors": errors,
            "current_stage": "categorization",
            "progress_pct": 80,
        }

    try:
        import numpy as np

        from samplemind.core.library.auto_categorizer import SmartAutoCategorizer

        categorizer = SmartAutoCategorizer()

        # Load audio
        try:
            import librosa

            y, sr = librosa.load(file_path, sr=22050, mono=True)
        except ImportError:
            logger.warning("librosa unavailable — skipping categorization")
            return {
                "categorization": None,
                "errors": errors + ["categorizer: librosa not available"],
                "current_stage": "categorization",
                "progress_pct": 80,
            }

        result = categorizer.categorize(y, sr, filename=Path(file_path).name)

        messages.append(
            f"🏷️ Categorized: {result.category}/{result.subcategory} "
            f"({result.confidence:.0%} confidence)"
        )

        return {
            "categorization": result.to_dict(),
            "messages": messages,
            "current_stage": "categorization",
            "progress_pct": 80,
        }

    except Exception as exc:
        logger.error("CategorizerAgent failed: %s", exc)
        errors.append(f"categorizer: {exc}")
        return {
            "categorization": None,
            "errors": errors,
            "current_stage": "categorization",
            "progress_pct": 80,
        }
