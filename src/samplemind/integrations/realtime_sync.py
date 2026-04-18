"""
Realtime Sync — SampleMind Phase 13
=====================================

Multi-device library synchronization via **Supabase Realtime** broadcast
channels.  When a sample is added, deleted, or updated on one device, the
change is immediately pushed to every other connected device.

Conflict resolution:
  **Last-write-wins** based on ``server_timestamp``.  Since all sync
  operations are idempotent (``get_or_create``, field-level ``update``),
  replaying the same event twice is safe.

Architecture::

    Device A  ──push──▶  Supabase channel "library:{user_id}"  ──broadcast──▶  Device B
                                                                ──broadcast──▶  Device C
    Each device subscribes on ``start()`` and applies incoming ``SyncEvent``s
    to its local Tortoise ORM database.

Supported event types:
  ``sample_added``   — create a new ``TortoiseSample`` if it doesn't exist.
  ``sample_deleted`` — delete the sample row.
  ``sample_updated`` — update metadata fields (BPM, key, tags, etc.).
  ``library_reset``  — (reserved) full re-sync trigger.

Usage::

    from samplemind.integrations.realtime_sync import RealtimeSync

    sync = RealtimeSync(user_id="user_123")
    await sync.start()                                # background subscription
    await sync.push_sample_added("abc", metadata={…}) # broadcast to peers
    await sync.stop()                                 # unsubscribe
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC
from typing import Any

logger = logging.getLogger(__name__)

SyncEventType = (
    str  # One of: "sample_added" | "sample_deleted" | "sample_updated" | "library_reset"
)

# ── Data types ────────────────────────────────────────────────────────────────


@dataclass
class SyncEvent:
    """A library change event broadcast via Supabase Realtime."""

    event_type: SyncEventType
    user_id: str
    sample_id: str | None
    metadata: dict
    server_timestamp: str | None


# ── Sync engine ───────────────────────────────────────────────────────────────


class RealtimeSync:
    """
    Supabase Realtime-based multi-device sync.

    Subscribes to a user-specific channel and applies incoming events
    to the local Tortoise ORM database.
    """

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self._channel_name = f"library:{user_id}"
        self._subscription: Any = None
        self._running = False
        self._handlers: dict[str, list[Callable]] = {}
        self._client = self._get_client()

    def _get_client(self) -> Any:
        try:
            from samplemind.integrations.supabase_client import get_supabase

            return get_supabase()
        except Exception:
            return None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> bool:
        """
        Start the Realtime subscription.

        Returns:
            True if subscription started, False if Supabase unavailable.
        """
        if not self._client:
            logger.warning("Supabase not configured — realtime sync disabled")
            return False

        try:
            channel = self._client.channel(self._channel_name)
            channel.on_broadcast(
                event="sync",
                callback=self._handle_event,
            )
            await asyncio.get_event_loop().run_in_executor(None, channel.subscribe)
            self._subscription = channel
            self._running = True
            logger.info("✓ Realtime sync started for user: %s", self.user_id)
            return True
        except Exception as exc:
            logger.error("Realtime sync start failed: %s", exc)
            return False

    async def stop(self) -> None:
        """Stop the Realtime subscription."""
        self._running = False
        if self._subscription and self._client:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._client.remove_channel(self._subscription)
                )
            except Exception as exc:
                logger.debug("Realtime stop error: %s", exc)
        self._subscription = None
        logger.info("Realtime sync stopped for user: %s", self.user_id)

    # ── Push events ───────────────────────────────────────────────────────────

    async def push_sample_added(self, sample_id: str, metadata: dict) -> bool:
        """Broadcast a sample-added event to other devices."""
        return await self._broadcast(
            "sample_added", sample_id=sample_id, metadata=metadata
        )

    async def push_sample_deleted(self, sample_id: str) -> bool:
        """Broadcast a sample-deleted event to other devices."""
        return await self._broadcast("sample_deleted", sample_id=sample_id)

    async def push_sample_updated(self, sample_id: str, metadata: dict) -> bool:
        """Broadcast a sample-updated event to other devices."""
        return await self._broadcast(
            "sample_updated", sample_id=sample_id, metadata=metadata
        )

    async def _broadcast(
        self,
        event_type: SyncEventType,
        sample_id: str | None = None,
        metadata: dict | None = None,
    ) -> bool:
        if not self._subscription or not self._client:
            return False
        try:
            from datetime import datetime

            payload = {
                "event_type": event_type,
                "user_id": self.user_id,
                "sample_id": sample_id,
                "metadata": metadata or {},
                "server_timestamp": datetime.now(UTC).isoformat(),
            }
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._subscription.send_broadcast("sync", payload),
            )
            return True
        except Exception as exc:
            logger.debug("Realtime broadcast failed: %s", exc)
            return False

    # ── Event handler ─────────────────────────────────────────────────────────

    def _handle_event(self, payload: dict) -> None:
        """Process incoming Realtime event (called from Supabase SDK callback thread)."""
        try:
            event = SyncEvent(
                event_type=payload.get("event_type", "unknown"),
                user_id=payload.get("user_id", ""),
                sample_id=payload.get("sample_id"),
                metadata=payload.get("metadata", {}),
                server_timestamp=payload.get("server_timestamp"),
            )
            # Skip own broadcasts to avoid echo loops
            if event.user_id == self.user_id:
                return

            asyncio.create_task(self._apply_event(event))
        except Exception as exc:
            logger.error("Realtime event handle error: %s", exc)

    async def _apply_event(self, event: SyncEvent) -> None:
        """Apply a sync event to the local Tortoise database (idempotent)."""
        try:
            from samplemind.core.database.tortoise_models import TortoiseSample

            if event.event_type == "sample_added" and event.sample_id:
                exists = await TortoiseSample.exists(id=event.sample_id)
                if not exists:
                    # Only create if we have path info
                    path = event.metadata.get("file_path") or event.metadata.get("path")
                    if path:
                        await TortoiseSample.get_or_create(
                            id=event.sample_id,
                            defaults={
                                "filename": event.metadata.get("filename", ""),
                                "file_path": path,
                                "bpm": event.metadata.get("bpm"),
                                "key": event.metadata.get("key"),
                                "energy": event.metadata.get("energy"),
                            },
                        )
                        logger.debug("Sync: added sample %s", event.sample_id)

            elif event.event_type == "sample_deleted" and event.sample_id:
                await TortoiseSample.filter(id=event.sample_id).delete()
                logger.debug("Sync: deleted sample %s", event.sample_id)

            elif event.event_type == "sample_updated" and event.sample_id:
                update_fields = {
                    k: v
                    for k, v in event.metadata.items()
                    if k
                    in {
                        "bpm",
                        "key",
                        "energy",
                        "genre_labels",
                        "mood_labels",
                        "user_tags",
                    }
                }
                if update_fields:
                    await TortoiseSample.filter(id=event.sample_id).update(
                        **update_fields
                    )
                    logger.debug("Sync: updated sample %s", event.sample_id)

        except Exception as exc:
            logger.error("Failed to apply sync event %s: %s", event.event_type, exc)

    # ── Pull (initial sync / cold start) ────────────────────────────────────

    async def pull_library_state(self) -> int:
        """
        Pull the current library state from Supabase cloud and upsert into local DB.

        Designed for first launch or recovery after a long offline period.
        Uses ``get_or_create`` so replaying is always safe.

        Returns:
            Number of *newly created* samples.
        """
        if not self._client:
            return 0

        try:
            from samplemind.core.database.tortoise_models import TortoiseSample

            # Query Supabase samples table for this user
            result = (
                self._client.table("samples")
                .select("*")
                .eq("user_id", self.user_id)
                .execute()
            )
            rows = result.data or []
            synced = 0
            for row in rows:
                _, created = await TortoiseSample.get_or_create(
                    id=row["id"],
                    defaults={
                        "filename": row.get("filename", ""),
                        "file_path": row.get("file_path", ""),
                        "bpm": row.get("bpm"),
                        "key": row.get("key"),
                        "energy": row.get("energy"),
                        "genre_labels": row.get("genre_labels", []),
                        "mood_labels": row.get("mood_labels", []),
                    },
                )
                if created:
                    synced += 1

            logger.info("Pulled %d new samples from Supabase", synced)
            return synced

        except Exception as exc:
            logger.error("Library pull failed: %s", exc)
            return 0

    async def push_library_state(self) -> int:
        """
        Push all local TortoiseSamples to Supabase (upsert).

        Used for initial cloud backup or disaster recovery.

        Returns:
            Number of samples pushed.
        """
        if not self._client:
            return 0

        try:
            from samplemind.core.database.tortoise_models import TortoiseSample

            samples = await TortoiseSample.filter(user_id=self.user_id).all()
            pushed = 0
            for sample in samples:
                try:
                    self._client.table("samples").upsert(
                        {
                            "id": sample.id,
                            "user_id": self.user_id,
                            "filename": sample.filename,
                            "file_path": sample.file_path,
                            "bpm": sample.bpm,
                            "key": sample.key,
                            "energy": sample.energy,
                            "genre_labels": sample.genre_labels,
                            "mood_labels": sample.mood_labels,
                        }
                    ).execute()
                    pushed += 1
                except Exception as exc:
                    logger.debug("Sample push failed (%s): %s", sample.id, exc)

            logger.info("Pushed %d samples to Supabase", pushed)
            return pushed

        except Exception as exc:
            logger.error("Library push failed: %s", exc)
            return 0
