"""
Predictive Trend Engine — Analyze genre/BPM/key trends and forecast gaps.

Endpoints:
  GET /api/v1/trends/analysis   — Current trend data + predictions
  GET /api/v1/trends/gaps       — Identify library gaps vs industry trends
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trends", tags=["trends"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class TrendItem(BaseModel):
    category: str
    value: str
    count: int
    percentage: float
    direction: str = Field(..., description="up|down|stable")
    confidence: float = Field(0.8, ge=0.0, le=1.0)


class TrendForecast(BaseModel):
    prediction: str
    rationale: str
    confidence: float
    timeframe: str = "next 3 months"


class TrendAnalysis(BaseModel):
    generated_at: str
    library_size: int
    bpm_trends: list[TrendItem]
    key_trends: list[TrendItem]
    genre_trends: list[TrendItem]
    mood_trends: list[TrendItem]
    energy_distribution: list[TrendItem]
    forecasts: list[TrendForecast] = []


class GapItem(BaseModel):
    category: str
    gap: str
    severity: str = Field(..., description="high|medium|low")
    recommendation: str
    sample_count_needed: int


class GapAnalysis(BaseModel):
    total_gaps: int
    gaps: list[GapItem]
    library_health_score: float = Field(..., ge=0.0, le=100.0)
    ai_summary: str


# ── Helpers ───────────────────────────────────────────────────────────────────


def _compute_distribution(
    values: list[str], total: int
) -> list[TrendItem]:
    """Count values and return sorted trend items."""
    counts: dict[str, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1

    items = []
    for value, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        items.append(
            TrendItem(
                category="distribution",
                value=value,
                count=count,
                percentage=round((count / total) * 100, 1) if total else 0,
                direction="stable",
            )
        )
    return items


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/analysis")
@rate_limit("30/minute")
async def get_trend_analysis(
    request: Request,
    include_forecasts: bool = Query(True, description="Include AI forecasts"),
) -> TrendAnalysis:
    """
    Analyze your library's trends: BPM ranges, key distribution,
    genre clusters, mood balance, and energy levels.
    Optionally includes AI-powered forecasts.
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return TrendAnalysis(
                generated_at=datetime.now().isoformat(),
                library_size=0,
                bpm_trends=[],
                key_trends=[],
                genre_trends=[],
                mood_trends=[],
                energy_distribution=[],
            )

        entries = idx._entries
        total = len(entries)

        # Collect distributions
        bpm_ranges: list[str] = []
        keys: list[str] = []
        genres: list[str] = []
        moods: list[str] = []
        energies: list[str] = []

        for e in entries:
            if e.bpm:
                if e.bpm < 80:
                    bpm_ranges.append("60-80 (Slow)")
                elif e.bpm < 100:
                    bpm_ranges.append("80-100 (Moderate)")
                elif e.bpm < 120:
                    bpm_ranges.append("100-120 (Medium)")
                elif e.bpm < 140:
                    bpm_ranges.append("120-140 (Fast)")
                elif e.bpm < 160:
                    bpm_ranges.append("140-160 (High)")
                else:
                    bpm_ranges.append("160+ (Very Fast)")
            if e.key:
                keys.append(e.key)
            for g in e.genre_labels or []:
                genres.append(g)
            for m in e.mood_labels or []:
                moods.append(m)
            if e.energy:
                energies.append(e.energy)

        bpm_trends = _compute_distribution(bpm_ranges, total)
        key_trends = _compute_distribution(keys, total)
        genre_trends = _compute_distribution(genres, total)
        mood_trends = _compute_distribution(moods, total)
        energy_dist = _compute_distribution(energies, total)

        # For trends, update category names
        for t in bpm_trends:
            t.category = "bpm"
        for t in key_trends:
            t.category = "key"
        for t in genre_trends:
            t.category = "genre"
        for t in mood_trends:
            t.category = "mood"
        for t in energy_dist:
            t.category = "energy"

        forecasts: list[TrendForecast] = []
        if include_forecasts:
            forecasts = await _generate_forecasts(
                genre_trends, bpm_trends, mood_trends, total
            )

        return TrendAnalysis(
            generated_at=datetime.now().isoformat(),
            library_size=total,
            bpm_trends=bpm_trends,
            key_trends=key_trends,
            genre_trends=genre_trends,
            mood_trends=mood_trends,
            energy_distribution=energy_dist,
            forecasts=forecasts,
        )

    except Exception as exc:
        logger.error("Trend analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Trend analysis failed")


