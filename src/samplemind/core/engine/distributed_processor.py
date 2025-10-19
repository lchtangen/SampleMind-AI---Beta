"""
Distributed audio processing utilities.

This module provides utilities for parallel processing of audio files
across multiple CPU cores or machines using Dask.
"""
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import dask
import dask.bag as db
import numpy as np
from dask.distributed import Client, LocalCluster, get_worker
from loguru import logger

from ..monitoring.monitor import AudioProcessingMetrics, Monitor
from .audio_engine import AdvancedFeatureExtractor
from .feature_cache import cache


class DistributedAudioProcessor:
    """
    Distributed audio processing using Dask for parallel execution.
    
    This class provides methods to process multiple audio files in parallel,
    with built-in progress tracking and result aggregation.
    """
    
    def __init__(
        self,
        n_workers: int = -1,
        threads_per_worker: int = 1,
        memory_limit: str = '4GB',
        local_dir: str = './dask-worker-space',
        use_cache: bool = True,
        monitor: Optional[Monitor] = None
    ):
        """
        Initialize the distributed processor.
        
        Args:
            n_workers: Number of worker processes to use. If -1, uses all available cores.
            threads_per_worker: Number of threads per worker process.
            memory_limit: Memory limit per worker (e.g., '4GB').
            local_dir: Directory for Dask worker files.
            use_cache: Whether to use the feature cache.
            monitor: Optional Monitor instance for collecting metrics.
        """
        self.n_workers = os.cpu_count() if n_workers == -1 else n_workers
        self.threads_per_worker = threads_per_worker
        self.memory_limit = memory_limit
        self.local_dir = Path(local_dir)
        self.use_cache = use_cache
        self._client = None
        self._cluster = None
        
        # Initialize monitoring
        self.monitor = monitor or Monitor(service_name='samplemind-audio-distributed')
        
        # Create local directory if it doesn't exist
        self.local_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize feature extractor with monitoring
        self.extractor = AdvancedFeatureExtractor(use_cache=use_cache)
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
    
    def start(self) -> None:
        """Start the Dask client and cluster."""
        if self._client is not None:
            logger.warning("Client already running")
            return
            
        logger.info(f"Starting Dask cluster with {self.n_workers} workers")
        
        # Configure Dask to use disk-based spilling
        dask.config.set({
            'temporary_directory': str(self.local_dir.absolute()),
            'distributed.worker.memory.target': 0.6,  # Target memory usage (fraction of total)
            'distributed.worker.memory.spill': 0.7,   # Spill to disk at 70% memory usage
            'distributed.worker.memory.pause': 0.8,   # Pause at 80% memory usage
            'distributed.worker.memory.terminate': 0.95,  # Terminate at 95% memory usage
        })
        
        # Start a local Dask cluster
        self._cluster = LocalCluster(
            n_workers=self.n_workers,
            threads_per_worker=self.threads_per_worker,
            memory_limit=self.memory_limit,
            local_directory=str(self.local_dir.absolute()),
            silence_logs=30  # Only show warnings and above
        )
        
        # Start the Dask client
        self._client = Client(self._cluster)
        logger.info(f"Dask dashboard available at: {self._client.dashboard_link}")
    
    def stop(self) -> None:
        """Stop the Dask client and cluster."""
        if self._client is not None:
            self._client.close()
            self._client = None
            
        if self._cluster is not None:
            self._cluster.close()
            self._cluster = None
            
        logger.info("Stopped Dask cluster")
    
    def process_audio_files(
        self,
        file_paths: List[Union[str, Path]],
        feature_type: str = 'all',
        level: str = 'standard',
        batch_size: int = 10,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Process multiple audio files in parallel.
        
        Args:
            file_paths: List of paths to audio files
            feature_type: Type of features to extract ('rhythm', 'spectral', 'mfcc', 'all')
            level: Analysis level ('basic', 'standard', 'advanced')
            batch_size: Number of files to process in each batch
            progress_callback: Optional callback for progress updates (current, total)
            
        Returns:
            Dictionary mapping file paths to extracted features
        """
        if self._client is None:
            raise RuntimeError("Dask client not started. Call start() first.")
        
        if not file_paths:
            return {}
        
        # Record processing start time
        start_time = time.time()
        
        # Convert Path objects to strings
        file_paths = [str(p) for p in file_paths]
        total_files = len(file_paths)
        
        # Record metrics
        self.monitor.audio_metrics.record_processing_time(
            file_path="batch",
            duration_seconds=0,  # Will be updated below
            feature_type=feature_type,
            success=True
        )
        
        logger.info(f"Processing {total_files} files with {self.n_workers} workers")
        
        # Process files in batches to manage memory usage
        results = {}
        processed_count = 0
        
        try:
            for i in range(0, total_files, batch_size):
                batch = file_paths[i:i + batch_size]
                batch_start_time = time.time()
                
                logger.debug(f"Processing batch {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}")
                
                # Create a Dask bag from the batch
                bag = db.from_sequence(batch, npartitions=min(len(batch), self.n_workers * 2))
                
                # Process the batch in parallel with error handling
                try:
                    batch_results = dict(bag.map(
                        lambda x: (x, self._process_single_file(x, feature_type, level))
                    ).compute())
                    
                    # Update results
                    results.update(batch_results)
                    processed_count += len(batch_results)
                    
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    # Record failed batch
                    for file_path in batch:
                        if file_path not in results:
                            results[file_path] = {
                                '_error': str(e),
                                '_file_path': file_path,
                                '_timestamp': time.time()
                            }
                
                # Record batch metrics
                batch_duration = time.time() - batch_start_time
                self.monitor.audio_metrics.record_feature_extraction(
                    feature_type=f'batch_{feature_type}',
                    duration_seconds=batch_duration
                )
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(processed_count, total_files)
            
            # Record overall metrics
            total_duration = time.time() - start_time
            self.monitor.audio_metrics.record_processing_time(
                file_path="batch",
                duration_seconds=total_duration,
                feature_type=feature_type,
                success=True
            )
            
            logger.info(f"Processed {processed_count}/{total_files} files in {total_duration:.2f} seconds")
            
            return results
            
        except Exception as e:
            # Record error metric
            self.monitor.audio_metrics.record_processing_time(
                file_path="batch",
                duration_seconds=time.time() - start_time,
                feature_type=feature_type,
                success=False
            )
            raise
    
    def _process_single_file(
        self,
        file_path: str,
        feature_type: str,
        level: str
    ) -> Dict[str, Any]:
        """
        Process a single audio file.
        
        This method is executed on worker nodes.
        """
        # Get worker ID for logging
        try:
            worker = get_worker()
            worker_id = f"{worker.id}"
        except (ValueError, AttributeError):
            worker_id = "local"
        
        # Record start time
        start_time = time.time()
        
        try:
            # Record file processing start
            logger.debug(f"Processing {file_path} on worker {worker_id}")
            
            # Load audio file with timing
            load_start = time.time()
            y, sr = self._load_audio(file_path)
            load_time = time.time() - load_start
            
            # Record file size metric if available
            try:
                file_size = os.path.getsize(file_path)
                if hasattr(self, 'monitor'):
                    self.monitor.audio_metrics.record_file_size(file_path, file_size)
            except (OSError, AttributeError):
                pass
            
            # Extract requested features
            features = {}
            
            # Track feature extraction times
            feature_times = {}
            
            def time_feature_extraction(feature_name, extract_func, *args):
                """Helper to time feature extraction functions."""
                start = time.time()
                try:
                    result = extract_func(*args)
                    duration = time.time() - start
                    feature_times[feature_name] = duration
                    
                    # Record metric if monitor is available
                    if hasattr(self, 'monitor'):
                        self.monitor.audio_metrics.record_feature_extraction(
                            feature_type=feature_name,
                            duration_seconds=duration
                        )
                    
                    return result
                except Exception as e:
                    logger.warning(f"Error extracting {feature_name} from {file_path}: {e}")
                    return None
            
            # Extract features based on requested type
            if feature_type in ['rhythm', 'all']:
                rhythm = time_feature_extraction(
                    'rhythm', 
                    self.extractor.extract_rhythmic_features, 
                    y
                )
                if rhythm:
                    features.update(rhythm)
            
            if feature_type in ['spectral', 'all']:
                spectral = time_feature_extraction(
                    'spectral',
                    self.extractor.extract_spectral_features,
                    y
                )
                if spectral:
                    features.update(spectral)
            
            if feature_type in ['mfcc', 'all']:
                mfcc = time_feature_extraction(
                    'mfcc',
                    self.extractor.extract_mfcc_features,
                    y
                )
                if mfcc:
                    features.update(mfcc)
            
            if level in ['standard', 'advanced'] and feature_type in ['all', 'tonal']:
                try:
                    chroma = time_feature_extraction(
                        'chroma',
                        self.extractor._extract_chroma_features,
                        y
                    )
                    if chroma:
                        features.update(chroma)
                except Exception as e:
                    logger.warning(f"Failed to extract chroma features: {e}")
            
            # Calculate total processing time
            total_time = time.time() - start_time
            
            # Add metadata
            features.update({
                '_file_path': file_path,
                '_sample_rate': sr,
                '_duration': len(y) / sr if sr > 0 else 0,
                '_timestamp': time.time(),
                '_processing_metadata': {
                    'worker_id': worker_id,
                    'load_time_seconds': load_time,
                    'total_processing_time_seconds': total_time,
                    'feature_extraction_times': feature_times,
                    'success': True
                }
            })
            
            # Record successful processing
            if hasattr(self, 'monitor'):
                self.monitor.audio_metrics.record_processing_time(
                    file_path=file_path,
                    duration_seconds=total_time,
                    feature_type=feature_type,
                    success=True
                )
            
            logger.debug(f"Processed {file_path} in {total_time:.2f}s")
            
            return features
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing {file_path}: {error_msg}")
            
            # Record failed processing
            if hasattr(self, 'monitor'):
                self.monitor.audio_metrics.record_processing_time(
                    file_path=file_path,
                    duration_seconds=time.time() - start_time,
                    feature_type=feature_type,
                    success=False
                )
            
            return {
                '_error': error_msg,
                '_file_path': file_path,
                '_timestamp': time.time(),
                '_processing_metadata': {
                    'worker_id': worker_id,
                    'success': False,
                    'error': error_msg
                }
            }
    
    def _load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load an audio file with error handling and metrics.
        
        This method is executed on worker nodes.
        """
        import librosa
        
        # Record start time for metrics
        start_time = time.time()
        
        try:
            # Check if file exists and is accessible
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Get file size for metrics
            file_size = os.path.getsize(file_path)
            
            # Record file loading start
            logger.debug(f"Loading audio file: {file_path} ({file_size/1024/1024:.2f} MB)")
            
            # Load with resampling to target sample rate if needed
            y, sr = librosa.load(
                file_path,
                sr=self.extractor.sample_rate,
                mono=True,
                res_type='kaiser_fast'  # Faster resampling
            )
            
            # Ensure audio is not empty
            if len(y) == 0:
                raise ValueError("Audio file is empty")
            
            # Record successful load metrics
            load_time = time.time() - start_time
            if hasattr(self, 'monitor'):
                self.monitor.audio_metrics.record_feature_extraction(
                    feature_type='audio_loading',
                    duration_seconds=load_time
                )
            
            logger.debug(f"Loaded {file_path} in {load_time:.2f}s")
                
            return y, sr
            
        except Exception as e:
            # Record error metrics
            if hasattr(self, 'monitor'):
                self.monitor.audio_metrics.record_processing_time(
                    file_path=file_path,
                    duration_seconds=time.time() - start_time,
                    feature_type='audio_loading',
                    success=False
                )
            
            logger.error(f"Error loading {file_path}: {str(e)}")
            raise RuntimeError(f"Failed to load {file_path}: {str(e)}")


def process_audio_files_parallel(
    file_paths: List[Union[str, Path]],
    n_workers: int = -1,
    feature_type: str = 'all',
    level: str = 'standard',
    use_cache: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Process multiple audio files in parallel using a temporary Dask cluster.
    
    This is a convenience function that creates and manages a DistributedAudioProcessor
    instance for a single batch of files.
    
    Args:
        file_paths: List of paths to audio files
        n_workers: Number of worker processes to use (-1 for all available cores)
        feature_type: Type of features to extract ('rhythm', 'spectral', 'mfcc', 'all')
        level: Analysis level ('basic', 'standard', 'advanced')
        use_cache: Whether to use the feature cache
        **kwargs: Additional arguments to pass to DistributedAudioProcessor
        
    Returns:
        Dictionary mapping file paths to extracted features
    """
    with DistributedAudioProcessor(n_workers=n_workers, use_cache=use_cache, **kwargs) as processor:
        return processor.process_audio_files(file_paths, feature_type, level)
