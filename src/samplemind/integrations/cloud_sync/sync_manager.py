"""
Cloud Sync Manager
Manages cloud synchronization with offline-first support
"""

import logging
import asyncio
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SyncAction(str, Enum):
    """Sync actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class SyncEvent:
    """Single synchronization event"""
    event_id: str
    user_id: str
    collection: str  # 'samples', 'analyses', 'workspaces'
    document_id: str
    action: str  # 'create', 'update', 'delete'
    data: Dict[str, Any]
    timestamp: datetime
    device_id: str
    version: int


class OfflineQueue:
    """Manages offline operation queue"""

    def __init__(self, max_size: int = 1000) -> None:
        self.queue: List[SyncEvent] = []
        self.max_size = max_size

    def add_event(self, event: SyncEvent) -> bool:
        """Add event to queue"""
        if len(self.queue) >= self.max_size:
            logger.warning(f"Offline queue full ({self.max_size} events)")
            return False

        self.queue.append(event)
        logger.debug(f"Event queued: {event.event_id} ({event.action} {event.collection})")
        return True

    def get_pending(self, limit: int = 100) -> List[SyncEvent]:
        """Get pending events"""
        return self.queue[:limit]

    def mark_synced(self, event_id: str) -> bool:
        """Mark event as synced (remove from queue)"""
        before = len(self.queue)
        self.queue = [e for e in self.queue if e.event_id != event_id]
        synced = len(self.queue) < before
        if synced:
            logger.debug(f"Event marked synced: {event_id}")
        return synced

    def clear(self) -> int:
        """Clear all pending events"""
        count = len(self.queue)
        self.queue = []
        return count

    def size(self) -> int:
        """Get queue size"""
        return len(self.queue)


class ConflictResolver:
    """Resolves conflicts between local and remote versions"""

    @staticmethod
    def resolve_conflict(
        local_doc: Dict[str, Any],
        remote_event: SyncEvent
    ) -> SyncEvent:
        """
        Resolve conflict using last-write-wins strategy

        Args:
            local_doc: Local document version
            remote_event: Remote change event

        Returns:
            Resolved SyncEvent (either local or remote)
        """
        local_timestamp = local_doc.get('updated_at')
        remote_timestamp = remote_event.timestamp

        if isinstance(local_timestamp, str):
            local_timestamp = datetime.fromisoformat(local_timestamp)

        # Compare timestamps
        if local_timestamp > remote_timestamp:
            # Local is newer, keep local
            logger.info(
                f"Conflict resolved: keeping local version "
                f"({local_doc.get('_id')} - local:{local_timestamp} > remote:{remote_timestamp})"
            )

            return SyncEvent(
                event_id=str(uuid.uuid4()),
                user_id=remote_event.user_id,
                collection=remote_event.collection,
                document_id=remote_event.document_id,
                action="update",
                data=local_doc,
                timestamp=datetime.utcnow(),
                device_id=local_doc.get('device_id', 'unknown'),
                version=local_doc.get('version', 1) + 1
            )
        else:
            # Remote is newer or same, use remote
            logger.info(
                f"Conflict resolved: accepting remote version "
                f"({remote_event.document_id} - remote:{remote_timestamp} >= local:{local_timestamp})"
            )
            return remote_event


class CloudSyncManager:
    """Manages cloud synchronization with offline support"""

    def __init__(
        self,
        mongodb_client=None,
        redis_client=None,
        s3_client=None,
        sync_interval: int = 60,
        enable_auto_sync: bool = True
    ):
        self.mongodb = mongodb_client
        self.redis = redis_client
        self.s3 = s3_client
        self.sync_interval = sync_interval
        self.enable_auto_sync = enable_auto_sync

        # State management
        self.sync_enabled: Dict[str, bool] = {}
        self.sync_workers: Dict[str, asyncio.Task] = {}
        self.offline_queues: Dict[str, OfflineQueue] = {}

    async def enable_sync(self, user_id: str) -> bool:
        """
        Enable cloud sync for user

        Args:
            user_id: User ID

        Returns:
            True if sync was enabled successfully
        """
        logger.info(f"Enabling cloud sync for user: {user_id}")

        try:
            # Mark as enabled
            self.sync_enabled[user_id] = True

            # Initialize offline queue
            if user_id not in self.offline_queues:
                self.offline_queues[user_id] = OfflineQueue()

            # Store sync state in database
            if self.mongodb:
                from samplemind.core.database.mongo import UserSettings
                settings = await UserSettings.find_one(
                    UserSettings.user_id == user_id
                )
                if settings:
                    settings.cloud_sync_enabled = True
                    await settings.save()

            # Start background sync worker if auto-sync is enabled
            if self.enable_auto_sync:
                if user_id in self.sync_workers:
                    self.sync_workers[user_id].cancel()

                task = asyncio.create_task(self._sync_worker(user_id))
                self.sync_workers[user_id] = task

            logger.info(f"✅ Cloud sync enabled for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable sync for {user_id}: {str(e)}", exc_info=True)
            return False

    async def disable_sync(self, user_id: str) -> bool:
        """
        Disable cloud sync for user

        Args:
            user_id: User ID

        Returns:
            True if sync was disabled successfully
        """
        logger.info(f"Disabling cloud sync for user: {user_id}")

        try:
            # Cancel sync worker
            if user_id in self.sync_workers:
                self.sync_workers[user_id].cancel()
                del self.sync_workers[user_id]

            # Mark as disabled
            self.sync_enabled[user_id] = False

            # Store sync state in database
            if self.mongodb:
                from samplemind.core.database.mongo import UserSettings
                settings = await UserSettings.find_one(
                    UserSettings.user_id == user_id
                )
                if settings:
                    settings.cloud_sync_enabled = False
                    await settings.save()

            logger.info(f"✅ Cloud sync disabled for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to disable sync for {user_id}: {str(e)}", exc_info=True)
            return False

    async def queue_event(
        self,
        user_id: str,
        collection: str,
        document_id: str,
        action: str,
        data: Dict[str, Any],
        device_id: str
    ) -> Optional[SyncEvent]:
        """
        Queue a sync event

        Args:
            user_id: User ID
            collection: Collection name
            document_id: Document ID
            action: Action type (create, update, delete)
            data: Document data
            device_id: Device ID

        Returns:
            The queued SyncEvent
        """
        try:
            event = SyncEvent(
                event_id=str(uuid.uuid4()),
                user_id=user_id,
                collection=collection,
                document_id=document_id,
                action=action,
                data=data,
                timestamp=datetime.utcnow(),
                device_id=device_id,
                version=1
            )

            # Get or create offline queue
            if user_id not in self.offline_queues:
                self.offline_queues[user_id] = OfflineQueue()

            queue = self.offline_queues[user_id]
            if queue.add_event(event):
                logger.debug(f"Event queued for user {user_id}: {event.event_id}")
                return event
            else:
                logger.error(f"Failed to queue event for user {user_id} (queue full)")
                return None

        except Exception as e:
            logger.error(f"Error queuing event: {str(e)}", exc_info=True)
            return None

    async def sync(self, user_id: str) -> Dict[str, Any]:
        """
        Perform manual sync for user

        Args:
            user_id: User ID

        Returns:
            Sync result with statistics
        """
        logger.info(f"Manual sync triggered for user: {user_id}")

        result = {
            "user_id": user_id,
            "pushed": 0,
            "pulled": 0,
            "conflicts_resolved": 0,
            "errors": []
        }

        try:
            # Push local changes
            pushed = await self._push_changes(user_id)
            result["pushed"] = pushed

            # Pull remote changes
            pulled = await self._pull_changes(user_id)
            result["pulled"] = pulled

            logger.info(f"✅ Sync completed for user {user_id}: pushed={pushed}, pulled={pulled}")

        except Exception as e:
            logger.error(f"Sync error for {user_id}: {str(e)}", exc_info=True)
            result["errors"].append(str(e))

        return result

    async def _sync_worker(self, user_id: str):
        """
        Background worker for periodic sync

        Args:
            user_id: User ID
        """
        logger.info(f"Starting sync worker for user: {user_id}")

        while self.sync_enabled.get(user_id):
            try:
                # Perform sync
                await self.sync(user_id)

                # Wait for next sync
                await asyncio.sleep(self.sync_interval)

            except asyncio.CancelledError:
                logger.info(f"Sync worker cancelled for user: {user_id}")
                break
            except Exception as e:
                logger.error(f"Sync worker error for {user_id}: {str(e)}", exc_info=True)
                await asyncio.sleep(self.sync_interval)

    async def _push_changes(self, user_id: str) -> int:
        """
        Push local changes to cloud

        Args:
            user_id: User ID

        Returns:
            Number of events pushed
        """
        if user_id not in self.offline_queues:
            return 0

        queue = self.offline_queues[user_id]
        pending_events = queue.get_pending(limit=100)
        pushed = 0

        for event in pending_events:
            try:
                # Upload event to cloud storage (e.g., S3)
                if self.s3:
                    await self._upload_event(event)

                # Mark as synced
                queue.mark_synced(event.event_id)
                pushed += 1

                logger.debug(f"Event pushed: {event.event_id}")

            except Exception as e:
                logger.error(f"Failed to push event {event.event_id}: {str(e)}")

        if pushed > 0:
            logger.info(f"Pushed {pushed} events for user {user_id}")

        return pushed

    async def _pull_changes(self, user_id: str) -> int:
        """
        Pull remote changes from cloud

        Args:
            user_id: User ID

        Returns:
            Number of changes pulled
        """
        pulled = 0

        try:
            # Get last sync timestamp
            last_sync = await self._get_last_sync_time(user_id)

            # Fetch changes since last sync from cloud storage
            if self.s3:
                changes = await self._fetch_remote_changes(user_id, since=last_sync)

                for change in changes:
                    try:
                        # Apply change with conflict resolution
                        await self._apply_change(user_id, change)
                        pulled += 1
                    except Exception as e:
                        logger.error(f"Failed to apply change: {str(e)}")

            # Update last sync timestamp
            await self._set_last_sync_time(user_id, datetime.utcnow())

        except Exception as e:
            logger.error(f"Failed to pull changes: {str(e)}")

        if pulled > 0:
            logger.info(f"Pulled {pulled} changes for user {user_id}")

        return pulled

    async def _apply_change(self, user_id: str, change: SyncEvent):
        """
        Apply remote change with conflict resolution

        Args:
            user_id: User ID
            change: Change to apply
        """
        try:
            if not self.mongodb:
                return

            # Get collection
            if change.collection == "samples":
                from samplemind.core.database.mongo import AudioFile
                collection_class = AudioFile
            elif change.collection == "analyses":
                from samplemind.core.database.mongo import Analysis
                collection_class = Analysis
            else:
                logger.warning(f"Unknown collection: {change.collection}")
                return

            # Check for conflicts
            local_doc = await collection_class.find_one(
                collection_class.id == change.document_id  # type: ignore
            )

            if local_doc and hasattr(local_doc, 'version'):
                if local_doc.version != change.version - 1:  # type: ignore
                    # Conflict detected
                    logger.warning(f"Conflict detected for {change.document_id}")
                    resolved = ConflictResolver.resolve_conflict(
                        local_doc.dict() if hasattr(local_doc, 'dict') else local_doc,
                        change
                    )
                    change = resolved

            # Apply change
            if change.action == SyncAction.CREATE:
                doc = collection_class(**change.data)
                await doc.insert()
            elif change.action == SyncAction.UPDATE:
                if local_doc:
                    for key, value in change.data.items():
                        if hasattr(local_doc, key):
                            setattr(local_doc, key, value)
                    await local_doc.save()  # type: ignore
            elif change.action == SyncAction.DELETE:
                if local_doc:
                    await local_doc.delete()  # type: ignore

            logger.debug(f"Change applied: {change.document_id} ({change.action})")

        except Exception as e:
            logger.error(f"Error applying change: {str(e)}", exc_info=True)
            raise

    async def _upload_event(self, event: SyncEvent):
        """Upload event to cloud storage"""
        if not self.s3:
            return

        try:
            # Implement S3 upload
            # This is a placeholder
            logger.debug(f"Uploading event to cloud: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to upload event: {str(e)}")
            raise

    async def _fetch_remote_changes(
        self,
        user_id: str,
        since: Optional[datetime] = None
    ) -> List[SyncEvent]:
        """Fetch remote changes from cloud storage"""
        # Placeholder implementation
        return []

    async def _get_last_sync_time(self, user_id: str) -> Optional[datetime]:
        """Get last sync timestamp from database"""
        try:
            if self.redis:
                last_sync = await self.redis.get(f"user:{user_id}:last_sync")
                if last_sync:
                    return datetime.fromisoformat(last_sync)
        except Exception as e:
            logger.warning(f"Failed to get last sync time: {str(e)}")

        return None

    async def _set_last_sync_time(self, user_id: str, timestamp: datetime):
        """Set last sync timestamp in cache"""
        try:
            if self.redis:
                await self.redis.set(
                    f"user:{user_id}:last_sync",
                    timestamp.isoformat(),
                    ex=30 * 24 * 60 * 60  # 30 days expiry
                )
        except Exception as e:
            logger.warning(f"Failed to set last sync time: {str(e)}")

    def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get sync status for user"""
        return {
            "enabled": self.sync_enabled.get(user_id, False),
            "syncing": user_id in self.sync_workers and not self.sync_workers[user_id].done(),
            "pending_events": self.offline_queues.get(user_id, OfflineQueue()).size(),
        }
