# ⚡ Performance Optimization Guide

## Frontend Optimizations

### Code Splitting
```typescript
// Dynamic imports for heavy components
const AudioVisualizer = dynamic(() => import('@/components/AudioVisualizer'), {
  loading: () => <Skeleton />,
  ssr: false
});

// Route-based code splitting (automatic with Next.js)
```

### Image Optimization
```typescript
import Image from 'next/image';

<Image
  src="/audio-wave.png"
  width={800}
  height={400}
  alt="Waveform"
  priority={false}
  loading="lazy"
/>
```

### Bundle Size Reduction
```bash
# Analyze bundle
pnpm build
pnpm analyze

# Remove unused dependencies
pnpm prune

# Use lighter alternatives
# moment.js → date-fns
# lodash → lodash-es (tree-shakeable)
```

### Caching Strategy
```typescript
// API responses
const { data } = useQuery(['audio', id], fetchAudio, {
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
});

// Static assets
// Cache-Control: public, max-age=31536000, immutable
```

### Lazy Loading
```typescript
// Images
<img loading="lazy" src="..." />

// Components
const HeavyComponent = lazy(() => import('./Heavy'));

// Routes (automatic with Next.js App Router)
```

## Backend Optimizations

### Database Query Optimization
```python
# Bad: N+1 queries
for audio in audios:
    user = db.query(User).filter(User.id == audio.user_id).first()

# Good: Join or eager loading
audios = db.query(Audio).options(joinedload(Audio.user)).all()

# Use indexes
class Audio(Base):
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, index=True)
```

### Caching with Redis
```python
from redis import Redis
cache = Redis.from_url(settings.REDIS_URL)

async def get_audio(audio_id: int):
    # Try cache first
    cached = cache.get(f"audio:{audio_id}")
    if cached:
        return json.loads(cached)
    
    # Query database
    audio = db.query(Audio).get(audio_id)
    
    # Cache result
    cache.setex(f"audio:{audio_id}", 300, json.dumps(audio))
    return audio
```

### Response Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
    compresslevel=6     # Balance between size and speed
)
```

### Connection Pooling
```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Async Operations
```python
# Bad: Blocking
def process_audio(file):
    result = heavy_computation(file)  # Blocks
    return result

# Good: Async with Celery
@celery.task
def process_audio_task(file_id):
    result = heavy_computation(file_id)
    return result

# Trigger async
task = process_audio_task.delay(file_id)
```

## Database Optimizations

### Indexing Strategy
```sql
-- Frequently queried columns
CREATE INDEX idx_audio_user_id ON audio(user_id);
CREATE INDEX idx_audio_created_at ON audio(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_audio_user_status ON audio(user_id, status);

-- Partial indexes
CREATE INDEX idx_audio_processing ON audio(id) WHERE status = 'processing';
```

### Query Optimization
```python
# Bad: Load everything
audios = db.query(Audio).all()

# Good: Pagination
audios = db.query(Audio).offset(skip).limit(limit).all()

# Good: Select specific columns
audios = db.query(Audio.id, Audio.filename).all()

# Good: Count efficiently
count = db.query(func.count(Audio.id)).scalar()
```

### Database Connection Management
```python
# Use context managers
async def get_db():
    async with AsyncSession() as session:
        yield session
        
# Dependency injection
@app.get("/audio")
async def list_audio(db: Session = Depends(get_db)):
    return db.query(Audio).all()
```

## API Optimizations

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("60/minute")
async def get_data():
    return {"data": "..."}
```

### Response Pagination
```python
@app.get("/audio")
async def list_audio(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(func.count(Audio.id)).scalar()
    items = db.query(Audio).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }
```

### Field Selection
```python
@app.get("/audio")
async def list_audio(
    fields: str = Query(None, description="Comma-separated fields")
):
    # Only return requested fields
    if fields:
        field_list = fields.split(',')
        return db.query(*[getattr(Audio, f) for f in field_list]).all()
    return db.query(Audio).all()
```

## WebSocket Optimizations

### Message Batching
```python
class WebSocketManager:
    def __init__(self):
        self.message_queue = asyncio.Queue()
    
    async def batch_sender(self):
        while True:
            messages = []
            # Collect messages for 100ms
            try:
                while len(messages) < 10:
                    msg = await asyncio.wait_for(
                        self.message_queue.get(), 
                        timeout=0.1
                    )
                    messages.append(msg)
            except asyncio.TimeoutError:
                pass
            
            if messages:
                await self.send_batch(messages)
```

### Connection Management
```python
# Limit connections per user
MAX_CONNECTIONS_PER_USER = 5

async def connect(user_id: int):
    if len(connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
        raise Exception("Too many connections")
    
    # Add connection
    connections[user_id].add(websocket)
```

## File Upload Optimizations

### Chunked Upload
```python
@app.post("/upload")
async def upload_chunk(
    chunk: UploadFile,
    chunk_number: int,
    total_chunks: int,
    file_id: str
):
    # Save chunk
    chunk_path = f"temp/{file_id}/chunk_{chunk_number}"
    with open(chunk_path, 'wb') as f:
        f.write(await chunk.read())
    
    # Assemble when complete
    if chunk_number == total_chunks - 1:
        await assemble_file(file_id, total_chunks)
```

### Streaming Response
```python
from fastapi.responses import StreamingResponse

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    def iter_file():
        with open(f"files/{file_id}", 'rb') as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        iter_file(),
        media_type="audio/mpeg"
    )
```

## Monitoring Performance

### Backend Metrics
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        
        # Log slow queries
        if duration > 1.0:
            logger.warning(f"{func.__name__} took {duration:.2f}s")
        
        return result
    return wrapper

@measure_time
async def slow_operation():
    pass
```

### Frontend Metrics
```typescript
// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);

// Custom metrics
const startTime = performance.now();
await fetchData();
const duration = performance.now() - startTime;
console.log(`API call took ${duration}ms`);
```

## Performance Testing

### Load Testing
```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/audio

# Artillery
artillery quick --count 100 --num 10 http://localhost:8000/

# Locust
locust -f locustfile.py --host http://localhost:8000
```

### Profiling
```python
# Python profiler
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## Quick Wins Checklist

- [ ] Enable Gzip compression
- [ ] Add database indexes
- [ ] Implement response caching
- [ ] Use CDN for static assets
- [ ] Optimize images (WebP, compression)
- [ ] Enable HTTP/2
- [ ] Minify CSS/JS
- [ ] Lazy load images
- [ ] Use connection pooling
- [ ] Implement pagination
- [ ] Add rate limiting
- [ ] Use async/await consistently
- [ ] Cache API responses
- [ ] Optimize database queries
- [ ] Use production builds

## Performance Targets

### Frontend
- Lighthouse score: >90
- First Contentful Paint: <1s
- Time to Interactive: <3s
- Bundle size: <500KB
- Image optimization: WebP, lazy loading

### Backend
- API response time: <100ms (p95)
- Database queries: <50ms (p95)
- Throughput: >1000 req/s
- Error rate: <0.1%
- Uptime: >99.9%

### Infrastructure
- Server CPU: <70%
- Server Memory: <80%
- Database connections: <80% pool
- Redis memory: <80%
- Network latency: <50ms

---

**Status:** Optimization guidelines ready  
**Apply:** Incrementally based on profiling data  
**Measure:** Before and after each optimization
