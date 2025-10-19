# 🚀 SAMPLEMIND AI - REPLIT AGENT 3 QUICK REFERENCE GUIDE

## Essential Commands & Workflows for Rapid Development

---

## 🎯 PROJECT INITIALIZATION

### Backend Setup (FastAPI)
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install fastapi[all]==0.119.1 uvicorn[standard]==0.30.0
pip install motor pymongo redis celery
pip install librosa essentia-tensorflow pydub soundfile
pip install torch torchvision torchaudio transformers
pip install chromadb sentence-transformers
pip install python-jose[cryptography] passlib[bcrypt]
pip install boto3 python-multipart aiofiles

# Save requirements
pip freeze > requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (Next.js 15)
```bash
# Create Next.js project
npx create-next-app@latest samplemind-web \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

cd samplemind-web

# Install dependencies
npm install zustand @tanstack/react-query axios
npm install three @react-three/fiber @react-three/drei
npm install framer-motion clsx tailwind-merge
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-tabs
npm install react-hook-form zod @hookform/resolvers
npm install tone howler.js wavesurfer.js

# Run development server
npm run dev
```

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0

  mongo:
    image: mongo:8.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7.4-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery_worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - redis
      - mongo
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379

  celery_beat:
    build: ./backend
    command: celery -A tasks beat --loglevel=info
    depends_on:
      - redis

volumes:
  mongo_data:
  redis_data:
```

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

---

## 📁 PROJECT STRUCTURE

### Backend Structure
```
samplemind-backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition
├── .env                    # Environment variables
│
├── api/
│   ├── routes/
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── audio.py       # Audio upload/analysis
│   │   ├── search.py      # Search & similarity
│   │   └── users.py       # User management
│   └── dependencies.py    # Route dependencies
│
├── core/
│   ├── config.py          # Configuration management
│   ├── database.py        # MongoDB connection
│   ├── security.py        # JWT & password hashing
│   └── cache.py           # Redis caching
│
├── models/
│   ├── user.py            # User model
│   ├── audio.py           # Audio file model
│   └── playlist.py        # Playlist model
│
├── services/
│   ├── audio_processor.py # Audio analysis service
│   ├── ai_manager.py      # AI model orchestration
│   ├── storage.py         # S3/file storage
│   └── embeddings.py      # Vector embeddings
│
├── ml/
│   ├── models/            # AI model implementations
│   ├── inference.py       # Model inference
│   └── training.py        # Model training scripts
│
├── tasks/
│   ├── celery_app.py      # Celery configuration
│   └── audio_tasks.py     # Background tasks
│
├── utils/
│   ├── logger.py          # Logging utilities
│   ├── validators.py      # Input validation
│   └── helpers.py         # Helper functions
│
└── tests/
    ├── test_api.py        # API tests
    ├── test_audio.py      # Audio processing tests
    └── test_models.py     # Model tests
```

### Frontend Structure
```
samplemind-web/
├── package.json           # Node dependencies
├── next.config.js         # Next.js configuration
├── tailwind.config.ts     # Tailwind config
├── tsconfig.json          # TypeScript config
│
├── src/
│   ├── app/
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx       # Home page
│   │   ├── globals.css    # Global styles
│   │   │
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   │
│   │   ├── library/
│   │   │   └── page.tsx
│   │   │
│   │   └── analyze/
│   │       └── page.tsx
│   │
│   ├── components/
│   │   ├── ui/            # Reusable UI components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── modal.tsx
│   │   │
│   │   ├── layout/        # Layout components
│   │   │   ├── navbar.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── footer.tsx
│   │   │
│   │   ├── audio/         # Audio components
│   │   │   ├── waveform.tsx
│   │   │   ├── player.tsx
│   │   │   └── uploader.tsx
│   │   │
│   │   └── visualization/ # 3D visualizations
│   │       ├── spectral-waterfall.tsx
│   │       └── harmonic-constellation.tsx
│   │
│   ├── lib/
│   │   ├── api/           # API client
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   └── audio.ts
│   │   │
│   │   ├── hooks/         # Custom React hooks
│   │   ├── utils/         # Utility functions
│   │   └── store/         # Zustand stores
│   │
│   └── styles/
│       ├── theme.css      # CSS variables
│       └── animations.css # Custom animations
```

---

## 🔑 KEY API ENDPOINTS

### Authentication
```typescript
// Register
POST /api/v1/auth/register
Body: { email, password, name }
Response: { user, access_token, refresh_token }

// Login
POST /api/v1/auth/login
Body: { email, password }
Response: { access_token, refresh_token }

// Refresh Token
POST /api/v1/auth/refresh
Body: { refresh_token }
Response: { access_token }

