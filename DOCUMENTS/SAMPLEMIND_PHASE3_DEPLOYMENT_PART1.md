# 🚀 SAMPLEMIND AI - PRODUCTION DEPLOYMENT
## Complete Guide to Cloud Infrastructure, Docker, CI/CD, and Monitoring

---

## 📚 2026 Q2-Q4: DEPLOYING TO PRODUCTION

### What is Deployment?

**Understanding Development vs Production:**

```
Development (Your Laptop):
- Works on your machine
- Easy to debug
- Can break things safely
- Fast iteration
- Limited users (just you)

Production (The Cloud):
- Works for thousands of users
- Must be reliable (99.9% uptime)
- Can't easily debug
- Changes require caution
- Real money at stake
```

**The Deployment Challenge:**

```
"It works on my machine!" ← Famous last words

Problems when deploying:
- Different operating systems
- Missing dependencies
- Configuration differences
- Environment variables
- Database versions
- Port conflicts

Solution: Containerization (Docker)
```

---

## 🐳 Docker (Containerization Explained)

### What is Docker?

**Understanding Containers:**

```
Traditional Deployment:
Server → Install Python → Install packages → Run app
Problem: "It worked on my laptop!"

Docker Container:
Server → Run container (everything included)
Benefit: Guaranteed to work everywhere
```

**Shipping Container Analogy:**

```
Without Docker (Traditional):
🚢 Ship carries: Boxes, bags, barrels, crates
   - Different sizes
   - Hard to stack
   - Inefficient

With Docker (Containers):
🚢 Ship carries: Standard containers 📦📦📦
   - Same size
   - Easy to stack
   - Efficient
   - Ship, train, truck all work the same

Docker does this for software!
```

**Docker Components:**

```
1. IMAGE (Recipe):
   - Blueprint for container
   - Like a frozen meal (not running)
   - Immutable (doesn't change)

2. CONTAINER (Running Instance):
   - Image that's running
   - Like heated-up meal (active)
   - Can have many from one image

3. DOCKERFILE (Recipe File):
   - Instructions to build image
   - Text file with commands
   - Version controlled
```

---

### Creating Dockerfiles

**Backend Dockerfile:**

```dockerfile
# backend/Dockerfile

# === STAGE 1: Builder ===
# This stage installs dependencies
FROM python:3.11-slim as builder

# CONCEPT: Multi-stage builds
# Why?
# - Smaller final image
# - Faster builds
# - More secure (fewer tools in production)
# 
# Stage 1: Install everything (large)
# Stage 2: Copy only what's needed (small)

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

"""
CONCEPT: Why install system packages?

gcc/g++: Compile Python packages with C extensions
libsndfile1: Audio file reading (for librosa)
ffmpeg: Audio processing/conversion

rm -rf /var/lib/apt/lists/*:
- Deletes package cache
- Reduces image size
- Good practice
"""

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

"""
CONCEPT: Why --no-dev?

Development dependencies not needed in production:
- pytest (testing)
- black (formatting)
- mypy (type checking)

Production only needs:
- FastAPI (server)
- librosa (audio processing)
- torch (AI models)

Smaller image, faster deploys!
"""

# === STAGE 2: Production ===
FROM python:3.11-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

"""
CONCEPT: Security - Non-root User

Why not run as root?
- If app compromised, attacker has root access
- Can modify entire system
- Security best practice: least privilege

With appuser:
- Limited permissions
- Can't modify system
- Safer if breached
"""

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

"""
--chown=appuser:appuser
- Sets file ownership
- Files owned by appuser, not root
- Security best practice
"""

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

"""
EXPOSE 8000
- Documents which port app uses
- Doesn't actually publish port
- Like a label, not a function
"""

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

"""
CONCEPT: Health Checks

Docker periodically checks if app is healthy:
- interval=30s: Check every 30 seconds
- timeout=3s: Wait max 3 seconds for response
- start-period=40s: Wait 40s before first check (startup time)
- retries=3: Fail after 3 failed checks

If unhealthy:
- Docker can restart container
- Load balancer can route traffic elsewhere
- Alerts can be triggered
"""

# Command to run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

"""
CONCEPT: CMD vs ENTRYPOINT

CMD: Default command (can be overridden)
ENTRYPOINT: Always runs (harder to override)

We use CMD for flexibility:
- Production: uvicorn main:app --host 0.0.0.0
- Debug: docker run ... /bin/bash (override)
"""
```

**Frontend Dockerfile:**

