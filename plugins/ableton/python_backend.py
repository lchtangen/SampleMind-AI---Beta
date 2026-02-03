#!/usr/bin/env python3
"""
SampleMind AI - Ableton Live Backend API Server
REST API for Max for Live device integration

Provides:
- Real-time audio analysis
- Sample similarity search
- Project sync recommendations
- MIDI generation
- Library management
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# DATA MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """Audio analysis request"""
    file_path: str
    analysis_level: str = "STANDARD"  # BASIC, STANDARD, DETAILED, PROFESSIONAL


class AnalysisResult(BaseModel):
    """Audio analysis result"""
    tempo_bpm: float
    key: str
    primary_genre: str
    mood: str
    energy_level: float
    confidence_score: float
    duration_seconds: float
    timestamp: str


class ProjectSyncRequest(BaseModel):
    """Project sync recommendation request"""
    project_bpm: float
    project_key: str
    limit: int = 10


class SimilarSamplesRequest(BaseModel):
    """Similar samples search request"""
    file_path: str
    limit: int = 10


class MIDIGenerationRequest(BaseModel):
    """MIDI generation request"""
    file_path: str
    extraction_type: str  # melody, harmony, drums, bass_line


class MIDIGenerationResult(BaseModel):
    """MIDI generation result"""
    midi_file_path: str
    notes_count: int
    duration_seconds: float
    notes: List[Dict[str, Any]]


class HealthStatus(BaseModel):
    """Health check status"""
    status: str
    version: str
    timestamp: str
    backend_ready: bool
    services: Dict[str, bool]


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="SampleMind AI - Ableton Live Backend",
    description="REST API for Max for Live integration",
    version="1.0.0"
)

# Add CORS middleware for Max for Live communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize SampleMind components (lazy loading)
audio_engine = None
midi_generator = None
db_manager = None


async def initialize_components():
    """Initialize SampleMind components on startup"""
    global audio_engine, midi_generator, db_manager

    try:
        from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
        from samplemind.core.processing.midi_generator import MIDIGenerator
        from samplemind.core.database.chroma import ChromaDBManager

        logger.info("Initializing SampleMind components...")

        audio_engine = AudioEngine()
        midi_generator = MIDIGenerator()
        db_manager = ChromaDBManager()

        logger.info("SampleMind components initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Called when server starts"""
    await initialize_components()
    logger.info("SampleMind Ableton Backend API started")


@app.on_event("shutdown")
async def shutdown_event():
    """Called when server shuts down"""
    logger.info("SampleMind Ableton Backend API shutting down")


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Check backend health and component status"""
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        backend_ready=audio_engine is not None,
        services={
            "audio_engine": audio_engine is not None,
            "midi_generator": midi_generator is not None,
            "database": db_manager is not None,
        }
    )


@app.get("/status")
async def status():
    """Get detailed status information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "components_initialized": {
            "audio_engine": audio_engine is not None,
            "midi_generator": midi_generator is not None,
            "database": db_manager is not None,
        },
        "api_endpoints": {
            "analyze": "/api/analyze",
            "similar": "/api/similar",
            "project_sync": "/api/project-sync",
            "generate_midi": "/api/generate-midi",
            "health": "/health",
        }
    }


