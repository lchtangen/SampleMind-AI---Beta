import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from samplemind.core.database.chroma import query_similar
from samplemind.core.exceptions import SearchIndexError, ValidationError
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
    filename: str | None = None
    metadata: dict | None = None


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

    results: list[SearchResult]
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
            status_code=503, detail="Neural engine not available for semantic search"
        )

    try:
        # Generate text embedding
        text_embedding = audio_engine.neural_extractor.generate_text_embedding(
            request.query
        )

        if not text_embedding:
            raise HTTPException(
                status_code=500, detail="Failed to generate query embedding"
            )

        # Query ChromaDB
        results = await query_similar(embedding=text_embedding, n_results=request.limit)

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

                search_results.append(
                    SearchResult(
                        file_id=file_id,
                        score=float(dist),
                        filename=meta.get("filename") or "Unknown",
                        metadata=meta,
                    )
                )

        return SearchResponse(results=search_results, total_found=len(search_results))

    except ValidationError as exc:
        logger.warning(
            "Search validation failed",
            extra={"query": request.query, "error": str(exc)},
        )
        raise HTTPException(status_code=400, detail=f"Invalid request: {exc}")
    except SearchIndexError as exc:
        logger.error(
            "Search index error",
            extra={"query": request.query},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Search engine unavailable")
    except Exception as exc:
        logger.error(
            "Unexpected error in search",
            extra={"query": request.query, "error_type": type(exc).__name__},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# ── FAISS-powered semantic search endpoints (Phase 11) ────────────────────────


class FAISSSearchResult(BaseModel):
    """Single FAISS semantic search result."""

    index_id: int
    path: str
    filename: str
    score: float
    bpm: float | None = None
    key: str | None = None
    energy: str | None = None
    genre_labels: list[str] = []
    mood_labels: list[str] = []
    sample_id: str | None = None


class FAISSSearchResponse(BaseModel):
    """FAISS search response."""

    query: str
    results: list[FAISSSearchResult]
    total: int
    index_size: int


@router.get("/faiss")
async def faiss_text_search(
    q: str,
    limit: int = 20,
) -> FAISSSearchResponse:
    """
    Semantic sample search using CLAP embeddings + FAISS index.

    Finds samples matching a natural language description.
    Falls back to MFCC-based search if CLAP model unavailable.

    Example: GET /api/v1/ai/search/faiss?q=dark+trap+kick&limit=10
    """
    from samplemind.core.search.faiss_index import get_index

    idx = get_index()
    if idx.is_empty:
        return FAISSSearchResponse(query=q, results=[], total=0, index_size=0)

    try:
        raw_results = idx.search_text(q, top_k=min(limit, 100))
        results = [
            FAISSSearchResult(
                index_id=r.index_id,
                path=r.path,
                filename=r.filename,
                score=r.score,
                bpm=r.metadata.get("bpm"),
                key=r.metadata.get("key"),
                energy=r.metadata.get("energy"),
                genre_labels=r.metadata.get("genre_labels", []),
                mood_labels=r.metadata.get("mood_labels", []),
                sample_id=r.metadata.get("sample_id"),
            )
            for r in raw_results
        ]
        return FAISSSearchResponse(
            query=q,
            results=results,
            total=len(results),
            index_size=idx.size,
        )
    except ValidationError as exc:
        logger.warning(
            "FAISS search validation failed",
            extra={"query": q, "limit": limit, "error": str(exc)},
        )
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {exc}")
    except SearchIndexError as exc:
        logger.error(
            "FAISS index failed",
            extra={"query": q},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Search failed")
    except TimeoutError as exc:
        logger.error("FAISS search timeout", extra={"query": q}, exc_info=True)
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as exc:
        logger.error(
            "Unexpected error in FAISS search",
            extra={"query": q, "error_type": type(exc).__name__},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/faiss/build")
async def faiss_build_index(
    paths: list[str],
) -> dict:
    """
    Build or rebuild the FAISS index from a list of audio file paths.

    This is a blocking operation — for large libraries use the CLI:
      samplemind index rebuild
    """
    from samplemind.core.search.faiss_index import FAISSIndex

    try:
        idx = FAISSIndex()
        idx.build(audio_paths=paths)
        idx.save()
        # Update global singleton
        import samplemind.core.search.faiss_index as _fi

        _fi._global_index = idx
        return {"status": "ok", "indexed": idx.size}
    except ValidationError as exc:
        logger.warning(
            "FAISS build validation failed",
            extra={"path_count": len(paths), "error": str(exc)},
        )
        raise HTTPException(status_code=400, detail=f"Invalid paths: {exc}")
    except SearchIndexError as exc:
        logger.error(
            "FAISS index build failed",
            extra={"path_count": len(paths)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Index build failed")
    except TimeoutError as exc:
        logger.error(
            "FAISS build timeout",
            extra={"path_count": len(paths)},
            exc_info=True,
        )
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as exc:
        logger.error(
            "Unexpected error building FAISS index",
            extra={"path_count": len(paths), "error_type": type(exc).__name__},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")
