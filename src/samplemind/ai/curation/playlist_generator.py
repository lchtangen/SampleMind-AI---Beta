"""
Smart Playlist Generator — SampleMind Phase 12

LiteLLM-powered AI curation: generates ordered playlists from a sample library
matching a requested mood, energy arc, and duration.

Energy arcs:
  - "build":   low → mid → high (progressive build-up)
  - "drop":    high → mid → low (winding down)
  - "plateau": stable energy throughout
  - "tension": mid → high → mid → high (tension/release)
  - "custom":  provide explicit arc as comma-separated energy levels

Algorithm:
  1. Retrieve candidate samples from FAISS (mood + energy match)
  2. Order by energy arc using BPM + energy progression
  3. Apply harmonic key compatibility (Camelot Wheel)
  4. Use LiteLLM to write a human-readable narrative description

Usage::

    from samplemind.ai.curation.playlist_generator import PlaylistGenerator

    gen = PlaylistGenerator()
    playlist = await gen.generate(
        mood="dark",
        energy_arc="build",
        duration_minutes=30,
        sample_library=[{"path": ..., "bpm": ..., "energy": ...}, ...]
    )
    print(playlist.name, [s["filename"] for s in playlist.samples])
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

EnergyArc = Literal["build", "drop", "plateau", "tension", "custom"]
ENERGY_ORDER = {"low": 0, "mid": 1, "high": 2}

# Camelot Wheel: adjacent keys are harmonically compatible
CAMELOT_NEIGHBORS: dict[str, list[str]] = {
    "1A": ["12A", "2A", "1B"],
    "2A": ["1A", "3A", "2B"],
    "3A": ["2A", "4A", "3B"],
    "4A": ["3A", "5A", "4B"],
    "5A": ["4A", "6A", "5B"],
    "6A": ["5A", "7A", "6B"],
    "7A": ["6A", "8A", "7B"],
    "8A": ["7A", "9A", "8B"],
    "9A": ["8A", "10A", "9B"],
    "10A": ["9A", "11A", "10B"],
    "11A": ["10A", "12A", "11B"],
    "12A": ["11A", "1A", "12B"],
    "1B": ["12B", "2B", "1A"],
    "2B": ["1B", "3B", "2A"],
    "3B": ["2B", "4B", "3A"],
    "4B": ["3B", "5B", "4A"],
    "5B": ["4B", "6B", "5A"],
    "6B": ["5B", "7B", "6A"],
    "7B": ["6B", "8B", "7A"],
    "8B": ["7B", "9B", "8A"],
    "9B": ["8B", "10B", "9A"],
    "10B": ["9B", "11B", "10A"],
    "11B": ["10B", "12B", "11A"],
    "12B": ["11B", "1B", "12A"],
}


@dataclass
class GeneratedPlaylist:
    """Output of PlaylistGenerator.generate()."""

    name: str
    mood: str
    energy_arc: str
    duration_s: float
    samples: list[dict]  # Each dict: filename, path, bpm, key, energy, ...
    narrative: str  # LiteLLM-generated description
    model_used: str = "rules"


def _arc_energy_sequence(arc: EnergyArc, n_slots: int) -> list[str]:
    """
    Return a target energy level for each position in the playlist.

    Args:
        arc: Energy arc type.
        n_slots: Number of samples in the playlist.

    Returns:
        List of "low" / "mid" / "high" strings.
    """
    if arc == "build":
        thirds = n_slots // 3 or 1
        return ["low"] * thirds + ["mid"] * thirds + ["high"] * (n_slots - 2 * thirds)
    if arc == "drop":
        thirds = n_slots // 3 or 1
        return ["high"] * thirds + ["mid"] * thirds + ["low"] * (n_slots - 2 * thirds)
    if arc == "plateau":
        return ["mid"] * n_slots
    if arc == "tension":
        seq = []
        for i in range(n_slots):
            phase = (i % 4) / 3
            if phase < 0.5:
                seq.append("high")
            elif phase < 0.75:
                seq.append("mid")
            else:
                seq.append("high")
        return seq
    # custom / unknown — default plateau
    return ["mid"] * n_slots


def _harmonic_score(key_a: str | None, key_b: str | None) -> float:
    """Score harmonic compatibility between two Camelot keys. 1.0 = perfect."""
    if not key_a or not key_b:
        return 0.5
    if key_a == key_b:
        return 1.0
    if key_b in CAMELOT_NEIGHBORS.get(key_a, []):
        return 0.85
    return 0.3


def _bpm_score(bpm_a: float | None, bpm_b: float | None) -> float:
    """Score BPM compatibility. Penalizes large jumps."""
    if not bpm_a or not bpm_b:
        return 0.5
    ratio = max(bpm_a, bpm_b) / min(bpm_a, bpm_b)
    if ratio <= 1.05:
        return 1.0
    if ratio <= 1.10:
        return 0.85
    if ratio <= 1.25:
        return 0.60
    return 0.3


class PlaylistGenerator:
    """
    AI-curated playlist generator.

    Combines rule-based energy arc sorting with LiteLLM narrative generation.
    """

    def __init__(self) -> None:
        self._llm_available: bool = True

    async def generate(
        self,
        mood: str,
        energy_arc: EnergyArc = "build",
        duration_minutes: float = 30.0,
        sample_library: list[dict] | None = None,
        use_faiss: bool = True,
    ) -> GeneratedPlaylist:
        """
        Generate a curated playlist.

        Args:
            mood: Target mood (e.g. "dark", "euphoric", "chill").
            energy_arc: Energy progression pattern.
            duration_minutes: Desired total playlist duration.
            sample_library: Optional list of sample dicts. If None, queries FAISS.
            use_faiss: Whether to query FAISS for initial candidates.

        Returns:
            GeneratedPlaylist with ordered samples and narrative.
        """
        target_duration_s = duration_minutes * 60.0

        # Step 1: Get candidate samples
        candidates = await self._get_candidates(
            mood=mood,
            energy_arc=energy_arc,
            sample_library=sample_library,
            use_faiss=use_faiss,
        )

        if not candidates:
            return GeneratedPlaylist(
                name=f"{mood.title()} — {energy_arc.title()} ({duration_minutes:.0f} min)",
                mood=mood,
                energy_arc=energy_arc,
                duration_s=0.0,
                samples=[],
                narrative="No matching samples found in library.",
            )

        # Step 2: Select and order samples to fill duration
        ordered = self._order_by_arc(
            candidates=candidates,
            energy_arc=energy_arc,
            target_duration_s=target_duration_s,
        )

        actual_duration = sum(s.get("duration_s", 30.0) for s in ordered)

        # Step 3: Generate narrative with LiteLLM
        narrative, model_used = await self._generate_narrative(
            mood=mood,
            energy_arc=energy_arc,
            samples=ordered,
            duration_minutes=actual_duration / 60.0,
        )

        name = f"{mood.title()} — {energy_arc.title()} ({actual_duration / 60:.1f} min)"
        return GeneratedPlaylist(
            name=name,
            mood=mood,
            energy_arc=energy_arc,
            duration_s=actual_duration,
            samples=ordered,
            narrative=narrative,
            model_used=model_used,
        )

    async def _get_candidates(
        self,
        mood: str,
        energy_arc: EnergyArc,
        sample_library: list[dict] | None,
        use_faiss: bool,
    ) -> list[dict]:
        """Get candidate samples matching the mood."""
        if sample_library:
            # Filter by mood if mood_labels available
            filtered = [
                s
                for s in sample_library
                if not s.get("mood_labels")
                or mood.lower() in [m.lower() for m in s.get("mood_labels", [])]
            ]
            return filtered or sample_library  # fallback: all samples

        if use_faiss:
            try:
                from samplemind.core.search.faiss_index import get_index

                idx = get_index()
                if not idx.is_empty:
                    query = f"{mood} audio sample"
                    results = idx.search_text(query, top_k=100)
                    return [
                        {
                            "filename": r.filename,
                            "path": r.path,
                            "bpm": r.metadata.get("bpm"),
                            "key": r.metadata.get("key"),
                            "camelot_key": None,
                            "energy": r.metadata.get("energy"),
                            "duration_s": 30.0,  # default if unknown
                            "mood_labels": r.metadata.get("mood_labels", []),
                            "genre_labels": r.metadata.get("genre_labels", []),
                        }
                        for r in results
                    ]
            except Exception as exc:
                logger.warning("FAISS query failed: %s", exc)

        return []

    def _order_by_arc(
        self,
        candidates: list[dict],
        energy_arc: EnergyArc,
        target_duration_s: float,
    ) -> list[dict]:
        """Order candidates to match the energy arc, filling target duration."""
        # Group by energy level
        by_energy: dict[str, list[dict]] = {"low": [], "mid": [], "high": []}
        for s in candidates:
            energy = (s.get("energy") or "mid").lower()
            if energy not in by_energy:
                energy = "mid"
            by_energy[energy].append(s)

        # Estimate how many slots we need
        avg_duration = 30.0
        if candidates:
            durations = [
                s.get("duration_s", 30.0) for s in candidates if s.get("duration_s")
            ]
            if durations:
                avg_duration = sum(durations) / len(durations)

        n_slots = max(4, int(target_duration_s / avg_duration))
        arc_sequence = _arc_energy_sequence(energy_arc, n_slots)

        # Greedily pick samples following the arc
        used_indices: dict[str, int] = {"low": 0, "mid": 0, "high": 0}
        ordered: list[dict] = []
        accumulated_s = 0.0

        for target_energy in arc_sequence:
            pool = by_energy[target_energy]
            if not pool:
                # fall back to any
                for fallback in ["mid", "low", "high"]:
                    if by_energy[fallback]:
                        pool = by_energy[fallback]
                        target_energy = fallback
                        break

            if not pool:
                continue

            idx = used_indices[target_energy] % len(pool)
            sample = pool[idx]
            used_indices[target_energy] += 1

            ordered.append(sample)
            accumulated_s += sample.get("duration_s", 30.0)

            if accumulated_s >= target_duration_s:
                break

        return ordered

    async def _generate_narrative(
        self,
        mood: str,
        energy_arc: str,
        samples: list[dict],
        duration_minutes: float,
    ) -> tuple[str, str]:
        """Generate a narrative description using LiteLLM."""
        if not self._llm_available or not samples:
            return (
                self._fallback_narrative(
                    mood, energy_arc, len(samples), duration_minutes
                ),
                "rules",
            )

        sample_summary = "; ".join(
            f"{s['filename']} ({s.get('energy', '?')} energy, {s.get('bpm', '?')} BPM)"
            for s in samples[:8]
        )

        prompt = (
            f"Write a 2-sentence DJ set description for a {duration_minutes:.0f}-minute "
            f"'{mood}' playlist with a '{energy_arc}' energy arc. "
            f"Sample selection: {sample_summary}. "
            "Be evocative and music-production focused. No hashtags."
        )

        try:
            from samplemind.integrations.litellm_router import chat_completion

            response = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                prefer_fast=True,
                max_tokens=150,
                temperature=0.8,
            )
            text = response.choices[0].message.content.strip()
            model = response.model or "litellm"
            return text, model

        except Exception as exc:
            logger.debug("LiteLLM narrative failed: %s", exc)
            self._llm_available = False
            return (
                self._fallback_narrative(
                    mood, energy_arc, len(samples), duration_minutes
                ),
                "rules",
            )

    @staticmethod
    def _fallback_narrative(mood: str, arc: str, count: int, duration: float) -> str:
        return (
            f"A {duration:.0f}-minute {mood} session with {count} samples, "
            f"following a {arc} energy arc. "
            "Curated by SampleMind AI for maximum creative flow."
        )
