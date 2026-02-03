from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from samplemind.core.database.repositories.collection_repository import (
    CollectionRepository,
)

from ..dependencies import get_app_state
from ..schemas.collections import CollectionCreate, CollectionResponse, CollectionUpdate

router = APIRouter(prefix="/collections", tags=["collections"])

# Mock database (Fallback)
MOCK_COLLECTIONS = [
    {
        "id": "col_1",
        "user_id": "user_1",
        "name": "Favorites",
        "description": "My favorite tracks",
        "is_public": False,
        "tags": ["best", "favorites"],
        "metadata": {},
        "file_count": 12,
        "total_duration": 345.5,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "col_2",
        "user_id": "user_1",
        "name": "Project Alpha",
        "description": "Samples for Project Alpha",
        "is_public": True,
        "tags": ["work", "project-alpha"],
        "metadata": {},
        "file_count": 5,
        "total_duration": 120.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

def is_db_available() -> bool:
    """Check if MongoDB is available"""
    return get_app_state("mongodb") or False

@router.get("/", response_model=List[CollectionResponse])
async def list_collections(
    request: Request,
    skip: int = 0,
    limit: int = 100
):
    """List all collections"""
    if is_db_available():
        # Get user ID from request state (injected by AuthMiddleware)
        user_id = request.state.user["id"]
        cols = await CollectionRepository.get_by_user(user_id, skip, limit)
        # Convert Beanie objects to Schema response
        return [
            CollectionResponse(
                id=c.collection_id,
                user_id=c.user_id,
                name=c.name,
                description=c.description,
                is_public=c.is_public,
                tags=c.tags,
                metadata=c.metadata,
                file_count=c.file_count,
                total_duration=c.total_duration,
                created_at=c.created_at,
                updated_at=c.updated_at
            ) for c in cols
        ]

    return MOCK_COLLECTIONS[skip : skip + limit]

@router.post("/", response_model=CollectionResponse)
async def create_collection(collection: CollectionCreate):
    """Create a new collection"""

    if is_db_available():
        user_id = "test_user_v6"
        db_col = await CollectionRepository.create(
            user_id=user_id,
            name=collection.name,
            description=collection.description,
            is_public=collection.is_public,
            tags=collection.tags,
            metadata=collection.metadata
        )
        return CollectionResponse(
            id=db_col.collection_id,
            user_id=db_col.user_id,
            name=db_col.name,
            description=db_col.description,
            is_public=db_col.is_public,
            tags=db_col.tags,
            metadata=db_col.metadata,
            file_count=db_col.file_count,
            total_duration=db_col.total_duration,
            created_at=db_col.created_at,
            updated_at=db_col.updated_at
        )

    # Fallback to Mock
    new_col = collection.dict()
    new_col["id"] = f"col_{len(MOCK_COLLECTIONS) + 1}"
    new_col["user_id"] = "user_1"
    new_col["file_count"] = 0
    new_col["total_duration"] = 0.0
    new_col["created_at"] = datetime.now()
    new_col["updated_at"] = datetime.now()

    MOCK_COLLECTIONS.append(new_col)
    return new_col

@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: str):
    """Get a specific collection"""
    if is_db_available():
        c = await CollectionRepository.get_by_id(collection_id)
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        return CollectionResponse(
            id=c.collection_id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            is_public=c.is_public,
            tags=c.tags,
            metadata=c.metadata,
            file_count=c.file_count,
            total_duration=c.total_duration,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    for col in MOCK_COLLECTIONS:
        if col["id"] == collection_id:
            return col
    raise HTTPException(status_code=404, detail="Collection not found")

@router.put("/{collection_id}", response_model=CollectionResponse)
async def update_collection(collection_id: str, collection: CollectionUpdate):
    """Update a collection"""

    if is_db_available():
        update_data = collection.dict(exclude_unset=True)
        c = await CollectionRepository.update(collection_id, **update_data)
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        return CollectionResponse(
            id=c.collection_id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            is_public=c.is_public,
            tags=c.tags,
            metadata=c.metadata,
            file_count=c.file_count,
            total_duration=c.total_duration,
            created_at=c.created_at,
            updated_at=c.updated_at
        )

    for i, col in enumerate(MOCK_COLLECTIONS):
        if col["id"] == collection_id:
            update_data = collection.dict(exclude_unset=True)
            updated_col = col.copy()
            updated_col.update(update_data)
            updated_col["updated_at"] = datetime.now()
            MOCK_COLLECTIONS[i] = updated_col
            return updated_col

    raise HTTPException(status_code=404, detail="Collection not found")

@router.delete("/{collection_id}")
async def delete_collection(collection_id: str):
    """Delete a collection"""

    if is_db_available():
        success = await CollectionRepository.delete(collection_id)
        if not success:
            raise HTTPException(status_code=404, detail="Collection not found")
        return {"ok": True}

    for i, col in enumerate(MOCK_COLLECTIONS):
        if col["id"] == collection_id:
            MOCK_COLLECTIONS.pop(i)
            return {"ok": True}

    raise HTTPException(status_code=404, detail="Collection not found")

@router.get("/{collection_id}/items", response_model=List[Dict[str, Any]])
async def get_collection_items(collection_id: str):
    """Get items in a collection"""
    if is_db_available():
        # Verify collection exists first
        c = await CollectionRepository.get_by_id(collection_id)
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")

        items = await CollectionRepository.get_collection_items(collection_id)
        # Convert AudioFile beanie models to dicts
        return [
            {
                "id": item.file_id,
                "filename": item.filename,
                "duration": item.duration,
                "format": item.format,
                "created_at": item.created_at
            }
            for item in items
        ]

    # Verify collection exists
    found = False
    for col in MOCK_COLLECTIONS:
        if col["id"] == collection_id:
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Return mock items
    return [
        {
            "id": "audio_1",
            "filename": "Drum_Loop_120bpm.wav",
            "duration": 4.5,
            "format": "wav",
            "created_at": datetime.now()
        },
        {
            "id": "audio_2",
            "filename": "Synth_Pad_Am.mp3",
            "duration": 12.0,
            "format": "mp3",
            "created_at": datetime.now()
        }
    ]
