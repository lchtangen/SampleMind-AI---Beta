"""
AI Music Generation API Routes

Endpoints for AI-powered music generation using Google Gemini Lyria.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from samplemind.core.generation import (
    LyriaRealTimeEngine,
    MusicGenerationRequest as CoreMusicRequest,
    MusicStyle,
    MusicMood
)

router = APIRouter(prefix="/generate", tags=["Music Generation"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MusicGenerationRequest(BaseModel):
    """Request model for music generation"""
    prompt: str
    style: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[int] = None
    key: Optional[str] = None
    duration: int = 30
    variations: int = 1


class MusicGenerationResponse(BaseModel):
    """Response model for music generation"""
    success: bool
    message: str
    generation_id: str
    audio_url: Optional[str] = None
    generation_time: float
    metadata: dict


class VariationsRequest(BaseModel):
    """Request model for generating variations"""
    prompt: str
    count: int = 3
    style: Optional[str] = None
    mood: Optional[str] = None
    tempo: Optional[int] = None


class VariationsResponse(BaseModel):
    """Response model for variations"""
    success: bool
    total_variations: int
    completed: int
    failed: int
    results: List[dict]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/music", response_model=MusicGenerationResponse)
async def generate_music(request: MusicGenerationRequest):
    """
    Generate AI music from text prompt

    Uses Google Gemini Lyria RealTime for high-quality instrumental music generation.

    Supported styles:
    - electronic, ambient, orchestral, rock, jazz, classical, hip-hop, pop, experimental

    Supported moods:
    - energetic, calm, dark, bright, melancholic, uplifting, tense, relaxed

    Example:
        ```
        POST /api/v1/generate/music
        {
            "prompt": "Upbeat electronic music for coding",
            "style": "electronic",
            "mood": "energetic",
            "tempo": 128,
            "duration": 60
        }
        ```
    """
    try:
        # Initialize engine
        engine = LyriaRealTimeEngine()

        # Build core request
        core_request = CoreMusicRequest(
            prompt=request.prompt,
            style=MusicStyle(request.style.lower()) if request.style else None,
            mood=MusicMood(request.mood.lower()) if request.mood else None,
            tempo=request.tempo,
            key=request.key,
            duration=request.duration,
            variations=request.variations
        )

        # Generate music
        result = await engine.generate_music(core_request)

        if result.success:
            # Generate unique ID
            import uuid
            generation_id = str(uuid.uuid4())

            return MusicGenerationResponse(
                success=True,
                message="Music generated successfully",
                generation_id=generation_id,
                audio_url=str(result.audio_path) if result.audio_path else None,
                generation_time=result.generation_time,
                metadata=result.metadata
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.metadata.get("error", "Generation failed")
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variations", response_model=VariationsResponse)
async def generate_variations(request: VariationsRequest):
    """
    Generate multiple variations of a music prompt

    Creates N different versions of the same musical concept with slight variations.

    Example:
        ```
        POST /api/v1/generate/variations
        {
            "prompt": "Electronic beat for dancing",
            "count": 5,
            "style": "electronic",
            "tempo": 128
        }
        ```
    """
    try:
        engine = LyriaRealTimeEngine()

        # Build base request
        base_request = CoreMusicRequest(
            prompt=request.prompt,
            style=MusicStyle(request.style.lower()) if request.style else None,
            mood=MusicMood(request.mood.lower()) if request.mood else None,
            tempo=request.tempo,
            duration=30
        )

        # Generate variations
        results = await engine.generate_variations(
            base_request,
            num_variations=request.count
        )

        # Process results
        completed = sum(1 for r in results if r.success)
        failed = len(results) - completed

        results_data = [
            {
                "success": r.success,
                "generation_time": r.generation_time,
                "audio_url": str(r.audio_path) if r.audio_path else None,
                "metadata": r.metadata
            }
            for r in results
        ]

        return VariationsResponse(
            success=True,
            total_variations=request.count,
            completed=completed,
            failed=failed,
            results=results_data
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles")
async def list_music_styles():
    """
    List available music styles

    Returns all supported music generation styles with descriptions.

    Example:
        GET /api/v1/generate/styles
    """
    styles = [
        {
            "name": "electronic",
            "display_name": "Electronic",
            "description": "Electronic dance music, techno, house, trance",
            "typical_tempo": "120-140 BPM"
        },
        {
            "name": "ambient",
            "display_name": "Ambient",
            "description": "Atmospheric, ethereal soundscapes",
            "typical_tempo": "60-90 BPM"
        },
        {
            "name": "orchestral",
            "display_name": "Orchestral",
            "description": "Classical orchestra, cinematic scores",
            "typical_tempo": "60-120 BPM"
        },
        {
            "name": "rock",
            "display_name": "Rock",
            "description": "Rock, indie, alternative",
            "typical_tempo": "100-140 BPM"
        },
        {
            "name": "jazz",
            "display_name": "Jazz",
            "description": "Jazz, swing, bebop",
            "typical_tempo": "100-180 BPM"
        },
        {
            "name": "classical",
            "display_name": "Classical",
            "description": "Classical music, piano, strings",
            "typical_tempo": "60-120 BPM"
        },
        {
            "name": "hip-hop",
            "display_name": "Hip-Hop",
            "description": "Hip-hop, rap beats, trap",
            "typical_tempo": "70-90 BPM"
        },
        {
            "name": "pop",
            "display_name": "Pop",
            "description": "Popular music, catchy melodies",
            "typical_tempo": "100-130 BPM"
        },
        {
            "name": "experimental",
            "display_name": "Experimental",
            "description": "Avant-garde, unusual sounds",
            "typical_tempo": "Variable"
        }
    ]

    return {
        "styles": styles,
        "total": len(styles)
    }


@router.get("/moods")
async def list_music_moods():
    """
    List available music moods

    Returns all supported music generation moods with descriptions.

    Example:
        GET /api/v1/generate/moods
    """
    moods = [
        {
            "name": "energetic",
            "display_name": "Energetic",
            "description": "High energy, motivating, upbeat",
            "emotion": "excited"
        },
        {
            "name": "calm",
            "display_name": "Calm",
            "description": "Peaceful, relaxed, tranquil",
            "emotion": "serene"
        },
        {
            "name": "dark",
            "display_name": "Dark",
            "description": "Mysterious, ominous, intense",
            "emotion": "tense"
        },
        {
            "name": "bright",
            "display_name": "Bright",
            "description": "Cheerful, optimistic, happy",
            "emotion": "joyful"
        },
        {
            "name": "melancholic",
            "display_name": "Melancholic",
            "description": "Sad, nostalgic, emotional",
            "emotion": "sorrowful"
        },
        {
            "name": "uplifting",
            "display_name": "Uplifting",
            "description": "Inspiring, hopeful, positive",
            "emotion": "motivated"
        },
        {
            "name": "tense",
            "display_name": "Tense",
            "description": "Suspenseful, dramatic, intense",
            "emotion": "anxious"
        },
        {
            "name": "relaxed",
            "display_name": "Relaxed",
            "description": "Chill, easy-going, mellow",
            "emotion": "peaceful"
        }
    ]

    return {
        "moods": moods,
        "total": len(moods)
    }


@router.get("/examples")
async def generation_examples():
    """
    Get example music generation prompts

    Provides inspiration and examples for music generation.

    Example:
        GET /api/v1/generate/examples
    """
    examples = [
        {
            "prompt": "Upbeat electronic music for coding",
            "style": "electronic",
            "mood": "energetic",
            "tempo": 128,
            "use_case": "Focus music"
        },
        {
            "prompt": "Calm ambient soundscape for meditation",
            "style": "ambient",
            "mood": "calm",
            "tempo": 60,
            "use_case": "Relaxation"
        },
        {
            "prompt": "Epic orchestral theme for a video game",
            "style": "orchestral",
            "mood": "uplifting",
            "tempo": 90,
            "use_case": "Game soundtrack"
        },
        {
            "prompt": "Smooth jazz for a coffee shop",
            "style": "jazz",
            "mood": "relaxed",
            "tempo": 110,
            "use_case": "Background music"
        },
        {
            "prompt": "Dark electronic beats for a thriller",
            "style": "electronic",
            "mood": "dark",
            "tempo": 100,
            "use_case": "Film score"
        },
        {
            "prompt": "Energetic rock anthem",
            "style": "rock",
            "mood": "energetic",
            "tempo": 130,
            "use_case": "Workout music"
        },
        {
            "prompt": "Melancholic piano piece",
            "style": "classical",
            "mood": "melancholic",
            "tempo": 70,
            "use_case": "Emotional scene"
        },
        {
            "prompt": "Trap beat for hip-hop vocals",
            "style": "hip-hop",
            "mood": "energetic",
            "tempo": 75,
            "use_case": "Beat production"
        }
    ]

    return {
        "examples": examples,
        "total": len(examples)
    }


@router.get("/health")
async def generation_health():
    """
    Check music generation service health

    Example:
        GET /api/v1/generate/health
    """
    import os

    api_key_configured = bool(os.getenv("GOOGLE_AI_API_KEY"))

    return {
        "status": "healthy" if api_key_configured else "degraded",
        "api_configured": api_key_configured,
        "model": "lyria-realtime",
        "message": "Music generation available" if api_key_configured else "API key not configured"
    }
