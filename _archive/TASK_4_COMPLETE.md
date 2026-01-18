# Task 4: Background Tasks & Job Queue - COMPLETE ✅

## Overview
Built a complete Celery-based background task processing system with Redis as broker, supporting async audio analysis, batch processing, progress tracking, and monitoring.

## Components Created

### 1. Celery Core (`src/samplemind/core/tasks/`)

#### `celery_app.py` (94 lines)
- **Celery application configuration**
- Redis broker and result backend
- Task serialization: JSON
- Multiple queues with routing:
  - `default` - General tasks
  - `audio_processing` - Audio analysis tasks
  - `ai_analysis` - AI-specific tasks
  - `embeddings` - Vector embedding generation
- Task settings:
  - Time limits: 1 hour hard, 50 min soft
  - Task acknowledgement: late ACK for reliability
  - Result expiry: 24 hours
  - Progress tracking enabled
- Celery Beat schedule for periodic tasks
- Connection retry and pooling

#### `audio_tasks.py` (417 lines)
**Background task definitions:**

1. **`process_audio_analysis`**
   - Async audio file analysis
   - Progress updates (0% → 20% → 50% → 80% → 100%)
   - AudioEngine feature extraction
   - AI Manager analysis
   - Database persistence
   - Retry logic (3 attempts, 60s delay)
   - Returns: Analysis results with file_id, analysis_id, features, AI insights

2. **`batch_process_audio_files`**
   - Parallel processing of multiple files
   - Uses Celery groups for concurrency
   - Tracks success/failure counts
   - Updates batch status in database
   - Returns: Batch summary with results

3. **`generate_audio_embeddings`**
   - Creates vector embeddings from audio features
   - 128-dimensional normalized vectors
   - Stores in ChromaDB for similarity search
   - Extracts: tempo, key, spectral features
   - Returns: Embedding generation result

4. **`cleanup_old_results`**
   - Periodic task (runs hourly via Beat)
   - Cleans up results older than 30 days
   - Scheduled in celery_app beat_schedule

**CallbackTask base class:**
- on_success() - Log successful completion
- on_failure() - Log errors
- on_retry() - Log retry attempts

### 2. API Integration

#### `schemas/tasks.py` (76 lines)
**Request/Response schemas:**
- `TaskSubmitRequest` - Submit single task
- `BatchTaskSubmitRequest` - Submit batch of tasks
- `TaskStatusResponse` - Task status with progress
- `TaskSubmitResponse` - Task submission confirmation
- `TaskListResponse` - List of tasks
- `WorkerInfo` - Worker status info
- `WorkersStatusResponse` - All workers status
- `QueueStats` - Queue statistics
- `QueueStatsResponse` - All queues stats

#### `routes/tasks.py` (191 lines)
**API endpoints:**

1. **POST /api/v1/tasks/analyze**
   - Submit audio file for background analysis
   - Requires authentication
   - Returns task_id for tracking
   - Routes to `audio_processing` queue

2. **POST /api/v1/tasks/analyze/batch**
   - Submit multiple files for batch processing
   - Requires authentication
   - Parallel execution
   - Returns batch task_id

3. **GET /api/v1/tasks/{task_id}**
   - Get task status and result
   - Requires authentication
   - Returns: status (PENDING/STARTED/PROGRESS/SUCCESS/FAILURE)
   - Includes progress percentage and message
   - Returns result when completed

4. **GET /api/v1/tasks/workers/status**
   - Get Celery workers status
   - Lists all active workers
   - Shows active and processed task counts

5. **GET /api/v1/tasks/queues/stats**
   - Get queue statistics
   - Shows message counts and consumers
   - For all configured queues

### 3. Startup Scripts

#### `start_celery_worker.sh`
```bash
celery -A samplemind.core.tasks.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --queues=default,audio_processing,ai_analysis,embeddings
```

#### `start_celery_beat.sh`
```bash
celery -A samplemind.core.tasks.celery_app beat \
    --loglevel=info \
    --schedule=./data/celerybeat-schedule
```

#### `start_flower.sh`
```bash
celery -A samplemind.core.tasks.celery_app flower \
    --port=5555 \
    --persistent=True
```

### 4. Integration with FastAPI

Updated `main.py`:
- Import tasks router
- Register `/api/v1/tasks/*` endpoints
- Full integration with authentication

## Architecture

### Task Flow

```
1. User uploads audio file via API
   ↓
2. API submits task to Celery (process_audio_analysis)
   ↓
3. Task queued in Redis (audio_processing queue)
   ↓
4. Celery worker picks up task
   ↓
5. Worker loads audio → extracts features → runs AI analysis
   ↓
6. Progress updates: 0% → 20% → 50% → 80% → 100%
   ↓
7. Results saved to MongoDB
   ↓
8. Task marked as SUCCESS
   ↓
9. User polls GET /api/v1/tasks/{task_id} for status
   ↓
10. User retrieves analysis results
```

### Queue Routing

| Task | Queue | Exchange | Routing Key |
|------|-------|----------|-------------|
| process_audio_analysis | audio_processing | audio | audio.process |
| batch_process_audio_files | audio_processing | audio | audio.process |
| generate_audio_embeddings | embeddings | embeddings | embeddings.generate |
| Other tasks | default | default | default |

## Usage Examples

### 1. Start Services

```bash
# Terminal 1: Start API
./start_api.sh

# Terminal 2: Start Celery Worker
./start_celery_worker.sh

# Terminal 3: Start Celery Beat (optional)
./start_celery_beat.sh

# Terminal 4: Start Flower UI (optional)
./start_flower.sh
```

### 2. Submit Task via API

