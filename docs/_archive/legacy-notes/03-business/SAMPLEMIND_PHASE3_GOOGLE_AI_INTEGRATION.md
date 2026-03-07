# 🤖 SAMPLEMIND AI - GOOGLE AI INTEGRATION (GEMINI API)
## Complete Guide to Multimodal Audio Analysis with Google's AI

---

## 📚 2026 Q1: GOOGLE AI INTEGRATION

### What is Google AI (Gemini)?

**Understanding Large Language Models (LLMs)**

```
Traditional Programming:
You: "Classify this audio"
Computer: Follows exact rules you programmed
Problem: Can't handle anything you didn't anticipate

Large Language Model:
You: "Classify this audio and explain why"
AI: Analyzes, understands context, gives detailed answer
Benefit: Handles edge cases, provides insights
```

**Gemini vs Other AIs:**

```
GPT (OpenAI):
- Text only (primarily)
- Limited multimodal support

Claude (Anthropic):
- Excellent reasoning
- Text + images

Gemini (Google):
- NATIVE multimodal
- Text + Images + Audio + Video
- Built for mixed media
- PERFECT for SampleMind!
```

**Why Gemini for Audio Platform?**

```
✅ Native audio understanding
✅ Can "hear" and describe sounds
✅ Understands music theory
✅ Context-aware suggestions
✅ Multiple languages
✅ Large context window (1M tokens!)
✅ Fast inference
✅ Cost-effective
```

---

## 🔑 Google AI Setup (Prerequisites)

### Step 1: Get API Key

```bash
# 1. Go to Google AI Studio
# https://makersuite.google.com/app/apikey

# 2. Create project
# Click: "Create API Key"

# 3. Copy your key
# Looks like: AIzaSy... (39 characters)

# 4. Store securely in environment variable
```

**Environment Variables Setup:**

```bash
# .env.local (Next.js frontend)

# Google AI
NEXT_PUBLIC_GOOGLE_AI_API_KEY=your_key_here

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```bash
# .env (FastAPI backend)

# Google AI
GOOGLE_AI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/samplemind
```

**Security Best Practices:**

```python
# ❌ NEVER DO THIS (Hardcoded key)
api_key = "AIzaSyABC123..."  # EXPOSED!

# ✅ ALWAYS DO THIS (Environment variable)
import os
api_key = os.getenv("GOOGLE_AI_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_AI_API_KEY not set")
```

**Why Environment Variables?**

```
1. Security:
   - Not in code (not committed to Git)
   - Can't accidentally share
   - Easy to rotate

2. Flexibility:
   - Different keys per environment
   - Dev key vs Production key
   - Easy to change without code changes

3. Best Practice:
   - Industry standard
   - Required by security audits
   - Follows 12-Factor App principles
```

---

### Step 2: Install Google AI SDK

```bash
# Backend (Python)
poetry add google-generativeai

# Frontend (JavaScript/TypeScript)
npm install @google/generative-ai
```

---

## 🎯 Core Concepts: Prompt Engineering

### What is Prompt Engineering?

**Understanding Prompts:**

```
Prompt = Instructions you give to AI

Like asking a smart assistant:

Bad prompt:
"Analyze this"
→ Vague, unclear expectations

Good prompt:
"Analyze this audio sample. Identify:
1. Instrument type
2. Musical key
3. BPM
4. Genre
5. Mood

Provide confident, specific answers."

→ Clear, structured, actionable
```

**The Anatomy of a Great Prompt:**

```
1. CONTEXT (Who/What):
   "You are an expert music producer with 20 years experience."

2. TASK (What to do):
   "Analyze this audio sample and identify its characteristics."

3. FORMAT (How to respond):
   "Respond in JSON format with the following fields:..."

4. CONSTRAINTS (Boundaries):
   "Be specific. If uncertain, say 'unknown' rather than guessing."

