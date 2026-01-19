# 🤖 AI INTEGRATION SETUP GUIDE

## Complete Setup for Gemini and Claude AI APIs

### Table of Contents
1. [Overview](#overview)
2. [Google Gemini Setup](#google-gemini-setup)
3. [Anthropic Claude Setup](#anthropic-claude-setup)
4. [Using AI in Your Code](#using-ai-in-your-code)
5. [Hybrid AI Architecture](#hybrid-ai-architecture)
6. [Testing AI Features](#testing-ai-features)
7. [Best Practices](#best-practices)

---

## 🎯 Overview

### AI in SampleMind

SampleMind uses multiple AI models for different tasks:

| Model | Provider | Best For | Cost |
|-------|----------|----------|------|
| **Gemini 3 Flash** | Google | Fast analysis, suggestions | $0.075/1M tokens |
| **Claude 3.5 Sonnet** | Anthropic | Complex reasoning, coaching | $3/1M tokens |
| **Phi3/Qwen2.5** | Ollama (Local) | Offline mode, no cost | Free |

### Hybrid Architecture

```
┌─────────────────────────────────────────┐
│         Your Application                │
│     (CLI, API, Web Interface)           │
└────────────────┬────────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐   ┌────▼──────────┐
    │ Online   │   │ Offline       │
    │ Models   │   │ Models        │
    └────┬─────┘   └────┬──────────┘
         │              │
    ┌────▼──────┐ ┌────▼──────┐
    │ Gemini    │ │ Ollama    │
    │ Claude    │ │ (Local)   │
    └──────────┘ └──────────┘
```

---

## 🔐 Google Gemini Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Name: `samplemind-ai`
4. Click "Create"
5. Wait for project creation (1-2 minutes)

### Step 2: Enable Gemini API

1. In Cloud Console, search for "Generative AI API"
2. Click on it and select "Enable"
3. Wait for activation

### Step 3: Create API Key

1. Go to "Credentials" in Cloud Console
2. Click "Create Credentials" → "API Key"
3. Copy the key (looks like: `AIzaSy...`)
4. Click "Restrict Key" button:
   - Application restrictions: Select "Android apps", "iOS apps", or "Web applications"
   - API restrictions: Select "Generative AI API"
5. Save the key somewhere safe

### Step 4: Set Environment Variable

**On Linux Ubuntu:**

```bash
# Add to ~/.bashrc or ~/.zshrc
export GOOGLE_API_KEY="your-key-here"

# Reload shell
source ~/.bashrc

# Verify
echo $GOOGLE_API_KEY
```

**For VSCode (permanent):**

Create `.env` file in project root:
```env
GOOGLE_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

Add to `.gitignore`:
```
.env
.env.local
```

### Step 5: Test Gemini Connection

```python
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Test connection
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello, what is 2+2?")
print(response.text)  # "2+2 equals 4"
```

**Or in terminal:**
```bash
python -c "
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('Test: What AI models are you aware of?')
print('✓ Gemini API works!')
print(response.text[:100])  # Print first 100 chars
"
```

---

## 🧠 Anthropic Claude Setup

### Step 1: Create Anthropic Account

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Click "Sign Up" (or "Sign In" if you have account)
3. Enter email and password
4. Verify email

### Step 2: Create API Key

1. Go to "Settings" → "API Keys"
2. Click "Generate New Key"
3. Name it: `samplemind-development`
4. Copy the key (looks like: `sk-ant-...`)
5. **Save it immediately** - you won't see it again!

### Step 3: Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export ANTHROPIC_API_KEY="your-key-here"

# Reload shell
source ~/.bashrc

# Verify
echo $ANTHROPIC_API_KEY
```

### Step 4: Test Claude Connection

```python
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, what is 2+2?"}
    ]
)

print(message.content[0].text)  # "2+2 equals 4"
```

**Or in terminal:**
```bash
python -c "
import os
import anthropic

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
message = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Say hello!'}]
)
print('✓ Claude API works!')
print(message.content[0].text)
"
```

---

## 💻 Using AI in Your Code

### Pattern 1: Simple Text Generation

#### Using Gemini:
```python
import google.generativeai as genai
import os

def get_production_tips(genre: str, tempo: int) -> str:
    """Get production tips using Gemini"""

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    I'm producing a {genre} track at {tempo} BPM.
    Give me 3 specific production tips.
    Keep response concise (under 100 words).
    """

    response = model.generate_content(prompt)
    return response.text

# Usage in CLI
tips = get_production_tips("house", 120)
print(f"Production Tips:\n{tips}")
```

#### Using Claude:
```python
import anthropic
import os

def get_production_tips(genre: str, tempo: int) -> str:
    """Get production tips using Claude"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": f"""
                I'm producing a {genre} track at {tempo} BPM.
                Give me 3 specific production tips.
                Keep response concise (under 100 words).
                """
            }
        ]
    )

    return message.content[0].text

# Usage in CLI
tips = get_production_tips("house", 120)
print(f"Production Tips:\n{tips}")
```

### Pattern 2: Streaming Responses

Great for long responses - show results as they arrive:

```python
import google.generativeai as genai
import os

def stream_production_guide(genre: str):
    """Stream production guide (appears in real-time)"""

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Create a beginner's guide to producing {genre} music"

    # Stream responses
    for chunk in model.generate_content(prompt, stream=True):
        print(chunk.text, end="", flush=True)

    print()  # New line at end

# Usage
stream_production_guide("techno")
```

### Pattern 3: JSON Extraction

Use AI to structure unstructured data:

```python
import json
import google.generativeai as genai
import os

def extract_song_info(description: str) -> dict:
    """Extract song info from natural language"""

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Extract song information from this description:
    "{description}"

    Return ONLY valid JSON with: tempo (int), key (str), genre (str), mood (str)
    Example: {{"tempo": 120, "key": "C Major", "genre": "House", "mood": "energetic"}}
    """

    response = model.generate_content(prompt)

    # Parse JSON from response
    try:
        json_str = response.text.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("```")[1].replace("json", "")
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {"error": "Could not parse response"}

# Usage
result = extract_song_info("Fast 140 BPM industrial techno, dark and aggressive")
print(f"Tempo: {result.get('tempo')} BPM")
print(f"Genre: {result.get('genre')}")
```

### Pattern 4: Vision/Image Analysis

Analyze images using Claude:

```python
import anthropic
import base64
import os

def analyze_waveform_image(image_path: str) -> str:
    """Analyze waveform image"""

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze this waveform image. What can you tell about the audio?"
                    }
                ],
            }
        ]
    )

    return message.content[0].text

# Usage
analysis = analyze_waveform_image("waveform.png")
print(analysis)
```

### Pattern 5: Retry Logic (Handle Errors)

```python
import google.generativeai as genai
import os
import time

def get_response_with_retry(
    prompt: str,
    max_retries: int = 3,
    model_name: str = "gemini-1.5-flash"
) -> str:
    """Get AI response with automatic retry on failure"""

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(model_name)

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt, timeout=30)
            return response.text

        except genai.types.APIError as e:
            if attempt == max_retries - 1:
                return f"Failed after {max_retries} attempts: {e}"

            # Wait before retry (exponential backoff)
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
            time.sleep(wait_time)

        except Exception as e:
            return f"Unexpected error: {e}"

# Usage
result = get_response_with_retry("Explain music production")
print(result)
```

---

## 🏗️ Hybrid AI Architecture

### Smart Model Selection

Choose the right model for the task:

```python
import os
import google.generativeai as genai
import anthropic

class AIAssistant:
    """Smart AI assistant that selects best model for task"""

    def __init__(self):
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_suggestion(self, task_type: str, content: str) -> str:
        """Get suggestion using best model for task"""

        if task_type == "fast_analysis":
            # Use fast Gemini for quick analysis
            response = self.gemini_model.generate_content(
                f"Analyze: {content}\nBe concise."
            )
            return response.text

        elif task_type == "deep_reasoning":
            # Use Claude for complex reasoning
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Explain: {content}"
                }]
            )
            return message.content[0].text

        elif task_type == "creative":
            # Use Claude for creativity
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"Create something creative about: {content}"
                }]
            )
            return message.content[0].text

        else:
            # Default to Gemini
            response = self.gemini_model.generate_content(content)
            return response.text

