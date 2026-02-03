"""
Feature caching for audio processing results.

This module provides a caching mechanism for audio feature extraction
results to improve performance for repeated analyses.
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import numpy as np
from loguru import logger


class FeatureCache:
    """
    Disk-based cache for audio features.
    
    Features are stored in a cache directory with filenames derived from
    the audio content and feature extraction parameters.
    """
    
    def __init__(self, cache_dir: str = ".feature_cache") -> None:
        """
        Initialize the feature cache.
        
        Args:
            cache_dir: Directory to store cached features
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized feature cache at {self.cache_dir.absolute()}")
    
    def _get_cache_key(self, audio_data: np.ndarray, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for the given audio data and parameters.
        
        Args:
            audio_data: Audio data as a numpy array
            params: Dictionary of feature extraction parameters
            
        Returns:
            A unique string key for the cache entry
        """
        # Create a hash of the audio data and parameters
        hash_input = (
            audio_data.tobytes() + 
            json.dumps(params, sort_keys=True).encode()
        )
        return hashlib.sha256(hash_input).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get the filesystem path for a cache key.
        
        Args:
            key: Cache key
            
        Returns:
            Path to the cache file
        """
        return self.cache_dir / f"{key}.npz"
    
    def get(self, audio_data: np.ndarray, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached features for the given audio data and parameters.
        
        Args:
            audio_data: Audio data as a numpy array
            params: Dictionary of feature extraction parameters
            
        Returns:
            Cached features as a dictionary, or None if not found
        """
        key = self._get_cache_key(audio_data, params)
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
            
        try:
            # Load cached data
            data = np.load(cache_path, allow_pickle=True)
            features = {k: data[k] for k in data.files}
            
            # Convert any numpy arrays back to their original types
            for k, v in features.items():
                if isinstance(v, np.ndarray) and v.dtype == object:
                    features[k] = v.item()
            
            logger.debug(f"Cache hit: {key}")
            return features
            
        except Exception as e:
            logger.warning(f"Error loading from cache: {e}")
            return None
    
    def set(self, audio_data: np.ndarray, params: Dict[str, Any], features: Dict[str, Any]) -> None:
        """
        Cache features for the given audio data and parameters.
        
        Args:
            audio_data: Audio data as a numpy array
            params: Dictionary of feature extraction parameters
            features: Features to cache
        """
        key = self._get_cache_key(audio_data, params)
        cache_path = self._get_cache_path(key)
        
        try:
            # Convert any non-numpy values to numpy arrays for storage
            np.savez_compressed(
                cache_path,
                **{
                    k: np.array(v) if not isinstance(v, np.ndarray) else v
                    for k, v in features.items()
                }
            )
            logger.debug(f"Cached features: {key}")
            
        except Exception as e:
            logger.error(f"Error caching features: {e}")
    
    def clear(self) -> None:
        """Clear all cached features."""
        for path in self.cache_dir.glob("*.npz"):
            try:
                path.unlink()
            except Exception as e:
                logger.error(f"Error clearing cache file {path}: {e}")
        
        logger.info("Cleared feature cache")


# Global cache instance
cache = FeatureCache()
