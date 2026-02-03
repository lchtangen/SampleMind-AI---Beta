"""
Sync Service
Manages synchronization between local library and cloud storage.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .storage import StorageProvider

logger = logging.getLogger(__name__)

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
                        # Basic optimization: Skip if exists.
                        # TODO: Add hash/size check for update
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
                    # TODO: Check size/modtime
                    continue

                # Download
                success = await self.storage.download_file(remote_path, local_dest)
                if success:
                    count += 1
            except Exception as e:
                logger.error(f"Failed to download {remote_path}: {e}")

        return count
