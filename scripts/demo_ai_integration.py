#!/usr/bin/env python3
"""
SampleMind AI - AI Integration Demo
Demonstrates Google Gemini and OpenAI integration for beta testers
"""

import sys
import asyncio
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from samplemind.integrations import GoogleAIMusicProducer, OpenAIMusicProducer, SampleMindAIManager
from samplemind.core.engine.audio_engine import AudioEngine
from samplemind.utils import select_audio_file


async def demo_ai_integration():
    """Demo: AI-powered music analysis"""
    print("🤖 SampleMind AI - AI Integration Demo")
    print("=" * 60)

    # Check API keys
    has_google = bool(os.getenv('GOOGLE_AI_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))

    print("\n🔑 API Keys Status:")
    print(f"   Google Gemini: {'✅ Configured' if has_google else '❌ Not configured'}")
    print(f"   OpenAI: {'✅ Configured' if has_openai else '❌ Not configured'}")

    if not (has_google or has_openai):
        print("\n❌ No API keys found in .env file")
        print("   Please add GOOGLE_AI_API_KEY or OPENAI_API_KEY")
        return

    # Select audio file
    print("\n📁 Select an audio file to analyze with AI...")
    audio_file = select_audio_file("Choose Audio File")

    if not audio_file:
        print("❌ No file selected. Exiting.")
        return

    print(f"\n🎵 Analyzing: {audio_file.name}")
    print("-" * 60)

    # Extract audio features first
    print("\n1️⃣  Extracting audio features...")
    engine = AudioEngine()
    features = await engine.analyze_audio_async(audio_file)
    print(f"   ✅ Features extracted")
    print(f"      Tempo: {features.tempo:.1f} BPM")
    print(f"      Key: {features.key}")
    print(f"      Energy: {features.energy:.2f}")

    # Convert to dict for AI
    feature_dict = {
        'tempo': features.tempo,
        'key': features.key,
        'energy': features.energy,
        'mood': features.mood,
    }

    # Demo with available provider
    if has_google:
        print("\n2️⃣  Analyzing with Google Gemini AI...")
        producer = GoogleAIMusicProducer()

        try:
            result = await producer.analyze_music_comprehensive(
                audio_features=feature_dict,
                analysis_type='comprehensive'
            )

            print(f"   ✅ AI Analysis Complete!")
            print(f"\n   📝 Summary:")
            print(f"      Genre: {result.primary_genre}")
            print(f"      Mood: {result.primary_mood}")
            print(f"      Energy: {result.energy_level}")
            print(f"\n   🎨 Creative Suggestions:")
            if result.creative_applications:
                for i, idea in enumerate(result.creative_applications[:3], 1):
                    print(f"      {i}. {idea}")

            stats = producer.get_performance_stats()
            print(f"\n   📊 Stats:")
            print(f"      Analyses: {stats['total_analyses']}")
            print(f"      Tokens used: {stats['total_tokens_used']}")
            print(f"      Avg time: {stats['avg_response_time']:.2f}s")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    elif has_openai:
        print("\n2️⃣  Analyzing with OpenAI GPT...")
        producer = OpenAIMusicProducer()

        try:
            result = await producer.analyze_music(
                audio_features=feature_dict,
                analysis_type='comprehensive'
            )

            print(f"   ✅ AI Analysis Complete!")
            print(f"\n   📝 Analysis:")
            print(f"      {result.analysis[:200]}...")

            stats = producer.get_performance_stats()
            print(f"\n   📊 Stats:")
            print(f"      Analyses: {stats['total_analyses']}")
            print(f"      Cache hits: {stats['cache_hits']}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Demo AI Manager (auto-selection)
    print("\n3️⃣  Testing AI Manager (auto provider selection)...")
    manager = SampleMindAIManager()

    try:
        result = await manager.analyze_music(feature_dict)
        print(f"   ✅ Analysis complete via {result.provider_used}")
        print(f"      Response time: {result.response_time:.2f}s")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ AI Integration Demo complete!")

    # Cleanup
    await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(demo_ai_integration())
