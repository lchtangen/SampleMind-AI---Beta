"""
Distributed Audio Processing Example

This script demonstrates how to use the DistributedAudioProcessor to process
multiple audio files in parallel using Dask.
"""
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

from samplemind.core.engine.distributed_processor import (
    DistributedAudioProcessor,
    process_audio_files_parallel
)


def process_directory(
    input_dir: str,
    output_file: str,
    n_workers: int = -1,
    feature_type: str = 'all',
    level: str = 'standard',
    batch_size: int = 10,
    use_cache: bool = True,
    recursive: bool = False
) -> None:
    """
    Process all audio files in a directory using distributed processing.
    
    Args:
        input_dir: Directory containing audio files
        output_file: Path to save results (JSON)
        n_workers: Number of worker processes (-1 for all available cores)
        feature_type: Type of features to extract
        level: Analysis level ('basic', 'standard', 'advanced')
        batch_size: Number of files to process in each batch
        use_cache: Whether to use the feature cache
        recursive: Whether to search for audio files recursively
    """
    # Find all audio files in the directory
    audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.aif', '.aiff', '.m4a'}
    input_path = Path(input_dir)
    
    if recursive:
        audio_files = [
            str(p) for p in input_path.rglob('*')
            if p.suffix.lower() in audio_extensions
        ]
    else:
        audio_files = [
            str(p) for p in input_path.glob('*')
            if p.suffix.lower() in audio_extensions
        ]
    
    if not audio_files:
        print(f"No audio files found in {input_dir}")
        return
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Process the files
    start_time = time.time()
    
    def progress_callback(current: int, total: int) -> None:
        """Print progress updates."""
        progress = (current / total) * 100
        elapsed = time.time() - start_time
        print(f"\rProgress: {current}/{total} ({progress:.1f}%) | "
              f"Elapsed: {elapsed:.1f}s | "
              f"Files/s: {current / (elapsed + 1e-6):.2f}", end='')
    
    try:
        # Process files using the context manager
        results = process_audio_files_parallel(
            file_paths=audio_files,
            n_workers=n_workers,
            feature_type=feature_type,
            level=level,
            use_cache=use_cache,
            memory_limit='4GB',
            batch_size=batch_size,
            progress_callback=progress_callback
        )
        
        # Save results to JSON
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert numpy arrays to lists for JSON serialization
        def convert_for_json(obj):
            if isinstance(obj, (dict, list, str, int, float, bool, type(None))):
                return obj
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            else:
                return str(obj)
        
        # Convert results to JSON-serializable format
        serializable_results = {
            k: {k2: convert_for_json(v2) for k2, v2 in v.items()}
            for k, v in results.items()
        }
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        total_time = time.time() - start_time
        print(f"\nProcessing complete! Results saved to {output_path}")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"Average time per file: {total_time / len(audio_files):.2f} seconds")
        
    except Exception as e:
        print(f"\nError during processing: {e}")
        raise


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Process audio files in parallel')
    parser.add_argument('input_dir', help='Directory containing audio files')
    parser.add_argument('output_file', help='Output JSON file for results')
    parser.add_argument('--workers', type=int, default=-1,
                       help='Number of worker processes (-1 for all cores)')
    parser.add_argument('--feature-type', default='all',
                       choices=['all', 'rhythm', 'spectral', 'mfcc'],
                       help='Type of features to extract')
    parser.add_argument('--level', default='standard',
                       choices=['basic', 'standard', 'advanced'],
                       help='Analysis level')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of files to process in each batch')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable feature caching')
    parser.add_argument('--recursive', action='store_true',
                       help='Search for audio files recursively')
    
    args = parser.parse_args()
    
    process_directory(
        input_dir=args.input_dir,
        output_file=args.output_file,
        n_workers=args.workers,
        feature_type=args.feature_type,
        level=args.level,
        batch_size=args.batch_size,
        use_cache=not args.no_cache,
        recursive=args.recursive
    )


if __name__ == '__main__':
    main()
