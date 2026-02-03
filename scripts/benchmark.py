#!/usr/bin/env python3
"""
Performance Benchmark for SampleMind AI
Measures analysis speed, memory usage, and throughput
"""

import time
import psutil
import statistics
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from samplemind.core.engine.audio_engine import AudioEngine


@dataclass
class BenchmarkResult:
    """Results from a benchmark run"""
    operation: str
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float  # files per second
    memory_mb: float


class PerformanceBenchmark:
    """Benchmark audio processing performance"""
    
    def __init__(self):
        self.engine = AudioEngine(max_workers=4)
        self.results: List[BenchmarkResult] = []
    
    def benchmark_analysis(self, test_files: List[Path], iterations: int = 3) -> BenchmarkResult:
        """Benchmark audio analysis speed"""
        print(f"\n🎯 Benchmarking audio analysis ({len(test_files)} files, {iterations} iterations)...")
        
        times = []
        process = psutil.Process()
        
        for i in range(iterations):
            start_mem = process.memory_info().rss / 1024 / 1024
            start_time = time.time()
            
            for file_path in test_files:
                self.engine.analyze_audio(file_path)
            
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            end_mem = process.memory_info().rss / 1024 / 1024
            print(f"  Iteration {i+1}: {elapsed:.2f}s ({end_mem - start_mem:.1f}MB)")
        
        result = BenchmarkResult(
            operation="audio_analysis",
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            throughput=len(test_files) / statistics.mean(times),
            memory_mb=end_mem - start_mem
        )
        
        self.results.append(result)
        return result
    
    def benchmark_parallel(self, test_files: List[Path], workers: List[int] = [1, 2, 4, 8]) -> Dict[int, BenchmarkResult]:
        """Benchmark parallel processing with different worker counts"""
        print(f"\n⚡ Benchmarking parallel processing...")
        
        results = {}
        
        for num_workers in workers:
            print(f"\n  Testing with {num_workers} workers...")
            engine = AudioEngine(max_workers=num_workers)
            
            start_time = time.time()
            for file_path in test_files:
                engine.analyze_audio(file_path)
            elapsed = time.time() - start_time
            
            result = BenchmarkResult(
                operation=f"parallel_{num_workers}w",
                total_time=elapsed,
                avg_time=elapsed / len(test_files),
                min_time=elapsed,
                max_time=elapsed,
                std_dev=0,
                throughput=len(test_files) / elapsed,
                memory_mb=0
            )
            
            results[num_workers] = result
            print(f"    {elapsed:.2f}s ({result.throughput:.2f} files/sec)")
        
        return results
    
    def benchmark_cache(self, test_file: Path, iterations: int = 10) -> Dict[str, BenchmarkResult]:
        """Benchmark cache performance"""
        print(f"\n💾 Benchmarking cache performance...")
        
        # Cold cache
        self.engine.clear_cache()
        cold_times = []
        for _ in range(3):
            start = time.time()
            self.engine.analyze_audio(test_file, use_cache=False)
            cold_times.append(time.time() - start)
        
        cold_result = BenchmarkResult(
            operation="cache_cold",
            total_time=sum(cold_times),
            avg_time=statistics.mean(cold_times),
            min_time=min(cold_times),
            max_time=max(cold_times),
            std_dev=statistics.stdev(cold_times),
            throughput=1 / statistics.mean(cold_times),
            memory_mb=0
        )
        
        # Warm cache
        self.engine.analyze_audio(test_file, use_cache=True)  # Prime cache
        warm_times = []
        for _ in range(iterations):
            start = time.time()
            self.engine.analyze_audio(test_file, use_cache=True)
            warm_times.append(time.time() - start)
        
        warm_result = BenchmarkResult(
            operation="cache_warm",
            total_time=sum(warm_times),
            avg_time=statistics.mean(warm_times),
            min_time=min(warm_times),
            max_time=max(warm_times),
            std_dev=statistics.stdev(warm_times),
            throughput=1 / statistics.mean(warm_times),
            memory_mb=0
        )
        
        speedup = cold_result.avg_time / warm_result.avg_time
        print(f"  Cold cache: {cold_result.avg_time:.3f}s")
        print(f"  Warm cache: {warm_result.avg_time:.3f}s")
        print(f"  Speedup: {speedup:.1f}x")
        
        return {"cold": cold_result, "warm": warm_result}
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*60)
        print("📊 BENCHMARK SUMMARY")
        print("="*60)
        
        for result in self.results:
            print(f"\n{result.operation.upper()}")
            print(f"  Average Time: {result.avg_time:.3f}s")
            print(f"  Throughput: {result.throughput:.2f} files/sec")
            print(f"  Std Dev: {result.std_dev:.3f}s")
            print(f"  Memory: {result.memory_mb:.1f}MB")


def main():
    """Run performance benchmarks"""
    print("🚀 SampleMind AI Performance Benchmark")
    print("="*60)
    
    # Find test files
    test_dir = Path("tests/fixtures")
    if not test_dir.exists():
        print("❌ Test fixtures directory not found")
        return
    
    test_files = list(test_dir.glob("*.wav"))[:5]  # Use first 5 files
    
    if not test_files:
        print("❌ No test files found")
        return
    
    print(f"📁 Found {len(test_files)} test files")
    
    # Run benchmarks
    benchmark = PerformanceBenchmark()
    
    # 1. Basic analysis
    benchmark.benchmark_analysis(test_files, iterations=3)
    
    # 2. Parallel processing
    benchmark.benchmark_parallel(test_files, workers=[1, 2, 4])
    
    # 3. Cache performance
    if test_files:
        benchmark.benchmark_cache(test_files[0], iterations=10)
    
    # Print summary
    benchmark.print_summary()
    
    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
