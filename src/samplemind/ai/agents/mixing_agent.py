"""
MixingAgent — BPM/key compatibility, harmonic analysis, and layering recommendations.

Uses the Camelot Wheel for harmonic key matching and generates mixing/layering
advice based on audio features and the analysis result.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)

# ── Camelot Wheel — key → Camelot position ───────────────────────────────────
# Maps (key_name, scale) to Camelot number (1–12) and letter (A=minor, B=major)
_CAMELOT: Dict[str, str] = {
    # Major keys (B)
    "C major": "8B",  "G major": "9B",  "D major": "10B", "A major": "11B",
    "E major": "12B", "B major": "1B",  "F# major": "2B", "Db major": "3B",
    "Ab major": "4B", "Eb major": "5B", "Bb major": "6B", "F major": "7B",
    # Minor keys (A)
    "A minor": "8A",  "E minor": "9A",  "B minor": "10A", "F# minor": "11A",
    "C# minor": "12A","G# minor": "1A", "D# minor": "2A", "Bb minor": "3A",
    "F minor": "4A",  "C minor": "5A",  "G minor": "6A",  "D minor": "7A",
}


def _camelot_position(key: str, scale: str) -> str:
    """Return Camelot Wheel position string like '8B' or '5A'."""
    lookup = f"{key} {scale}"
    return _CAMELOT.get(lookup, "Unknown")


def _compatible_keys(position: str) -> List[str]:
    """Return list of compatible Camelot positions (±1 number, same or opposite letter)."""
    if position == "Unknown" or len(position) < 2:
        return []
    try:
        num = int(position[:-1])
        letter = position[-1]
    except ValueError:
        return []
    other = "A" if letter == "B" else "B"
    return [
        f"{(num - 1) % 12 or 12}{letter}",
        f"{num % 12 + 1 or 1}{letter}",
        f"{num}{other}",  # relative major/minor
    ]


def mixing_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Generate mixing and layering recommendations.
    """
    features = state.get("audio_features", {})
    tags = state.get("tags", {})

    updates: Dict[str, Any] = {
        "current_stage": "mixing",
        "progress_pct": 70,
        "messages": state.get("messages", []) + ["🎚️ Computing mixing recommendations…"],
    }

    bpm = features.get("bpm") or 0.0
    key = features.get("key", "Unknown")
    scale = features.get("scale", "major")
    energy = tags.get("energy", "medium") if tags else "medium"
    rms = features.get("rms_energy") or 0.0
    spectral_centroid = features.get("spectral_centroid") or 0.0

    camelot = _camelot_position(key, scale)
    compatible = _compatible_keys(camelot)

    # ── BPM compatibility range (±6%) ───────────────────────────────────────
    bpm_lo = round(bpm * 0.94, 1) if bpm else 0
    bpm_hi = round(bpm * 1.06, 1) if bpm else 0

    # ── Frequency layering advice based on spectral centroid ─────────────────
    if spectral_centroid > 3000:
        freq_role = "high-frequency element (synth lead, hi-hat, snare)"
        layer_with = "bass and kick (sub + low-mid elements)"
    elif spectral_centroid > 800:
        freq_role = "mid-frequency element (pad, chord, mid percussion)"
        layer_with = "bass below and high elements above for full spectrum"
    else:
        freq_role = "low-frequency element (bass, kick, sub)"
        layer_with = "high-frequency percussion and lead elements"

    # ── EQ headroom suggestions ──────────────────────────────────────────────
    eq_tips: List[str] = []
    if rms > 0.2:
        eq_tips.append("High RMS — consider -3dB gain reduction before mixing")
    if spectral_centroid < 500:
        eq_tips.append("Heavy low-end — high-pass at 40Hz to clean sub frequencies")
    if spectral_centroid > 4000:
        eq_tips.append("Bright top-end — consider gentle shelving cut above 12kHz")

    # ── Tempo sync suggestions ───────────────────────────────────────────────
    tempo_tips: List[str] = []
    if bpm:
        half = round(bpm / 2, 1)
        double = round(bpm * 2, 1)
        tempo_tips = [
            f"Original BPM: {bpm:.1f}",
            f"Compatible BPM range: {bpm_lo}–{bpm_hi}",
            f"Half-time: {half} | Double-time: {double}",
        ]

    mixing_rec = {
        "key": key,
        "scale": scale,
        "camelot_position": camelot,
        "compatible_camelot_keys": compatible,
        "bpm": bpm,
        "bpm_compatible_range": f"{bpm_lo}–{bpm_hi}",
        "frequency_role": freq_role,
        "layer_with": layer_with,
        "energy_level": energy,
        "eq_tips": eq_tips,
        "tempo_tips": tempo_tips,
        "summary": (
            f"This sample is a {freq_role}. "
            f"Key: {key} {scale} (Camelot: {camelot}). "
            f"Mix with keys: {', '.join(compatible) or 'any'}. "
            f"Target BPM: {bpm_lo}–{bpm_hi}."
        ),
    }

    updates["mixing_recommendations"] = mixing_rec
    updates["messages"] = state.get("messages", []) + ["✅ Mixing recommendations ready"]
    updates["progress_pct"] = 78

    return updates