```dockerfile
# frontend/Dockerfile

# === STAGE 1: Dependencies ===
FROM node:20-alpine AS deps

# CONCEPT: Alpine Linux
# 
# Regular node image: ~900 MB
# Alpine node image: ~170 MB
# 
# Alpine:
# - Minimal Linux distribution
# - Much smaller
# - Still has everything Node needs
# 
# Perfect for Docker!

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci --only=production

"""
CONCEPT: npm ci vs npm install

npm install:
- Uses package-lock.json if available
- Can modify package-lock.json
- Slower

npm ci (Continuous Integration):
- Requires package-lock.json
- Never modifies it
- Faster
- Deterministic (same result every time)
- Perfect for production!
"""

# === STAGE 2: Builder ===
FROM node:20-alpine AS builder

WORKDIR /app

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build Next.js
RUN npm run build

"""
Next.js build process:
1. Compiles TypeScript
2. Optimizes images
3. Bundles JavaScript
4. Pre-renders pages
5. Creates production build in .next/

Output is optimized for production:
- Minified JavaScript
- Tree-shaken (unused code removed)
- Code-split (smaller chunks)
- Image optimization
"""

# === STAGE 3: Production ===
FROM node:20-alpine AS runner

WORKDIR /app

# Environment
ENV NODE_ENV production

"""
NODE_ENV=production tells Next.js:
- Don't include dev dependencies
- Enable performance optimizations
- Disable source maps
- Smaller bundle size
"""

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy necessary files
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

"""
Next.js standalone mode:
- Copies only necessary files
- Minimal dependencies
- Smaller final image
- Faster startup

Enabled in next.config.js:
output: 'standalone'
"""

# Switch to non-root user
USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Health check
HEALTHCHECK CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

CMD ["node", "server.js"]
```

---

### Docker Compose (Orchestrating Multiple Containers)

**What is Docker Compose?**

```
Problem:
- Backend needs database
- Frontend needs backend
- Need to start everything in right order
- Need to connect them together

Solution: Docker Compose
- Define all services in one file
- Start everything with one command
- Automatic networking
- Manages dependencies
```

**Complete docker-compose.yml:**

```yaml
# docker-compose.yml

version: '3.8'

services:
  # === DATABASE ===
  postgres:
    image: postgres:15-alpine
    """
    Using official PostgreSQL image
    - Version 15 (latest stable)
    - Alpine variant (smaller)
    """
    
    environment:
      POSTGRES_DB: samplemind
      POSTGRES_USER: samplemind
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      """
      Environment variables configure PostgreSQL
      ${DB_PASSWORD} comes from .env file
      """
    
    volumes:
      - postgres_data:/var/lib/postgresql/data
      """
      CONCEPT: Volumes (Persistent Storage)
      
      Problem:
      - Container data deleted when container stops
      - Database would lose all data!
      
      Solution: Volumes
      - Data stored on host machine
      - Persists after container stops
      - Can be backed up
      - Shared between containers
      
      /var/lib/postgresql/data:
      - PostgreSQL's data directory
      - Stores all tables, indexes, etc.
      """
    
    ports:
      - "5432:5432"
      """
      Port mapping: host:container
      - 5432 on host → 5432 in container
      - Allows external connections
      - First number can be different
      """
    
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U samplemind"]
      interval: 10s
      timeout: 5s
      retries: 5
      """
      PostgreSQL health check
      - pg_isready: PostgreSQL utility
      - Returns 0 if ready
      - Ensures DB is ready before app starts
      """
    
    networks:
      - samplemind-network
  
  # === REDIS (Caching) ===
  redis:
    image: redis:7-alpine
    
    command: redis-server --appendonly yes
    """
    --appendonly yes:
    - Enables persistence
    - Redis writes changes to disk
    - Survives restarts
    - Trade-off: Slightly slower, but safer
    """
    
    volumes:
      - redis_data:/data
    
    ports:
      - "6379:6379"
    
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    
    networks:
      - samplemind-network
  
  # === BACKEND ===
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      """
      Build from Dockerfile instead of using image
      - context: Directory with code
      - dockerfile: Which Dockerfile to use
      """
    
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      """
      CONCEPT: Dependencies
      
      Backend needs database to be ready
      - depends_on: Wait for postgres & redis
      - condition: service_healthy: Wait until healthy
      
      Start order:
      1. PostgreSQL starts, becomes healthy
      2. Redis starts, becomes healthy
      3. Backend starts
      
      Prevents connection errors!
      """
    
    environment:
      DATABASE_URL: postgresql://samplemind:${DB_PASSWORD}@postgres:5432/samplemind
      REDIS_URL: redis://redis:6379
      GOOGLE_AI_API_KEY: ${GOOGLE_AI_API_KEY}
      """
      Connection strings use service names:
      - @postgres: Docker DNS resolves to postgres container
      - @redis: Resolves to redis container
      
      No hardcoded IPs!
      Docker handles networking automatically
      """
    
    volumes:
      - ./backend:/app
      - uploaded_files:/app/uploads
      """
      Development convenience:
      - Mount source code
      - Changes reflect immediately
      - No rebuild needed
      
      Production:
      - Remove code mount
      - Use baked-in code from build
      """
    
    ports:
      - "8000:8000"
    
    networks:
      - samplemind-network
  
  # === FRONTEND ===
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    
    depends_on:
      - backend
    
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
      """
      Frontend can reach backend:
      - http://backend:8000 (internal)
      - Docker networking magic!
      """
    
    ports:
      - "3000:3000"
    
    networks:
      - samplemind-network
  
  # === NGINX (Reverse Proxy) ===
  nginx:
    image: nginx:alpine
    
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      """
      :ro = read-only
      - Prevents container from modifying config
      - Security best practice
      """
    
    ports:
      - "80:80"
      - "443:443"
      """
      80: HTTP
      443: HTTPS (SSL/TLS)
      """
    
    depends_on:
      - frontend
      - backend
    
    networks:
      - samplemind-network

# === NETWORKS ===
networks:
  samplemind-network:
    driver: bridge
    """
    CONCEPT: Docker Networks
    
    Creates isolated network for services:
    - Services can talk to each other
    - Use service names as hostnames
    - Isolated from other containers
    - Secure by default
    
    bridge driver:
    - Default network type
    - Allows container-to-container communication
    - Perfect for single-host deployments
    """

# === VOLUMES ===
volumes:
  postgres_data:
    """Persists PostgreSQL data"""
  
  redis_data:
    """Persists Redis data"""
  
  uploaded_files:
    """Persists uploaded audio files"""

"""
CONCEPT: Named Volumes

Docker manages these volumes:
- Location: /var/lib/docker/volumes/
- Automatic cleanup available
- Easy backups
- Can be shared

Alternative: Bind mounts
- volumes:
    - ./local/path:/container/path
- Use for development
- Named volumes better for production
"""
```