# Usage
ai = AIAssistant()

# Fast analysis
result = ai.get_suggestion("fast_analysis", "Analyze this kick drum")
print(f"Fast: {result}")

# Deep reasoning
result = ai.get_suggestion("deep_reasoning", "Why is stereo width important in production?")
print(f"Deep: {result}")

# Creative
result = ai.get_suggestion("creative", "Generate a production workflow")
print(f"Creative: {result}")
```

### Fallback Strategy

```python
def get_ai_response_with_fallback(prompt: str, preferred: str = "gemini") -> str:
    """Try preferred model, fall back to other if fails"""

    if preferred == "gemini":
        try:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt, timeout=30)
            return response.text
        except Exception as e:
            print(f"Gemini failed: {e}. Trying Claude...")
            # Fall back to Claude
            preferred = "claude"

    if preferred == "claude":
        try:
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Both AI services failed: {e}"

# Usage
result = get_ai_response_with_fallback("Explain music theory", preferred="gemini")
print(result)
```

---

## ✅ Testing AI Features

### Test 1: Basic Connectivity

```bash
# Create test_ai.py
python << 'EOF'
import os
import google.generativeai as genai
import anthropic

print("Testing AI connectivity...")

# Test Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Gemini works!'")
    print("✓ Gemini: " + response.text)
