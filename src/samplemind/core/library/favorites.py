"""
Favorites and Collections Management System

Allows users to:
- Create collections (curated lists of samples)
- Add/remove samples from collections
- Mark samples as favorites
- Export collections
- Search across collections
- Manage collection metadata
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class CollectionType(Enum):
    """Types of collections"""
    FAVORITES = "favorites"
    CUSTOM = "custom"
    WORKFLOW = "workflow"
    ARCHIVE = "archive"


class Sample:
    """Represents a sample in a collection"""

    def __init__(
        self,
        id: str,
        filename: str,
        path: str,
        metadata: Optional[Dict] = None,
        added_at: Optional[str] = None
    ):
        self.id = id
        self.filename = filename
        self.path = path
        self.metadata = metadata or {}
        self.added_at = added_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "path": self.path,
            "metadata": self.metadata,
            "added_at": self.added_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Sample":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            filename=data["filename"],
            path=data["path"],
            metadata=data.get("metadata", {}),
            added_at=data.get("added_at")
        )


class Collection:
    """Represents a collection of samples"""

    def __init__(
        self,
        id: str,
        name: str,
        collection_type: CollectionType = CollectionType.CUSTOM,
        description: str = "",
        metadata: Optional[Dict] = None,
        created_at: Optional[str] = None
    ):
        self.id = id
        self.name = name
        self.collection_type = collection_type
        self.description = description
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.samples: Dict[str, Sample] = {}

    def add_sample(self, sample: Sample) -> bool:
        """Add sample to collection"""
        if sample.id in self.samples:
            logger.debug(f"Sample {sample.id} already in collection {self.name}")
            return False

        self.samples[sample.id] = sample
        logger.debug(f"Added {sample.filename} to {self.name}")
        return True

    def remove_sample(self, sample_id: str) -> bool:
        """Remove sample from collection"""
        if sample_id not in self.samples:
            logger.warning(f"Sample {sample_id} not in collection {self.name}")
            return False

        del self.samples[sample_id]
        logger.debug(f"Removed {sample_id} from {self.name}")
        return True

    def get_sample(self, sample_id: str) -> Optional[Sample]:
        """Get sample by ID"""
        return self.samples.get(sample_id)

    def list_samples(self) -> List[Sample]:
        """Get all samples in collection"""
        return list(self.samples.values())

    def search_samples(self, query: str) -> List[Sample]:
        """Search samples by filename or metadata"""
        query_lower = query.lower()
        results = []

        for sample in self.samples.values():
            # Search filename
            if query_lower in sample.filename.lower():
                results.append(sample)
                continue

            # Search metadata values
            for key, value in sample.metadata.items():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(sample)
                    break

        return results

    def get_size(self) -> int:
        """Get number of samples in collection"""
        return len(self.samples)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.collection_type.value,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "samples": [s.to_dict() for s in self.samples.values()]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Collection":
        """Create from dictionary"""
        collection = cls(
            id=data["id"],
            name=data["name"],
            collection_type=CollectionType(data.get("type", "custom")),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at")
        )

        # Add samples
        for sample_data in data.get("samples", []):
            sample = Sample.from_dict(sample_data)
            collection.add_sample(sample)

        return collection


class FavoritesManager:
    """
    Manages user favorites and collections.

    Provides:
    - Collection management (create, delete, rename)
    - Sample management (add, remove, search)
    - Persistence to disk
    - Collection export/import
    """

    def __init__(self, storage_dir: str = ".samplemind/collections"):
        """
        Initialize favorites manager.

        Args:
            storage_dir: Directory for storing collections
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.collections: Dict[str, Collection] = {}
        self._init_favorites_collection()
        self._load_collections()

        logger.info(f"Favorites manager initialized at {self.storage_dir.absolute()}")

    def _init_favorites_collection(self) -> None:
        """Initialize default favorites collection"""
        favorites = Collection(
            id="favorites",
            name="Favorites",
            collection_type=CollectionType.FAVORITES,
            description="Your favorite samples"
        )
        self.collections["favorites"] = favorites

    def create_collection(
        self,
        name: str,
        description: str = "",
        collection_type: CollectionType = CollectionType.CUSTOM,
        metadata: Optional[Dict] = None
    ) -> Collection:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Collection description
            collection_type: Type of collection
            metadata: Additional metadata

        Returns:
            Created collection
        """
        # Generate ID from name
        collection_id = name.lower().replace(" ", "_")

        if collection_id in self.collections:
            logger.warning(f"Collection {name} already exists")
            return self.collections[collection_id]

        collection = Collection(
            id=collection_id,
            name=name,
            collection_type=collection_type,
            description=description,
            metadata=metadata
        )

        self.collections[collection_id] = collection
        self._save_collection(collection)

        logger.info(f"Created collection: {name}")
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Get collection by ID"""
        return self.collections.get(collection_id)

    def list_collections(self, collection_type: Optional[CollectionType] = None) -> List[Collection]:
        """
        List collections.

        Args:
            collection_type: Filter by type (None = all)

        Returns:
            List of collections
        """
        collections = list(self.collections.values())

        if collection_type:
            collections = [c for c in collections if c.collection_type == collection_type]

        return sorted(collections, key=lambda c: c.created_at)

    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete collection.

        Args:
            collection_id: ID of collection to delete

        Returns:
            True if deleted
        """
        if collection_id == "favorites":
            logger.warning("Cannot delete favorites collection")
            return False

        if collection_id not in self.collections:
            logger.warning(f"Collection {collection_id} not found")
            return False

        collection_name = self.collections[collection_id].name
        del self.collections[collection_id]
        self._delete_collection_file(collection_id)

        logger.info(f"Deleted collection: {collection_name}")
        return True

    def rename_collection(self, collection_id: str, new_name: str) -> bool:
        """Rename collection"""
        if collection_id not in self.collections:
            return False

        old_name = self.collections[collection_id].name
        self.collections[collection_id].name = new_name
        self._save_collection(self.collections[collection_id])

        logger.info(f"Renamed {old_name} to {new_name}")
        return True

    def add_to_favorites(self, sample: Sample) -> bool:
        """Add sample to favorites"""
        favorites = self.collections["favorites"]
        return favorites.add_sample(sample)

    def remove_from_favorites(self, sample_id: str) -> bool:
        """Remove sample from favorites"""
        favorites = self.collections["favorites"]
        return favorites.remove_sample(sample_id)

    def add_to_collection(self, collection_id: str, sample: Sample) -> bool:
        """
        Add sample to collection.

        Args:
            collection_id: ID of collection
            sample: Sample to add

        Returns:
            True if added
        """
        collection = self.get_collection(collection_id)
        if not collection:
            logger.warning(f"Collection {collection_id} not found")
            return False

        success = collection.add_sample(sample)
        if success:
            self._save_collection(collection)

        return success

    def remove_from_collection(self, collection_id: str, sample_id: str) -> bool:
        """
        Remove sample from collection.

        Args:
            collection_id: ID of collection
            sample_id: ID of sample to remove

        Returns:
            True if removed
        """
        collection = self.get_collection(collection_id)
        if not collection:
            return False

        success = collection.remove_sample(sample_id)
        if success:
            self._save_collection(collection)

        return success

    def search_all_collections(self, query: str) -> Dict[str, List[Sample]]:
        """
        Search across all collections.

        Args:
            query: Search query

        Returns:
            Dictionary of collection_id -> matching samples
        """
        results = {}

        for collection_id, collection in self.collections.items():
            matches = collection.search_samples(query)
            if matches:
                results[collection_id] = matches

        return results

    def export_collection(self, collection_id: str, export_path: str) -> bool:
        """
        Export collection to JSON file.

        Args:
            collection_id: ID of collection to export
            export_path: Path to export to

        Returns:
            True if exported
        """
        collection = self.get_collection(collection_id)
        if not collection:
            return False

        try:
            with open(export_path, "w") as f:
                json.dump(collection.to_dict(), f, indent=2)

            logger.info(f"Exported {collection.name} to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export collection: {e}")
            return False

    def import_collection(self, import_path: str) -> Optional[Collection]:
        """
        Import collection from JSON file.

        Args:
            import_path: Path to import from

        Returns:
            Imported collection or None
        """
        try:
            with open(import_path, "r") as f:
                data = json.load(f)

            collection = Collection.from_dict(data)
            self.collections[collection.id] = collection
            self._save_collection(collection)

            logger.info(f"Imported collection: {collection.name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to import collection: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get collections statistics"""
        total_samples = sum(c.get_size() for c in self.collections.values())

        return {
            "total_collections": len(self.collections),
            "total_samples": total_samples,
            "favorites_count": self.collections["favorites"].get_size(),
            "custom_collections": len([c for c in self.collections.values() if c.collection_type == CollectionType.CUSTOM]),
        }

    def _save_collection(self, collection: Collection) -> None:
        """Save collection to disk"""
        file_path = self.storage_dir / f"{collection.id}.json"

        try:
            with open(file_path, "w") as f:
                json.dump(collection.to_dict(), f, indent=2)
            logger.debug(f"Saved collection {collection.name}")
        except Exception as e:
            logger.error(f"Failed to save collection: {e}")

    def _load_collections(self) -> None:
        """Load all collections from disk"""
        for json_file in self.storage_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                collection = Collection.from_dict(data)
                if collection.id != "favorites":  # Skip, already initialized
                    self.collections[collection.id] = collection

                logger.debug(f"Loaded collection: {collection.name}")
            except Exception as e:
                logger.warning(f"Failed to load collection from {json_file}: {e}")

    def _delete_collection_file(self, collection_id: str) -> None:
        """Delete collection file from disk"""
        file_path = self.storage_dir / f"{collection_id}.json"

        try:
            file_path.unlink(missing_ok=True)
            logger.debug(f"Deleted collection file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete collection file: {e}")


# Global favorites manager instance
_favorites_manager: Optional[FavoritesManager] = None


def init_favorites(storage_dir: str = ".samplemind/collections") -> FavoritesManager:
    """Initialize global favorites manager"""
    global _favorites_manager
    _favorites_manager = FavoritesManager(storage_dir)
    return _favorites_manager


def get_favorites() -> FavoritesManager:
    """Get global favorites manager instance"""
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager()
    return _favorites_manager
