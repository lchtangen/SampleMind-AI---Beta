"""
Stem Remix Studio — Demucs stem separation + AI-powered mixing suggestions.

Endpoints:
  POST /api/v1/remix/separate      — Submit stem separation task (Celery)
  GET  /api/v1/remix/{task_id}/stems — Get separated stem audio URLs
  POST /api/v1/remix/{task_id}/suggest-mix — AI mixing suggestions per stem
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from samplemind.interfaces.api.rate_limiter import limit as rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/remix", tags=["remix"])

# ── Schemas ───────────────────────────────────────────────────────────────────


class SeparateRequest(BaseModel):
    file_path: str = Field(..., description="Path to audio file for stem separation")
    model: str = Field("htdemucs_6s", description="Demucs model name")


class StemInfo(BaseModel):
    name: str
    filename: str
    url: str
    duration_s: float | None = None


class SeparateResponse(BaseModel):
    task_id: str
    status: str
    stems: list[StemInfo] = []


class MixSuggestion(BaseModel):
    stem: str
    suggestions: list[str]
    eq_tips: list[str] = []
    effects: list[str] = []
    gain_db: float = 0.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)


class MixSuggestResponse(BaseModel):
    task_id: str
    mix_suggestions: list[MixSuggestion]
    overall_tips: list[str]
    model_used: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/separate")
@rate_limit("10/minute")
async def separate_stems(request: Request, body: SeparateRequest) -> dict[str, Any]:
    """
    Submit a stem separation task via Celery.
    Returns a task_id for tracking progress.
    """
    import uuid

    file_path = Path(body.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {body.file_path}")

    task_id = str(uuid.uuid4())

    # Queue Celery task for async processing
    try:
        from samplemind.core.tasks.celery_app import celery_app

        celery_app.send_task(
            "samplemind.tasks.separate_stems",
            args=[str(file_path), body.model, task_id],
        )
        return {"task_id": task_id, "status": "queued", "model": body.model}
    except Exception:
        logger.warning("Celery not available, running synchronous separation")

    # Synchronous fallback
    try:
        from samplemind.ai.separation.demucs_separator import DemucsProcessor

        processor = DemucsProcessor()
        output_dir = file_path.parent / f"stems_{task_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        result = await processor.separate(
            audio_path=str(file_path),
            output_dir=str(output_dir),
            model_name=body.model,
        )

        return {
            "task_id": task_id,
            "status": "completed",
            "stems": [
                {"name": name, "filename": f"{name}.wav", "url": f"/stems/{task_id}/{name}.wav"}
                for name in result.get("stems", ["vocals", "drums", "bass", "other", "guitar", "piano"])
            ],
        }
    except Exception as exc:
        logger.error("Stem separation failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Separation failed: {exc}")


@router.get("/{task_id}/stems")
@rate_limit("60/minute")
async def get_stems(request: Request, task_id: str) -> dict[str, Any]:
    """Get the separated stem files for a completed task."""
    from samplemind.interfaces.api.config import get_settings

    settings = get_settings()
    stems_dir = settings.CACHE_DIR / f"stems_{task_id}"

    if not stems_dir.exists():
        # Check Celery task status
        try:
            from celery.result import AsyncResult  # noqa: E402

            from samplemind.core.tasks.celery_app import celery_app

            result = AsyncResult(task_id, app=celery_app)
            return {
                "task_id": task_id,
                "status": result.state,
                "stems": [],
            }
        except Exception:
            raise HTTPException(status_code=404, detail="Task not found")

    stem_files = list(stems_dir.glob("*.wav"))
    stems = [
        StemInfo(
            name=f.stem,
            filename=f.name,
            url=f"/api/v1/remix/files/{task_id}/{f.name}",
        )
        for f in stem_files
    ]

    return {"task_id": task_id, "status": "completed", "stems": [s.model_dump() for s in stems]}


@router.post("/{task_id}/suggest-mix")
@rate_limit("20/minute")
async def suggest_mix(request: Request, task_id: str) -> MixSuggestResponse:
    """
    AI analyzes the separated stems and suggests mixing parameters.
    Returns per-stem EQ, compression, reverb, and gain recommendations.
    """
    from samplemind.integrations.litellm_router import chat_completion
    from samplemind.interfaces.api.config import get_settings

    settings = get_settings()
    stems_dir = settings.CACHE_DIR / f"stems_{task_id}"

    stem_names = ["vocals", "drums", "bass", "other", "guitar", "piano"]
    available_stems = []

    if stems_dir.exists():
        available_stems = [f.stem for f in stems_dir.glob("*.wav")]
    if not available_stems:
        available_stems = stem_names

    prompt = f"""Analyze these audio stems and provide professional mixing suggestions.

Available stems: {', '.join(available_stems)}

For EACH stem, provide:
1. 2-3 specific mixing tips (e.g. "Cut 200-400Hz to reduce muddiness")
2. Recommended EQ adjustments (frequency, gain, Q)
3. Suggested effects (reverb, compression, saturation, etc.)
4. Gain adjustment in dB (-6 to +6)
5. Pan position (-1.0 left to 1.0 right)

Also provide 2-3 overall mix tips.

Respond in this exact JSON format:
{{
  "stems": [
    {{
      "name": "vocals",
      "suggestions": ["High-pass at 80Hz", "Add 2dB at 3kHz for presence"],
      "eq_tips": ["Cut 200-400Hz by 3dB", "Boost 8-12kHz by 2dB for air"],
      "effects": ["Plate reverb (1.5s decay)", "Light compression (3:1 ratio)"],
      "gain_db": 0.0,
      "pan": 0.0
    }}
  ],
  "overall_tips": ["Check mono compatibility", "Use reference track for level balance"]
}}"""

    try:
        response = await chat_completion(
            messages=[
                {"role": "system", "content": "You are a professional mixing engineer. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            prefer_fast=True,
            max_tokens=2048,
        )

        content = response.choices[0].message.content
        # Parse JSON from response
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re

            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
            else:
                data = {"stems": [], "overall_tips": ["Could not parse AI response"]}

        mix_suggestions = [
            MixSuggestion(
                stem=s.get("name", "unknown"),
                suggestions=s.get("suggestions", []),
                eq_tips=s.get("eq_tips", []),
                effects=s.get("effects", []),
                gain_db=s.get("gain_db", 0.0),
                pan=s.get("pan", 0.0),
            )
            for s in data.get("stems", [])
        ]

        return MixSuggestResponse(
            task_id=task_id,
            mix_suggestions=mix_suggestions,
            overall_tips=data.get("overall_tips", []),
            model_used="litellm",
        )

    except Exception as exc:
        logger.error("Mix suggestion failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Mix suggestion failed")
