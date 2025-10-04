#!/usr/bin/env python3
"""
SampleMind AI - Batch Processing Demo
Demonstrates processing multiple audio files for beta testers
"""

import sys
import asyncio
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.utils import select_directory


async def demo_batch_processing():
    """Demo: Batch process audio files"""
    print("📦 SampleMind AI - Batch Processing Demo")
    print("=" * 60)

    # Initialize engine
    print("\n📊 Initializing Audio Engine...")
    engine = AudioEngine()
    print("✅ Engine ready!")

    # Select folder
    print("\n📁 Select a folder containing audio files...")
    folder = select_directory("Choose Audio Folder")

    if not folder:
        print("❌ No folder selected. Exiting.")
        return

    # Find audio files
    print(f"\n🔍 Scanning: {folder}")
    audio_extensions = {'.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg'}
    audio_files = [
        f for f in folder.rglob('*')
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]

    if not audio_files:
        print("❌ No audio files found in folder.")
        return

    print(f"✅ Found {len(audio_files)} audio files")

    # Process files
    print("\n" + "=" * 60)
    print(f"📊 Processing {len(audio_files)} files...")
    print("=" * 60)

    start_time = time.time()
    results = {}

    # Show which files will be processed
    print("\nFiles to process:")
    for i, file in enumerate(audio_files[:10], 1):  # Show first 10
        print(f"   {i}. {file.name}")
    if len(audio_files) > 10:
        print(f"   ... and {len(audio_files) - 10} more")

    # Batch process
    print(f"\n🚀 Starting batch analysis...")
    print("   (Using cache for faster processing)")

    batch_results = await engine.batch_analyze(
        audio_files,
        level=AnalysisLevel.STANDARD
    )

    # Show results
    print(f"\n✅ Batch processing complete!")
    print(f"   Files processed: {len(batch_results)}")
    print(f"   Time taken: {time.time() - start_time:.2f}s")

    # Summary statistics
    print("\n📊 Summary Statistics:")
    print("-" * 60)

    tempos = [r.tempo for r in batch_results.values() if r and hasattr(r, 'tempo')]
    energies = [r.energy for r in batch_results.values() if r and hasattr(r, 'energy')]

    if tempos:
        print(f"   Average Tempo: {sum(tempos)/len(tempos):.1f} BPM")
        print(f"   Tempo Range: {min(tempos):.1f} - {max(tempos):.1f} BPM")

    if energies:
        print(f"   Average Energy: {sum(energies)/len(energies):.2f}")
        print(f"   Energy Range: {min(energies):.2f} - {max(energies):.2f}")

    # Show individual results
    print("\n📋 Individual Results:")
    print("-" * 60)

    for i, (file_path, result) in enumerate(list(batch_results.items())[:5], 1):
        if result:
            print(f"\n{i}. {file_path.name}")
            print(f"   Tempo: {result.tempo:.1f} BPM")
            print(f"   Key: {result.key}")
            print(f"   Energy: {result.energy:.2f}")
            print(f"   Mood: {result.mood}")

    if len(batch_results) > 5:
        print(f"\n   ... and {len(batch_results) - 5} more results")

    # Performance stats
    print("\n" + "=" * 60)
    print("⚡ Performance Stats:")
    stats = engine.get_performance_stats()
    print(f"   Total analyses: {stats['total_analyses']}")
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Avg time per file: {stats['avg_analysis_time']:.3f}s")
    print(f"   Total time: {time.time() - start_time:.2f}s")

    print("\n" + "=" * 60)
    print("✅ Batch processing demo complete!")

    # Cleanup
    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_batch_processing())
