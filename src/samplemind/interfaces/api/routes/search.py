import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from samplemind.core.database.chroma import query_similar
from samplemind.interfaces.api.dependencies import get_app_state

router = APIRouter(prefix="/search", tags=["Search"])
logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Search result containing file information and similarity score.
    
    Attributes:
        file_id: Unique identifier for the audio file
        score: Similarity score (0-1, higher is more similar)
        filename: Optional filename of the audio file
        metadata: Optional metadata dictionary with additional file info
    """
    file_id: str
    score: float
    filename: Optional[str] = None
    metadata: Optional[dict] = None

class SearchRequest(BaseModel):
    """Request for semantic search operation.
    
    Attributes:
        query: Text description to search for
        limit: Maximum number of results to return (default: 10)
    """
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    """Response containing search results.
    
    Attributes:
        results: List of search results ordered by relevance
        total_found: Total number of matching results found
    """
    results: List[SearchResult]
    total_found: int

@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Perform semantic search on audio library using text description.
    Example: "upbeat drum loop with jazz influence"
    """
    logger.info(f"Semantic search query: {request.query}")
    
    # Get AudioEngine from app state
    audio_engine = get_app_state("audio_engine")
    if not audio_engine or not audio_engine.neural_extractor:
        raise HTTPException(
            status_code=503, 
            detail="Neural engine not available for semantic search"
        )
    
    try:
        # Generate text embedding
        text_embedding = audio_engine.neural_extractor.generate_text_embedding(request.query)
        
        if not text_embedding:
             raise HTTPException(status_code=500, detail="Failed to generate query embedding")

        # Query ChromaDB
        results = await query_similar(
            embedding=text_embedding,
            n_results=request.limit
        )
        
        # Format results
        search_results = []
        ids = results.get("ids", [])
        distances = results.get("distances", [])
        metadatas = results.get("metadatas", [])
        
        # Chroma/Langchain usually returns list of lists if multiple queries
        # But query_similar wrapper in chroma.py seems to handle singular query
        # Let's double check chroma.py:
        # results = collection.query(...)
        # return { "ids": results["ids"][0] ... }
        # Yes, it unwraps the first result.
        
        if ids:
            for i, file_id in enumerate(ids):
                dist = distances[i]
                meta = metadatas[i] if i < len(metadatas) else {}
                
                search_results.append(SearchResult(
                    file_id=file_id,
                    score=float(dist),
                    filename=meta.get("filename") or "Unknown",
                    metadata=meta
                ))
        
        return SearchResponse(
            results=search_results,
            total_found=len(search_results)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
