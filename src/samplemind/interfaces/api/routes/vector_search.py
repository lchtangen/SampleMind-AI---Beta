"""
Vector Search API Routes

Endpoints for similarity search and smart recommendations
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Path as PathParam
from pydantic import BaseModel, Field
import tempfile
import os

from samplemind.ai.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/vector", tags=["Vector Search"])


# Request/Response Models
class IndexFileRequest(BaseModel):
    """Request to index an audio file"""
    file_path: str = Field(..., description="Path to audio file")
    analysis_level: str = Field("STANDARD", description="Analysis level")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class IndexDirectoryRequest(BaseModel):
    """Request to index a directory"""
    directory: str = Field(..., description="Directory path")
    recursive: bool = Field(True, description="Search recursively")
    analysis_level: str = Field("STANDARD", description="Analysis level")
    extensions: Optional[List[str]] = Field(None, description="File extensions to index")


class SimilarSearchRequest(BaseModel):
    """Request to search for similar files"""
    file_path: str = Field(..., description="Reference file path")
    n_results: int = Field(10, ge=1, le=50, description="Number of results")
    exclude_self: bool = Field(True, description="Exclude query file from results")


class FeatureSearchRequest(BaseModel):
    """Request to search by features"""
    features: Dict[str, Any] = Field(..., description="Audio features")
    n_results: int = Field(10, ge=1, le=50, description="Number of results")
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class RecommendationRequest(BaseModel):
    """Request for smart recommendations"""
    file_path: str = Field(..., description="Reference file path")
    n_results: int = Field(5, ge=1, le=20, description="Number of recommendations per category")
    diversity: float = Field(0.3, ge=0.0, le=1.0, description="Diversity factor")


class SimilarFile(BaseModel):
    """Similar file result"""
    id: str
    file_path: str
    metadata: Dict[str, Any]
    distance: float
    similarity: float


class RecommendationResponse(BaseModel):
    """Smart recommendation response"""
    reference_file: str
    similar_samples: List[SimilarFile]
    complementary_samples: List[SimilarFile]
    contrasting_samples: List[SimilarFile]
    total_results: int


# API Endpoints
@router.post("/index/file")
async def index_file(request: IndexFileRequest) -> Dict[str, Any]:
    """
    Index an audio file for vector search

    Analyzes the audio file and stores its feature vector for similarity search.
    """
    try:
        embedding_service = get_embedding_service()
        result = await embedding_service.index_audio_file(
            file_path=request.file_path,
            analysis_level=request.analysis_level,
            metadata=request.metadata
        )
        return result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error indexing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/upload")
async def index_upload(
    file: UploadFile = File(...),
    analysis_level: str = Query("STANDARD", description="Analysis level")
) -> Dict[str, Any]:
    """
    Upload and index an audio file

    Uploads an audio file, analyzes it, and indexes it for similarity search.
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            embedding_service = get_embedding_service()
            result = await embedding_service.index_audio_file(
                file_path=temp_path,
                analysis_level=analysis_level,
                metadata={'original_filename': file.filename}
            )

            # Update file path in result
            result['original_filename'] = file.filename

            return result

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        logger.error(f"Error indexing uploaded file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/directory")
async def index_directory(request: IndexDirectoryRequest) -> Dict[str, Any]:
    """
    Index all audio files in a directory

    Recursively scans a directory for audio files and indexes them for similarity search.
    """
    try:
        embedding_service = get_embedding_service()
        result = await embedding_service.index_directory(
            directory=request.directory,
            recursive=request.recursive,
            analysis_level=request.analysis_level,
            extensions=request.extensions
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error indexing directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/similar")
async def search_similar(request: SimilarSearchRequest) -> List[SimilarFile]:
    """
    Find similar audio files

    Searches for audio files similar to the reference file based on audio features.
    """
    try:
        embedding_service = get_embedding_service()
        results = await embedding_service.find_similar(
            file_path=request.file_path,
            n_results=request.n_results,
            exclude_self=request.exclude_self
        )

        return [SimilarFile(**r) for r in results]

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching for similar files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/features")
async def search_by_features(request: FeatureSearchRequest) -> List[SimilarFile]:
    """
    Find similar audio files by features

    Searches for audio files matching the provided feature vector.
    """
    try:
        embedding_service = get_embedding_service()
        results = await embedding_service.find_similar_by_features(
            features=request.features,
            n_results=request.n_results,
            filter_metadata=request.filter_metadata
        )

        return [SimilarFile(**r) for r in results]

    except Exception as e:
        logger.error(f"Error searching by features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend")
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get smart sample recommendations

    Returns categorized recommendations: similar, complementary, and contrasting samples.
    """
    try:
        embedding_service = get_embedding_service()
        results = await embedding_service.get_recommendations(
            file_path=request.file_path,
            n_results=request.n_results,
            diversity=request.diversity
        )

        # Convert to response model
        return RecommendationResponse(
            reference_file=results['reference_file'],
            similar_samples=[SimilarFile(**s) for s in results['similar_samples']],
            complementary_samples=[SimilarFile(**s) for s in results['complementary_samples']],
            contrasting_samples=[SimilarFile(**s) for s in results['contrasting_samples']],
            total_results=results['total_results']
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/index/{file_path:path}")
async def remove_from_index(file_path: str = PathParam(..., description="File path to remove")) -> Dict[str, Any]:
    """
    Remove a file from the index

    Deletes the audio file's feature vector from the search index.
    """
    try:
        embedding_service = get_embedding_service()
        success = await embedding_service.remove_from_index(file_path)

        if success:
            return {"status": "removed", "file_path": file_path}
        else:
            raise HTTPException(status_code=404, detail="File not found in index")

    except Exception as e:
        logger.error(f"Error removing from index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reindex")
async def reindex_file(request: IndexFileRequest) -> Dict[str, Any]:
    """
    Reindex an audio file

    Removes and re-analyzes the audio file with updated settings.
    """
    try:
        embedding_service = get_embedding_service()
        result = await embedding_service.reindex_file(
            file_path=request.file_path,
            analysis_level=request.analysis_level
        )
        return result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error reindexing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_index_stats() -> Dict[str, Any]:
    """
    Get vector index statistics

    Returns information about the number of indexed files and storage.
    """
    try:
        embedding_service = get_embedding_service()
        stats = embedding_service.get_stats()
        return stats

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
