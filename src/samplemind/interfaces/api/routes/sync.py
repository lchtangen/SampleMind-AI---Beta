"""
Cloud Sync API Routes
Manages cloud synchronization endpoints
"""

import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status

from samplemind.core.auth import get_current_active_user
from samplemind.interfaces.api.dependencies import get_app_state

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["Cloud Sync"])


@router.post("/enable")
async def enable_cloud_sync(current_user=Depends(get_current_active_user)):
    """
    Enable cloud sync for current user

    Requires authentication (Bearer token)
    """
    logger.info(f"Enabling cloud sync for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        success = await sync_manager.enable_sync(current_user.user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enable cloud sync"
            )

        return {
            "message": "Cloud sync enabled successfully",
            "user_id": current_user.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable cloud sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable cloud sync"
        )


@router.post("/disable")
async def disable_cloud_sync(current_user=Depends(get_current_active_user)):
    """
    Disable cloud sync for current user

    Requires authentication (Bearer token)
    """
    logger.info(f"Disabling cloud sync for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        success = await sync_manager.disable_sync(current_user.user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable cloud sync"
            )

        return {
            "message": "Cloud sync disabled successfully",
            "user_id": current_user.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable cloud sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable cloud sync"
        )


@router.get("/status")
async def get_sync_status(current_user=Depends(get_current_active_user)):
    """
    Get cloud sync status for current user

    Returns synchronization status including enabled state, pending events, etc.
    """
    logger.info(f"Fetching sync status for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        status_info = sync_manager.get_sync_status(current_user.user_id)

        return {
            "user_id": current_user.user_id,
            "enabled": status_info.get("enabled", False),
            "syncing": status_info.get("syncing", False),
            "pending_events": status_info.get("pending_events", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sync status"
        )


@router.post("/now")
async def sync_now(current_user=Depends(get_current_active_user)):
    """
    Trigger immediate cloud sync

    Pushes pending local changes and pulls remote changes
    """
    logger.info(f"Manual sync triggered for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        result = await sync_manager.sync(current_user.user_id)

        return {
            "message": "Sync completed",
            "user_id": current_user.user_id,
            "pushed": result.get("pushed", 0),
            "pulled": result.get("pulled", 0),
            "errors": result.get("errors", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to sync: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform sync"
        )


@router.post("/events")
async def queue_sync_event(
    collection: str,
    document_id: str,
    action: str,
    data: dict,
    device_id: Optional[str] = None,
    current_user=Depends(get_current_active_user)
) -> None:
    """
    Queue a sync event (used by client for offline operations)

    - **collection**: Collection name ('samples', 'analyses', 'workspaces')
    - **document_id**: Document ID
    - **action**: Action type ('create', 'update', 'delete')
    - **data**: Document data
    - **device_id**: Optional device ID
    """
    logger.info(
        f"Queueing sync event for user: {current_user.user_id} "
        f"({action} {collection}/{document_id})"
    )

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        # Validate inputs
        if collection not in ["samples", "analyses", "workspaces"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid collection: {collection}"
            )

        if action not in ["create", "update", "delete"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {action}"
            )

        # Queue event
        event = await sync_manager.queue_event(
            user_id=current_user.user_id,
            collection=collection,
            document_id=document_id,
            action=action,
            data=data,
            device_id=device_id or "unknown"
        )

        if not event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to queue sync event"
            )

        return {
            "message": "Event queued for sync",
            "event_id": event.event_id,
            "collection": collection,
            "document_id": document_id,
            "action": action,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to queue sync event: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue sync event"
        )


@router.get("/changes")
async def get_remote_changes(
    since: Optional[str] = None,
    limit: int = 100,
    current_user=Depends(get_current_active_user)
) -> None:
    """
    Get remote changes since specified timestamp

    - **since**: ISO timestamp to fetch changes since (optional)
    - **limit**: Maximum number of changes to return (default: 100)
    """
    logger.info(f"Fetching remote changes for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        # Parse since timestamp
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid timestamp format. Use ISO format (YYYY-MM-DD HH:MM:SS)"
                )

        # Fetch changes (placeholder - actual implementation would fetch from cloud)
        changes = []

        return {
            "user_id": current_user.user_id,
            "since": since or "beginning",
            "changes": changes,
            "count": len(changes),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch remote changes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch remote changes"
        )


@router.get("/stats")
async def get_sync_stats(current_user=Depends(get_current_active_user)):
    """
    Get cloud sync statistics for current user

    Returns statistics about sync performance and data
    """
    logger.info(f"Fetching sync stats for user: {current_user.user_id}")

    try:
        sync_manager = get_app_state("sync_manager")
        if not sync_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cloud sync service not available"
            )

        # Get sync status
        status_info = sync_manager.get_sync_status(current_user.user_id)

        return {
            "user_id": current_user.user_id,
            "enabled": status_info.get("enabled", False),
            "pending_events": status_info.get("pending_events", 0),
            "syncing": status_info.get("syncing", False),
            # Add more statistics as needed
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sync stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sync stats"
        )
