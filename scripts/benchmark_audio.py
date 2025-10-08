#!/usr/bin/env python3
"""
Audio Processing Benchmark Script

Compares performance of Essentia vs librosa audio analysis.
Tests various audio formats and file sizes to verify 2-3x speedup target.

Usage:
    python scripts/benchmark_audio.py
    python scripts/benchmark_audio.py --test-files tests/fixtures/*.wav
    python scripts/benchmark_audio.py --iterations 10 --output benchmark_results.json
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from samplemind.audio.hybrid_analyzer import HybridAnalyzer, AnalysisBackend
    from samplemind.audio.essentia_analyzer import ESSENTIA_AVAILABLE
    from loguru import logger
    AUDIO_MODULE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import audio modules: {e}")
    AUDIO_MODULE_AVAILABLE = False


class AudioBenchmark:
    """
    Benchmark audio analysis performance.
    
    Tests:
    - Essentia vs librosa speed comparison
    - Various file sizes and formats
    - Feature extraction accuracy
    - Memory usage
    """
    
    def __init__(self, iterations: int = 3):
        """
        Initialize benchmark.
        
        Args:
            iterations: Number of iterations per test
        """
        self.iterations = iterations
        self.results = []
        
        # Initialize analyzers
        try:
            self.hybrid_analyzer = HybridAnalyzer()
            logger.info("Hybrid analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize analyzer: {e}")
            raise
    
    def benchmark_file(
        self,
        file_path: Path,
        backend: AnalysisBackend
    ) -> Dict[str, Any]:
        """
        Benchmark a single file with specified backend.
        
        Args:
            file_path: Path to audio file
            backend: Backend to use for analysis
            
        Returns:
            Dictionary with benchmark results
        """
        times = []
        features = None
        error = None
        
        for i in range(self.iterations):
            try:
                start_time = time.time()
                result = self.hybrid_analyzer.analyze(file_path, backend=backend)
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if i == 0:  # Store features from first run
                    features = {
                        'bpm': result.tempo,
                        'key': result.key,
                        'mode': result.mode,
                        'duration': result.duration,
                    }
                
                logger.debug(
                    f"Iteration {i+1}/{self.iterations}: "
                    f"{backend.value} took {elapsed:.2f}s"
                )
                
            except Exception as e:
                error = str(e)
                logger.error(f"Benchmark failed: {e}")
                break
        
        if not times:
            return {
                'backend': backend.value,
                'success': False,
                'error': error,
            }
        
        return {
            'backend': backend.value,
            'success': True,
            'iterations': len(times),
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'total_time': sum(times),
            'features': features,
        }
    
    def benchmark_comparison(self, file_path: Path) -> Dict[str, Any]:
        """
        Compare Essentia vs librosa on the same file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with comparison results
        """
        logger.info(f"Benchmarking: {file_path.name}")
        
        result = {
            'file': str(file_path),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
        }
        
        # Test Essentia
        if ESSENTIA_AVAILABLE:
            essentia_result = self.benchmark_file(file_path, AnalysisBackend.ESSENTIA)
            result['essentia'] = essentia_result
        else:
            result['essentia'] = {
                'backend': 'essentia',
                'success': False,
                'error': 'Essentia not available',
            }
        
        # Test librosa
        librosa_result = self.benchmark_file(file_path, AnalysisBackend.LIBROSA)
        result['librosa'] = librosa_result
        
        # Calculate speedup
        if (result['essentia']['success'] and result['librosa']['success']):
            essentia_time = result['essentia']['avg_time']
            librosa_time = result['librosa']['avg_time']
            
            speedup = librosa_time / essentia_time
            result['speedup'] = speedup
            result['faster_backend'] = 'essentia' if speedup > 1 else 'librosa'
            
            # Check if target met (2-3x faster)
            result['target_met'] = speedup >= 2.0
            
            # Feature comparison
            if result['essentia'].get('features') and result['librosa'].get('features'):
                e_feat = result['essentia']['features']
                l_feat = result['librosa']['features']
                
                result['feature_comparison'] = {
                    'bpm_diff': abs(e_feat['bpm'] - l_feat['bpm']),
                    'bpm_match': abs(e_feat['bpm'] - l_feat['bpm']) < 5,
                    'key_match': e_feat['key'] == l_feat['key'],
                }
            
            logger.info(
                f"✓ {file_path.name}: "
                f"Essentia {essentia_time:.2f}s, "
                f"librosa {librosa_time:.2f}s, "
                f"speedup: {speedup:.2f}x {'✓' if speedup >= 2 else '✗'}"
            )
        else:
            result['speedup'] = None
            result['target_met'] = False
            logger.warning(f"✗ {file_path.name}: One or both backends failed")
        
        self.results.append(result)
        return result
    
    def benchmark_batch(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Benchmark multiple files.
        
        Args:
            file_paths: List of audio file paths
            
        Returns:
            List of benchmark results
        """
        logger.info(f"Starting batch benchmark of {len(file_paths)} files")
        
        results = []
        for file_path in file_paths:
            if file_path.exists():
                result = self.benchmark_comparison(file_path)
                results.append(result)
            else:
                logger.warning(f"File not found: {file_path}")
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive benchmark report.
        
        Returns:
            Dictionary with aggregate statistics
        """
        if not self.results:
            return {'error': 'No benchmark results available'}
        
        # Aggregate statistics
        total_files = len(self.results)
        successful_comparisons = sum(
            1 for r in self.results 
            if r.get('speedup') is not None
        )
        
        speedups = [
            r['speedup'] for r in self.results 
            if r.get('speedup') is not None
        ]
        
        targets_met = sum(
            1 for r in self.results 
            if r.get('target_met', False)
        )
        
        report = {
            'summary': {
                'total_files': total_files,
                'successful_comparisons': successful_comparisons,
                'targets_met': targets_met,
                'target_met_percentage': (targets_met / successful_comparisons * 100) 
                    if successful_comparisons > 0 else 0,
            },
            'performance': {
                'avg_speedup': sum(speedups) / len(speedups) if speedups else 0,
                'min_speedup': min(speedups) if speedups else 0,
                'max_speedup': max(speedups) if speedups else 0,
                'median_speedup': sorted(speedups)[len(speedups)//2] if speedups else 0,
            },
            'details': self.results,
        }
        
        # Performance tier classification
        if report['performance']['avg_speedup'] >= 3.0:
            report['performance_tier'] = 'Excellent (3x+ faster)'
        elif report['performance']['avg_speedup'] >= 2.0:
            report['performance_tier'] = 'Good (2-3x faster)'
        elif report['performance']['avg_speedup'] >= 1.5:
            report['performance_tier'] = 'Moderate (1.5-2x faster)'
        else:
            report['performance_tier'] = 'Needs improvement (<1.5x faster)'
        
        return report
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted report to console"""
        print("\n" + "=" * 70)
        print("AUDIO PROCESSING BENCHMARK REPORT")
        print("=" * 70)
        
        summary = report['summary']
        perf = report['performance']
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total files tested: {summary['total_files']}")
        print(f"  Successful comparisons: {summary['successful_comparisons']}")
        print(f"  Performance targets met: {summary['targets_met']} "
              f"({summary['target_met_percentage']:.1f}%)")
        
        print(f"\n⚡ PERFORMANCE:")
        print(f"  Average speedup: {perf['avg_speedup']:.2f}x")
        print(f"  Min speedup: {perf['min_speedup']:.2f}x")
        print(f"  Max speedup: {perf['max_speedup']:.2f}x")
        print(f"  Median speedup: {perf['median_speedup']:.2f}x")
        print(f"  Performance tier: {report['performance_tier']}")
        
        print(f"\n📁 FILE DETAILS:")
        for result in report['details']:
            status = "✓" if result.get('target_met') else "✗"
            speedup = result.get('speedup', 0)
            print(f"  {status} {result['file_name']}: {speedup:.2f}x speedup")
        
        print("\n" + "=" * 70)
        
        # Overall verdict
        if perf['avg_speedup'] >= 2.0:
            print("🎉 SUCCESS: Performance targets MET (2-3x faster)!")
        else:
            print("⚠️  WARNING: Performance targets NOT met.")
        
        print("=" * 70 + "\n")