```bash
# Login first
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=SecurePass123" \
  | jq -r '.access_token')

# Submit analysis task
curl -X POST http://localhost:8000/api/v1/tasks/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "test-file-123",
    "file_path": "/path/to/audio.wav",
    "analysis_options": {"ai_provider": "google_ai"}
  }'

# Response:
{
  "task_id": "abc123-def456-ghi789",
  "status": "submitted",
  "message": "Audio analysis task submitted"
}
```

### 3. Check Task Status

```bash
TASK_ID="abc123-def456-ghi789"

curl -X GET http://localhost:8000/api/v1/tasks/$TASK_ID \
  -H "Authorization: Bearer $TOKEN"

# Response (in progress):
{
  "task_id": "abc123-def456-ghi789",
  "status": "PROGRESS",
  "progress": 50,
  "progress_message": "Running AI analysis...",
  "result": null
}

# Response (completed):
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "progress": 100,
  "result": {
    "file_id": "test-file-123",
    "analysis_id": "analysis_test-file-123_1234567890",
    "audio_features": {...},
    "ai_analysis": {...},
    "status": "completed",
    "completed_at": "2024-01-01T12:00:00"
  }
}
```

### 4. Submit Batch Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/analyze/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch-001",
    "file_infos": [
      {"file_id": "file1", "file_path": "/path/to/file1.wav"},
      {"file_id": "file2", "file_path": "/path/to/file2.wav"},
      {"file_id": "file3", "file_path": "/path/to/file3.wav"}
    ]
  }'
```

### 5. Monitor Workers

```bash
# Via API
curl -X GET http://localhost:8000/api/v1/tasks/workers/status \
  -H "Authorization: Bearer $TOKEN"

# Via Flower UI
open http://localhost:5555
```

### 6. Check Queue Stats

```bash
curl -X GET http://localhost:8000/api/v1/tasks/queues/stats \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "queues": [
    {"name": "default", "messages": 0, "consumers": 1},
    {"name": "audio_processing", "messages": 5, "consumers": 4},
    {"name": "embeddings", "messages": 2, "consumers": 1}
  ],
  "total_queues": 4
}
```

## Configuration

Add to `.env`:
```bash
# Celery/Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Task settings
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3000
```

## Monitoring with Flower

Flower provides:
- Real-time task monitoring
- Worker status and stats
- Task history and details
- Task retry/revoke controls
- Broker stats
- Web UI at http://localhost:5555

## Production Considerations

### Scaling Workers

```bash
# Run multiple workers
celery -A samplemind.core.tasks.celery_app worker --concurrency=8

# Run specialized workers
celery -A samplemind.core.tasks.celery_app worker --queues=audio_processing
celery -A samplemind.core.tasks.celery_app worker --queues=embeddings
```

### Supervisord Configuration

```ini
[program:samplemind-celery-worker]
command=/path/to/venv/bin/celery -A samplemind.core.tasks.celery_app worker --loglevel=info
directory=/path/to/project
user=samplemind
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/samplemind/celery-worker.log
```

### Docker Compose

```yaml
services:
  celery-worker:
    build: .
    command: celery -A samplemind.core.tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
      - mongodb
    environment:
      - REDIS_URL=redis://redis:6379/0
```

## Error Handling

- **Automatic retries**: 3 attempts with 60s delay
- **Soft time limit**: 50 minutes (SoftTimeLimitExceeded)
- **Hard time limit**: 1 hour (task killed)
- **Late ACK**: Tasks requeued if worker dies
- **Exponential backoff**: Available via retry decorator

## Performance Tuning

- **Concurrency**: Adjust based on CPU cores
- **Prefetch multiplier**: Set to 1 for long-running tasks
- **Max tasks per child**: Prevents memory leaks
- **Result expiration**: Keep results for 24 hours
- **Connection pooling**: Max 10 broker connections

## Files Created/Modified

### Created:
- `src/samplemind/core/tasks/__init__.py` (18 lines)
- `src/samplemind/core/tasks/celery_app.py` (94 lines)
- `src/samplemind/core/tasks/audio_tasks.py` (417 lines)
- `src/samplemind/interfaces/api/schemas/tasks.py` (76 lines)
- `src/samplemind/interfaces/api/routes/tasks.py` (191 lines)
- `start_celery_worker.sh` (32 lines)
- `start_celery_beat.sh` (22 lines)
- `start_flower.sh` (28 lines)
- `TASK_4_COMPLETE.md` (this file)

### Modified:
- `src/samplemind/interfaces/api/main.py` - Added tasks router

## Dependencies Added

```
celery[redis]==5.5.3      # Distributed task queue
redis==5.2.1               # Redis client (broker)
flower==2.0.1              # Monitoring UI
kombu==5.5.4               # Messaging library
billiard==4.2.2            # Process pool
vine==5.1.0                # Promises/futures
```

## Next Steps

With Task 4 complete, the backend now has:
- ✅ Task 1: FastAPI Backend Server
- ✅ Task 2: Database Layer
- ✅ Task 3: Authentication & Authorization
- ✅ Task 4: Background Tasks & Job Queue

**Ready for Task 5: React/Next.js Frontend**

The background task system enables:
- Async audio processing without blocking API
- Scalable parallel processing
- Progress tracking for long-running tasks
- Reliable task execution with retries
- Production-ready monitoring

## Testing Checklist

- [x] Celery worker starts successfully
- [x] Tasks route to correct queues
- [x] Progress tracking works
- [x] Tasks complete and store results
- [x] Retry logic activates on failure
- [x] Batch processing runs in parallel
- [x] Embeddings generated and stored
- [x] API endpoints return task status
- [x] Worker monitoring endpoints work
- [x] Queue stats accessible
- [x] Flower UI accessible
- [x] Beat scheduler works

**Task 4: Background Tasks & Job Queue - 100% COMPLETE** ✅
