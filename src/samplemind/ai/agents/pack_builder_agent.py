"""
PackBuilderAgent — Automated sample pack organization and metadata generation.

Given analysis + tags, generates a structured pack manifest: folder structure,
file naming convention, metadata JSON, and README template.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


def pack_builder_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Build a sample pack manifest from the analysis results.
    """
    file_path = state.get("file_path", "")
    tags = state.get("tags", {}) or {}
    features = state.get("audio_features", {}) or {}
    mixing = state.get("mixing_recommendations", {}) or {}
    analysis = state.get("analysis_result", {}) or {}

    updates: dict[str, Any] = {
        "current_stage": "pack_builder",
        "progress_pct": 92,
        "messages": state.get("messages", []) + ["📦 Building pack manifest…"],
    }

    # ── Derive pack metadata ─────────────────────────────────────────────────
    genre = (tags.get("genre") or ["unknown"])[0]
    bpm = features.get("bpm") or 0.0
    key = features.get("key", "Unknown")
    scale = features.get("scale", "major")
    energy = tags.get("energy", "medium")
    camelot = mixing.get("camelot_position", "")

    # ── Build suggested filename ─────────────────────────────────────────────
    stem = Path(file_path).stem if file_path else "sample"
    bpm_str = f"{round(bpm)}bpm" if bpm else "unknownbpm"
    key_str = f"{key}{scale[0].upper()}" if key != "Unknown" else "UNK"
    suggested_filename = f"{stem}_{bpm_str}_{key_str}_{energy}.wav"

    # ── Build folder structure suggestion ────────────────────────────────────
    folder_path = f"{genre.replace(' ', '-').lower()}/{bpm_str}/{key_str}"

    # ── Pack metadata dict (JSON-serializable) ───────────────────────────────
    pack_manifest = {
        "version": "1.0",
        "source_file": file_path,
        "suggested_filename": suggested_filename,
        "folder_path": folder_path,
        "metadata": {
            "bpm": round(bpm, 2) if bpm else None,
            "key": key,
            "scale": scale,
            "camelot": camelot,
            "genre": tags.get("genre", []),
            "mood": tags.get("mood", []),
            "energy": energy,
            "instrument_hints": tags.get("instrument_hints", []),
            "raw_labels": tags.get("raw_labels", []),
            "duration_s": features.get("duration"),
            "sample_rate": features.get("sample_rate"),
        },
        "ai_summary": analysis.get("summary", ""),
        "readme_template": (
            f"# {stem}\n\n"
            f"**Genre:** {genre}  \n"
            f"**BPM:** {round(bpm)} | **Key:** {key} {scale} (Camelot: {camelot})  \n"
            f"**Energy:** {energy}  \n"
            f"**Mood:** {', '.join(tags.get('mood', []))}  \n\n"
            f"## AI Notes\n{analysis.get('summary', '_No AI analysis available._')}\n\n"
            f"## Mixing Tips\n"
            f"Compatible keys: {', '.join(mixing.get('compatible_camelot_keys', []))}  \n"
            f"BPM range: {mixing.get('bpm_compatible_range', 'N/A')}\n"
        ),
    }

    updates["pack_manifest"] = pack_manifest
    updates["messages"] = state.get("messages", []) + ["✅ Pack manifest ready"]
    updates["progress_pct"] = 95

    return updates
