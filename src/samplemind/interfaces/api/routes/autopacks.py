"""
Auto Sample Pack Curator — AI-powered pack generation from your library.

Endpoints:
  POST /api/v1/autopacks/generate     — Trigger AI pack curation
  GET  /api/v1/autopacks/suggestions   — AI suggests pack themes
  GET  /api/v1/autopacks/{task_id}     — Get generated pack
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/autopacks", tags=["autopacks"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class PackGenerateRequest(BaseModel):
    theme: str = Field(..., description="Pack theme, e.g. 'Dark Trap Essentials'")
    max_samples: int = Field(25, ge=5, le=100, description="Max samples in pack")
    target_mood: str | None = Field(None, description="Filter by mood")
    target_energy: str | None = Field(None, description="Filter by energy")


class PackSample(BaseModel):
    filename: str
    bpm: float | None = None
    key: str | None = None
    energy: str | None = None
    genre: list[str] = []
    similarity_score: float | None = None


class PackSuggestion(BaseModel):
    theme: str
    description: str
    estimated_samples: int
    moods: list[str] = []
    genres: list[str] = []


class GeneratedPack(BaseModel):
    name: str
    description: str
    tags: list[str]
    samples: list[PackSample]
    sample_count: int
    cover_art_prompt: str
    status: str = "generated"


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/suggestions")
@rate_limit("30/minute")
async def suggest_pack_themes(request: Request) -> list[PackSuggestion]:
    """
    AI analyzes your library and suggests 5 potential pack themes
    based on genre clusters, mood distribution, and sample density.
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            return [
                PackSuggestion(
                    theme="Getting Started",
                    description="Index your library first with `samplemind index rebuild`",
                    estimated_samples=0,
                )
            ]

        # Analyze library composition
        entries = idx._entries
        genre_counts: dict[str, int] = {}
        mood_counts: dict[str, int] = {}
        energy_counts: dict[str, int] = {}

        for e in entries:
            for g in e.genre_labels or []:
                genre_counts[g] = genre_counts.get(g, 0) + 1
            for m in e.mood_labels or []:
                mood_counts[m] = mood_counts.get(m, 0) + 1
            if e.energy:
                energy_counts[e.energy] = energy_counts.get(e.energy, 0) + 1

        # Use AI to suggest themes
        from samplemind.integrations.litellm_router import chat_completion

        prompt = f"""Based on this sample library analysis, suggest 5 themed sample packs:

Library size: {len(entries)} samples
Top genres: {dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10])}
Mood distribution: {mood_counts}
Energy distribution: {energy_counts}

For each pack, provide:
- theme: catchy pack name
- description: 1-sentence description
- estimated_samples: how many samples would fit
- moods: relevant moods
- genres: relevant genres

Respond as a JSON array."""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            prefer_fast=True,
            max_tokens=1024,
        )

        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return [PackSuggestion(**item) for item in data[:5]]
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback: rule-based suggestions
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [
            PackSuggestion(
                theme=f"{genre.title()} Collection",
                description=f"Curated {genre} samples from your library",
                estimated_samples=count,
                genres=[genre],
            )
            for genre, count in top_genres
        ]

    except Exception as exc:
        logger.error("Pack suggestions failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Suggestions failed")


@router.post("/generate")
@rate_limit("5/minute")
async def generate_pack(
    request: Request, body: PackGenerateRequest
) -> GeneratedPack:
    """
    AI curates a sample pack: selects best samples matching the theme,
    generates metadata (name, description, tags, cover art prompt).
    """
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index(auto_load=True)
        if idx.is_empty:
            raise HTTPException(status_code=400, detail="No samples indexed")

        # Search for samples matching the theme
        results = idx.search_text(body.theme, top_k=body.max_samples * 2)

        # Filter by mood/energy if specified
        filtered = []
        for r in results:
            if body.target_mood and body.target_mood not in (r.metadata.get("mood_labels") or []):
                continue
            if body.target_energy and r.metadata.get("energy") != body.target_energy:
                continue
            filtered.append(r)

        if not filtered:
            filtered = list(results)

        # Select top samples up to max
        selected = filtered[: body.max_samples]

        pack_samples = [
            PackSample(
                filename=s.filename,
                bpm=s.metadata.get("bpm"),
                key=s.metadata.get("key"),
                energy=s.metadata.get("energy"),
                genre=s.metadata.get("genre_labels", []),
                similarity_score=round(s.score, 3),
            )
            for s in selected
        ]

        # Generate pack metadata with AI
        from samplemind.integrations.litellm_router import chat_completion

        prompt = f"""Create metadata for a sample pack:
Theme: {body.theme}
Samples: {len(pack_samples)} audio samples
Genres: {list({g for s in pack_samples for g in s.genre})}
Moods: {body.target_mood or 'mixed'}

Provide:
1. name: Catchy pack name (2-4 words)
2. description: Marketing description (1-2 sentences)
3. tags: 5-8 search tags
4. cover_art_prompt: Text-to-image prompt for cover art (cyberpunk/neon aesthetic)

Respond as JSON."""

        response = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            prefer_fast=True,
            max_tokens=512,
        )

        content = response.choices[0].message.content
        try:
            meta = json.loads(content)
        except json.JSONDecodeError:
            meta = {
                "name": body.theme,
                "description": f"AI-curated {body.theme} sample pack",
                "tags": [body.theme.lower()],
                "cover_art_prompt": f"Cyberpunk neon {body.theme} album cover",
            }

        return GeneratedPack(
            name=meta.get("name", body.theme),
            description=meta.get("description", ""),
            tags=meta.get("tags", []),
            samples=pack_samples,
            sample_count=len(pack_samples),
            cover_art_prompt=meta.get("cover_art_prompt", ""),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Pack generation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Pack generation failed")