**Starting Everything:**

```bash
# Start all services
docker-compose up -d

"""
-d flag (detached mode):
- Runs in background
- Doesn't lock terminal
- Logs available with: docker-compose logs
"""

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

"""
-f flag (follow):
- Streams logs in real-time
- Like tail -f
- Ctrl+C to exit
"""

# Stop everything
docker-compose down

# Stop and remove volumes (CAREFUL!)
docker-compose down -v
```

---

## ☁️ Cloud Deployment (Google Cloud Platform)

### Why Google Cloud?

```
Google Cloud Platform (GCP) advantages:
✅ Native Google AI integration (Gemini API)
✅ Generous free tier
✅ Global network (fast everywhere)
✅ Kubernetes origin (invented by Google)
✅ Advanced AI/ML tools
✅ Automatic scaling
✅ 99.95% SLA (very reliable)

Cost comparison (approximate):
AWS: $150-200/month
Azure: $140-180/month
GCP: $120-160/month (10-20% cheaper)
```

### GCP Services We'll Use:

```
1. Cloud Run:
   - Serverless containers
   - Auto-scaling (0 to 1000+ instances)
   - Pay per use (idle = free)
   - Perfect for SampleMind!

2. Cloud SQL:
   - Managed PostgreSQL
   - Automatic backups
   - High availability
   - No maintenance

3. Cloud Storage:
   - Object storage for audio files
   - Cheap ($0.02/GB/month)
   - CDN integration
   - 11 nines durability (99.999999999%)

4. Cloud Build:
   - CI/CD pipeline
   - Automatic deployments
   - Docker image building

5. Cloud Monitoring:
   - Logs, metrics, alerts
   - Performance tracking
   - Error detection
```

---

### Cloud Run Deployment

**What is Cloud Run?**

```
Cloud Run = Serverless + Containers

Traditional server:
- Runs 24/7
- Pay even when idle
- Manual scaling
- Maintenance required

Cloud Run:
- Runs when needed
- Pay only for requests
- Automatic scaling
- Zero maintenance

Perfect for:
- APIs (FastAPI)
- Web apps (Next.js)
- Batch jobs
- Microservices
```

**Deploying Backend to Cloud Run:**