def main():
    """Main benchmark execution"""
    parser = argparse.ArgumentParser(
        description='Benchmark audio processing performance'
    )
    parser.add_argument(
        '--test-files',
        nargs='+',
        help='Audio files to test (default: tests/fixtures/*.wav)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=3,
        help='Number of iterations per test (default: 3)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file for results'
    )
    
    args = parser.parse_args()
    
    # Get test files
    if args.test_files:
        test_files = [Path(f) for f in args.test_files]
    else:
        # Default test files
        test_dir = Path(__file__).parent.parent / 'tests' / 'fixtures'
        if test_dir.exists():
            test_files = list(test_dir.glob('*.wav'))
            test_files.extend(test_dir.glob('*.mp3'))
        else:
            logger.error(f"Test directory not found: {test_dir}")
            logger.info("Please specify test files with --test-files")
            return 1
    
    if not test_files:
        logger.error("No test files found")
        return 1
    
    logger.info(f"Found {len(test_files)} test files")
    
    # Run benchmark
    try:
        benchmark = AudioBenchmark(iterations=args.iterations)
        benchmark.benchmark_batch(test_files)
        report = benchmark.generate_report()
        
        # Print report
        benchmark.print_report(report)
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Results saved to: {output_path}")
        
        # Return exit code based on performance
        if report['performance']['avg_speedup'] >= 2.0:
            return 0  # Success
        else:
            return 1  # Performance target not met
            
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())