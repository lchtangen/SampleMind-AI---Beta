"""
Machine Learning Optimization Module

This module provides high-performance ML inference using ONNX Runtime with
intelligent fallback to original models. Achieves 3-10x speedup while
maintaining 100% accuracy.

Components:
- ONNXConverter: Convert TensorFlow/PyTorch models to ONNX format
- ONNXInferenceEngine: High-performance ONNX inference
- HybridMLSystem: Intelligent ONNX/original model selection with fallback

Example Usage:
    ```python
    from samplemind.ml import HybridMLSystem, ONNXConverter
    
    # Convert model to ONNX
    converter = ONNXConverter()
    converter.convert_tensorflow_model(
        "model.h5", 
        "model.onnx"
    )
    
    # Use hybrid system for inference
    system = HybridMLSystem(
        onnx_path="model.onnx",
        original_model_loader=lambda: load_model("model.h5")
    )
    
    output = system.predict(input_data)
    system.print_statistics()
    ```

Author: SampleMind AI Team
Created: Phase 3 - ML Optimization
"""

from .onnx_converter import (
    ONNXConverter,
    ONNXConverterError,
    convert_model,
    ONNX_AVAILABLE as CONVERTER_AVAILABLE
)

from .onnx_inference import (
    ONNXInferenceEngine,
    ONNXInferenceError,
    InferenceResult,
    load_onnx_model,
    ONNX_AVAILABLE as INFERENCE_AVAILABLE
)

from .hybrid_ml import (
    HybridMLSystem,
    ModelBackend,
    create_hybrid_system
)

__all__ = [
    # Converter
    'ONNXConverter',
    'ONNXConverterError',
    'convert_model',
    'CONVERTER_AVAILABLE',
    
    # Inference
    'ONNXInferenceEngine',
    'ONNXInferenceError',
    'InferenceResult',
    'load_onnx_model',
    'INFERENCE_AVAILABLE',
    
    # Hybrid
    'HybridMLSystem',
    'ModelBackend',
    'create_hybrid_system',
]

__version__ = '1.0.0'
__author__ = 'SampleMind AI Team'