```bash
# 1. Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# 2. Login
gcloud auth login

# 3. Set project
gcloud config set project samplemind-ai

# 4. Enable required APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    storage.googleapis.com

"""
Why enable APIs?
- GCP features disabled by default
- Only pay for what you use
- Must explicitly enable
- Security/cost control
"""

# 5. Build and deploy backend
gcloud run deploy samplemind-backend \
    --source ./backend \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=postgresql://...,GOOGLE_AI_API_KEY=..." \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 0

"""
PARAMETERS EXPLAINED:

--source ./backend:
- Builds from Dockerfile in backend/
- Automatic image creation

--region us-central1:
- Iowa, USA
- Choose closest to users
- Available: us, europe, asia

--platform managed:
- Fully managed (vs Kubernetes)
- Easiest option

--allow-unauthenticated:
- Public access
- For authenticated: remove this flag

--set-env-vars:
- Environment variables
- Secrets better in Secret Manager

--memory 2Gi:
- 2 gigabytes RAM
- AI models need memory
- Options: 256Mi, 512Mi, 1Gi, 2Gi, 4Gi, 8Gi

--cpu 2:
- 2 vCPUs
- Faster processing
- Options: 1, 2, 4, 8

--max-instances 10:
- Scale up to 10 containers
- Prevents runaway costs
- Increase for viral growth

--min-instances 0:
- Scale to zero when idle
- Save money
- Cold starts acceptable?
- Set to 1 for always-on
"""

# 6. Get URL
gcloud run services describe samplemind-backend \
    --region us-central1 \
    --format 'value(status.url)'

# Example output:
# https://samplemind-backend-abc123-uc.a.run.app
```

**Deploying Frontend to Cloud Run:**

```bash
gcloud run deploy samplemind-frontend \
    --source ./frontend \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://samplemind-backend-abc123-uc.a.run.app" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 20 \
    --min-instances 1

"""
Frontend differences:
- Less memory (1Gi vs 2Gi)
- Fewer CPUs (static serving)
- More instances (handle traffic)
- Min 1 instance (always responsive)
"""
```

---

## 🔄 CI/CD Pipeline (Continuous Integration/Deployment)

### What is CI/CD?

```
Traditional deployment:
1. Write code on laptop
2. Test manually
3. Build manually
4. Deploy manually
5. Hope it works
Problem: Slow, error-prone, scary

CI/CD (Automated):
1. Push code to GitHub
2. Automatic tests run
3. Automatic build
4. Automatic deployment
5. Guaranteed working
Benefit: Fast, reliable, confident
```

**CI/CD Pipeline Flow:**

```
Developer pushes code
        ↓
GitHub triggers workflow
        ↓
Run tests
        ├─ FAIL → Stop, notify developer
        └─ PASS → Continue
        ↓
Build Docker image
        ↓
Push to Container Registry
        ↓
Deploy to Cloud Run
        ↓
Health check
        ├─ FAIL → Rollback to previous version
        └─ PASS → Done!
        ↓
Notify team (Slack/Email)
```

**GitHub Actions Workflow:**

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches:
      - main
  """
  Trigger: When code pushed to main branch
  
  Alternative triggers:
  - pull_request: On PR creation
  - schedule: Cron job (periodic)
  - workflow_dispatch: Manual trigger
  """

jobs:
  test:
    runs-on: ubuntu-latest
    """
    runs-on: Which machine to use
    - ubuntu-latest: Linux (most common)
    - windows-latest: Windows
    - macos-latest: macOS
    """
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        """
        Clones repository
        - Gets your code
        - Like: git clone
        """
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests
        run: |
          poetry run pytest
          """
          If tests fail:
          - Workflow stops
          - No deployment
          - Email notification
          
          Prevents broken code in production!
          """
      
      - name: Run linter
        run: |
          poetry run black --check .
          poetry run mypy .
          """
          Code quality checks:
          - black: Formatting
          - mypy: Type checking
          
          Ensures code quality
          """
  
  build-and-deploy:
    needs: test
    """
    CONCEPT: Job Dependencies
    
    needs: test
    - Only runs if 'test' job passes
    - Sequential execution
    - Saves time/money (no deploy if tests fail)
    """
    
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          """
          CONCEPT: Secrets Management
          
          secrets.GCP_SA_KEY:
          - Stored in GitHub Secrets
          - Not in code (secure)
          - Encrypted at rest
          - Only available during workflow
          
          To add secrets:
          Settings → Secrets → New repository secret
          """
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
      
      - name: Build and push Docker image
        run: |
          gcloud builds submit \
            --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/samplemind-backend:${{ github.sha }} \
            backend/
          """
          gcr.io = Google Container Registry
          ${{ github.sha }} = Commit hash (unique)
          
          Every build tagged with:
          - Latest commit
          - Enables rollbacks
          - Traceability
          """
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy samplemind-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/samplemind-backend:${{ github.sha }} \
            --region us-central1 \
            --platform managed
      
      - name: Notify Slack
        if: success()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Deployment successful!"
            }
        """
        if: success()
        - Only runs if previous steps succeeded
        
        Alternative conditions:
        - if: failure() (only on failure)
        - if: always() (always run)
        """
```

---

This completes Phase 3! Continuing with monitoring, security, and final production checklist... 🚀