// Get Current User
GET /api/v1/auth/me
Headers: { Authorization: Bearer <token> }
Response: { user }
```

### Audio
```typescript
// Upload Audio
POST /api/v1/audio/upload
Headers: { Authorization: Bearer <token> }
Body: FormData { file }
Response: { file_id, task_id, status }

// Get Analysis
GET /api/v1/audio/{file_id}/analysis
Headers: { Authorization: Bearer <token> }
Response: { bpm, key, genre, mood, instruments }

// Search Similar
POST /api/v1/audio/{file_id}/similar
Headers: { Authorization: Bearer <token> }
Body: { limit: 20 }
Response: { similar_samples: [...] }

// Download Audio
GET /api/v1/audio/{file_id}/download
Headers: { Authorization: Bearer <token> }
Response: Audio file (binary)
```

### Search
```typescript
// Text Search
GET /api/v1/search?q=<query>&limit=50
Headers: { Authorization: Bearer <token> }
Response: { results: [...] }

// Filter Search
POST /api/v1/search/filter
Body: { 
  genre: ["electronic"], 
  bpm_min: 120, 
  bpm_max: 140,
  key: "C",
  mood: ["energetic"]
}
Response: { results: [...] }
```

---

## 🧠 AI MODEL INTEGRATION EXAMPLES

### BPM Detection (Librosa)
```python
import librosa

def detect_bpm(audio_path: str) -> float:
    """Detect BPM using beat tracking."""
    y, sr = librosa.load(audio_path)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(tempo)
```

### Key Detection (Librosa)
```python
import librosa
import numpy as np

def detect_key(audio_path: str) -> str:
    """Detect musical key using chroma features."""
    y, sr = librosa.load(audio_path)
    
    # Compute chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Average across time
    chroma_mean = np.mean(chroma, axis=1)
    
    # Find dominant key
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key_index = np.argmax(chroma_mean)
    
    return key_names[key_index]
```

### Genre Classification (BEATs)
```python
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import torch

class GenreClassifier:
    def __init__(self):
        self.model_name = "microsoft/beats-base-ft-audioset"
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = AutoModelForAudioClassification.from_pretrained(self.model_name)
    
    def classify(self, audio_path: str) -> dict:
        # Load audio
        import librosa
        y, sr = librosa.load(audio_path, sr=16000)
        
        # Extract features
        inputs = self.feature_extractor(y, sampling_rate=sr, return_tensors="pt")
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get top 5 predictions
        top5_idx = torch.topk(predictions, 5).indices[0].tolist()
        top5_scores = torch.topk(predictions, 5).values[0].tolist()
        
        results = []
        for idx, score in zip(top5_idx, top5_scores):
            label = self.model.config.id2label[idx]
            results.append({"label": label, "score": float(score)})
        
        return results
```

### Audio Embedding (OpenL3)
```python
import openl3
import soundfile as sf

def generate_embedding(audio_path: str) -> np.ndarray:
    """Generate audio embedding using OpenL3."""
    audio, sr = sf.read(audio_path)
    
    # Generate embedding
    emb, ts = openl3.get_audio_embedding(
        audio, 
        sr,
        content_type="music",
        embedding_size=512
    )
    
    # Average across time
    embedding = emb.mean(axis=0)
    
    return embedding
