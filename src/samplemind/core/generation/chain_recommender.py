"""
Sample Chain Recommender (Phase 14)

Intelligent kit building assistant that recommends compatible samples
based on a starting "seed" sample.
"""

import logging
import math
from dataclasses import dataclass, field
from pathlib import Path

# We'll need AudioEngine to get features if not cached
# from samplemind.core.engine.audio_engine import AudioEngine

logger = logging.getLogger(__name__)


@dataclass
class ChainSlot:
    """Definition of a slot in a sample chain"""

    name: str  # e.g., "Snare", "HiHat"
    required_keywords: list[str]  # e.g., ["snare", "clap"]
    frequency_range: tuple[int, int] = (20, 20000)
    preferred_duration_max: float = 5.0


@dataclass
class SampleNode:
    """A sample in the chain"""

    file_path: Path
    slot_name: str
    compatibility_score: float = 0.0
    features: dict = field(default_factory=dict)


class ChainContext:
    """Context for the current chain being built"""

    def __init__(
        self, seed_sample: Path, bpm: float | None = None, key: str | None = None
    ):
        self.seed_sample = seed_sample
        self.bpm = bpm
        self.key = key
        self.nodes: list[SampleNode] = []

    def add_node(self, node: SampleNode):
        self.nodes.append(node)


class ChainRecommender:
    """
    AI-powered sample chain recommender.
    """

    # Standard Kits
    KIT_TEMPLATES = {
        "standard_kit": [
            ChainSlot("Kick", ["kick", "bass drum"], (20, 100)),
            ChainSlot("Snare", ["snare", "clap", "rim"], (200, 5000)),
            ChainSlot("HiHat", ["hat", "closed", "cymbal"], (1000, 20000)),
            ChainSlot("Perc", ["perc", "tom", "bongo", "conga"], (100, 10000)),
        ],
        "techno_rumble": [
            ChainSlot("Kick", ["kick", "rumble"], (20, 80)),
            ChainSlot("Rumble", ["reverb", "sub", "bass"], (30, 100)),
            ChainSlot("Hat_O", ["open", "hat"], (5000, 15000)),
            ChainSlot("Hat_C", ["closed", "hat"], (8000, 18000)),
        ],
    }

    def __init__(self, library_path: Path | None = None):
        """
        Initialize recommender.

        Args:
            library_path: Base path to search for candidates.
                          If None, will need to be provided per request.
        """
        self.library_path = library_path
        logger.info("Chain Recommender Initialized")

    def build_chain(
        self,
        seed_sample: Path,
        template_name: str = "standard_kit",
        search_paths: list[Path] | None = None,
        creativity: float = 0.5,
    ) -> ChainContext:
        """
        Build a complete chain starting from a seed sample.

        Args:
            seed_sample: The starting sample file
            template_name: Name of the kit structure to use
            search_paths: List of directories to search for candidates
            creativity: 0.0 (safe/strict) to 1.0 (random/experimental)

        Returns:
            ChainContext containing the chosen samples
        """
        if template_name not in self.KIT_TEMPLATES:
            logger.warning(f"Template {template_name} not found, using standard_kit")
            template_name = "standard_kit"

        template = self.KIT_TEMPLATES[template_name]

        # Analyze seed to identify what slot it fits (if not specified)
        # For simplicity, we assume the seed is the FIRST slot of the template for now,
        # or we just add it as "Seed" and fill the rest.

        # Let's assume the seed IS the Kick (or first item)
        chain_ctx = ChainContext(seed_sample)

        # Add Seed as first node
        chain_ctx.add_node(SampleNode(seed_sample, template[0].name, 1.0))

        # Search for candidates for remaining slots
        search_dirs = search_paths or ([self.library_path] if self.library_path else [])
        if not search_dirs:
            logger.error("No search paths provided")
            return chain_ctx

        # Iterate remaining slots
        for slot in template[1:]:  # Skip first as it's the seed
            candidates = self._find_candidates(slot, search_dirs)

            if not candidates:
                logger.warning(f"No candidates found for {slot.name}")
                continue

            # Score and Pick
            best_candidate = self._pick_best_candidate(
                candidates, chain_ctx, slot, creativity
            )

            if best_candidate:
                chain_ctx.add_node(best_candidate)

        return chain_ctx

    def _find_candidates(self, slot: ChainSlot, search_dirs: list[Path]) -> list[Path]:
        """Find potential files for a slot based on keywords"""
        candidates = []
        extensions = {".wav", ".mp3", ".flac", ".aiff"}

        # Limit to avoid scanning entire disk if too large
        MAX_CANDIDATES = 50

        for directory in search_dirs:
            if not directory.exists():
                continue

            # Walk and find matches
            for p in directory.rglob("*"):
                if p.suffix.lower() in extensions:
                    # Check keywords
                    name_lower = p.name.lower()
                    if any(kw in name_lower for kw in slot.required_keywords):
                        candidates.append(p)
                        if len(candidates) >= MAX_CANDIDATES:
                            break
            if len(candidates) >= MAX_CANDIDATES:
                break

        return candidates

    def _pick_best_candidate(
        self,
        candidates: list[Path],
        context: ChainContext,
        slot: ChainSlot,
        creativity: float,
    ) -> SampleNode | None:
        """
        Score candidates and pick the best match for the slot.

        Scoring factors (deterministic):
        1. Keyword proximity — how many of the slot's required keywords appear
           in the filename (normalized 0–1).
        2. Frequency range hint — filenames with high/low/mid frequency
           descriptors are matched against the slot's target range.
        3. Creativity factor — blends top score with a diversity bonus to
           surface non-obvious but still contextually appropriate picks.
        """
        if not candidates:
            return None

        scored: list[tuple[float, Path]] = []
        slot_keywords = set(slot.required_keywords)
        freq_lo, freq_hi = slot.frequency_range
        slot_center = (freq_lo + freq_hi) / 2

        # Frequency descriptor hints in filenames → approximate center frequency
        _FREQ_HINTS: dict[str, float] = {
            "sub": 60,
            "bass": 120,
            "low": 200,
            "mid": 1000,
            "upper": 4000,
            "high": 8000,
            "air": 12000,
            "bright": 10000,
        }

        for candidate in candidates:
            name_lower = candidate.stem.lower()

            # 1. Keyword match score (0–1)
            matching_kw = sum(1 for kw in slot_keywords if kw in name_lower)
            keyword_score = matching_kw / max(len(slot_keywords), 1)

            # 2. Frequency proximity score (0–1)
            # Estimate file's frequency focus from name descriptors
            detected_centers = [
                freq for hint, freq in _FREQ_HINTS.items() if hint in name_lower
            ]
            if detected_centers:
                file_center = sum(detected_centers) / len(detected_centers)
                # Normalise distance on a log scale (octaves)
                octave_distance = abs(
                    math.log2(max(file_center, 1)) - math.log2(max(slot_center, 1))
                )
                freq_score = max(0.0, 1.0 - octave_distance / 4.0)
            else:
                freq_score = 0.5  # neutral when no hint found

            # 3. Composite score with creativity blending
            # Low creativity → weight toward keyword match
            # High creativity → give more weight to freq diversity
            base_score = (1 - creativity) * keyword_score + creativity * freq_score
            scored.append((base_score, candidate))

        # Sort descending by score; pick the top candidate
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, chosen = scored[0]

        return SampleNode(
            file_path=chosen,
            slot_name=slot.name,
            compatibility_score=round(best_score, 4),
        )
