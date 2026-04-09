"""AI integration endpoints"""

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from samplemind.integrations.ai_manager import AIProvider
from samplemind.interfaces.api.dependencies import get_app_state
from samplemind.interfaces.api.rate_limiter import limit as rate_limit
from samplemind.interfaces.api.schemas.ai import (
    AIProviderInfo,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/providers", response_model=list[AIProviderInfo])
@rate_limit("100/minute")
async def list_ai_providers(request: Request):
    """List available AI providers and their status"""
    ai_manager = get_app_state("ai_manager")

    if not ai_manager:
        return []

    providers = ai_manager.get_available_providers()
    stats = ai_manager.get_global_stats()

    result = []
    for provider in [AIProvider.GOOGLE_AI, AIProvider.OPENAI]:
        is_available = provider in providers
        provider_stats = stats.get("provider_usage", {}).get(provider.value, {})

        result.append(
            AIProviderInfo(
                name=provider.value,
                status="available" if is_available else "unavailable",
                model=provider_stats.get("model"),
                features=[
                    "comprehensive_analysis",
                    "production_coaching",
                    "creative_suggestions",
                ],
                avg_response_time=provider_stats.get("avg_response_time"),
            )
        )

    return result


# ── Curation endpoints (Phase 12) ─────────────────────────────────────────────


class PlaylistRequest(BaseModel):
    mood: str = "dark"
    energy_arc: str = "build"  # build | drop | plateau | tension
    duration_minutes: float = 30.0
    samples: list[dict] | None = None  # if None, queries FAISS


class PlaylistResponse(BaseModel):
    name: str
    mood: str
    energy_arc: str
    duration_s: float
    sample_count: int
    samples: list[dict]
    narrative: str
    model_used: str


class GapReportResponse(BaseModel):
    total_samples: int
    coverage_score: float
    gap_count: int
    critical_gaps: list[dict]
    moderate_gaps: list[dict]
    suggestions: list[str]
    summary: str
    model_used: str


@router.post("/curate/playlist")
@rate_limit("100/minute")
async def generate_playlist(request: Request, body: PlaylistRequest) -> PlaylistResponse:
    """
    Generate an AI-curated playlist with a specific mood and energy arc.

    If `samples` is not provided, queries the FAISS index.
    Requires `samplemind index rebuild` to have been run first.
    """
    from samplemind.ai.curation.playlist_generator import PlaylistGenerator

    gen = PlaylistGenerator()
    try:
        playlist = await gen.generate(
            mood=body.mood,
            energy_arc=body.energy_arc,  # type: ignore[arg-type]
            duration_minutes=body.duration_minutes,
            sample_library=body.samples,
        )
        return PlaylistResponse(
            name=playlist.name,
            mood=playlist.mood,
            energy_arc=playlist.energy_arc,
            duration_s=playlist.duration_s,
            sample_count=len(playlist.samples),
            samples=playlist.samples,
            narrative=playlist.narrative,
            model_used=playlist.model_used,
        )
    except Exception as exc:
        logger.error("Playlist generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/curate/gaps")
@rate_limit("100/minute")
async def library_gap_analysis(
    request: Request,
    limit: int = 100,
) -> GapReportResponse:
    """
    Analyze the FAISS-indexed library for genre/mood/key/BPM coverage gaps.

    Returns a prioritized list of gaps with suggestions.
    """
    from samplemind.ai.curation.gap_analyzer import GapAnalyzer
    from samplemind.core.search.faiss_index import get_index

    idx = get_index()
    if idx.is_empty:
        return GapReportResponse(
            total_samples=0,
            coverage_score=0.0,
            gap_count=0,
            critical_gaps=[],
            moderate_gaps=[],
            suggestions=["Run `samplemind index rebuild` to index your library first."],
            summary="No samples indexed.",
            model_used="rules",
        )

    # Convert index entries to sample dicts
    sample_library = [
        {
            "filename": e.filename,
            "path": e.path,
            "bpm": e.bpm,
            "key": e.key,
            "energy": e.energy,
            "genre_labels": e.genre_labels,
            "mood_labels": e.mood_labels,
        }
        for e in idx._entries[:limit]
    ]

    analyzer = GapAnalyzer()
    try:
        report = await analyzer.analyze(sample_library)
        critical = [
            {
                "dimension": g.dimension,
                "value": g.value,
                "current_pct": g.current_pct,
                "deficit": g.deficit,
                "suggestion": g.suggestion,
            }
            for g in report.gaps
            if g.severity == "critical"
        ]
        moderate = [
            {
                "dimension": g.dimension,
                "value": g.value,
                "current_pct": g.current_pct,
                "deficit": g.deficit,
                "suggestion": g.suggestion,
            }
            for g in report.gaps
            if g.severity == "moderate"
        ]
        return GapReportResponse(
            total_samples=report.total_samples,
            coverage_score=report.coverage_score,
            gap_count=len(report.gaps),
            critical_gaps=critical,
            moderate_gaps=moderate,
            suggestions=report.suggestions,
            summary=report.summary,
            model_used=report.model_used,
        )
    except Exception as exc:
        logger.error("Gap analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/curate/energy-arc")
@rate_limit("100/minute")
async def suggest_energy_arc(
    request: Request,
    sample_ids: list[str],
) -> dict:
    """
    Given a list of sample paths/IDs, suggest the best energy arc ordering.

    Returns samples reordered for maximum energy flow.
    """
    from samplemind.ai.curation.playlist_generator import EnergyArc, PlaylistGenerator
    from samplemind.core.search.faiss_index import get_index

    idx = get_index()
    entries_by_path = {e.path: e for e in idx._entries}

    samples = []
    for sid in sample_ids:
        entry = entries_by_path.get(sid)
        if entry:
            samples.append(
                {
                    "filename": entry.filename,
                    "path": entry.path,
                    "bpm": entry.bpm,
                    "key": entry.key,
                    "energy": entry.energy,
                    "duration_s": 30.0,
                }
            )

    if not samples:
        return {"ordered": [], "suggested_arc": "plateau"}

    # Determine best arc based on energy distribution
    energies = [s.get("energy", "mid") for s in samples]
    energy_vals = {"low": 0, "mid": 1, "high": 2}
    e_nums = [energy_vals.get(e, 1) for e in energies]
    trend = (
        sum(b - a for a, b in zip(e_nums[:-1], e_nums[1:], strict=False)) if len(e_nums) > 1 else 0
    )
    suggested_arc: EnergyArc = "plateau"
    if trend > len(e_nums) * 0.3:
        suggested_arc = "build"
    elif trend < -len(e_nums) * 0.3:
        suggested_arc = "drop"

    gen = PlaylistGenerator()
    ordered = gen._order_by_arc(
        candidates=samples,
        energy_arc=suggested_arc,
        target_duration_s=sum(s.get("duration_s", 30.0) for s in samples),
    )

    return {
        "suggested_arc": suggested_arc,
        "ordered": ordered,
    }
