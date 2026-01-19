"""
Workspace Management Routes
Multi-project organization and management
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from samplemind.core.auth import get_current_active_user
from samplemind.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


# Pydantic schemas
from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    """Create workspace request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class WorkspaceUpdate(BaseModel):
    """Update workspace request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class WorkspaceResponse(BaseModel):
    """Workspace response"""
    workspace_id: str
    user_id: str
    name: str
    description: Optional[str]
    sample_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceDetailResponse(WorkspaceResponse):
    """Detailed workspace response"""
    samples: List[str] = Field(default_factory=list)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    request: WorkspaceCreate,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Create a new workspace

    - **name**: Workspace name (required)
    - **description**: Workspace description (optional)
    """
    logger.info(f"Creating workspace for user: {current_user.user_id}")

    try:
        workspace_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Store in database
        workspace = {
            '_id': workspace_id,
            'workspace_id': workspace_id,
            'user_id': current_user.user_id,
            'name': request.name,
            'description': request.description,
            'samples': [],
            'created_at': now,
            'updated_at': now,
        }

        # Insert into MongoDB
        result = await db.workspaces.insert_one(workspace)

        logger.info(f"✅ Workspace created: {workspace_id} ({request.name})")

        return WorkspaceResponse(
            workspace_id=workspace_id,
            user_id=current_user.user_id,
            name=request.name,
            description=request.description,
            sample_count=0,
            created_at=now,
            updated_at=now,
        )

    except Exception as e:
        logger.error(f"Failed to create workspace: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace"
        )


@router.get("")
async def list_workspaces(
    current_user=Depends(get_current_active_user),
    limit: int = 50,
    offset: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    List all workspaces for current user

    Returns paginated list of workspaces
    """
    logger.info(f"Listing workspaces for user: {current_user.user_id}")

    try:
        # Query from database
        cursor = db.workspaces.find(
            {'user_id': current_user.user_id}
        ).skip(offset).limit(limit)

        workspaces = []
        async for workspace in cursor:
            workspaces.append({
                'workspace_id': workspace['workspace_id'],
                'name': workspace['name'],
                'description': workspace.get('description'),
                'sample_count': len(workspace.get('samples', [])),
                'created_at': workspace['created_at'],
                'updated_at': workspace['updated_at'],
                'user_id': workspace['user_id'],
            })

        # Get total count
        total = await db.workspaces.count_documents({'user_id': current_user.user_id})

        logger.info(f"Retrieved {len(workspaces)} workspaces for user {current_user.user_id}")

        return {
            "workspaces": workspaces,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        logger.error(f"Failed to list workspaces: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list workspaces"
        )


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
async def get_workspace(
    workspace_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Get workspace details

    Returns detailed workspace information including samples
    """
    logger.info(f"Fetching workspace: {workspace_id}")

    try:
        # Query from database with authorization check
        workspace = await db.workspaces.find_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )

        logger.info(f"Retrieved workspace {workspace_id} for user {current_user.user_id}")

        return WorkspaceDetailResponse(
            workspace_id=workspace_id,
            user_id=current_user.user_id,
            name=workspace.get('name', ''),
            description=workspace.get('description'),
            sample_count=len(workspace.get('samples', [])),
            samples=workspace.get('samples', []),
            created_at=workspace.get('created_at', datetime.utcnow()),
            updated_at=workspace.get('updated_at', datetime.utcnow()),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get workspace"
        )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    request: WorkspaceUpdate,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Update workspace

    Update workspace name and description
    """
    logger.info(f"Updating workspace: {workspace_id}")

    try:
        # Query from database with authorization check
        workspace = await db.workspaces.find_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )

        # Update fields
        update_data = {'updated_at': datetime.utcnow()}
        if request.name:
            update_data['name'] = request.name
        if request.description is not None:
            update_data['description'] = request.description

        # Save to database
        result = await db.workspaces.update_one(
            {'workspace_id': workspace_id},
            {'$set': update_data}
        )

        logger.info(f"✅ Workspace updated: {workspace_id} (matched={result.matched_count}, modified={result.modified_count})")

        # Fetch updated workspace
        updated = await db.workspaces.find_one({'workspace_id': workspace_id})

        return WorkspaceResponse(
            workspace_id=workspace_id,
            user_id=current_user.user_id,
            name=updated['name'],
            description=updated.get('description'),
            sample_count=len(updated.get('samples', [])),
            created_at=updated.get('created_at', datetime.utcnow()),
            updated_at=updated.get('updated_at', datetime.utcnow()),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workspace: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workspace"
        )


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Delete a workspace

    Permanently deletes the workspace and all associated data
    """
    logger.info(f"Deleting workspace: {workspace_id}")

    try:
        # Query from database with authorization check
        workspace = await db.workspaces.find_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )

        # Delete from database
        result = await db.workspaces.delete_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        logger.info(f"✅ Workspace deleted: {workspace_id} (deleted={result.deleted_count})")

        return {
            "message": "Workspace successfully deleted",
            "workspace_id": workspace_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workspace: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workspace"
        )


@router.post("/{workspace_id}/samples/{sample_id}")
async def add_sample_to_workspace(
    workspace_id: str,
    sample_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Add sample to workspace

    Associates an audio sample with a workspace
    """
    logger.info(f"Adding sample {sample_id} to workspace {workspace_id}")

    try:
        # Verify workspace ownership and sample ownership
        workspace = await db.workspaces.find_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )

        # Verify sample belongs to user
        sample = await db.samples.find_one({
            'sample_id': sample_id,
            'user_id': current_user.user_id
        })

        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sample not found or access denied"
            )

        # Check if sample already in workspace
        if sample_id in workspace.get('samples', []):
            return {
                "message": "Sample already in workspace",
                "workspace_id": workspace_id,
                "sample_id": sample_id,
            }

        # Add sample to workspace
        result = await db.workspaces.update_one(
            {'workspace_id': workspace_id},
            {
                '$push': {'samples': sample_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        logger.info(f"✅ Sample {sample_id} added to workspace {workspace_id}")

        return {
            "message": "Sample added to workspace",
            "workspace_id": workspace_id,
            "sample_id": sample_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add sample: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add sample to workspace"
        )


@router.delete("/{workspace_id}/samples/{sample_id}")
async def remove_sample_from_workspace(
    workspace_id: str,
    sample_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Remove sample from workspace

    Disassociates an audio sample from a workspace
    """
    logger.info(f"Removing sample {sample_id} from workspace {workspace_id}")

    try:
        # Verify workspace ownership and sample ownership
        workspace = await db.workspaces.find_one({
            'workspace_id': workspace_id,
            'user_id': current_user.user_id
        })

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )

        # Verify sample belongs to user
        sample = await db.samples.find_one({
            'sample_id': sample_id,
            'user_id': current_user.user_id
        })

        if not sample:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sample not found or access denied"
            )

        # Remove sample from workspace
        result = await db.workspaces.update_one(
            {'workspace_id': workspace_id},
            {
                '$pull': {'samples': sample_id},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        logger.info(f"✅ Sample {sample_id} removed from workspace {workspace_id}")

        return {
            "message": "Sample removed from workspace",
            "workspace_id": workspace_id,
            "sample_id": sample_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove sample: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove sample from workspace"
        )
