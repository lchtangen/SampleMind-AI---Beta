#!/usr/bin/env python3
"""
SampleMind AI - Audio Analysis Demo
Demonstrates basic audio file analysis for beta testers
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from samplemind.core.engine.audio_engine import AudioEngine, AnalysisLevel
from samplemind.utils import select_audio_file


async def demo_audio_analysis():
    """Demo: Analyze an audio file"""
    print("🎵 SampleMind AI - Audio Analysis Demo")
    print("=" * 60)

    # Initialize engine
    print("\n📊 Initializing Audio Engine...")
    engine = AudioEngine()
    print("✅ Engine ready!")

    # Select audio file
    print("\n📁 Select an audio file to analyze...")
    audio_file = select_audio_file("Choose Audio File")

    if not audio_file:
        print("❌ No file selected. Exiting.")
        return

    print(f"\n🎵 Analyzing: {audio_file.name}")
    print("-" * 60)

    # Load audio
    print("\n1️⃣  Loading audio...")
    audio_data, sr = engine.load_audio(audio_file)
    print(f"   ✅ Loaded: {len(audio_data)} samples at {sr}Hz")
    print(f"   Duration: {len(audio_data)/sr:.2f} seconds")

    # Analyze - Basic
    print("\n2️⃣  Running BASIC analysis...")
    basic_result = await engine.analyze_audio_async(
        audio_file,
        level=AnalysisLevel.BASIC
    )
    print(f"   ✅ Tempo: {basic_result.tempo:.1f} BPM")
    print(f"   ✅ Key: {basic_result.key}")

    # Analyze - Detailed
    print("\n3️⃣  Running DETAILED analysis...")
    detailed_result = await engine.analyze_audio_async(
        audio_file,
        level=AnalysisLevel.DETAILED
    )
    print(f"   ✅ Tempo: {detailed_result.tempo:.1f} BPM")
    print(f"   ✅ Key: {detailed_result.key}")
    print(f"   ✅ Energy: {detailed_result.energy:.2f}")
    print(f"   ✅ Mood: {detailed_result.mood}")

    # Show performance stats
    print("\n4️⃣  Performance Stats:")
    stats = engine.get_performance_stats()
    print(f"   Total analyses: {stats['total_analyses']}")
    print(f"   Cache size: {stats['cache_size']}")
    print(f"   Avg time: {stats['avg_analysis_time']:.3f}s")

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    print("\nResults summary:")
    print(f"   File: {audio_file.name}")
    print(f"   Tempo: {detailed_result.tempo:.1f} BPM")
    print(f"   Key: {detailed_result.key}")
    print(f"   Energy: {detailed_result.energy:.2f}")
    print(f"   Mood: {detailed_result.mood}")

    # Cleanup
    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_audio_analysis())