```

---

## 🎨 FRONTEND COMPONENT EXAMPLES

### Glassmorphic Button
```tsx
// components/ui/button.tsx
import { forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        default: "bg-neon-cyan text-black hover:shadow-neon",
        glass: "glass-card text-white hover:border-neon-cyan",
        outline: "border-2 border-neon-cyan text-neon-cyan hover:bg-neon-cyan hover:text-black",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        md: "h-11 px-6 text-base",
        lg: "h-13 px-8 text-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### Waveform Visualizer
```tsx
// components/audio/waveform.tsx
'use client'

import { useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

export function Waveform({ audioUrl }: { audioUrl: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const wavesurferRef = useRef<WaveSurfer | null>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Initialize WaveSurfer
    wavesurferRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: 'rgba(0, 245, 255, 0.5)',
      progressColor: '#00F5FF',
      cursorColor: '#B026FF',
      barWidth: 2,
      barGap: 1,
      height: 128,
      normalize: true,
      backend: 'WebAudio',
    })

    // Load audio
    wavesurferRef.current.load(audioUrl)

    return () => {
      wavesurferRef.current?.destroy()
    }
  }, [audioUrl])

  return (
    <div className="glass-card p-4">
      <div ref={containerRef} className="w-full" />
      <div className="flex gap-2 mt-4">
        <button
          onClick={() => wavesurferRef.current?.playPause()}
          className="glass-card px-4 py-2 hover:border-neon-cyan"
        >
          Play/Pause
        </button>
      </div>
    </div>
  )
}
```

### 3D Spectral Waterfall
```tsx
// components/visualization/spectral-waterfall.tsx
'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

export function SpectralWaterfall({ fftData }: { fftData: Float32Array }) {
  const mountRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const geometryRef = useRef<THREE.BufferGeometry | null>(null)

  useEffect(() => {
    if (!mountRef.current) return

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0a0f)
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(
      75,
      mountRef.current.clientWidth / mountRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.set(0, 5, 10)

    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight)
    mountRef.current.appendChild(renderer.domElement)

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true

    // Create geometry
    const geometry = new THREE.BufferGeometry()
    const positions = new Float32Array(fftData.length * 3 * 100) // 100 time slices
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    geometryRef.current = geometry

    // Material
    const material = new THREE.LineBasicMaterial({
      color: 0x00f5ff,
      transparent: true,
      opacity: 0.8
    })

    const line = new THREE.Line(geometry, material)
    scene.add(line)

    // Animation loop
    function animate() {
      requestAnimationFrame(animate)
      controls.update()
      renderer.render(scene, camera)
    }
    animate()

    // Cleanup
    return () => {
      renderer.dispose()
      mountRef.current?.removeChild(renderer.domElement)
    }
  }, [])

  // Update FFT data
  useEffect(() => {
    if (!geometryRef.current) return

    const positions = geometryRef.current.attributes.position.array as Float32Array

    // Shift existing data back
    for (let i = positions.length - 3; i >= fftData.length * 3; i -= 3) {
      positions[i] = positions[i - fftData.length * 3]
      positions[i + 1] = positions[i - fftData.length * 3 + 1]
      positions[i + 2] = positions[i - fftData.length * 3 + 2] + 0.1
    }

    // Add new FFT data
    for (let i = 0; i < fftData.length; i++) {
      positions[i * 3] = i * 0.1 - fftData.length * 0.05
      positions[i * 3 + 1] = fftData[i] * 10
      positions[i * 3 + 2] = 0
    }

    geometryRef.current.attributes.position.needsUpdate = true
  }, [fftData])

  return <div ref={mountRef} className="w-full h-[600px] glass-card" />
}
```

---

## 🐛 DEBUGGING TIPS

### Backend Debugging
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Print request details
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    response = await call_next(request)
    return response

# Use pdb for breakpoints
import pdb; pdb.set_trace()
```

### Frontend Debugging
```typescript
// Console logging
console.log('Data:', data)
console.table(arrayData)
console.group('API Request')
console.log('URL:', url)
console.log('Method:', method)
console.groupEnd()

// React DevTools
// Install: https://react.dev/learn/react-developer-tools

// Network inspection
// Chrome DevTools -> Network tab
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### Backend
```python
# Use async/await
async def process_audio(file: UploadFile):
    result = await heavy_computation(file)
    return result

# Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=1000)
def compute_embedding(audio_hash: str):
    # Expensive operation
    pass

# Batch processing
async def process_batch(files: List[UploadFile]):
    tasks = [process_audio(f) for f in files]
    return await asyncio.gather(*tasks)
```

### Frontend
```typescript
// Lazy load components
const HeavyComponent = lazy(() => import('./HeavyComponent'))

// Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data)
}, [data])

// Debounce search
const debouncedSearch = useDebounce(searchTerm, 500)
```

---

## 📊 MONITORING & METRICS

### Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "mongodb": await check_mongodb(),
            "redis": await check_redis(),
            "celery": await check_celery()
        }
    }
```

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🚀 DEPLOYMENT

### Production Checklist
- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] SSL/TLS certificates active
- [ ] CDN configured
- [ ] Monitoring dashboards set up
- [ ] Error tracking enabled (Sentry)
- [ ] Load balancer configured
- [ ] Auto-scaling rules defined
- [ ] CI/CD pipeline active
- [ ] Security audit completed

### Common Issues & Solutions

**Issue:** MongoDB connection timeout  
**Solution:** Check connection string, firewall rules, network connectivity

**Issue:** Redis out of memory  
**Solution:** Increase memory limit, enable eviction policy, clear old cache

**Issue:** Slow API responses  
**Solution:** Add caching, optimize queries, use connection pooling

**Issue:** High CPU usage  
**Solution:** Profile code, optimize algorithms, use async operations

---

## 📞 QUICK SUPPORT

**Documentation:** https://docs.samplemind.ai  
**GitHub Issues:** https://github.com/samplemind/issues  
**Discord:** https://discord.gg/samplemind  
**Email:** support@samplemind.ai  

---

*This quick reference guide is meant to be your go-to resource during development. Keep it handy!*