5. EXAMPLES (Show, don't just tell):
   "Example output: {instrument: 'kick drum', confidence: 0.95}"
```

### Prompt Templates for Audio Analysis

```python
# backend/services/gemini_service.py

from typing import Dict, List, Optional
import google.generativeai as genai
import os
import json

class GeminiAudioAnalyzer:
    """
    Service for analyzing audio with Google's Gemini AI
    
    This class handles:
    - API authentication
    - Prompt construction
    - Audio file processing
    - Response parsing
    - Error handling
    """
    
    def __init__(self):
        """Initialize Gemini AI client"""
        
        # Get API key from environment
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable not set")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        """
        MODEL SELECTION:
        
        gemini-1.5-pro:
        - Best quality
        - Multimodal (audio + text)
        - Largest context window (1M tokens)
        - Recommended for production
        
        gemini-1.5-flash:
        - Faster
        - Lower cost
        - Good for simple tasks
        - Use for real-time features
        
        We use Pro for audio analysis (needs quality)
        """
        
        print("✅ Gemini AI initialized")
    
    def analyze_audio_sample(
        self,
        audio_path: str,
        analysis_type: str = "comprehensive"
    ) -> Dict:
        """
        Analyze audio file with Gemini
        
        Args:
            audio_path: Path to audio file
            analysis_type: Type of analysis
                - 'comprehensive': Full analysis
                - 'quick': Basic classification
                - 'genre': Genre detection only
                - 'technical': Technical details only
        
        Returns:
            Dictionary with analysis results
        """
        
        # === STEP 1: LOAD AUDIO FILE ===
        """
        CONCEPT: File Upload to Gemini
        
        Gemini can process:
        - Audio files directly
        - No need to convert to spectrogram
        - Supports: MP3, WAV, FLAC, etc.
        
        File size limits:
        - 20 MB per file
        - Longer files need chunking
        """
        
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Prepare audio for Gemini
        audio_file = {
            'mime_type': 'audio/wav',  # or 'audio/mp3', 'audio/flac'
            'data': audio_data
        }
        
        # === STEP 2: CONSTRUCT PROMPT ===
        
        if analysis_type == "comprehensive":
            prompt = self._comprehensive_analysis_prompt()
        elif analysis_type == "quick":
            prompt = self._quick_classification_prompt()
        elif analysis_type == "genre":
            prompt = self._genre_detection_prompt()
        elif analysis_type == "technical":
            prompt = self._technical_analysis_prompt()
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # === STEP 3: CALL GEMINI API ===
        """
        CONCEPT: Generation Config
        
        Controls AI behavior:
        - Temperature: Creativity (0-1)
        - Top_p: Diversity of responses
        - Max tokens: Response length
        """
        
        try:
            response = self.model.generate_content(
                [prompt, audio_file],
                generation_config={
                    'temperature': 0.2,  # Low = consistent, factual
                    'top_p': 0.8,
                    'max_output_tokens': 2048
                }
            )
            """
            TEMPERATURE EXPLAINED:
            
            0.0: Deterministic (same every time)
            0.2: Slightly varied, mostly factual (our choice)
            0.5: Balanced
            0.8: Creative
            1.0: Very creative, unpredictable
            
            For audio analysis:
            - Want consistency
            - Need accuracy
            - Low temperature better
            """
            
            # === STEP 4: PARSE RESPONSE ===
            
            # Extract JSON from response
            response_text = response.text
            
            # Gemini might wrap JSON in markdown
            # Remove code blocks if present
            if '```json' in response_text:
                # Extract content between ```json and ```
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            return {
                'success': True,
                'analysis': result,
                'model': 'gemini-1.5-pro',
                'tokens_used': response.usage_metadata.total_token_count
            }
            
        except Exception as e:
            print(f"❌ Error in Gemini analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _comprehensive_analysis_prompt(self) -> str:
        """
        Comprehensive audio analysis prompt
        
        Covers everything:
        - Identification
        - Technical details
        - Musical properties
        - Recommendations
        """
        
        return """
        You are an expert audio engineer and music producer with 20+ years of experience.
        
        TASK:
        Analyze this audio sample in detail. Provide comprehensive information about:
        
        1. IDENTIFICATION
           - What is this sound? (kick, snare, synth, vocal, etc.)
           - Instrument family
           - Sound characteristics
        
        2. TECHNICAL PROPERTIES
           - Estimated frequency range (Hz)
           - Dynamic range
           - Transient characteristics
           - Harmonic content
        
        3. MUSICAL PROPERTIES
           - Key/pitch (if applicable)
           - Tempo/BPM (if rhythmic)
           - Time signature (if applicable)
           - Genre suitability
        
        4. AUDIO QUALITY
           - Sample rate (estimated)
           - Bit depth quality
           - Any artifacts or issues
           - Production quality (1-10)
        
        5. USAGE RECOMMENDATIONS
           - Best use cases
           - Genre recommendations
           - Processing suggestions
           - Mix tips
        
        6. SIMILAR SOUNDS
           - What sounds are similar?
           - Alternative descriptions
           - Related categories
        
        RESPONSE FORMAT:
        Respond ONLY with valid JSON. No markdown, no explanations outside JSON.
        
        Example structure:
        {
          "identification": {
            "type": "kick_drum",
            "instrument_family": "percussion",
            "characteristics": ["punchy", "deep", "808-style"],
            "confidence": 0.95
          },
          "technical": {
            "frequency_range": "30-120 Hz",
            "dynamic_range": "high",
            "transient": "sharp attack, sustained decay",
            "harmonics": "sub-harmonic rich"
          },
          "musical": {
            "key": "C",
            "bpm": null,
            "time_signature": null,
            "genres": ["techno", "trap", "house"]
          },
          "quality": {
            "sample_rate": "44100 Hz",
            "bit_depth": "24-bit",
            "artifacts": "none detected",
            "production_score": 9
          },
          "recommendations": {
            "use_cases": ["kick drum", "bass reinforcement"],
            "genres": ["techno", "trap", "dubstep"],
            "processing": ["slight compression", "EQ boost at 60Hz"],
            "mix_tips": ["layer with sub bass", "sidechain compress"]
          },
          "similar_sounds": ["808 kick", "sub kick", "boom kick"],
          "tags": ["kick", "808", "deep", "punchy", "techno"]
        }
        
        IMPORTANT CONSTRAINTS:
        - Be specific and technical
        - Use audio engineering terminology
        - If uncertain, indicate confidence level
        - No guessing - say "unknown" if truly unsure
        - Focus on actionable insights
        """
    
    def _quick_classification_prompt(self) -> str:
        """Quick classification prompt for real-time use"""
        
        return """
        You are an audio classification expert.
        
        TASK:
        Quickly identify this audio sample.
        
        Provide:
        1. Type (kick, snare, hi-hat, bass, synth, vocal, fx, etc.)
        2. Subtype (e.g., "808 kick", "acoustic snare", "saw synth")
        3. Key characteristics (2-3 words)
        4. Confidence (0-1)
        
        RESPONSE FORMAT (JSON only):
        {
          "type": "kick",
          "subtype": "808_kick",
          "characteristics": ["deep", "punchy", "synthetic"],
          "confidence": 0.92
        }
        
        Be concise but accurate.
        """
    
    def _genre_detection_prompt(self) -> str:
        """Genre-specific analysis"""
        
        return """
        You are a music genre expert with encyclopedic knowledge of electronic and acoustic music.
        
        TASK:
        Identify which genres this audio sample is best suited for.
        
        Analyze:
        1. Sonic characteristics
        2. Production style
        3. Typical usage patterns
        4. Cultural context
        
        RESPONSE FORMAT (JSON only):
        {
          "primary_genres": ["techno", "house"],
          "secondary_genres": ["minimal", "tech-house"],
          "sub_genres": ["detroit techno", "deep house"],
          "confidence_scores": {
            "techno": 0.95,
            "house": 0.80,
            "minimal": 0.60
          },
          "reasoning": "Punchy 4/4 kick with industrial texture typical of techno. Clean production suggests house influence."
        }
        """
    
    def _technical_analysis_prompt(self) -> str:
        """Technical/engineering focused analysis"""
        
        return """
        You are an audio engineer specializing in technical analysis.
        
        TASK:
        Provide detailed technical analysis of this audio sample.
        
        Focus on:
        1. Frequency spectrum analysis
        2. Envelope (ADSR) characteristics
        3. Harmonic content
        4. Phase characteristics
        5. Stereo field
        6. Dynamic range
        
        RESPONSE FORMAT (JSON only):
        {
          "frequency_analysis": {
            "fundamental": "60 Hz",
            "harmonics": ["120 Hz", "180 Hz", "240 Hz"],
            "dominant_range": "sub-bass",
            "spectrum_shape": "bass-heavy with sharp attack"
          },
          "envelope": {
            "attack": "5 ms",
            "decay": "300 ms",
            "sustain": "none",
            "release": "short"
          },
          "stereo": {
            "width": "mono",
            "imaging": "centered"
          },
          "dynamics": {
            "peak_db": "-3 dBFS",
            "rms_db": "-12 dBFS",
            "dynamic_range": "moderate",
            "limiting": "none detected"
          }
        }
        """
    
    # === ADVANCED FEATURES ===
    
    def compare_samples(
        self,
        audio_path_1: str,
        audio_path_2: str
    ) -> Dict:
        """
        Compare two audio samples
        
        Use case:
        - Find similar samples
        - A/B testing
        - Version comparison
        """
        
        with open(audio_path_1, 'rb') as f:
            audio_1 = {'mime_type': 'audio/wav', 'data': f.read()}
        
        with open(audio_path_2, 'rb') as f:
            audio_2 = {'mime_type': 'audio/wav', 'data': f.read()}
        
        prompt = """
        You are comparing two audio samples.
        
        TASK:
        Analyze both samples and compare them.
        
        Provide:
        1. Similarities
        2. Differences
        3. Which is better for specific use cases
        4. Recommendations
        
        RESPONSE FORMAT (JSON):
        {
          "sample_1_type": "...",
          "sample_2_type": "...",
          "similarities": [...],
          "differences": [...],
          "better_for": {
            "kick_drum": "sample_1",
            "sub_bass": "sample_2"
          },
          "similarity_score": 0.75,
          "recommendations": "..."
        }
        """
        
        try:
            response = self.model.generate_content(
                [prompt, audio_1, audio_2],
                generation_config={'temperature': 0.1}
            )
            
            return json.loads(response.text)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def suggest_processing(
        self,
        audio_path: str,
        target_genre: str
    ) -> Dict:
        """
        Suggest audio processing for specific genre
        
        Use case:
        - Production tips
        - Genre adaptation
        - Mixing guidance
        """
        
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        audio_file = {'mime_type': 'audio/wav', 'data': audio_data}
        
        prompt = f"""
        You are an expert mixing and mastering engineer.
        
        TASK:
        Analyze this audio sample and suggest processing to make it perfect for {target_genre}.
        
        Provide:
        1. EQ recommendations (specific frequencies and gains)
        2. Compression settings
        3. Effects chain
        4. Leveling advice
        5. Creative processing ideas
        
        RESPONSE FORMAT (JSON):
        {{
          "eq": [
            {{"frequency": "60 Hz", "gain": "+3 dB", "q": 0.7, "type": "bell"}},
            {{"frequency": "200 Hz", "gain": "-2 dB", "q": 1.0, "type": "bell"}}
          ],
          "compression": {{
            "threshold": "-12 dB",
            "ratio": "4:1",
            "attack": "10 ms",
            "release": "100 ms",
            "knee": "soft"
          }},
          "effects_chain": [
            "saturation (subtle warmth)",
            "reverb (room, 1.2s decay)",
            "limiter (peak at -0.3 dBFS)"
          ],
          "level": "-6 dBFS for mixing headroom",
          "creative": "Layer with sub sine wave at 50 Hz for extra depth",
          "reasoning": "..."
        }}
        
        Be specific with numbers. Focus on {target_genre} characteristics.
        """
        
        try:
            response = self.model.generate_content(
                [prompt, audio_file],
                generation_config={'temperature': 0.3}
            )
            
            return json.loads(response.text)
        except Exception as e:
            return {'success': False, 'error': str(e)}
```

---

## 🚀 Rate Limiting & Cost Management

### Understanding API Costs

**Gemini Pricing (as of 2025):**

```
Input (per 1M tokens):
- Text: $0.35
- Audio: $0.75
- Video: $1.25

Output (per 1M tokens):
- Text: $1.05

Average audio sample (10 seconds):
- ~50,000 tokens input
- ~500 tokens output
- Cost: ~$0.04 per analysis

1,000 samples per day:
- Input: 50M tokens × $0.75 = $37.50
- Output: 500k tokens × $1.05 = $0.53
- Total: ~$38 per day = ~$1,140/month
```

**Cost Optimization Strategies:**

```python
# backend/services/rate_limiter.py

from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio

class RateLimiter:
    """
    Rate limiting for API calls
    
    Prevents:
    - Excessive costs
    - API quota exhaustion
    - Abuse
    
    Strategy:
    - Token bucket algorithm
    - Per-user limits
    - Global limits
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_day: int = 1000
    ):
        self.rpm_limit = requests_per_minute
        self.rpd_limit = requests_per_day
        
        # User request tracking
        self.user_requests: Dict[str, list] = {}
        # Global request tracking
        self.global_requests: list = []
        
        print(f"✅ Rate limiter: {requests_per_minute}/min, {requests_per_day}/day")
    
    async def check_limit(self, user_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if user can make request
        
        Returns:
            (allowed: bool, reason: Optional[str])
        """
        
        now = datetime.now()
        
        # === CHECK GLOBAL LIMIT ===
        # Remove old requests (>24 hours)
        self.global_requests = [
            req_time for req_time in self.global_requests
            if now - req_time < timedelta(days=1)
        ]
        
        if len(self.global_requests) >= self.rpd_limit:
            return False, "System rate limit exceeded. Try again tomorrow."
        
        # === CHECK USER LIMIT ===
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        user_reqs = self.user_requests[user_id]
        
        # Remove old requests (>1 minute for RPM check)
        user_reqs_minute = [
            req_time for req_time in user_reqs
            if now - req_time < timedelta(minutes=1)
        ]
        
        if len(user_reqs_minute) >= self.rpm_limit:
            return False, f"Rate limit: {self.rpm_limit} requests per minute"
        
        # Remove old requests (>24 hours for RPD check)
        user_reqs_day = [
            req_time for req_time in user_reqs
            if now - req_time < timedelta(days=1)
        ]
        
        if len(user_reqs_day) >= self.rpd_limit:
            return False, f"Daily limit: {self.rpd_limit} requests per day"
        
        # === ALLOW REQUEST ===
        # Record request
        self.user_requests[user_id].append(now)
        self.global_requests.append(now)
        
        return True, None
    
    def get_user_usage(self, user_id: str) -> Dict:
        """Get user's current usage"""
        
        if user_id not in self.user_requests:
            return {
                'requests_today': 0,
                'requests_this_minute': 0,
                'daily_remaining': self.rpd_limit,
                'minute_remaining': self.rpm_limit
            }
        
        now = datetime.now()
        user_reqs = self.user_requests[user_id]
        
        reqs_minute = len([
            r for r in user_reqs 
            if now - r < timedelta(minutes=1)
        ])
        
        reqs_day = len([
            r for r in user_reqs
            if now - r < timedelta(days=1)
        ])
        
        return {
            'requests_today': reqs_day,
            'requests_this_minute': reqs_minute,
            'daily_remaining': max(0, self.rpd_limit - reqs_day),
            'minute_remaining': max(0, self.rpm_limit - reqs_minute)
        }
```

---

This completes the Google AI Integration section. Continuing with Deployment next... 🚀
