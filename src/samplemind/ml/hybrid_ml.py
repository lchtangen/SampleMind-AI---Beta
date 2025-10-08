"""
Hybrid ML System Module

Intelligently selects between ONNX and original models for optimal performance
with automatic fallback, performance tracking, and comprehensive monitoring.

Performance Target: 99%+ ONNX success rate, < 10ms fallback overhead
Author: SampleMind AI Team
Created: Phase 3 - ML Optimization
"""

import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import time
from enum import Enum

import numpy as np

from .onnx_inference import ONNXInferenceEngine, ONNXInferenceError, ONNX_AVAILABLE

logger = logging.getLogger(__name__)


class ModelBackend(Enum):
    """Available model backends"""
    ONNX = "onnx"
    ORIGINAL = "original"
    AUTO = "auto"


class HybridMLSystem:
    """
    Intelligent model selection with automatic fallback.
    
    This system attempts to use ONNX for optimal performance and automatically
    falls back to the original model if ONNX fails. It tracks success rates,
    performance metrics, and provides detailed logging.
    
    Features:
    - Automatic ONNX/original model selection
    - Graceful fallback on errors
    - Performance comparison logging
    - Success rate tracking
    - Prometheus metrics integration ready
    
    Example:
        ```python
        system = HybridMLSystem(
            onnx_path="model.onnx",
            original_model_loader=lambda: load_keras_model("model.h5")
        )
        
        result = system.predict(input_data)
        stats = system.get_statistics()
        print(f"ONNX success rate: {stats['onnx_success_rate']:.1f}%")
        ```
    """
    
    def __init__(
        self,
        onnx_path: str,
        original_model_loader: Optional[Callable] = None,
        original_model: Optional[Any] = None,
        prefer_onnx: bool = True,
        fallback_enabled: bool = True,
        use_gpu: bool = False
    ):
        """
        Initialize hybrid ML system.
        
        Args:
            onnx_path: Path to ONNX model file
            original_model_loader: Function that returns original model (lazy loading)
            original_model: Pre-loaded original model (alternative to loader)
            prefer_onnx: Try ONNX first when using AUTO mode
            fallback_enabled: Enable automatic fallback to original model
            use_gpu: Enable GPU for ONNX inference
            
        Note:
            Provide either original_model_loader or original_model, not both.
        """
        self.onnx_path = Path(onnx_path)
        self.original_model_loader = original_model_loader
        self._original_model = original_model
        self.prefer_onnx = prefer_onnx
        self.fallback_enabled = fallback_enabled
        self.use_gpu = use_gpu
        
        # Initialize ONNX engine
        self.onnx_engine: Optional[ONNXInferenceEngine] = None
        self._onnx_available = False
        
        if ONNX_AVAILABLE and self.onnx_path.exists():
            try:
                self.onnx_engine = ONNXInferenceEngine(
                    str(self.onnx_path),
                    use_gpu=use_gpu
                )
                self._onnx_available = True
                logger.info("ONNX engine initialized successfully ✓")
            except Exception as e:
                logger.warning(f"Failed to initialize ONNX engine: {e}")
                self._onnx_available = False
        else:
            if not ONNX_AVAILABLE:
                logger.warning("ONNX Runtime not available")
            if not self.onnx_path.exists():
                logger.warning(f"ONNX model not found: {self.onnx_path}")
        
        # Performance tracking
        self.stats = {
            'onnx_attempts': 0,
            'onnx_successes': 0,
            'onnx_failures': 0,
            'original_attempts': 0,
            'original_successes': 0,
            'original_failures': 0,
            'fallbacks': 0,
            'total_onnx_time_ms': 0.0,
            'total_original_time_ms': 0.0
        }
        
        logger.info(
            f"HybridMLSystem initialized\n"
            f"  ONNX available: {self._onnx_available}\n"
            f"  Prefer ONNX: {prefer_onnx}\n"
            f"  Fallback enabled: {fallback_enabled}"
        )
    
    @property
    def original_model(self):
        """Lazy-load original model"""
        if self._original_model is None and self.original_model_loader is not None:
            logger.info("Loading original model...")
            self._original_model = self.original_model_loader()
            logger.info("Original model loaded ✓")
        return self._original_model
    
    def predict(
        self,
        input_data: np.ndarray,
        backend: ModelBackend = ModelBackend.AUTO
    ) -> np.ndarray:
        """
        Run prediction with intelligent backend selection.
        
        Args:
            input_data: Input array for inference
            backend: ModelBackend.AUTO (try ONNX first), 
                    ModelBackend.ONNX (force ONNX),
                    ModelBackend.ORIGINAL (force original)
            
        Returns:
            Prediction output array
            
        Raises:
            RuntimeError: If all backends fail
            
        Example:
            ```python
            # Automatic selection (recommended)
            output = system.predict(input_data)
            
            # Force ONNX
            output = system.predict(input_data, ModelBackend.ONNX)
            ```
        """
        if backend == ModelBackend.AUTO:
            # Try ONNX first if preferred and available
            if self.prefer_onnx and self._onnx_available:
                try:
                    return self._predict_onnx(input_data)
                except Exception as e:
                    logger.warning(f"ONNX prediction failed: {e}")
                    self.stats['fallbacks'] += 1
                    
                    if self.fallback_enabled:
                        logger.info("Falling back to original model...")
                        return self._predict_original(input_data)
                    else:
                        raise
            else:
                # Use original model
                return self._predict_original(input_data)
        
        elif backend == ModelBackend.ONNX:
            return self._predict_onnx(input_data)
        
        elif backend == ModelBackend.ORIGINAL:
            return self._predict_original(input_data)
        
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    def _predict_onnx(self, input_data: np.ndarray) -> np.ndarray:
        """
        Run ONNX inference.
        
        Args:
            input_data: Input array
            
        Returns:
            Output array
        """
        if not self._onnx_available or self.onnx_engine is None:
            raise ONNXInferenceError("ONNX engine not available")
        
        self.stats['onnx_attempts'] += 1
        start_time = time.perf_counter()
        
        try:
            result = self.onnx_engine.predict(input_data)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            self.stats['onnx_successes'] += 1
            self.stats['total_onnx_time_ms'] += elapsed_ms
            
            logger.debug(f"ONNX inference: {elapsed_ms:.2f}ms ✓")
            
            return result.outputs[0]
            
        except Exception as e:
            self.stats['onnx_failures'] += 1
            logger.error(f"ONNX inference failed: {str(e)}")
            raise
    
    def _predict_original(self, input_data: np.ndarray) -> np.ndarray:
        """
        Run inference with original model.
        
        Args:
            input_data: Input array
            
        Returns:
            Output array
        """
        if self.original_model is None:
            raise RuntimeError("Original model not available")
        
        self.stats['original_attempts'] += 1
        start_time = time.perf_counter()
        
        try:
            # Call predict method on original model
            # This assumes the model has a .predict() method (Keras, sklearn, etc.)
            output = self.original_model.predict(input_data)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            
            self.stats['original_successes'] += 1
            self.stats['total_original_time_ms'] += elapsed_ms
            
            logger.debug(f"Original model inference: {elapsed_ms:.2f}ms ✓")
            
            return output
            
        except Exception as e:
            self.stats['original_failures'] += 1
            logger.error(f"Original model inference failed: {str(e)}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dict with comprehensive stats
        """
        # Calculate success rates
        onnx_success_rate = (
            (self.stats['onnx_successes'] / self.stats['onnx_attempts'] * 100)
            if self.stats['onnx_attempts'] > 0
            else 0.0
        )
        
        original_success_rate = (
            (self.stats['original_successes'] / self.stats['original_attempts'] * 100)
            if self.stats['original_attempts'] > 0
            else 0.0
        )
        
        # Calculate average times
        onnx_avg_time = (
            self.stats['total_onnx_time_ms'] / self.stats['onnx_successes']
            if self.stats['onnx_successes'] > 0
            else 0.0
        )
        
        original_avg_time = (
            self.stats['total_original_time_ms'] / self.stats['original_successes']
            if self.stats['original_successes'] > 0
            else 0.0
        )
        
        # Calculate speedup
        speedup = (
            original_avg_time / onnx_avg_time
            if onnx_avg_time > 0
            else 0.0
        )
        
        return {
            'onnx_available': self._onnx_available,
            'onnx_attempts': self.stats['onnx_attempts'],
            'onnx_successes': self.stats['onnx_successes'],
            'onnx_failures': self.stats['onnx_failures'],
            'onnx_success_rate': round(onnx_success_rate, 2),
            'onnx_avg_time_ms': round(onnx_avg_time, 2),
            'original_attempts': self.stats['original_attempts'],
            'original_successes': self.stats['original_successes'],
            'original_failures': self.stats['original_failures'],
            'original_success_rate': round(original_success_rate, 2),
            'original_avg_time_ms': round(original_avg_time, 2),
            'fallbacks': self.stats['fallbacks'],
            'speedup': round(speedup, 2),
            'prefer_onnx': self.prefer_onnx,
            'fallback_enabled': self.fallback_enabled
        }
    
    def print_statistics(self):
        """Print formatted statistics"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("HYBRID ML SYSTEM STATISTICS")
        print("="*60)
        
        if stats['onnx_available']:
            print(f"\n📊 ONNX Backend:")
            print(f"  Attempts:     {stats['onnx_attempts']}")
            print(f"  Successes:    {stats['onnx_successes']}")
            print(f"  Failures:     {stats['onnx_failures']}")
            print(f"  Success Rate: {stats['onnx_success_rate']:.1f}%")
            print(f"  Avg Time:     {stats['onnx_avg_time_ms']:.2f}ms")
        else:
            print(f"\n📊 ONNX Backend: Not Available")
        
        print(f"\n📊 Original Backend:")
        print(f"  Attempts:     {stats['original_attempts']}")
        print(f"  Successes:    {stats['original_successes']}")
        print(f"  Failures:     {stats['original_failures']}")
        print(f"  Success Rate: {stats['original_success_rate']:.1f}%")
        print(f"  Avg Time:     {stats['original_avg_time_ms']:.2f}ms")
        
        if stats['onnx_available'] and stats['speedup'] > 0:
            print(f"\n⚡ Performance:")
            print(f"  Speedup:      {stats['speedup']:.2f}x")
            print(f"  Fallbacks:    {stats['fallbacks']}")
        
        print(f"\n🔧 Configuration:")
        print(f"  Prefer ONNX:      {stats['prefer_onnx']}")
        print(f"  Fallback Enabled: {stats['fallback_enabled']}")
        print("="*60 + "\n")
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.stats = {
            'onnx_attempts': 0,
            'onnx_successes': 0,
            'onnx_failures': 0,
            'original_attempts': 0,
            'original_successes': 0,
            'original_failures': 0,
            'fallbacks': 0,
            'total_onnx_time_ms': 0.0,
            'total_original_time_ms': 0.0
        }
        
        if self.onnx_engine:
            self.onnx_engine.reset_stats()
        
        logger.info("Statistics reset")
    
    def get_onnx_info(self) -> Optional[Dict[str, Any]]:
        """Get ONNX model information"""
        if self.onnx_engine:
            return self.onnx_engine.get_model_info()
        return None
    
    def __repr__(self) -> str:
        return (
            f"HybridMLSystem("
            f"onnx_available={self._onnx_available}, "
            f"prefer_onnx={self.prefer_onnx}, "
            f"fallback={self.fallback_enabled})"
        )


def create_hybrid_system(
    onnx_path: str,
    original_model_loader: Optional[Callable] = None,
    **kwargs
) -> HybridMLSystem:
    """
    Convenience function to create hybrid ML system.
    
    Args:
        onnx_path: Path to ONNX model
        original_model_loader: Function to load original model
        **kwargs: Additional arguments for HybridMLSystem
        
    Returns:
        Initialized HybridMLSystem
        
    Example:
        ```python
        def load_model():
            return tf.keras.models.load_model("model.h5")
        
        system = create_hybrid_system(
            onnx_path="model.onnx",
            original_model_loader=load_model,
            use_gpu=True
        )
        ```
    """
    return HybridMLSystem(
        onnx_path=onnx_path,
        original_model_loader=original_model_loader,
        **kwargs
    )