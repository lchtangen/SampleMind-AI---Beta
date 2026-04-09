"""
TaggingAgent — Multi-label genre/mood/instrument classification + auto-tag writing.

Generates a rich tag set from audio features using:
1. Rule-based heuristics on BPM, key, spectral features (fast, always available)
2. AI-assisted genre/mood/instrument labels when available
"""

from __future__ import annotations

import logging
from typing import Any

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)

# ── BPM-based genre heuristics ────────────────────────────────────────────────
_BPM_GENRE_MAP: list[tuple[tuple[float, float], list[str]]] = [
    ((60, 90), ["hip-hop", "trap", "lo-fi"]),
    ((90, 110), ["r&b", "soul", "pop"]),
    ((110, 130), ["house", "dance-pop", "electropop"]),
    ((128, 145), ["tech-house", "techno", "progressive-house"]),
    ((140, 160), ["drum-and-bass", "jungle", "hardstyle"]),
    ((160, 200), ["gabber", "speedcore", "hard-techno"]),
]

# ── Key-based mood heuristics ─────────────────────────────────────────────────
_MAJOR_MOODS = ["energetic", "happy", "uplifting", "bright"]
_MINOR_MOODS = ["melancholic", "dark", "emotional", "introspective"]


def tagging_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Generate multi-label tags from audio features and analysis.
    """
    features = state.get("audio_features", {})
    state.get("analysis_result", {})

    updates: dict[str, Any] = {
        "current_stage": "tagging",
        "progress_pct": 55,
        "messages": state.get("messages", []) + ["🏷️ Generating tags…"],
    }

    tags: dict[str, Any] = {
        "genre": [],
        "mood": [],
        "energy": "medium",
        "key_info": {},
        "instrument_hints": [],
        "bpm_range": "",
        "raw_labels": [],
    }

    # ── BPM-based genre suggestions ──────────────────────────────────────────
    bpm = features.get("bpm") or 0.0
    genre_suggestions: list[str] = []
    for (lo, hi), genres in _BPM_GENRE_MAP:
        if lo <= bpm < hi:
            genre_suggestions.extend(genres)
            break
    if not genre_suggestions and bpm > 0:
        genre_suggestions = ["electronic"]
    tags["genre"] = genre_suggestions[:3]  # top 3

    # ── BPM range label ──────────────────────────────────────────────────────
    if bpm < 90:
        tags["bpm_range"] = "slow"
    elif bpm < 120:
        tags["bpm_range"] = "medium"
    elif bpm < 150:
        tags["bpm_range"] = "fast"
    else:
        tags["bpm_range"] = "very-fast"

    # ── Key / scale → mood ───────────────────────────────────────────────────
    key = features.get("key", "")
    scale = features.get("scale", "major")
    tags["key_info"] = {"key": key, "scale": scale}
    if "minor" in str(scale).lower():
        tags["mood"] = _MINOR_MOODS[:2]
    else:
        tags["mood"] = _MAJOR_MOODS[:2]

    # ── Energy from RMS ──────────────────────────────────────────────────────
    rms = features.get("rms_energy") or 0.0
    if rms > 0.15:
        tags["energy"] = "high"
    elif rms > 0.05:
        tags["energy"] = "medium"
    else:
        tags["energy"] = "low"

    # ── Spectral brightness → instrument hints ──────────────────────────────
    centroid = features.get("spectral_centroid") or 0.0
    if centroid > 3000:
        tags["instrument_hints"] = ["synth-lead", "hi-hat", "percussion"]
    elif centroid > 1000:
        tags["instrument_hints"] = ["pad", "pluck", "snare"]
    else:
        tags["instrument_hints"] = ["bass", "kick", "sub"]

    # ── Multi-label genre + mood + instrument (Steps 17 & 18) ────────────────
    file_path = state.get("file_path", "")
    if file_path:
        try:
            from samplemind.ai.classification.instrument_detector import (
                InstrumentDetector,
            )
            from samplemind.ai.classification.mood_detector import MoodDetector
            from samplemind.ai.classification.multi_label_genre import (
                MultiLabelGenreClassifier,
            )

            genre_clf = MultiLabelGenreClassifier(
                threshold=0.30, top_k=5, use_clap=False
            )
            genre_result = genre_clf.classify_file(file_path)
            if genre_result.all_genres:
                tags["genre"] = genre_result.all_genres
                tags["key_info"]["camelot"] = genre_result.camelot

            mood_det = MoodDetector(use_clap=False)
            mood_result = mood_det.detect_file(file_path)
            if mood_result.moods:
                tags["mood"] = mood_result.moods
                tags["valence"] = mood_result.valence
                tags["arousal"] = mood_result.arousal

            instr_det = InstrumentDetector(top_k=3, use_clap=False)
            instr_result = instr_det.detect_file(file_path)
            if instr_result.instruments:
                tags["instrument_hints"] = instr_result.instruments
                tags["instrument_families"] = list(dict.fromkeys(instr_result.families))
                tags["midi_programs"] = instr_result.midi_programs

        except Exception as exc:
            logger.warning("AI classifiers skipped: %s", exc)

    # ── Combine into flat raw_labels list ────────────────────────────────────
    tags["raw_labels"] = list(
        dict.fromkeys(
            tags["genre"]
            + tags["mood"]
            + [tags["energy"], tags["bpm_range"]]
            + tags["instrument_hints"]
        )
    )

    updates["tags"] = tags
    updates["messages"] = state.get("messages", []) + ["✅ Tags generated"]
    updates["progress_pct"] = 65

    return updates