@router.get("/gaps")
@rate_limit("20/minute")
async def get_gap_analysis(request: Request) -> GapAnalysis:
    """
    Identify gaps in your library by comparing against industry
    standard distributions for genres, BPM ranges, keys, and moods.
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return GapAnalysis(
                total_gaps=1,
                gaps=[
                    GapItem(
                        category="library",
                        gap="Empty library",
                        severity="high",
                        recommendation="Index your samples first",
                        sample_count_needed=0,
                    )
                ],
                library_health_score=0.0,
                ai_summary="No samples indexed yet.",
            )

        entries = idx._entries
        total = len(entries)

        # Industry standard BPM distribution targets
        bpm_targets = {
            "60-80": 0.05,
            "80-100": 0.15,
            "100-120": 0.20,
            "120-140": 0.30,
            "140-160": 0.20,
            "160+": 0.10,
        }

        # Key targets (roughly equal for all 12 keys * 2 modes)
        key_target = 1.0 / 24  # ~4.2% per key

        # Count actual distributions
        bpm_counts: dict[str, int] = {}
        key_counts: dict[str, int] = {}
        genre_counts: dict[str, int] = {}

        for e in entries:
            if e.bpm:
                if e.bpm < 80:
                    bpm_counts["60-80"] = bpm_counts.get("60-80", 0) + 1
                elif e.bpm < 100:
                    bpm_counts["80-100"] = bpm_counts.get("80-100", 0) + 1
                elif e.bpm < 120:
                    bpm_counts["100-120"] = bpm_counts.get("100-120", 0) + 1
                elif e.bpm < 140:
                    bpm_counts["120-140"] = bpm_counts.get("120-140", 0) + 1
                elif e.bpm < 160:
                    bpm_counts["140-160"] = bpm_counts.get("140-160", 0) + 1
                else:
                    bpm_counts["160+"] = bpm_counts.get("160+", 0) + 1

            if e.key:
                key_counts[e.key] = key_counts.get(e.key, 0) + 1
            for g in e.genre_labels or []:
                genre_counts[g] = genre_counts.get(g, 0) + 1

        gaps: list[GapItem] = []

        # BPM gap analysis
        for bpm_range, target_pct in bpm_targets.items():
            actual = bpm_counts.get(bpm_range, 0)
            actual_pct = actual / total if total else 0
            deficit = target_pct - actual_pct

            if deficit > 0.1:
                needed = int(deficit * total)
                gaps.append(
                    GapItem(
                        category="bpm",
                        gap=f"Missing {bpm_range} BPM samples",
                        severity="high" if deficit > 0.15 else "medium",
                        recommendation=f"Add ~{needed} samples in {bpm_range} BPM range",
                        sample_count_needed=needed,
                    )
                )

        # Key gap analysis — missing keys
        all_keys = [
            f"{note} {mode}"
            for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            for mode in ["major", "minor"]
        ]
        for key in all_keys:
            if key_counts.get(key, 0) == 0 and total > 50:
                gaps.append(
                    GapItem(
                        category="key",
                        gap=f"No samples in {key}",
                        severity="low",
                        recommendation=f"Add samples in {key} for harmonic diversity",
                        sample_count_needed=max(int(total * key_target), 2),
                    )
                )

        # Genre diversity check
        top_genre_pct = (
            max(genre_counts.values()) / sum(genre_counts.values())
            if genre_counts
            else 0
        )
        if top_genre_pct > 0.5:
            dominant = max(genre_counts, key=genre_counts.get)  # type: ignore[arg-type]
            gaps.append(
                GapItem(
                    category="genre",
                    gap=f"Library dominated by {dominant} ({top_genre_pct:.0%})",
                    severity="medium",
                    recommendation="Diversify genres for better creative range",
                    sample_count_needed=int(total * 0.2),
                )
            )

        # Health score
        bpm_coverage = len(bpm_counts) / len(bpm_targets) if bpm_targets else 0
        key_coverage = len(key_counts) / 24
        genre_diversity = 1.0 - top_genre_pct if genre_counts else 0
        health = (bpm_coverage * 30 + key_coverage * 30 + genre_diversity * 40)

        # AI summary
        ai_summary = await _generate_gap_summary(gaps, health, total)

        return GapAnalysis(
            total_gaps=len(gaps),
            gaps=gaps,
            library_health_score=round(min(health, 100), 1),
            ai_summary=ai_summary,
        )

    except Exception as exc:
        logger.error("Gap analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Gap analysis failed")


# ── AI helpers ────────────────────────────────────────────────────────────────


async def _generate_forecasts(
    genre_trends: list[TrendItem],
    bpm_trends: list[TrendItem],
    mood_trends: list[TrendItem],
    total: int,
) -> list[TrendForecast]:
    """AI-generated trend forecasts."""
    try:
        import json

        from samplemind.integrations.litellm_router import chat_completion

        trend_data = {
            "library_size": total,
            "top_genres": [(t.value, t.percentage) for t in genre_trends[:5]],
            "bpm_dist": [(t.value, t.percentage) for t in bpm_trends],
            "moods": [(t.value, t.percentage) for t in mood_trends[:5]],
        }

        response = await chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this music library and predict 3 trends:

{json.dumps(trend_data, indent=2)}

For each trend, provide:
- prediction: What will happen
- rationale: Why
- confidence: 0.0-1.0

Respond as JSON array.""",
                }
            ],
            prefer_fast=True,
            max_tokens=512,
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        if isinstance(data, list):
            return [TrendForecast(**item) for item in data[:3]]
    except Exception as exc:
        logger.warning("Forecast generation failed: %s", exc)

    return []


async def _generate_gap_summary(
    gaps: list[GapItem], health: float, total: int
) -> str:
    """AI-generated gap analysis summary."""
    try:
        from samplemind.integrations.litellm_router import chat_completion

        gap_list = [f"- {g.gap} ({g.severity}): {g.recommendation}" for g in gaps[:10]]

        response = await chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": f"""Summarize this library analysis in 2 sentences:

Library: {total} samples, health score: {health:.0f}/100
Gaps found:
{chr(10).join(gap_list) if gap_list else 'None found.'}""",
                }
            ],
            prefer_fast=True,
            max_tokens=200,
        )

        return response.choices[0].message.content.strip()

    except Exception as exc:
        logger.warning("Gap summary generation failed: %s", exc)
        if gaps:
            return f"Found {len(gaps)} gaps. Health score: {health:.0f}/100."
        return f"Library looks healthy ({health:.0f}/100) with {total} samples."
