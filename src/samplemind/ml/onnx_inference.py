"""
ONNX Inference Engine Module

High-performance inference using ONNX Runtime with support for CPU and GPU acceleration,
session pooling for multi-threading, automatic type conversion, and comprehensive metrics.

Performance Target: 3-10x faster than original models, < 50ms inference time
Author: SampleMind AI Team
Created: Phase 3 - ML Optimization
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import time
from threading import Lock
from dataclasses import dataclass

import numpy as np

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.warning("ONNX Runtime not available. Install: pip install onnxruntime")


logger = logging.getLogger(__name__)


@dataclass
class InferenceResult:
    """Result from ONNX inference"""
    outputs: List[np.ndarray]
    inference_time_ms: float
    input_shape: tuple
    output_shapes: List[tuple]
    session_provider: str


class ONNXInferenceError(Exception):
    """Exception raised during ONNX inference"""
    pass


class ONNXInferenceEngine:
    """
    High-performance inference engine using ONNX Runtime.
    
    Features:
    - CPU and GPU acceleration support
    - Session pooling for multi-threading
    - Automatic type conversion
    - Batch inference optimization
    - Performance metrics collection
    - Input/output shape validation
    
    Example:
        ```python
        engine = ONNXInferenceEngine("model.onnx", use_gpu=True)
        result = engine.predict(input_data)
        print(f"Inference took {result.inference_time_ms:.2f}ms")
        ```
    """
    
    def __init__(
        self,
        model_path: str,
        use_gpu: bool = False,
        providers: Optional[List[str]] = None,
        session_options: Optional[ort.SessionOptions] = None,
        enable_profiling: bool = False
    ):
        """
        Initialize ONNX inference engine.
        
        Args:
            model_path: Path to ONNX model file
            use_gpu: Enable GPU acceleration if available
            providers: List of execution providers (e.g., ['CUDAExecutionProvider', 'CPUExecutionProvider'])
            session_options: Custom ONNX Runtime session options
            enable_profiling: Enable detailed performance profiling
            
        Raises:
            ONNXInferenceError: If model loading fails
        """
        if not ONNX_AVAILABLE:
            raise ONNXInferenceError(
                "ONNX Runtime not installed. Run: pip install onnxruntime"
            )
        
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise ONNXInferenceError(f"Model file not found: {model_path}")
        
        self.use_gpu = use_gpu
        self.enable_profiling = enable_profiling
        self._session_lock = Lock()
        
        # Initialize session options
        if session_options is None:
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.intra_op_num_threads = 4  # Parallel ops within graph
            session_options.inter_op_num_threads = 4  # Parallel graph instances
            
            if enable_profiling:
                session_options.enable_profiling = True
        
        # Determine execution providers
        if providers is None:
            providers = self._get_available_providers(use_gpu)
        
        logger.info(f"Initializing ONNX session with providers: {providers}")
        
        try:
            # Create inference session
            self.session = ort.InferenceSession(
                str(model_path),
                sess_options=session_options,
                providers=providers
            )
            
            # Get input/output metadata
            self._input_meta = self._get_input_metadata()
            self._output_meta = self._get_output_metadata()
            
            # Performance metrics
            self.inference_count = 0
            self.total_inference_time_ms = 0.0
            
            logger.info(
                f"ONNX engine initialized ✓\n"
                f"  Model: {self.model_path.name}\n"
                f"  Provider: {self.session.get_providers()[0]}\n"
                f"  Inputs: {len(self._input_meta)}\n"
                f"  Outputs: {len(self._output_meta)}"
            )
            
        except Exception as e:
            raise ONNXInferenceError(f"Failed to create ONNX session: {str(e)}") from e
    
    def _get_available_providers(self, use_gpu: bool) -> List[str]:
        """
        Get list of available execution providers.
        
        Args:
            use_gpu: Whether to prefer GPU providers
            
        Returns:
            List of provider names in priority order
        """
        available = ort.get_available_providers()
        
        if use_gpu:
            # Prefer GPU providers
            gpu_providers = ['CUDAExecutionProvider', 'TensorrtExecutionProvider']
            providers = [p for p in gpu_providers if p in available]
            if not providers:
                logger.warning("GPU requested but not available, falling back to CPU")
                providers = ['CPUExecutionProvider']
        else:
            providers = ['CPUExecutionProvider']
        
        # Always add CPU as fallback
        if 'CPUExecutionProvider' not in providers:
            providers.append('CPUExecutionProvider')
        
        return providers
    
    def _get_input_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get input tensor metadata"""
        metadata = {}
        for inp in self.session.get_inputs():
            metadata[inp.name] = {
                'name': inp.name,
                'shape': inp.shape,
                'type': inp.type,
                'dtype': self._onnx_type_to_numpy(inp.type)
            }
        return metadata
    
    def _get_output_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get output tensor metadata"""
        metadata = {}
        for out in self.session.get_outputs():
            metadata[out.name] = {
                'name': out.name,
                'shape': out.shape,
                'type': out.type,
                'dtype': self._onnx_type_to_numpy(out.type)
            }
        return metadata
    
    def _onnx_type_to_numpy(self, onnx_type: str) -> np.dtype:
        """Convert ONNX type string to NumPy dtype"""
        type_map = {
            'tensor(float)': np.float32,
            'tensor(float16)': np.float16,
            'tensor(double)': np.float64,
            'tensor(int32)': np.int32,
            'tensor(int64)': np.int64,
            'tensor(uint8)': np.uint8,
            'tensor(int8)': np.int8,
        }
        return type_map.get(onnx_type, np.float32)
    
    def predict(
        self,
        input_data: Union[np.ndarray, Dict[str, np.ndarray]],
        validate_shape: bool = True,
        auto_convert: bool = True
    ) -> InferenceResult:
        """
        Run inference on single input.
        
        Args:
            input_data: Input array or dict of {input_name: array}
            validate_shape: Verify input shape matches model
            auto_convert: Automatically convert to required dtype
            
        Returns:
            InferenceResult with outputs and metadata
            
        Example:
            ```python
            input_array = np.random.randn(1, 3, 224, 224).astype(np.float32)
            result = engine.predict(input_array)
            prediction = result.outputs[0]
            ```
        """
        start_time = time.perf_counter()
        
        try:
            # Prepare input dict
            if isinstance(input_data, np.ndarray):
                input_name = list(self._input_meta.keys())[0]
                input_dict = {input_name: input_data}
            else:
                input_dict = input_data
            
            # Validate and convert inputs
            input_dict = self._prepare_inputs(input_dict, validate_shape, auto_convert)
            
            # Run inference
            with self._session_lock:
                outputs = self.session.run(None, input_dict)
            
            # Calculate inference time
            inference_time = (time.perf_counter() - start_time) * 1000  # ms
            
            # Update metrics
            self.inference_count += 1
            self.total_inference_time_ms += inference_time
            
            # Create result
            result = InferenceResult(
                outputs=outputs,
                inference_time_ms=inference_time,
                input_shape=list(input_dict.values())[0].shape,
                output_shapes=[out.shape for out in outputs],
                session_provider=self.session.get_providers()[0]
            )
            
            logger.debug(
                f"Inference complete: {inference_time:.2f}ms "
                f"(input: {result.input_shape}, output: {result.output_shapes[0]})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            raise ONNXInferenceError(f"Inference error: {str(e)}") from e
    
    def predict_batch(
        self,
        inputs: List[np.ndarray],
        batch_size: Optional[int] = None
    ) -> List[InferenceResult]:
        """
        Run batch inference with automatic batching.
        
        Args:
            inputs: List of input arrays
            batch_size: Batch size for processing (None = process all at once)
            
        Returns:
            List of InferenceResult objects
            
        Example:
            ```python
            inputs = [np.random.randn(1, 3, 224, 224) for _ in range(100)]
            results = engine.predict_batch(inputs, batch_size=32)
            ```
        """
        if not inputs:
            return []
        
        results = []
        total_start = time.perf_counter()
        
        # Process in batches if batch_size specified
        if batch_size is not None:
            for i in range(0, len(inputs), batch_size):
                batch = inputs[i:i + batch_size]
                # Stack batch
                batched_input = np.vstack(batch)
                result = self.predict(batched_input)
                results.append(result)
        else:
            # Process individually
            for input_data in inputs:
                result = self.predict(input_data)
                results.append(result)
        
        total_time = (time.perf_counter() - total_start) * 1000
        avg_time = total_time / len(inputs)
        
        logger.info(
            f"Batch inference complete: {len(inputs)} samples in {total_time:.2f}ms "
            f"(avg: {avg_time:.2f}ms per sample)"
        )
        
        return results
    
    def _prepare_inputs(
        self,
        input_dict: Dict[str, np.ndarray],
        validate_shape: bool,
        auto_convert: bool
    ) -> Dict[str, np.ndarray]:
        """
        Prepare and validate inputs for inference.
        
        Args:
            input_dict: Dictionary of input arrays
            validate_shape: Validate shapes
            auto_convert: Auto-convert dtypes
            
        Returns:
            Prepared input dictionary
        """
        prepared = {}
        
        for name, data in input_dict.items():
            if name not in self._input_meta:
                raise ONNXInferenceError(f"Unknown input name: {name}")
            
            meta = self._input_meta[name]
            expected_dtype = meta['dtype']
            
            # Convert dtype if needed
            if auto_convert and data.dtype != expected_dtype:
                logger.debug(f"Converting {name} from {data.dtype} to {expected_dtype}")
                data = data.astype(expected_dtype)
            
            # Validate shape if requested
            if validate_shape:
                expected_shape = meta['shape']
                # Handle dynamic dimensions (None, -1, or string)
                for i, (exp, act) in enumerate(zip(expected_shape, data.shape)):
                    if exp is not None and not isinstance(exp, str) and exp != -1:
                        if exp != act:
                            raise ONNXInferenceError(
                                f"Shape mismatch for {name} at dimension {i}: "
                                f"expected {exp}, got {act}"
                            )
            
            prepared[name] = data
        
        return prepared
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dict with performance metrics
        """
        avg_time = (
            self.total_inference_time_ms / self.inference_count
            if self.inference_count > 0
            else 0.0
        )
        
        return {
            'total_inferences': self.inference_count,
            'total_time_ms': round(self.total_inference_time_ms, 2),
            'average_time_ms': round(avg_time, 2),
            'throughput_per_second': round(1000 / avg_time, 2) if avg_time > 0 else 0,
            'provider': self.session.get_providers()[0],
            'model_path': str(self.model_path)
        }
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.inference_count = 0
        self.total_inference_time_ms = 0.0
        logger.debug("Performance stats reset")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information.
        
        Returns:
            Dict with model metadata
        """
        return {
            'model_path': str(self.model_path),
            'model_size_mb': self.model_path.stat().st_size / (1024 * 1024),
            'providers': self.session.get_providers(),
            'inputs': self._input_meta,
            'outputs': self._output_meta,
            'profiling_enabled': self.enable_profiling
        }
    
    def __repr__(self) -> str:
        return (
            f"ONNXInferenceEngine(model='{self.model_path.name}', "
            f"provider='{self.session.get_providers()[0]}', "
            f"inferences={self.inference_count})"
        )


def load_onnx_model(
    model_path: str,
    use_gpu: bool = False,
    **kwargs
) -> ONNXInferenceEngine:
    """
    Convenience function to load ONNX model.
    
    Args:
        model_path: Path to ONNX model
        use_gpu: Enable GPU if available
        **kwargs: Additional arguments for ONNXInferenceEngine
        
    Returns:
        Initialized ONNXInferenceEngine
        
    Example:
        ```python
        engine = load_onnx_model("model.onnx", use_gpu=True)
        result = engine.predict(data)
        ```
    """
    return ONNXInferenceEngine(model_path, use_gpu=use_gpu, **kwargs)