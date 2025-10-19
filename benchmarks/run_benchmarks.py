#!/usr/bin/env python3
"""
Run audio processing benchmarks and generate reports.

This script runs the audio effects and noise reduction benchmarks,
processes the results, and generates a comprehensive report.
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Add parent directory to path to import samplemind
sys.path.append(str(Path(__file__).parent.parent))

# Import benchmark modules
from audio_effects_benchmark import (
    benchmark_effects,
    benchmark_noise_reduction,
    analyze_effects_results,
    analyze_nr_results
)

class BenchmarkRunner:
    """Run and manage audio processing benchmarks."""
    
    def __init__(self, output_dir: str = "benchmark_results"):
        """Initialize the benchmark runner."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = self.output_dir / f"benchmark_{self.timestamp}"
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize results storage
        self.results = {
            'metadata': {
                'timestamp': self.timestamp,
                'system': self._get_system_info(),
                'python_version': sys.version,
                'numpy_version': np.__version__,
                'pandas_version': pd.__version__
            },
            'benchmarks': {}
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        import platform
        import psutil
        import cpuinfo
        
        cpu_info = cpuinfo.get_cpu_info()
        
        return {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu': {
                'brand': cpu_info.get('brand_raw', 'Unknown'),
                'hz_actual': cpu_info.get('hz_actual', [0])[0],
                'hz_advertised': cpu_info.get('hz_advertised', [0])[0],
                'cores_physical': psutil.cpu_count(logical=False),
                'cores_logical': psutil.cpu_count(logical=True)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available
            }
        }
    
    def run_effects_benchmark(self) -> Dict[str, Any]:
        """Run the audio effects benchmark."""
        print("\n" + "="*80)
        print("RUNNING AUDIO EFFECTS BENCHMARK")
        print("="*80)
        
        # Run benchmark
        start_time = time.time()
        df = benchmark_effects()
        elapsed = time.time() - start_time
        
        # Save raw results
        results_file = self.results_dir / 'audio_effects_results.csv'
        df.to_csv(results_file, index=False)
        
        # Generate analysis
        analysis = self._analyze_effects(df)
        
        # Save analysis
        with open(self.results_dir / 'audio_effects_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Store results
        self.results['benchmarks']['audio_effects'] = {
            'status': 'completed',
            'execution_time': elapsed,
            'results_file': str(results_file),
            'analysis': analysis,
            'summary': self._generate_effects_summary(analysis)
        }
        
        return self.results['benchmarks']['audio_effects']
    
    def run_noise_reduction_benchmark(self) -> Dict[str, Any]:
        """Run the noise reduction benchmark."""
        print("\n" + "="*80)
        print("RUNNING NOISE REDUCTION BENCHMARK")
        print("="*80)
        
        # Run benchmark
        start_time = time.time()
        df = benchmark_noise_reduction()
        elapsed = time.time() - start_time
        
        # Save raw results
        results_file = self.results_dir / 'noise_reduction_results.csv'
        df.to_csv(results_file, index=False)
        
        # Generate analysis
        analysis = self._analyze_noise_reduction(df)
        
        # Save analysis
        with open(self.results_dir / 'noise_reduction_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Store results
        self.results['benchmarks']['noise_reduction'] = {
            'status': 'completed',
            'execution_time': elapsed,
            'results_file': str(results_file),
            'analysis': analysis,
            'summary': self._generate_nr_summary(analysis)
        }
        
        return self.results['benchmarks']['noise_reduction']
    
    def _analyze_effects(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze audio effects benchmark results."""
        # Basic statistics
        stats = {
            'total_tests': len(df),
            'success_rate': float(df['success'].mean()),
            'by_effect': {},
            'by_sample_rate': {},
            'by_audio_type': {}
        }
        
        # By effect
        for effect in df['effect'].unique():
            effect_df = df[df['effect'] == effect]
            stats['by_effect'][effect] = {
                'count': len(effect_df),
                'success_rate': float(effect_df['success'].mean()),
                'avg_processing_time': float(effect_df['processing_time'].mean()),
                'avg_throughput': float((effect_df['num_samples'] / effect_df['processing_time']).mean()),
                'by_sample_rate': {}
            }
            
            # By sample rate for this effect
            for sr in effect_df['sample_rate'].unique():
                sr_df = effect_df[effect_df['sample_rate'] == sr]
                stats['by_effect'][effect]['by_sample_rate'][sr] = {
                    'avg_processing_time': float(sr_df['processing_time'].mean()),
                    'avg_throughput': float((sr_df['num_samples'] / sr_df['processing_time']).mean())
                }
        
        # By sample rate
        for sr in df['sample_rate'].unique():
            sr_df = df[df['sample_rate'] == sr]
            stats['by_sample_rate'][sr] = {
                'count': len(sr_df),
                'avg_processing_time': float(sr_df['processing_time'].mean()),
                'avg_throughput': float((sr_df['num_samples'] / sr_df['processing_time']).mean())
            }
        
        # By audio type
        for audio_type in df['audio_type'].unique():
            type_df = df[df['audio_type'] == audio_type]
            stats['by_audio_type'][audio_type] = {
                'count': len(type_df),
                'avg_processing_time': float(type_df['processing_time'].mean()),
                'success_rate': float(type_df['success'].mean())
            }
        
        return stats
    
    def _analyze_noise_reduction(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze noise reduction benchmark results."""
        # Basic statistics
        stats = {
            'total_tests': len(df),
            'success_rate': float(df['success'].mean()),
            'by_method': {},
            'by_sample_rate': {},
            'by_audio_type': {}
        }
        
        # By method
        for method in df['method'].unique():
            method_df = df[df['method'] == method]
            stats['by_method'][method] = {
                'count': len(method_df),
                'success_rate': float(method_df['success'].mean()),
                'avg_processing_time': float(method_df['processing_time'].mean()),
                'avg_snr_improvement': float(method_df['snr_improvement'].mean()),
                'avg_throughput': float((method_df['num_samples'] / method_df['processing_time']).mean())
            }
        
        # By sample rate
        for sr in df['sample_rate'].unique():
            sr_df = df[df['sample_rate'] == sr]
            stats['by_sample_rate'][sr] = {
                'count': len(sr_df),
                'avg_processing_time': float(sr_df['processing_time'].mean()),
                'avg_snr_improvement': float(sr_df['snr_improvement'].mean())
            }
        
        # By audio type
        for audio_type in df['audio_type'].unique():
            type_df = df[df['audio_type'] == audio_type]
            stats['by_audio_type'][audio_type] = {
                'count': len(type_df),
                'avg_processing_time': float(type_df['processing_time'].mean()),
                'avg_snr_improvement': float(type_df['snr_improvement'].mean())
            }
        
        return stats
    
    def _generate_effects_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary of effects benchmark results."""
        summary = [
            "=" * 80,
            "AUDIO EFFECTS BENCHMARK SUMMARY",
            "=" * 80,
            f"Total tests: {analysis['total_tests']}",
            f"Success rate: {analysis['success_rate']*100:.1f}%",
            "\nBY EFFECT:",
            "-" * 80
        ]
        
        # Sort effects by processing time (descending)
        effects_sorted = sorted(
            analysis['by_effect'].items(),
            key=lambda x: x[1]['avg_processing_time'],
            reverse=True
        )
        
        for effect, data in effects_sorted:
            summary.append(
                f"{effect.upper():<20} | "
                f"Time: {data['avg_processing_time']*1000:.2f}ms | "
                f"Throughput: {data['avg_throughput']/1e6:.2f}M samples/s | "
                f"Success: {data['success_rate']*100:.1f}%"
            )
        
        summary.extend([
            "\nBY SAMPLE RATE:",
            "-" * 80
        ])
        
        # Sort sample rates
        for sr in sorted(analysis['by_sample_rate'].keys()):
            data = analysis['by_sample_rate'][sr]
            summary.append(
                f"{sr} Hz: {data['avg_throughput']/1e6:.2f}M samples/s "
                f"({data['avg_processing_time']*1000:.2f} ms/op)"
            )
        
        return "\n".join(summary)
    
    def _generate_nr_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary of noise reduction benchmark results."""
        summary = [
            "=" * 80,
            "NOISE REDUCTION BENCHMARK SUMMARY",
            "=" * 80,
            f"Total tests: {analysis['total_tests']}",
            f"Success rate: {analysis['success_rate']*100:.1f}%",
            "\nBY METHOD:",
            "-" * 80
        ]
        
        # Sort methods by SNR improvement (descending)
        methods_sorted = sorted(
            analysis['by_method'].items(),
            key=lambda x: x[1]['avg_snr_improvement'],
            reverse=True
        )
        
        for method, data in methods_sorted:
            summary.append(
                f"{method.upper():<15} | "
                f"SNR: +{data['avg_snr_improvement']:.2f} dB | "
                f"Time: {data['avg_processing_time']*1000:.2f}ms | "
                f"Throughput: {data['avg_throughput']/1e6:.2f}M samples/s"
            )
        
        summary.extend([
            "\nBY AUDIO TYPE:",
            "-" * 80
        ])
        
        # Sort audio types by SNR improvement
        audio_types_sorted = sorted(
            analysis['by_audio_type'].items(),
            key=lambda x: x[1]['avg_snr_improvement'],
            reverse=True
        )
        
        for audio_type, data in audio_types_sorted:
            summary.append(
                f"{audio_type.upper():<15} | "
                f"SNR: +{data['avg_snr_improvement']:.2f} dB | "
                f"Time: {data['avg_processing_time']*1000:.2f}ms"
            )
        
        return "\n".join(summary)
    
    def generate_report(self) -> str:
        """Generate a comprehensive HTML report."""
        report_file = self.results_dir / 'benchmark_report.html'
        
        # Generate plots
        self._generate_plots()
        
        # HTML template
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <title>SampleMind AI - Audio Processing Benchmark Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .section {{ margin-bottom: 30px; }}
                .card {{ background: #fff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
                .plot {{ margin: 20px 0; text-align: center; }}
                .plot img {{ max-width: 100%; height: auto; border: 1px solid #eee; }}
                .summary {{ font-family: monospace; white-space: pre; background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                .metadata {{ font-size: 0.9em; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>SampleMind AI - Audio Processing Benchmark Report</h1>
                    <div class="metadata">
                        <p>Generated on: {self.timestamp.replace('_', ' at ')}</p>
                        <p>System: {self.results['metadata']['system']['system']} {self.results['metadata']['system']['release']} ({self.results['metadata']['system']['machine']})</p>
                        <p>CPU: {self.results['metadata']['system']['cpu']['brand']} ({self.results['metadata']['system']['cpu']['cores_physical']} cores)</p>
                    </div>
                </header>
                
                <div class="section">
                    <h2>Benchmark Summary</h2>
                    <div class="card">
                        <h3>Audio Effects</h3>
                        <div class="summary">
        """
        
        # Add effects summary
        if 'audio_effects' in self.results['benchmarks']:
            html += f"<h4>Audio Effects Summary</h4>"
            html += f"<p>Status: <span class='success'>{self.results['benchmarks']['audio_effects']['status'].upper()}</span></p>"
            html += f"<p>Execution time: {self.results['benchmarks']['audio_effects']['execution_time']:.2f} seconds</p>"
            
            # Add effects plot
            effects_plot = self.results_dir / 'audio_effects_plot.png'
            if effects_plot.exists():
                html += f"<div class='plot'><img src='{effects_plot.name}' alt='Audio Effects Performance'></div>"
            
            # Add summary text
            summary = self.results['benchmarks']['audio_effects']['summary'].replace('\n', '<br>').replace(' ', '&nbsp;')
            html += f"<div class='summary'>{summary}</div>"
        
        # Add noise reduction summary
        if 'noise_reduction' in self.results['benchmarks']:
            html += f"<h4>Noise Reduction Summary</h4>"
            html += f"<p>Status: <span class='success'>{self.results['benchmarks']['noise_reduction']['status'].upper()}</span></p>"
            html += f"<p>Execution time: {self.results['benchmarks']['noise_reduction']['execution_time']:.2f} seconds</p>"
            
            # Add noise reduction plot
            nr_plot = self.results_dir / 'noise_reduction_plot.png'
            if nr_plot.exists():
                html += f"<div class='plot'><img src='{nr_plot.name}' alt='Noise Reduction Performance'></div>"
            
            # Add summary text
            summary = self.results['benchmarks']['noise_reduction']['summary'].replace('\n', '<br>').replace(' ', '&nbsp;')
            html += f"<div class='summary'>{summary}</div>"
        
        # Close HTML
        html += """
                        </div>
                    </div>
                </div>
                
                <footer class="metadata">
                    <p>Generated by SampleMind AI Benchmarking Tool</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        # Save report
        with open(report_file, 'w') as f:
            f.write(html)
        
        return str(report_file)
    
    def _generate_plots(self):
        """Generate plots for the report."""
        try:
            # Plot for audio effects
            if 'audio_effects' in self.results['benchmarks']:
                analysis = self.results['benchmarks']['audio_effects']['analysis']
                
                # Prepare data
                effects = list(analysis['by_effect'].keys())
                times = [analysis['by_effect'][e]['avg_processing_time'] for e in effects]
                throughputs = [analysis['by_effect'][e]['avg_throughput'] / 1e6 for e in effects]  # Convert to Msamples/s
                
                # Sort by processing time
                sorted_idx = np.argsort(times)[::-1]
                effects = [effects[i] for i in sorted_idx]
                times = [times[i] for i in sorted_idx]
                throughputs = [throughputs[i] for i in sorted_idx]
                
                # Create figure
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
                
                # Plot processing time
                bars = ax1.bar(effects, times, color='skyblue')
                ax1.set_title('Average Processing Time by Effect')
                ax1.set_ylabel('Time (seconds)')
                ax1.tick_params(axis='x', rotation=45, ha='right')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height*1000:.1f}ms',
                            ha='center', va='bottom')
                
                # Plot throughput
                bars = ax2.bar(effects, throughputs, color='lightgreen')
                ax2.set_title('Average Throughput by Effect')
                ax2.set_ylabel('Throughput (Msamples/s)')
                ax2.tick_params(axis='x', rotation=45, ha='right')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}M',
                            ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(self.results_dir / 'audio_effects_plot.png', dpi=150, bbox_inches='tight')
                plt.close()
            
            # Plot for noise reduction
            if 'noise_reduction' in self.results['benchmarks']:
                analysis = self.results['benchmarks']['noise_reduction']['analysis']
                
                # Prepare data
                methods = list(analysis['by_method'].keys())
                snr_improvements = [analysis['by_method'][m]['avg_snr_improvement'] for m in methods]
                times = [analysis['by_method'][m]['avg_processing_time'] for m in methods]
                
                # Sort by SNR improvement
                sorted_idx = np.argsort(snr_improvements)[::-1]
                methods = [methods[i] for i in sorted_idx]
                snr_improvements = [snr_improvements[i] for i in sorted_idx]
                times = [times[i] for i in sorted_idx]
                
                # Create figure
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
                
                # Plot SNR improvement
                bars = ax1.bar(methods, snr_improvements, color='lightcoral')
                ax1.set_title('Average SNR Improvement by Method')
                ax1.set_ylabel('SNR Improvement (dB)')
                ax1.tick_params(axis='x', rotation=45, ha='right')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'+{height:.1f} dB',
                            ha='center', va='bottom')
                
                # Plot processing time
                bars = ax2.bar(methods, [t*1000 for t in times], color='lightblue')
                ax2.set_title('Average Processing Time by Method')
                ax2.set_ylabel('Time (milliseconds)')
                ax2.tick_params(axis='x', rotation=45, ha='right')
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}ms',
                            ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(self.results_dir / 'noise_reduction_plot.png', dpi=150, bbox_inches='tight')
                plt.close()
                
        except Exception as e:
            print(f"Error generating plots: {str(e)}")
    
    def save_results(self):
        """Save benchmark results to a JSON file."""
        results_file = self.results_dir / 'benchmark_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        return str(results_file)

def main():
    """Main function to run benchmarks."""
    print("=" * 80)
    print("SAMPLEMIND AI - AUDIO PROCESSING BENCHMARK")
    print("=" * 80)
    print("This will run comprehensive benchmarks for audio effects and noise reduction.")
    print("It may take several minutes to complete.\n")
    
    # Create benchmark runner
    runner = BenchmarkRunner()
    
    try:
        # Run benchmarks
        runner.run_effects_benchmark()
        runner.run_noise_reduction_benchmark()
        
        # Save results
        results_file = runner.save_results()
        print(f"\nBenchmark results saved to: {results_file}")
        
        # Generate report
        report_file = runner.generate_report()
        print(f"Benchmark report generated: {report_file}")
        
        print("\nBenchmarking completed successfully!")
        
    except KeyboardInterrupt:
        print("\nBenchmarking interrupted by user.")
    except Exception as e:
        print(f"\nError during benchmarking: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\nDone!")

if __name__ == "__main__":
    main()
