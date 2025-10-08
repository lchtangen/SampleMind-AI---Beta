#!/usr/bin/env python3
"""Simple Gemini API Test for Music Analysis"""
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure API - get key from environment
api_key = os.getenv('GOOGLE_AI_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_AI_API_KEY not found in environment variables. Please set it in .env file")

genai.configure(api_key=api_key)

print('🎵 Testing Gemini API for Music Production Analysis\n')
print('=' * 60)

# Test 1: Simple connectivity
print('\n📡 Test 1: API Connectivity')
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content('Say: Gemini API connected successfully!')
print(f'✅ {response.text}')

# Test 2: Music Analysis Capability
print('\n🎵 Test 2: Music Analysis Capability')
music_prompt = """
Analyze this audio sample and provide production advice:

Audio Features:
- Tempo: 128 BPM
- Key: C Major
- Duration: 3 minutes
- Genre: Electronic Dance Music
- Energy: High

Provide 3 FL Studio production tips in JSON format:
{
  "genre": "genre classification",
  "mood": "emotional mood",
  "fl_studio_tips": ["tip1", "tip2", "tip3"]
}
"""

generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    response_mime_type="application/json"
)

model_json = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    generation_config=generation_config
)

response = model_json.generate_content(music_prompt)
result = json.loads(response.text)

print(f'🎯 Genre: {result.get("genre", "N/A")}')
print(f'😊 Mood: {result.get("mood", "N/A")}')
print(f'🎛️ FL Studio Tips:')
for i, tip in enumerate(result.get("fl_studio_tips", []), 1):
    print(f'   {i}. {tip}')

# Test 3: Advanced Audio Classification
print('\n🔍 Test 3: Audio Classification')
classification_prompt = """
You are an AI audio classifier for a professional music production tool.
Classify this audio sample:

Features:
- Spectral Centroid: 2000 Hz
- RMS Energy: 0.6
- Tempo: 128 BPM
- Key: C Major

Classify the:
1. Primary genre
2. Subgenre
3. Production quality (1-10)
4. Commercial potential (1-10)

Respond in JSON format.
"""

response = model_json.generate_content(classification_prompt)
classification = json.loads(response.text)

print(f'📊 Classification Results:')
for key, value in classification.items():
    print(f'   • {key}: {value}')

print('\n' + '=' * 60)
print('✅ ALL TESTS PASSED!')
print('🎉 Gemini is ready for SampleMind AI audio analysis!')
print('🚀 Primary AI: GEMINI 2.5 Pro/Flash')
print('💰 Cost-effective alternative to OpenAI')
