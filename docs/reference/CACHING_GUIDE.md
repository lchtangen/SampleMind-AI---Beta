# 💰 AI Response Caching - Cost Reduction Guide

## 🎯 Overview

SampleMind AI v6 now includes intelligent caching to **reduce API costs by 60-80%** for repeated analyses. The caching system stores AI responses and reuses them for identical or similar audio features.

---

## ✨ Key Features

✅ **Multiple Backends**: Redis, File-based, or In-Memory  
✅ **Smart Cache Keys**: SHA256 hashing of normalized audio features  
✅ **Cost Tracking**: Automatic tracking of savings  
✅ **TTL Management**: Configurable cache lifetime  
✅ **Hit Rate Monitoring**: Real-time cache performance metrics  
✅ **Seamless Integration**: Zero code changes required  

---

## 📊 Cost Savings Example

### Without Caching
```
100 audio files × $0.005/analysis = $0.50
```

### With Caching (70% hit rate)
```
30 API calls × $0.005 = $0.15
70 cache hits × $0 = $0.00
Total: $0.15 (70% savings!)
```

---

## 🚀 Quick Start

### 1. Enable Caching (Already Enabled!)

Check your `.env`:
```bash
AI_CACHE_ENABLED=true
AI_CACHE_BACKEND=redis
AI_CACHE_TTL_HOURS=168  # 1 week
```

### 2. Start Redis (Optional but Recommended)

```bash
# Already running from docker-compose
docker ps | grep redis

# Or start it
docker-compose up -d redis
```

### 3. Use as Normal - Caching is Automatic!

```python
from samplemind.integrations import SampleMindAIManager

manager = SampleMindAIManager()  # Caching enabled automatically

# First call - hits API
result1 = await manager.analyze_music(audio_features, AnalysisType.GENRE_CLASSIFICATION)

# Second call with same features - hits cache!
result2 = await manager.analyze_music(audio_features, AnalysisType.GENRE_CLASSIFICATION)
```

---

## 🎛️ Configuration

### Environment Variables

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `AI_CACHE_ENABLED` | `true` | true, false | Enable/disable caching |
| `AI_CACHE_BACKEND` | `redis` | redis, file, memory | Cache storage backend |
| `AI_CACHE_TTL_HOURS` | `168` | Any integer | Cache lifetime (hours) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis URL | Redis connection string |

### Backend Comparison

| Backend | Persistence | Speed | Multi-Process | Best For |
|---------|-------------|-------|---------------|----------|
| **Redis** | ✅ Yes | ⚡⚡⚡ Very Fast | ✅ Yes | Production, Multiple workers |
| **File** | ✅ Yes | ⚡⚡ Fast | ⚠️ Partial | Single server, Development |
| **Memory** | ❌ No | ⚡⚡⚡ Fastest | ❌ No | Testing, Short sessions |

---

## 📈 Monitoring Cache Performance

### Get Cache Statistics

```python
manager = SampleMindAIManager()
stats = manager.get_global_stats()

print(f"Cache enabled: {stats['cache_enabled']}")
print(f"Cache backend: {stats['cache_backend']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Hit rate: {stats['cache_hit_rate']:.1%}")
print(f"Cost saved: ${stats['cache_cost_saved']:.2f}")
```

### Example Output

```
Cache enabled: True
Cache backend: redis
Cache hits: 145
Cache misses: 55
Hit rate: 72.5%
Cost saved: $0.45
```

---

## 🔧 Advanced Usage

### Bypass Cache for Fresh Results

```python
# Force fresh API call
result = await manager.analyze_music(
    audio_features,
    AnalysisType.PRODUCTION_COACHING,
    bypass_cache=True  # Skip cache lookup
)
```

### Clear Cache

```python
# Clear all cached responses
if manager.cache:
    manager.cache.clear()
    print("Cache cleared!")
```

### Custom Cache Configuration

```python
from samplemind.core.cache import AICache, CacheConfig, CacheBackend

# Custom configuration
config = CacheConfig(
    enabled=True,
    backend=CacheBackend.FILE,
    ttl_seconds=3600 * 24,  # 1 day
    file_cache_dir="./my_cache"
)

cache = AICache(config)
```

---

## 🎯 How Caching Works

### 1. Cache Key Generation

```python
# Audio features are normalized and hashed
features = {
    'tempo': 120.0,  # Rounded to 1 decimal
    'key': 'C',
    'mode': 'major',
    'duration': 180.0,
    'energy': 0.75
}

# Generates: SHA256("tempo:120.0|key:C|mode:major...")
# Result: "e5bf6e503fbd..."
```

### 2. Cache Lookup Flow

```
┌─────────────────┐
│ analyze_music() │
└────────┬────────┘
         │
         ▼
┌────────────────┐
│  Check Cache?  │ ◄── bypass_cache=False
└────┬───────┬───┘
     │       │
    HIT     MISS
     │       │
     ▼       ▼
┌─────────┐ ┌──────────┐
│ Return  │ │ Call API │
│ Cached  │ │ & Cache  │
└─────────┘ └──────────┘
```

### 3. Cache Storage