# ============================================================================
# AUDIO ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_audio(request: AnalysisRequest):
    """Analyze audio file and return analysis results"""
    if audio_engine is None:
        raise HTTPException(status_code=503, detail="Audio engine not initialized")

    try:
        file_path = Path(request.file_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        logger.info(f"Analyzing: {file_path.name}")

        # Map analysis level string to enum
        from samplemind.core.engine.audio_engine import AnalysisLevel
        analysis_level = AnalysisLevel[request.analysis_level]

        # Perform analysis
        result = audio_engine.analyze_audio(file_path, level=analysis_level)

        # Convert result to AnalysisResult
        return AnalysisResult(
            tempo_bpm=result.get("tempo_bpm", 0.0),
            key=result.get("key", "Unknown"),
            primary_genre=result.get("primary_genre", "Unknown"),
            mood=result.get("mood", "Unknown"),
            energy_level=result.get("energy_level", 0.0),
            confidence_score=result.get("confidence_score", 0.0),
            duration_seconds=result.get("duration_seconds", 0.0),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/batch")
async def analyze_batch(files: List[UploadFile] = File(...)):
    """Batch analyze multiple audio files"""
    if audio_engine is None:
        raise HTTPException(status_code=503, detail="Audio engine not initialized")

    results = []

    try:
        for file in files:
            try:
                # Save uploaded file temporarily
                temp_path = Path("/tmp") / f"samplemind_{file.filename}"

                content = await file.read()
                temp_path.write_bytes(content)

                # Analyze
                result = audio_engine.analyze_audio(temp_path)

                results.append({
                    "filename": file.filename,
                    "analysis": result,
                    "status": "success"
                })

                # Clean up temp file
                temp_path.unlink()

            except Exception as e:
                logger.error(f"Failed to analyze {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "error": str(e),
                    "status": "failed"
                })

        return {
            "total_files": len(files),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results
        }

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


# ============================================================================
# SIMILARITY & SEARCH ENDPOINTS
# ============================================================================

@app.post("/api/similar")
async def find_similar_samples(request: SimilarSamplesRequest):
    """Find samples similar to the provided file"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        file_path = Path(request.file_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        logger.info(f"Finding similar samples for: {file_path.name}")

        # Find similar samples
        results = db_manager.similarity_search(str(file_path), top_k=request.limit)

        return {
            "reference_file": file_path.name,
            "similar_count": len(results),
            "limit": request.limit,
            "samples": results,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")


@app.get("/api/search")
async def search_samples(query: str, limit: int = 10):
    """Semantic search for samples in library"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        logger.info(f"Searching for: {query}")

        # Perform semantic search
        results = db_manager.semantic_search(query, top_k=limit)

        return {
            "query": query,
            "results_count": len(results),
            "limit": limit,
            "samples": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# ============================================================================
# PROJECT SYNC ENDPOINTS
# ============================================================================

@app.post("/api/project-sync")
async def get_project_sync_recommendations(request: ProjectSyncRequest):
    """Get sample recommendations based on project BPM and key"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        logger.info(f"Project sync: BPM={request.project_bpm}, Key={request.project_key}")

        # Query for matching BPM/Key
        results = db_manager.find_by_criteria(
            bpm_range=(request.project_bpm - 5, request.project_bpm + 5),
            key=request.project_key,
            limit=request.limit
        )

        return {
            "project_bpm": request.project_bpm,
            "project_key": request.project_key,
            "recommendations_count": len(results),
            "samples": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Project sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Project sync failed: {str(e)}")


@app.get("/api/project-sync/available-keys")
async def get_available_keys():
    """Get list of available musical keys in library"""
    keys = [
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
        "Cm", "C#m", "Dm", "D#m", "Em", "Fm", "F#m", "Gm", "G#m", "Am", "A#m", "Bm"
    ]
    return {"available_keys": keys}


# ============================================================================
# MIDI GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/generate-midi", response_model=MIDIGenerationResult)
async def generate_midi(request: MIDIGenerationRequest):
    """Generate MIDI from audio file"""
    if midi_generator is None:
        raise HTTPException(status_code=503, detail="MIDI generator not initialized")

    try:
        file_path = Path(request.file_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        logger.info(f"Generating {request.extraction_type} MIDI from: {file_path.name}")

        # Generate MIDI
        result = midi_generator.extract(
            str(file_path),
            extraction_type=request.extraction_type
        )

        # Save MIDI file
        midi_path = file_path.parent / f"{file_path.stem}_{request.extraction_type}.mid"
        midi_generator.save_midi(result, midi_path)

        return MIDIGenerationResult(
            midi_file_path=str(midi_path),
            notes_count=len(result.get("notes", [])),
            duration_seconds=result.get("duration_seconds", 0.0),
            notes=result.get("notes", [])
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MIDI generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"MIDI generation failed: {str(e)}")


@app.get("/api/generate-midi/types")
async def get_midi_extraction_types():
    """Get available MIDI extraction types"""
    return {
        "extraction_types": [
            {
                "type": "melody",
                "description": "Extract main melody line"
            },
            {
                "type": "harmony",
                "description": "Extract chord progression"
            },
            {
                "type": "drums",
                "description": "Extract drum pattern"
            },
            {
                "type": "bass_line",
                "description": "Extract bass line"
            }
        ]
    }


# ============================================================================
# LIBRARY MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/library/stats")
async def get_library_stats():
    """Get statistics about the sample library"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    try:
        stats = db_manager.get_library_statistics()
        return stats

    except Exception as e:
        logger.error(f"Failed to get library stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/api/library/add")
async def add_samples_to_library(files: List[UploadFile] = File(...)):
    """Add audio files to library"""
    if db_manager is None:
        raise HTTPException(status_code=503, detail="Database not initialized")

    results = []

    try:
        for file in files:
            try:
                # Save uploaded file
                library_path = Path.home() / ".samplemind" / "library" / file.filename
                library_path.parent.mkdir(parents=True, exist_ok=True)

                content = await file.read()
                library_path.write_bytes(content)

                # Analyze and add to database
                if audio_engine:
                    analysis = audio_engine.analyze_audio(library_path)
                    db_manager.add_to_index(
                        file_id=file.filename,
                        file_path=str(library_path),
                        metadata=analysis
                    )

                results.append({
                    "filename": file.filename,
                    "status": "added",
                    "path": str(library_path)
                })

            except Exception as e:
                logger.error(f"Failed to add {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "total_files": len(files),
            "added": sum(1 for r in results if r["status"] == "added"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Add to library failed: {e}")
        raise HTTPException(status_code=500, detail=f"Add to library failed: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/info")
async def get_api_info():
    """Get API information"""
    return {
        "name": "SampleMind AI - Ableton Live Backend",
        "version": "1.0.0",
        "description": "REST API for Max for Live device integration",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "analyze": "/api/analyze",
            "analyze_batch": "/api/analyze/batch",
            "similar": "/api/similar",
            "search": "/api/search",
            "project_sync": "/api/project-sync",
            "generate_midi": "/api/generate-midi",
            "library_stats": "/api/library/stats",
            "library_add": "/api/library/add",
        }
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Start the API server"""
    logger.info("Starting SampleMind Ableton Live Backend API...")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )


if __name__ == "__main__":
    main()


__all__ = ["app", "main"]
