#!/usr/bin/env python3
"""Test Gemini API Integration for SampleMind AI"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.samplemind.integrations.google_ai_integration import GoogleAIMusicProducer, MusicAnalysisType

async def test_music_analysis():
    print('🎵 Testing Gemini for Music Production Analysis...\n')

    # Initialize Gemini Music Producer with API key from environment
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_AI_API_KEY not found in environment variables. Please set it in .env file")
    
    ai_producer = GoogleAIMusicProducer(api_key=api_key)

    # Mock audio features
    test_features = {
        'duration': 180.0,
        'tempo': 128.0,
        'key': 'C',
        'mode': 'major',
        'time_signature': (4, 4),
        'spectral_centroid': [2000, 2100, 1900],
        'spectral_bandwidth': [500, 550, 480],
        'spectral_rolloff': [4000, 4200, 3800],
        'rms_energy': [0.5, 0.6, 0.4],
        'rhythm_pattern': [1.0, 0.5, 0.8, 0.3],
        'onset_times': [0.5, 1.0, 1.5, 2.0]
    }

    print('📊 Analyzing audio features with Gemini 2.5 Pro...')

    # Perform comprehensive analysis
    analysis = await ai_producer.analyze_music_comprehensive(
        test_features,
        MusicAnalysisType.COMPREHENSIVE_ANALYSIS
    )

    print(f'\n✅ Analysis Complete!')
    print(f'🎯 Genre: {analysis.primary_genre}')
    print(f'😊 Mood: {analysis.primary_mood}')
    print(f'🎛️ FL Studio Plugins: {analysis.fl_plugin_recommendations[:3]}')
    print(f'💡 Creative Ideas: {analysis.arrangement_ideas[:2]}')
    print(f'⏱️  Processing Time: {analysis.processing_time:.2f}s')
    print(f'🤖 Model Used: {analysis.model_used.value}')

    # Show stats
    stats = ai_producer.get_performance_stats()
    print(f'\n📈 Performance Stats:')
    print(f'   Total Analyses: {stats["total_analyses"]}')
    print(f'   Avg Response Time: {stats["avg_response_time"]:.2f}s')
    print(f'   Cost Estimate: ${stats["cost_estimate_usd"]:.4f}')

    ai_producer.shutdown()
    print(f'\n🎉 GEMINI IS NOW YOUR PRIMARY AI FOR AUDIO ANALYSIS!')

if __name__ == "__main__":
    asyncio.run(test_music_analysis())
