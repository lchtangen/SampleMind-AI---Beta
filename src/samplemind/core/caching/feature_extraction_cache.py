"""
Optimized Feature Extraction Caching

Provides intelligent caching for audio feature extraction results
to minimize redundant computation and speed up repeated analyses.

Strategy:
1. Memory cache for frequently accessed features (LRU)
2. Disk cache for persistent storage (with SHA256 file hashing)
3. Adaptive TTL based on file modification time
4. Automatic invalidation on file changes
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from collections import OrderedDict

import numpy as np

logger = logging.getLogger(__name__)


class FeatureExtractionCache:
    """
    Optimized feature extraction cache with memory and disk storage.

    Features:
    - Memory cache with LRU eviction (configurable max size)
    - Disk-based persistent cache
    - File modification time tracking
    - Automatic invalidation on file changes
    - Cache statistics and monitoring
    """

    def __init__(
        self,
        memory_max_items: int = 1000,
        cache_dir: str = ".feature_cache",
        enable_disk_cache: bool = True
    ):
        """
        Initialize feature extraction cache.

        Args:
            memory_max_items: Maximum items to keep in memory (LRU)
            cache_dir: Directory for disk-based cache
            enable_disk_cache: Enable persistent disk caching
        """
        self.memory_max_items = memory_max_items
        self.cache_dir = Path(cache_dir)
        self.enable_disk_cache = enable_disk_cache

        if enable_disk_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache with LRU eviction
        self.memory_cache: OrderedDict[str, Tuple[Dict, float]] = OrderedDict()

        # File metadata tracking (path -> (mtime, hash))
        self.file_metadata: Dict[str, Tuple[float, str]] = {}

        # Statistics
        self.memory_hits = 0
        self.disk_hits = 0
        self.misses = 0
        self.invalidations = 0

        logger.info(
            f"Feature extraction cache initialized "
            f"(memory_max={memory_max_items}, disk_enabled={enable_disk_cache})"
        )

    def _get_file_hash(self, file_path: str) -> str:
        """
        Get SHA256 hash of file content.
        Used to detect file changes.
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Failed to hash file {file_path}: {e}")
            return "unknown"

    def _get_file_mtime(self, file_path: str) -> float:
        """Get file modification time."""
        try:
            return Path(file_path).stat().st_mtime
        except Exception:
            return 0.0

    def _generate_cache_key(
        self,
        file_path: str,
        analysis_level: str = "standard"
    ) -> str:
        """
        Generate deterministic cache key from file path and analysis level.

        Key includes file hash for change detection.
        """
        file_hash = self._get_file_hash(file_path)
        key_data = f"{file_path}:{analysis_level}:{file_hash}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_disk_cache_path(self, cache_key: str) -> Path:
        """Get filesystem path for cached features."""
        return self.cache_dir / f"{cache_key}.npz"

    def get(
        self,
        file_path: str,
        analysis_level: str = "standard"
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached features for audio file.

        Checks in order:
        1. Memory cache (fastest)
        2. Disk cache (fast)
        3. Returns None if not cached

        Args:
            file_path: Path to audio file
            analysis_level: Analysis complexity level

        Returns:
            Cached features dict or None if not found/invalid
        """
        cache_key = self._generate_cache_key(file_path, analysis_level)

        # Check memory cache
        if cache_key in self.memory_cache:
            features, timestamp = self.memory_cache[cache_key]

            # Verify file hasn't changed
            if self._is_cache_valid(file_path, cache_key):
                self.memory_hits += 1
                # Move to end (LRU)
                self.memory_cache.move_to_end(cache_key)
                logger.debug(f"Memory cache hit: {Path(file_path).name}")
                return features

            # Cache invalid, remove it
            del self.memory_cache[cache_key]
            self.invalidations += 1

        # Check disk cache
        if self.enable_disk_cache:
            disk_path = self._get_disk_cache_path(cache_key)
            if disk_path.exists():
                try:
                    if self._is_cache_valid(file_path, cache_key):
                        features = self._load_from_disk(disk_path)
                        if features is not None:
                            # Load into memory cache
                            self._add_to_memory_cache(cache_key, features)
                            self.disk_hits += 1
                            logger.debug(f"Disk cache hit: {Path(file_path).name}")
                            return features
                except Exception as e:
                    logger.warning(f"Failed to load from disk cache: {e}")

        self.misses += 1
        return None

    def set(
        self,
        file_path: str,
        features: Dict[str, Any],
        analysis_level: str = "standard"
    ) -> bool:
        """
        Cache extracted features for audio file.

        Stores in both memory and disk (if enabled).

        Args:
            file_path: Path to audio file
            features: Extracted audio features
            analysis_level: Analysis complexity level

        Returns:
            True if successful
        """
        try:
            cache_key = self._generate_cache_key(file_path, analysis_level)

            # Store metadata
            file_mtime = self._get_file_mtime(file_path)
            file_hash = self._get_file_hash(file_path)
            self.file_metadata[cache_key] = (file_mtime, file_hash)

            # Add to memory cache
            self._add_to_memory_cache(cache_key, features)

            # Save to disk
            if self.enable_disk_cache:
                disk_path = self._get_disk_cache_path(cache_key)
                self._save_to_disk(disk_path, features)

            logger.debug(f"Cached features: {Path(file_path).name}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache features: {e}")
            return False

    def _add_to_memory_cache(self, cache_key: str, features: Dict) -> None:
        """Add features to memory cache with LRU eviction."""
        # If already exists, remove it (to move to end)
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]

        # Check size limit
        if len(self.memory_cache) >= self.memory_max_items:
            # Remove oldest (first) item
            self.memory_cache.popitem(last=False)
            logger.debug("Memory cache LRU eviction triggered")

        # Add to end (most recent)
        self.memory_cache[cache_key] = (features, time.time())

    def _is_cache_valid(self, file_path: str, cache_key: str) -> bool:
        """
        Check if cached features are still valid.

        Cache is invalid if:
        - File has been modified
        - File hash doesn't match
        """
        if cache_key not in self.file_metadata:
            return False

        try:
            cached_mtime, cached_hash = self.file_metadata[cache_key]
            current_mtime = self._get_file_mtime(file_path)

            # Check modification time
            if current_mtime > cached_mtime:
                logger.debug(f"Cache invalidated: file modified {file_path}")
                return False

            # Check file hash (double check)
            current_hash = self._get_file_hash(file_path)
            if current_hash != cached_hash:
                logger.debug(f"Cache invalidated: file hash changed {file_path}")
                return False

            return True

        except Exception as e:
            logger.warning(f"Cache validation failed: {e}")
            return False

    def _load_from_disk(self, disk_path: Path) -> Optional[Dict[str, Any]]:
        """Load features from disk cache."""
        try:
            data = np.load(disk_path, allow_pickle=True)
            features = {k: data[k].item() if data[k].dtype == object else data[k] for k in data.files}
            return features
        except Exception as e:
            logger.warning(f"Failed to load from disk: {e}")
            return None

    def _save_to_disk(self, disk_path: Path, features: Dict[str, Any]) -> None:
        """Save features to disk cache."""
        try:
            # Convert numpy arrays and prepare for storage
            save_data = {}
            for key, value in features.items():
                if isinstance(value, np.ndarray):
                    save_data[key] = value
                else:
                    save_data[key] = np.array(value)

            np.savez_compressed(disk_path, **save_data)
        except Exception as e:
            logger.warning(f"Failed to save to disk: {e}")

    def invalidate(self, file_path: str) -> None:
        """Manually invalidate cache for a file."""
        cache_keys_to_remove = [
            k for k in self.file_metadata.keys()
            if file_path in str(k)
        ]

        for cache_key in cache_keys_to_remove:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            if cache_key in self.file_metadata:
                del self.file_metadata[cache_key]

            # Remove disk cache
            if self.enable_disk_cache:
                disk_path = self._get_disk_cache_path(cache_key)
                try:
                    disk_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete disk cache: {e}")

        logger.debug(f"Invalidated {len(cache_keys_to_remove)} cache entries for {file_path}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = self.memory_hits + self.disk_hits
        total_requests = total_hits + self.misses

        return {
            "memory_hits": self.memory_hits,
            "disk_hits": self.disk_hits,
            "misses": self.misses,
            "invalidations": self.invalidations,
            "hit_rate_percent": (
                (total_hits / total_requests * 100) if total_requests > 0 else 0.0
            ),
            "memory_items": len(self.memory_cache),
            "memory_max": self.memory_max_items,
            "disk_enabled": self.enable_disk_cache,
            "total_requests": total_requests
        }

    def clear(self) -> None:
        """Clear all caches."""
        self.memory_cache.clear()
        self.file_metadata.clear()
        self.memory_hits = 0
        self.disk_hits = 0
        self.misses = 0
        self.invalidations = 0

        if self.enable_disk_cache:
            for cache_file in self.cache_dir.glob("*.npz"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file: {e}")

        logger.info("Feature extraction cache cleared")


# Global instance
_feature_cache: Optional[FeatureExtractionCache] = None


def init_feature_cache(**kwargs) -> FeatureExtractionCache:
    """Initialize global feature extraction cache."""
    global _feature_cache
    _feature_cache = FeatureExtractionCache(**kwargs)
    return _feature_cache


def get_feature_cache() -> FeatureExtractionCache:
    """Get global feature extraction cache instance."""
    global _feature_cache
    if _feature_cache is None:
        _feature_cache = FeatureExtractionCache()
    return _feature_cache