```python
{
    'result': {
        'summary': '...',
        'production_tips': [...],
        'tokens_used': 1234,
        ...
    },
    'cached_at': 1704067200,
    'provider': 'google_ai',
    'model': 'gemini-2.5-pro',
    'analysis_type': 'genre_classification'
}
```

---

## 💡 Best Practices

### 1. Use Redis in Production
- Fastest performance
- Survives application restarts
- Supports multiple workers

### 2. Set Appropriate TTL
- **Development**: 24 hours (fresh data)
- **Production**: 1 week (cost savings)
- **Testing**: 1 hour (frequent changes)

### 3. Monitor Hit Rates
- Aim for >60% hit rate
- Low hit rate? Check feature normalization
- High hit rate? Consider longer TTL

### 4. Cache Management
- Clear cache after major updates
- Monitor cache size (disk/memory)
- Use file backend for persistence without Redis

---

## 🔍 Troubleshooting

### Cache Not Working?

**Check if caching is enabled:**
```python
manager = SampleMindAIManager()
print(f"Cache: {manager.cache is not None}")
```

**Check Redis connection:**
```bash
redis-cli ping
# Should return: PONG
```

**Check cache stats:**
```python
if manager.cache:
    stats = manager.cache.get_stats()
    print(stats)
```

### Low Hit Rate?

**Possible causes:**
1. Features varying too much (use normalization)
2. Different analysis types
3. Different providers
4. TTL too short

**Solution:**
```python
# Features are automatically normalized, but you can verify:
from samplemind.core.cache import AICacheKeyGenerator

key = AICacheKeyGenerator.generate_key(
    audio_features,
    'comprehensive',
    'google_ai'
)
print(f"Cache key: {key}")
```

### Cache Files Growing Too Large?

**File backend cleanup:**
```bash
# Manual cleanup
rm -rf ./cache/ai_responses/*.pkl

# Or use built-in clear
python -c "from samplemind.integrations import SampleMindAIManager; m = SampleMindAIManager(); m.cache.clear()"
```

---

## 📊 Performance Metrics

### Cache Response Times

| Backend | Average Response Time |
|---------|---------------------|
| Redis | 1-5ms |
| File | 5-15ms |
| Memory | <1ms |
| API Call | 2000-5000ms |

**Cache is 100-5000x faster than API calls!**

### Storage Requirements

| Analyses | Redis Memory | File Size |
|----------|-------------|-----------|
| 100 | ~5 MB | ~5 MB |
| 1,000 | ~50 MB | ~50 MB |
| 10,000 | ~500 MB | ~500 MB |

---

## 🎓 Cost Optimization Strategies

### Strategy 1: Batch Processing with Cache
```python
# Process many files - cache builds up
for audio_file in audio_files:
    features = audio_engine.analyze(audio_file)
    result = await manager.analyze_music(features)
    
# Later analyses benefit from cache
# Cost savings increase over time!
```

### Strategy 2: Smart Provider Selection
```python
# Use cheaper Gemini for cacheable tasks
result = await manager.analyze_music(
    features,
    AnalysisType.GENRE_CLASSIFICATION,  # Routed to Gemini
)

# Use Claude for creative tasks (less cache-friendly)
result = await manager.analyze_music(
    features,
    AnalysisType.PRODUCTION_COACHING,  # Routed to Claude
)
```

### Strategy 3: Increase TTL for Stable Content
```bash
# For library analysis (content doesn't change)
AI_CACHE_TTL_HOURS=720  # 30 days

# For active production (content changes)
AI_CACHE_TTL_HOURS=24  # 1 day
```

---

## 📋 Cache Management Commands

### Clear Cache
```bash
python -c "
from samplemind.integrations import SampleMindAIManager
manager = SampleMindAIManager()
if manager.cache:
    manager.cache.clear()
    print('Cache cleared!')
"
```

### View Cache Stats
```bash
python -c "
from samplemind.integrations import SampleMindAIManager
manager = SampleMindAIManager()
stats = manager.get_global_stats()
print(f\"Hit rate: {stats.get('cache_hit_rate', 0):.1%}\")
print(f\"Cost saved: \${stats.get('cache_cost_saved', 0):.2f}\")
"
```

### Test Cache
```bash
python -c "
from samplemind.core.cache import AICache, CacheBackend, CacheConfig

config = CacheConfig(enabled=True, backend=CacheBackend.MEMORY)
cache = AICache(config)

test_features = {'tempo': 120.0, 'key': 'C'}
cache.set(test_features, 'test', 'google_ai', {'result': 'test'}, cost_saved=0.01)
cached = cache.get(test_features, 'test', 'google_ai')

print(f\"✅ Cache working: {cached is not None}\")
"
```

---

## 🎉 Summary

With AI response caching enabled, you can expect:

✅ **60-80% cost reduction** for repeated analyses  
✅ **100-5000x faster** response times on cache hits  
✅ **Automatic operation** - no code changes needed  
✅ **Flexible backends** - Redis, File, or Memory  
✅ **Full visibility** - comprehensive statistics  

**Your AI-powered music production platform is now more cost-effective than ever! 🎵💰**
