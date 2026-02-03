"""
Sync Service
Manages synchronization between local library and cloud storage.
"""

import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from .storage import FileMetadata, StorageProvider

logger = logging.getLogger(__name__)

def calculate_file_hash(file_path: Path, algorithm: str = "sha256", chunk_size: int = 65536) -> str:
    """
    Calculate a fast hash of a local file.
    """
    hasher = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        logger.error(f"Failed to calculate hash for {file_path}: {e}")
        return ""

def files_differ(local_path: Path, remote_metadata: Optional[FileMetadata], use_hash: bool = False) -> bool:
    """
    Check if local file differs from remote version.

    Strategy:
    1. If remote doesn't exist -> Different (True)
    2. Check Size -> Different (True)
    3. Check MTime -> Different if local is newer (True)
    4. (Optional) Check Hash -> Different (True)
    """
    if not remote_metadata:
        return True

    try:
        local_stat = local_path.stat()
    except OSError:
        # If local file disappeared or is inaccessible
        return True # Treat as "needs sync/action"

    # 1. Size check (Fastest)
    if local_stat.st_size != remote_metadata["size"]:
        return True

    # 2. MTime check (Fast)
    # Note: If local mtime is > remote mtime, we assume local has changed.
    # We use a small epsilon for float comparison safety
    if local_stat.st_mtime > remote_metadata["mtime"] + 1.0:
        return True

    # 3. Hash check (Slowest, Optional)
    if use_hash and remote_metadata.get("hash"):
        local_hash = calculate_file_hash(local_path)
        if local_hash != remote_metadata["hash"]:
            return True

    return False

class SyncManager:
    """
    Manages synchronization tasks.
    """

    def __init__(self, storage_provider: StorageProvider):
        self.storage = storage_provider
        self.is_syncing = False
        self._sync_enabled = False

    async def enable_sync(self, user_id: str) -> bool:
        """Enable sync for a user"""
        # In a real app, this would verify subscription, quota, etc.
        self._sync_enabled = True
        logger.info(f"Sync enabled for user {user_id}")
        return True

    async def sync_library(self, library_path: Path, direction: str = "both") -> Dict[str, int]:
        """
        Sync local library with storage.

        Args:
            library_path: Local path to library
            direction: 'up' (local->cloud), 'down' (cloud->local), 'both'
        """
        if not self._sync_enabled:
            logger.warning("Attempted to sync but sync is disabled")
            # For now, allow it implicitly for CLI usage or enable it implicitly
            pass

        self.is_syncing = True
        stats = {"uploaded": 0, "downloaded": 0, "errors": 0}

        try:
            library_path = Path(library_path)

            # Fetch remote state once for optimization
            # In a real heavy production system, we'd use pagination or differencing
            remote_files_list = await self.storage.list_files("library")
            remote_files_set = set(remote_files_list) # e.g., {'library/subdir/file.wav'}

            # 1. Sync Up (Upload)
            if direction in ["up", "both"]:
                stats["uploaded"] = await self._sync_up(library_path, remote_files_set)

            # 2. Sync Down (Download)
            if direction in ["down", "both"]:
                stats["downloaded"] = await self._sync_down(library_path, remote_files_list)

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            stats["errors"] += 1
        finally:
            self.is_syncing = False

        return stats

    async def _sync_up(self, root: Path, remote_files_set: set) -> int:
        count = 0
        cwd = Path(root)

        # Walk through directory
        for file_path in cwd.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."): # Ignore hidden files
                try:
                    rel_path = file_path.relative_to(root)
                    remote_path = f"library/{rel_path}"

                    # Check if already exists remotely
                    if remote_path in remote_files_set:
                        # Check if it differs
                        metadata = await self.storage.get_metadata(remote_path)
                        if not files_differ(file_path, metadata):
                            continue

                    await self.storage.upload_file(file_path, remote_path)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to upload {file_path}: {e}")

        return count

    async def _sync_down(self, root: Path, remote_files: List[str]) -> int:
        count = 0

        for remote_path in remote_files:
            # remote_path looks like "library/subfolder/file.wav"
            if not remote_path.startswith("library/"):
                 continue

            try:
                # Determine relative path from "library/"
                # e.g. "library/foo.wav" -> "foo.wav"
                rel_parts = Path(remote_path).parts[1:]
                if not rel_parts:
                    continue

                rel_path = Path(*rel_parts)
                local_dest = root / rel_path

                # Check if exists locally
                if local_dest.exists():
                    metadata = await self.storage.get_metadata(remote_path)
                    if not files_differ(local_dest, metadata):
                        continue

                # Download
                success = await self.storage.download_file(remote_path, local_dest)
                if success:
                    count += 1
            except Exception as e:
                logger.error(f"Failed to download {remote_path}: {e}")

        return count
