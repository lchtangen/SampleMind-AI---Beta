"""
Gap Analyzer — SampleMind Phase 12

Analyzes a sample library to identify missing genre/mood/key/BPM coverage
and suggests specific samples/packs to fill the gaps.

Uses LiteLLM (Claude) to generate human-readable gap reports.

Usage::

    from samplemind.ai.curation.gap_analyzer import GapAnalyzer

    analyzer = GapAnalyzer()
    report = await analyzer.analyze(sample_library)
    print(report.summary)
    for gap in report.gaps:
        print(f"Missing: {gap.dimension} = {gap.value} ({gap.severity})")
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Target distribution targets (what a "complete" library looks like)
TARGET_ENERGY_DIST = {"low": 0.25, "mid": 0.45, "high": 0.30}
TARGET_MOOD_DIST = {
    "dark": 0.20, "chill": 0.18, "aggressive": 0.15,
    "euphoric": 0.15, "melancholic": 0.12, "neutral": 0.20,
}
COMMON_KEYS = ["C", "Cm", "Am", "Dm", "Fm", "Gm", "Bb", "Eb", "F", "G", "D"]
COMMON_BPM_RANGES = [(60, 90), (90, 120), (120, 140), (140, 160), (160, 200)]


@dataclass
class Gap:
    """A single identified gap in the library."""
    dimension: str          # "energy", "mood", "key", "bpm_range"
    value: str              # The missing value (e.g. "low", "Fm", "140-160")
    current_pct: float      # Current coverage percentage
    target_pct: float       # Ideal coverage percentage
    deficit: float          # target_pct - current_pct
    severity: str           # "critical" | "moderate" | "minor"
    suggestion: str         # Recommended sample type to add


@dataclass
class GapReport:
    """Full gap analysis report."""
    total_samples: int
    gaps: list[Gap]
    summary: str
    suggestions: list[str]  # 5 specific pack/sample suggestions
    coverage_score: float   # 0–100 overall coverage score
    model_used: str = "rules"


class GapAnalyzer:
    """
    Library gap analyzer using statistical analysis + LiteLLM.
    """

    async def analyze(
        self,
        sample_library: list[dict],
        use_llm: bool = True,
    ) -> GapReport:
        """
        Analyze a sample library for coverage gaps.

        Args:
            sample_library: List of sample dicts, each with:
                            filename, energy, mood_labels, key, bpm, genre_labels
            use_llm: Whether to enhance with LiteLLM narrative.

        Returns:
            GapReport with identified gaps and suggestions.
        """
        n = len(sample_library)
        if n == 0:
            return GapReport(
                total_samples=0,
                gaps=[],
                summary="Library is empty — add samples to begin analysis.",
                suggestions=[],
                coverage_score=0.0,
            )

        gaps: list[Gap] = []

        # Energy distribution analysis
        energy_counts = Counter(
            (s.get("energy") or "mid").lower() for s in sample_library
        )
        for level, target in TARGET_ENERGY_DIST.items():
            actual = energy_counts.get(level, 0) / n
            deficit = target - actual
            if deficit > 0.05:
                gaps.append(Gap(
                    dimension="energy",
                    value=level,
                    current_pct=round(actual * 100, 1),
                    target_pct=round(target * 100, 1),
                    deficit=round(deficit * 100, 1),
                    severity=_severity(deficit),
                    suggestion=f"Add more {level}-energy samples (loops, one-shots)",
                ))

        # Mood distribution analysis
        all_moods: list[str] = []
        for s in sample_library:
            moods = s.get("mood_labels") or []
            all_moods.extend(m.lower() for m in moods)
        mood_counts = Counter(all_moods) if all_moods else Counter()

        for mood, target in TARGET_MOOD_DIST.items():
            actual = mood_counts.get(mood, 0) / max(len(all_moods), 1)
            deficit = target - actual
            if deficit > 0.05:
                gaps.append(Gap(
                    dimension="mood",
                    value=mood,
                    current_pct=round(actual * 100, 1),
                    target_pct=round(target * 100, 1),
                    deficit=round(deficit * 100, 1),
                    severity=_severity(deficit),
                    suggestion=f"Add more {mood} mood samples",
                ))

        # Key coverage analysis
        keys_present = {(s.get("key") or "").strip() for s in sample_library if s.get("key")}
        for key in COMMON_KEYS:
            if key not in keys_present:
                gaps.append(Gap(
                    dimension="key",
                    value=key,
                    current_pct=0.0,
                    target_pct=5.0,
                    deficit=5.0,
                    severity="minor",
                    suggestion=f"Add samples in key {key} for harmonic diversity",
                ))

        # BPM range coverage
        bpms = [s.get("bpm") for s in sample_library if s.get("bpm")]
        for lo, hi in COMMON_BPM_RANGES:
            count = sum(1 for b in bpms if lo <= b < hi)
            pct = count / max(len(bpms), 1) * 100
            if pct < 10.0:
                gaps.append(Gap(
                    dimension="bpm_range",
                    value=f"{lo}–{hi}",
                    current_pct=round(pct, 1),
                    target_pct=15.0,
                    deficit=round(15.0 - pct, 1),
                    severity=_severity((15.0 - pct) / 100),
                    suggestion=f"Add samples at {lo}–{hi} BPM",
                ))

        # Sort by severity
        severity_order = {"critical": 0, "moderate": 1, "minor": 2}
        gaps.sort(key=lambda g: (severity_order.get(g.severity, 3), -g.deficit))

        # Coverage score: penalize gaps
        critical = sum(1 for g in gaps if g.severity == "critical")
        moderate = sum(1 for g in gaps if g.severity == "moderate")
        coverage_score = max(0.0, 100.0 - critical * 15 - moderate * 5 - len(gaps) * 1)

        # Build suggestions list (top 5 gaps → specific recommendations)
        top_gaps = gaps[:5]
        suggestions = [g.suggestion for g in top_gaps]
        if not suggestions:
            suggestions = ["Library coverage looks good! Add more variety to expand options."]

        # Generate summary with LiteLLM
        summary, model_used = await self._generate_summary(
            n=n,
            gaps=top_gaps,
            coverage_score=coverage_score,
            use_llm=use_llm,
        )

        return GapReport(
            total_samples=n,
            gaps=gaps,
            summary=summary,
            suggestions=suggestions,
            coverage_score=round(coverage_score, 1),
            model_used=model_used,
        )

    async def _generate_summary(
        self,
        n: int,
        gaps: list[Gap],
        coverage_score: float,
        use_llm: bool,
    ) -> tuple[str, str]:
        """Generate a human-readable summary using LiteLLM."""
        if not use_llm or not gaps:
            return self._fallback_summary(n, gaps, coverage_score), "rules"

        gaps_desc = "; ".join(
            f"{g.dimension}={g.value} (only {g.current_pct:.0f}%, need {g.target_pct:.0f}%)"
            for g in gaps[:4]
        )
        prompt = (
            f"Write a 2-sentence producer-friendly library analysis. "
            f"Library: {n} samples, coverage score: {coverage_score:.0f}/100. "
            f"Top gaps: {gaps_desc}. "
            "Focus on what the producer should buy/create next. Be direct and actionable."
        )

        try:
            from samplemind.integrations.litellm_router import chat_completion

            response = await chat_completion(
                messages=[{"role": "user", "content": prompt}],
                prefer_fast=True,
                max_tokens=120,
                temperature=0.6,
            )
            return response.choices[0].message.content.strip(), response.model or "litellm"

        except Exception as exc:
            logger.debug("LiteLLM gap summary failed: %s", exc)
            return self._fallback_summary(n, gaps, coverage_score), "rules"

    @staticmethod
    def _fallback_summary(n: int, gaps: list[Gap], score: float) -> str:
        critical = [g for g in gaps if g.severity == "critical"]
        if not gaps:
            return f"Your library of {n} samples has excellent coverage (score: {score:.0f}/100)."
        if critical:
            crit_desc = ", ".join(f"{g.dimension}={g.value}" for g in critical[:3])
            return (
                f"Library has {n} samples (score: {score:.0f}/100). "
                f"Critical gaps in: {crit_desc}. "
                "Prioritize adding these sample types."
            )
        return (
            f"Library of {n} samples scores {score:.0f}/100. "
            f"Moderate gaps detected in {len(gaps)} dimensions. "
            "See suggestions below."
        )


def _severity(deficit: float) -> str:
    if deficit > 0.15:
        return "critical"
    if deficit > 0.07:
        return "moderate"
    return "minor"
