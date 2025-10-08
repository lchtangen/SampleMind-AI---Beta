#!/usr/bin/env python3
"""
SampleMind AI v7 - Memory Profiling Script
Uses memray to analyze memory usage and detect leaks
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def profile_audio_engine():
    """Profile AudioEngine memory usage"""
    from src.samplemind.core.engine.audio_engine import AudioEngine
    import tempfile
    import numpy as np
    import soundfile as sf
    
    engine = AudioEngine()
    
    # Create a temporary audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        # Generate 10 seconds of test audio
        sample_rate = 44100
        duration = 10
        samples = np.random.randn(sample_rate * duration)
        sf.write(tmp.name, samples, sample_rate)
        
        # Profile audio analysis
        print(f"📊 Profiling audio analysis: {tmp.name}")
        for i in range(10):
            print(f"  Iteration {i+1}/10")
            features = engine.analyze_audio(tmp.name)
        
        # Cleanup
        os.unlink(tmp.name)
    
    print("✅ Audio engine profiling complete")


def profile_ai_analysis():
    """Profile AI analysis memory usage"""
    from src.samplemind.integrations.ai_manager import SampleMindAIManager
    import asyncio
    
    async def run_analysis():
        ai_manager = SampleMindAIManager()
        
        # Sample audio features
        sample_features = {
            "tempo": 120.0,
            "key": "C",
            "energy": 0.75,
            "duration": 180.0
        }
        
        print("📊 Profiling AI analysis")
        for i in range(5):
            print(f"  Iteration {i+1}/5")
            result = await ai_manager.analyze_music(
                sample_features,
                analysis_type="comprehensive"
            )
        
        print("✅ AI analysis profiling complete")
    
    asyncio.run(run_analysis())


def profile_caching():
    """Profile Redis caching operations"""
    import redis
    import json
    
    print("📊 Profiling Redis caching")
    
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Test data
        test_data = {
            "analysis": {
                "tempo": 120.0,
                "key": "C",
                "features": list(range(1000))
            }
        }
        
        # Profile cache operations
        for i in range(1000):
            key = f"test:cache:{i}"
            r.setex(key, 3600, json.dumps(test_data))
            r.get(key)
        
        # Cleanup
        r.flushdb()
        print("✅ Caching profiling complete")
        
    except Exception as e:
        print(f"⚠️ Redis profiling failed: {e}")


def main():
    """Run all profiling tests"""
    print("""
    🔍 SampleMind AI v7 - Memory Profiling
    ======================================
    
    This script profiles memory usage of core components.
    Run with memray for detailed analysis:
    
    memray run scripts/performance/profile_memory.py
    memray flamegraph output.bin
    
    """)
    
    # Profile individual components
    print("\n1️⃣ Profiling Audio Engine...")
    profile_audio_engine()
    
    print("\n2️⃣ Profiling AI Analysis...")
    profile_ai_analysis()
    
    print("\n3️⃣ Profiling Caching...")
    profile_caching()
    
    print("""
    
    ✅ Profiling Complete!
    
    View results:
    =============
    memray flamegraph output.bin -o flamegraph.html
    memray stats output.bin
    memray tree output.bin
    
    Look for:
    =========
    - Memory leaks (increasing allocations)
    - Large allocations
    - Allocation hotspots
    - Peak memory usage
    """)


if __name__ == "__main__":
    main()
