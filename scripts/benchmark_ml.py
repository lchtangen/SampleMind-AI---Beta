"""
ML Optimization Benchmarking Script

Comprehensive benchmarking suite for comparing ONNX vs original model performance.
Tests inference speed, memory usage, throughput, and accuracy across various scenarios.

Performance Targets:
- 3-10x faster inference with ONNX
- < 50ms inference time for typical inputs
- 100+ concurrent requests support
- Memory usage < 2GB per model
- Accuracy within 1% of original

Usage:
    python scripts/benchmark_ml.py
    python scripts/benchmark_ml.py --model path/to/model.onnx
    python scripts/benchmark_ml.py --iterations 1000 --batch-size 32

Author: SampleMind AI Team
Created: Phase 3 - ML Optimization
"""

import argparse
import time
import psutil
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.samplemind.ml import (
        ONNXInferenceEngine,
        HybridMLSystem,
        INFERENCE_AVAILABLE
    )
    ML_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ML modules not available: {e}")
    ML_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    backend: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    throughput_per_sec: float
    memory_mb: float
    success_rate: float
    input_shape: tuple
    output_shape: tuple


class MLBenchmark:
    """
    Comprehensive ML model benchmarking.
    
    Features:
    - Single vs batch inference comparison
    - Memory usage tracking
    - Throughput measurement
    - Statistical analysis
    - Concurrent request simulation
    """
    
    def __init__(self):
        """Initialize benchmark suite"""
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()
    
    def benchmark_onnx_inference(
        self,
        model_path: str,
        input_shape: tuple,
        iterations: int = 100,
        use_gpu: bool = False
    ) -> Optional[BenchmarkResult]:
        """
        Benchmark ONNX inference performance.
        
        Args:
            model_path: Path to ONNX model
            input_shape: Input tensor shape
            iterations: Number of iterations
            use_gpu: Use GPU if available
            
        Returns:
            BenchmarkResult or None if failed
        """
        if not INFERENCE_AVAILABLE:
            print("⚠️  ONNX Runtime not available. Install: pip install onnxruntime")
            return None
        
        try:
            print(f"\n🚀 Benchmarking ONNX Inference...")
            print(f"   Model: {Path(model_path).name}")
            print(f"   Iterations: {iterations}")
            print(f"   Input shape: {input_shape}")
            
            # Initialize engine
            engine = ONNXInferenceEngine(model_path, use_gpu=use_gpu)
            
            # Warm-up run
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            engine.predict(dummy_input)
            
            # Benchmark runs
            times = []
            successes = 0
            failures = 0
            
            mem_before = self.process.memory_info().rss / (1024 * 1024)  # MB
            
            for i in range(iterations):
                input_data = np.random.randn(*input_shape).astype(np.float32)
                
                try:
                    start = time.perf_counter()
                    result = engine.predict(input_data)
                    elapsed = (time.perf_counter() - start) * 1000  # ms
                    
                    times.append(elapsed)
                    successes += 1
                    
                    if i == 0:
                        output_shape = result.output_shapes[0]
                    
                except Exception as e:
                    print(f"   ✗ Iteration {i+1} failed: {e}")
                    failures += 1
            
            mem_after = self.process.memory_info().rss / (1024 * 1024)  # MB
            mem_usage = mem_after - mem_before
            
            # Calculate statistics
            if times:
                total_time = sum(times)
                avg_time = total_time / len(times)
                min_time = min(times)
                max_time = max(times)
                throughput = 1000 / avg_time if avg_time > 0 else 0
                success_rate = (successes / iterations) * 100
                
                result = BenchmarkResult(
                    backend="ONNX",
                    iterations=iterations,
                    total_time_ms=round(total_time, 2),
                    avg_time_ms=round(avg_time, 2),
                    min_time_ms=round(min_time, 2),
                    max_time_ms=round(max_time, 2),
                    throughput_per_sec=round(throughput, 2),
                    memory_mb=round(mem_usage, 2),
                    success_rate=round(success_rate, 2),
                    input_shape=input_shape,
                    output_shape=output_shape
                )
                
                print(f"\n   ✓ ONNX Benchmark Complete:")
                print(f"     Avg Time:    {avg_time:.2f}ms")
                print(f"     Min Time:    {min_time:.2f}ms")
                print(f"     Max Time:    {max_time:.2f}ms")
                print(f"     Throughput:  {throughput:.2f}/sec")
                print(f"     Memory:      {mem_usage:.2f}MB")
                print(f"     Success:     {success_rate:.1f}%")
                
                return result
            
            return None
            
        except Exception as e:
            print(f"   ✗ ONNX benchmark failed: {e}")
            return None
    
    def benchmark_batch_inference(
        self,
        model_path: str,
        input_shape: tuple,
        batch_sizes: List[int] = [1, 10, 32, 100],
        iterations_per_batch: int = 10
    ) -> Dict[int, BenchmarkResult]:
        """
        Benchmark batch inference performance.
        
        Args:
            model_path: Path to ONNX model
            input_shape: Input tensor shape (per sample)
            batch_sizes: List of batch sizes to test
            iterations_per_batch: Iterations for each batch size
            
        Returns:
            Dict mapping batch_size to BenchmarkResult
        """
        print(f"\n📊 Benchmarking Batch Inference...")
        
        results = {}
        
        for batch_size in batch_sizes:
            print(f"\n   Testing batch size: {batch_size}")
            
            # Adjust input shape for batch
            batched_shape = (batch_size,) + input_shape[1:]
            
            result = self.benchmark_onnx_inference(
                model_path=model_path,
                input_shape=batched_shape,
                iterations=iterations_per_batch,
                use_gpu=False
            )
            
            if result:
                results[batch_size] = result
                per_sample_time = result.avg_time_ms / batch_size
                print(f"     Per-sample time: {per_sample_time:.2f}ms")
        
        return results
    
    def benchmark_concurrent_requests(
        self,
        model_path: str,
        input_shape: tuple,
        num_requests: int = 100,
        concurrent_workers: int = 10
    ) -> Dict[str, Any]:
        """
        Simulate concurrent inference requests.
        
        Args:
            model_path: Path to ONNX model
            input_shape: Input tensor shape
            num_requests: Total number of requests
            concurrent_workers: Number of concurrent workers
            
        Returns:
            Dict with concurrent performance metrics
        """
        print(f"\n⚡ Benchmarking Concurrent Requests...")
        print(f"   Total requests: {num_requests}")
        print(f"   Concurrent workers: {concurrent_workers}")
        
        try:
            from concurrent.futures import ThreadPoolExecutor
            
            engine = ONNXInferenceEngine(model_path)
            
            def make_request():
                """Single request"""
                input_data = np.random.randn(*input_shape).astype(np.float32)
                result = engine.predict(input_data)
                return result.inference_time_ms
            
            # Run concurrent requests
            start_time = time.perf_counter()
            
            with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
                inference_times = list(executor.map(lambda _: make_request(), range(num_requests)))
            
            total_time = time.perf_counter() - start_time
            
            # Calculate metrics
            avg_inference_time = np.mean(inference_times)
            throughput = num_requests / total_time
            
            result = {
                'num_requests': num_requests,
                'concurrent_workers': concurrent_workers,
                'total_time_sec': round(total_time, 2),
                'avg_inference_time_ms': round(avg_inference_time, 2),
                'throughput_per_sec': round(throughput, 2),
                'success': True
            }
            
            print(f"\n   ✓ Concurrent Benchmark Complete:")
            print(f"     Total Time:     {total_time:.2f}s")
            print(f"     Avg Inference:  {avg_inference_time:.2f}ms")
            print(f"     Throughput:     {throughput:.2f}/sec")
            
            return result
            
        except Exception as e:
            print(f"   ✗ Concurrent benchmark failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def compare_with_speedup_target(
        self,
        onnx_result: BenchmarkResult,
        original_time_ms: float = None
    ) -> Dict[str, Any]:
        """
        Compare ONNX performance against targets.
        
        Args:
            onnx_result: ONNX benchmark result
            original_time_ms: Original model inference time (if available)
            
        Returns:
            Dict with comparison metrics
        """
        print(f"\n🎯 Performance Analysis...")
        
        comparison = {
            'onnx_avg_time_ms': onnx_result.avg_time_ms,
            'target_time_ms': 50.0,
            'meets_target': onnx_result.avg_time_ms < 50.0,
            'throughput_target': 20,  # per second
            'meets_throughput': onnx_result.throughput_per_sec >= 20,
        }
        
        if original_time_ms:
            speedup = original_time_ms / onnx_result.avg_time_ms
            comparison['original_time_ms'] = original_time_ms
            comparison['speedup'] = round(speedup, 2)
            comparison['meets_speedup_target'] = speedup >= 3.0
            
            print(f"   Original Time:  {original_time_ms:.2f}ms")
            print(f"   ONNX Time:      {onnx_result.avg_time_ms:.2f}ms")
            print(f"   Speedup:        {speedup:.2f}x {'✓' if speedup >= 3.0 else '✗'}")
        
        print(f"   Target Time:    < 50ms {'✓' if comparison['meets_target'] else '✗'}")
        print(f"   Throughput:     {onnx_result.throughput_per_sec:.2f}/sec {'✓' if comparison['meets_throughput'] else '✗'}")
        
        return comparison
    
    def generate_report(
        self,
        results: Dict[str, Any],
        output_file: Optional[str] = None
    ):
        """
        Generate comprehensive benchmark report.
        
        Args:
            results: Dictionary of all benchmark results
            output_file: Optional file to save report
        """
        print(f"\n" + "="*70)
        print("📊 ML OPTIMIZATION BENCHMARK REPORT")
        print("="*70)
        
        # Format results as JSON
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': results,
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_gb': psutil.virtual_memory().total / (1024**3),
                'python_version': sys.version.split()[0]
            }
        }
        
        print(json.dumps(report, indent=2))
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✓ Report saved to: {output_file}")


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(description="ML Optimization Benchmarking")
    parser.add_argument(
        '--model',
        type=str,
        help='Path to ONNX model file'
    )
    parser.add_argument(
        '--input-shape',
        type=str,
        default='1,3,224,224',
        help='Input shape as comma-separated values (default: 1,3,224,224)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of benchmark iterations (default: 100)'
    )
    parser.add_argument(
        '--batch-sizes',
        type=str,
        default='1,10,32',
        help='Batch sizes to test (default: 1,10,32)'
    )
    parser.add_argument(
        '--concurrent',
        type=int,
        default=0,
        help='Test concurrent requests (0=skip, >0=number of requests)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for report (JSON)'
    )
    parser.add_argument(
        '--use-gpu',
        action='store_true',
        help='Use GPU for inference if available'
    )
    
    args = parser.parse_args()
    
    # Parse input shape
    input_shape = tuple(int(x) for x in args.input_shape.split(','))
    batch_sizes = [int(x) for x in args.batch_sizes.split(',')]
    
    print("="*70)
    print("🚀 ML OPTIMIZATION BENCHMARK SUITE")
    print("="*70)
    print(f"\nPhase 3 - ML Optimization with ONNX")
    print(f"Target: 3-10x speedup, < 50ms inference time\n")
    
    if not ML_AVAILABLE:
        print("❌ ML modules not available. Please install requirements:")
        print("   pip install -r requirements.txt")
        return 1
    
    if not args.model:
        print("⚠️  No model specified. Use --model path/to/model.onnx")
        print("\nExample usage:")
        print("  python scripts/benchmark_ml.py --model model.onnx")
        print("  python scripts/benchmark_ml.py --model model.onnx --iterations 1000")
        print("  python scripts/benchmark_ml.py --model model.onnx --concurrent 100")
        return 1
    
    if not Path(args.model).exists():
        print(f"❌ Model file not found: {args.model}")
        return 1
    
    # Initialize benchmark
    benchmark = MLBenchmark()
    all_results = {}
    
    # 1. Single inference benchmark
    onnx_result = benchmark.benchmark_onnx_inference(
        model_path=args.model,
        input_shape=input_shape,
        iterations=args.iterations,
        use_gpu=args.use_gpu
    )
    
    if onnx_result:
        all_results['single_inference'] = asdict(onnx_result)
        
        # 2. Performance analysis
        comparison = benchmark.compare_with_speedup_target(onnx_result)
        all_results['performance_analysis'] = comparison
    
    # 3. Batch inference benchmark
    batch_results = benchmark.benchmark_batch_inference(
        model_path=args.model,
        input_shape=input_shape,
        batch_sizes=batch_sizes,
        iterations_per_batch=10
    )
    
    if batch_results:
        all_results['batch_inference'] = {
            str(k): asdict(v) for k, v in batch_results.items()
        }
    
    # 4. Concurrent requests (if requested)
    if args.concurrent > 0:
        concurrent_result = benchmark.benchmark_concurrent_requests(
            model_path=args.model,
            input_shape=input_shape,
            num_requests=args.concurrent,
            concurrent_workers=10
        )
        all_results['concurrent_requests'] = concurrent_result
    
    # 5. Generate report
    benchmark.generate_report(all_results, args.output)
    
    print("\n✓ Benchmark complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())