except Exception as e:
    print(f"✗ Gemini failed: {e}")

# Test Claude
try:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'Claude works!'"}]
    )
    print("✓ Claude: " + message.content[0].text)
except Exception as e:
    print(f"✗ Claude failed: {e}")

print("\nDone!")
EOF
```

### Test 2: Performance Comparison

```python
import time
import google.generativeai as genai
import anthropic
import os

def benchmark_models():
    """Compare response times"""

    prompt = "Explain music production in one sentence"

    # Test Gemini
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    start = time.time()
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    gemini_time = time.time() - start
    print(f"Gemini: {gemini_time:.2f}s - {response.text[:50]}...")

    # Test Claude
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    start = time.time()
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    claude_time = time.time() - start
    print(f"Claude: {claude_time:.2f}s - {message.content[0].text[:50]}...")

    print(f"\nFaster: {'Gemini' if gemini_time < claude_time else 'Claude'}")

benchmark_models()
```

---

## 🎯 Best Practices

### 1. Secure API Keys

```python
# ❌ DON'T
API_KEY = "AIzaSy..."  # Never hardcode!

# ✅ DO
import os
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not set in environment")
```

### 2. Handle Rate Limits

```python
import time

def call_api_with_rate_limit(
    api_call_func,
    max_calls_per_minute: int = 60
):
    """Respect rate limits"""

    call_times = []

    def rate_limited_call():
        nonlocal call_times

        # Remove calls older than 1 minute
        now = time.time()
        call_times = [t for t in call_times if now - t < 60]

        if len(call_times) >= max_calls_per_minute:
            # Wait before next call
            sleep_time = 60 - (now - call_times[0])
            print(f"Rate limit approaching. Waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)

        call_times.append(time.time())
        return api_call_func()

    return rate_limited_call()
```

### 3. Monitor Costs

```python
def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate API cost"""

    pricing = {
        "gemini-1.5-flash": {"input": 0.075 / 1_000_000, "output": 0.3 / 1_000_000},
        "claude-3-5-sonnet": {"input": 3 / 1_000_000, "output": 15 / 1_000_000}
    }

    if model not in pricing:
        return 0

    cost = (
        input_tokens * pricing[model]["input"] +
        output_tokens * pricing[model]["output"]
    )
    return cost

# Example
cost = estimate_cost(input_tokens=1000, output_tokens=500, model="gemini-1.5-flash")
print(f"Estimated cost: ${cost:.6f}")
```

### 4. Cache Responses

```python
import json
import hashlib
from datetime import datetime, timedelta

class AICache:
    """Cache AI responses"""

    def __init__(self, cache_file: str = ".ai_cache.json", ttl_hours: int = 24):
        self.cache_file = cache_file
        self.ttl = timedelta(hours=ttl_hours)
        self.cache = self._load_cache()

    def _load_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get(self, prompt: str):
        """Get cached response if exists"""
        key = hashlib.md5(prompt.encode()).hexdigest()

        if key in self.cache:
            cached = self.cache[key]
            created_at = datetime.fromisoformat(cached["created_at"])

            if datetime.now() - created_at < self.ttl:
                return cached["response"]  # Return cached

        return None

    def set(self, prompt: str, response: str):
        """Cache response"""
        key = hashlib.md5(prompt.encode()).hexdigest()
        self.cache[key] = {
            "response": response,
            "created_at": datetime.now().isoformat()
        }
        self._save_cache()

# Usage
cache = AICache()

prompt = "Explain music production"

# Try cache first
result = cache.get(prompt)
if result:
    print(f"From cache: {result}")
else:
    # Call API
    result = call_ai_api(prompt)
    # Save to cache
    cache.set(prompt, result)
    print(f"From API: {result}")
```

---

## 🚀 Next Steps

1. **Set up Gemini API** - Follow steps above
2. **Set up Claude API** - Follow steps above
3. **Test both** - Run connectivity tests
4. **Choose for features** - Use Gemini for speed, Claude for reasoning
5. **Implement in CLI** - Use patterns above in your code
6. **Monitor costs** - Track API spending
7. **Add fallbacks** - Implement fallback strategy

---

## 📚 Resources

- [Gemini API Documentation](https://ai.google.dev/)
- [Claude API Documentation](https://docs.anthropic.com)
- [Google Cloud Console](https://console.cloud.google.com)
- [Anthropic Console](https://console.anthropic.com)

Now you're ready to add AI superpowers to SampleMind! 🚀
