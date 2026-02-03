import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

@dataclass
@dataclass
class OrganizationResult:
    """Result of a file organization operation"""
    source: Path
    destination: Path
    success: bool
    error: Optional[str] = None
    action: str = "move"  # move, copy, skip

class OrganizationEngine:
    """
    Engine for organizing audio files based on metadata and patterns.
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run


    async def organize_file(
        self,
        file_path: Path,
        metadata: Dict,
        pattern: str = "{genre}/{bpm}/{key}/{filename}",
        root_dir: Optional[Path] = None,
        strategy: str = "move"
    ) -> OrganizationResult:
        """
        Organize a single file based on its metadata and a pattern.
        """
        try:
            file_path = Path(file_path).resolve()
            if not file_path.exists():
                return OrganizationResult(file_path, Path(""), False, "Source file does not exist", strategy)

            # Determine root directory if not provided
            target_root = root_dir if root_dir else file_path.parent
            target_root = Path(target_root).resolve()

            # Generate relative path from pattern
            rel_path = self._generate_path(metadata, pattern, file_path.name)
            destination = target_root / rel_path

            # Handle collisions
            destination = self._handle_collision(destination)

            # Create parent directories
            if not self.dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)

            # Execute Strategy
            if strategy == "move":
                if not self.dry_run:
                    shutil.move(str(file_path), str(destination))
                logger.info(f"Moved {file_path} to {destination}")
            elif strategy == "copy":
                if not self.dry_run:
                    shutil.copy2(str(file_path), str(destination))
                logger.info(f"Copied {file_path} to {destination}")
            else:
                return OrganizationResult(file_path, destination, False, f"Unknown strategy: {strategy}", strategy)

            return OrganizationResult(file_path, destination, True, action=strategy)

        except Exception as e:
            logger.error(f"Error organizing file {file_path}: {e}")
            return OrganizationResult(file_path, Path(""), False, str(e), strategy)

    def _generate_path(self, metadata: Dict, pattern: str, original_filename: str) -> Path:
        """
        Generate the destination path based on metadata and pattern.
        """
        # Prepare context data with defaults for missing fields
        context = {
            "genre": metadata.get("genre", "Uncategorized"),
            "bpm": metadata.get("bpm", "Unknown_BPM"),
            "key": metadata.get("key", "Unknown_Key"),
            "artist": metadata.get("artist", "Unknown_Artist"),
            "album": metadata.get("album", "Unknown_Album"),
            "type": metadata.get("type", "Samples"), # Loop, OneShot, etc.
            "filename": original_filename
        }

        # Sanitize values to be filesystem safe
        for k, v in context.items():
            context[k] = str(v).replace("/", "_").replace("\\", "_")

        # Format path
        try:
            # Handle potential extra keys in pattern that might not be in our basic context
            # We use safe substitution or a more robust template engine if needed.
            # For now, standard f-string like formatting requires keys to exist.
            # Let's use string.format but careful about missing keys.
            return Path(pattern.format(**context))
        except KeyError as e:
            # Fallback for missing keys in pattern
            logger.warning(f"Missing key for pattern {pattern}: {e}. using defaults.")
            # Let's fallback to a safe default path
            return Path(f"Unorganized/{original_filename}")

    def _handle_collision(self, destination: Path) -> Path:
        """
        Handle file name collisions by appending a counter.
        Example: file.wav -> file_1.wav
        """
        if not destination.exists():
            return destination

        # If dry run, we assume it's fine unless we want to simulate state.
        # But checking existing files is safe.

        counter = 1
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent

        while True:
            new_name = f"{stem}_{counter}{suffix}"
            candidate = parent / new_name
            if not candidate.exists():
                return candidate
            counter += 1
