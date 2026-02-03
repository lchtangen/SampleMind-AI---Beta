"""
Audio Similarity Search API
Find similar audio files using vector embeddings and ChromaDB
"""

from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
import numpy as np

from samplemind.core.engine.audio_engine import AudioEngine
from samplemind.core.database.chroma import (
    add_audio_to_collection,
    query_similar,
    get_collection_stats
)


router = APIRouter(prefix="/similarity", tags=["Similarity Search"])


class SimilarityResult(BaseModel):
    """Single similarity search result"""
    file_id: str
    file_path: str
    similarity_score: float
    features: dict


class SimilaritySearchResponse(BaseModel):
    """Response for similarity search"""
    query_file: str
    total_results: int
    results: List[SimilarityResult]
    search_time_ms: float


# Global audio engine
audio_engine = AudioEngine()


@router.post("/search", response_model=SimilaritySearchResponse)
async def find_similar_audio(
    file: UploadFile = File(...),
    limit: int = Query(10, ge=1, le=100),
    min_similarity: float = Query(0.7, ge=0.0, le=1.0)
) -> SimilaritySearchResponse:
    """
    Find similar audio files based on uploaded reference
    
    Args:
        file: Reference audio file
        limit: Maximum number of results
        min_similarity: Minimum similarity threshold (0-1)
    
    Returns:
        List of similar files with similarity scores
    """
    import time
    start_time = time.time()
    
    # Save uploaded file temporarily
    temp_path = Path(f"/tmp/{file.filename}")
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Extract features from reference audio
        features = audio_engine.analyze_audio(temp_path)
        
        # Query similar files from ChromaDB
        similar_files = query_similar(
            features.to_dict(),
            n_results=limit
        )
        
        # Filter by similarity threshold
        results = []
        for item in similar_files:
            if item.get("similarity", 0) >= min_similarity:
                results.append(SimilarityResult(
                    file_id=item["id"],
                    file_path=item.get("file_path", ""),
                    similarity_score=item.get("similarity", 0.0),
                    features=item.get("metadata", {})
                ))
        
        search_time = (time.time() - start_time) * 1000
        
        return SimilaritySearchResponse(
            query_file=file.filename,
            total_results=len(results),
            results=results,
            search_time_ms=search_time
        )
        
    finally:
        # Cleanup temp file
        if temp_path.exists():
            temp_path.unlink()


@router.post("/index")
async def index_audio_file(
    file: UploadFile = File(...),
    metadata: Optional[dict] = None
) -> dict:
    """
    Index an audio file for similarity search
    
    Args:
        file: Audio file to index
        metadata: Optional metadata to store
    
    Returns:
        Indexing status and file ID
    """
    # Save uploaded file
    temp_path = Path(f"/tmp/{file.filename}")
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Extract features
        features = audio_engine.analyze_audio(temp_path)
        
        # Add to ChromaDB
        file_id = add_audio_to_collection(
            file_path=str(temp_path),
            features=features.to_dict(),
            metadata=metadata or {}
        )
        
        return {
            "status": "indexed",
            "file_id": file_id,
            "file_name": file.filename
        }
        
    finally:
        if temp_path.exists():
            temp_path.unlink()


@router.get("/stats")
async def get_similarity_stats() -> dict:
    """Get statistics about indexed audio files"""
    stats = get_collection_stats()
    return {
        "total_indexed": stats.get("count", 0),
        "collection_name": stats.get("name", "audio_features"),
        "dimensions": stats.get("dimensions", 0)
    }


@router.post("/batch-search")
async def batch_similarity_search(
    files: List[UploadFile] = File(...),
    limit: int = Query(5, ge=1, le=50)
) -> dict:
    """
    Find similar files for multiple reference files
    
    Args:
        files: List of reference audio files
        limit: Results per file
    
    Returns:
        Dictionary mapping filenames to similarity results
    """
    results = {}
    
    for file in files:
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        try:
            features = audio_engine.analyze_audio(temp_path)
            similar = query_similar(features.to_dict(), n_results=limit)
            
            results[file.filename] = [
                {
                    "file_id": item["id"],
                    "similarity": item.get("similarity", 0.0)
                }
                for item in similar
            ]
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    return {
        "total_queries": len(files),
        "results": results
    }
