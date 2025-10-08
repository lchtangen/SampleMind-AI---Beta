# Database Schema Documentation 💾

## Table of Contents
- [Database Overview](#database-overview)
- [MongoDB Collections](#mongodb-collections)
- [Redis Key Patterns](#redis-key-patterns)
- [ChromaDB Vector Storage](#chromadb-vector-storage)
- [Index Strategies](#index-strategies)
- [Data Relationships](#data-relationships)
- [Migration Guide](#migration-guide)
- [Backup & Restore](#backup--restore)

---

## Database Overview

SampleMind AI v6 uses a **multi-database architecture** optimized for different data types and access patterns.

### Database Stack

```
┌──────────────────────────────────────────────────────┐
│              Database Architecture                    │
├──────────────────────────────────────────────────────┤
│                                                       │
│  MongoDB (Primary Database)                          │
│  ┌────────────────────────────────────────────┐     │
│  │ • Users & Authentication                   │     │
│  │ • Audio File Metadata                      │     │
│  │ • Analysis Results                         │     │
│  │ • Batch Jobs                               │     │
│  │                                             │     │
│  │ Port: 27017                                │     │
│  │ Driver: Motor (async)                      │     │
│  │ ODM: Beanie                                │     │
│  └────────────────────────────────────────────┘     │
│                                                       │
│  Redis (Cache & Queue)                               │
│  ┌────────────────────────────────────────────┐     │
│  │ • Application Cache                        │     │
│  │ • Session Storage                          │     │
│  │ • Rate Limiting                            │     │
│  │ • Celery Message Broker                    │     │
│  │                                             │     │
│  │ Port: 6379                                 │     │
│  │ Driver: redis-py (async)                   │     │
│  └────────────────────────────────────────────┘     │
│                                                       │
│  ChromaDB (Vector Database)                          │
│  ┌────────────────────────────────────────────┐     │
│  │ • Audio Embeddings                         │     │
│  │ • Similarity Search                        │     │
│  │ • Feature Vectors                          │     │
│  │                                             │     │
│  │ Port: 8002 (HTTP API)                      │     │
│  │ Storage: Persistent (disk)                 │     │
│  └────────────────────────────────────────────┘     │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Data Flow

```
┌────────────────────────────────────────────────────────┐
│                 Data Flow Diagram                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  User Request                                          │
│       │                                                 │
│       ├─▶ 1. Check Redis Cache                        │
│       │    └─▶ Cache Hit? → Return Cached Data ✅      │
│       │                                                 │
│       ├─▶ 2. Query MongoDB (if cache miss)            │
│       │    ├─▶ User Data                               │
│       │    ├─▶ Audio Metadata                          │
│       │    └─▶ Analysis Results                        │
│       │                                                 │
│       ├─▶ 3. Search ChromaDB (for similarity)         │
│       │    └─▶ Vector Similarity Search                │
│       │                                                 │
│       └─▶ 4. Store Result in Redis Cache               │
│            └─▶ Set TTL based on data type              │
│                                                         │
└────────────────────────────────────────────────────────┘
```

---

## MongoDB Collections

### Collection Overview

```
MongoDB Database: samplemind
┌──────────────────────────────────────┐
│ Collection       │ Docs  │ Size      │
├──────────────────────────────────────┤
│ users            │ ~1K   │ ~1MB      │
│ audio_files      │ ~10K  │ ~10MB     │
│ analyses         │ ~10K  │ ~50MB     │
│ batch_jobs       │ ~500  │ ~5MB      │
└──────────────────────────────────────┘

Total Collections: 4
Estimated Total Size: ~66MB (with indexes)
```

### 1. Users Collection

**Collection Name**: `users`

```javascript
{
  "_id": ObjectId("..."),
  "user_id": "uuid-v4-string",           // Unique identifier
  "email": "user@example.com",            // Unique, indexed
  "username": "johndoe",                  // Unique, indexed
  "hashed_password": "$2b$12$...",       // bcrypt hash
  "is_active": true,                      // Account status
  "is_verified": false,                   // Email verified
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "last_login": ISODate("2025-01-10T15:30:00Z"),
  "total_analyses": 42,                   // Usage tracking
  "total_uploads": 15
}
```

**Schema Diagram:**

```
┌─────────────────────────────────────────┐
│             users                        │
├─────────────────────────────────────────┤
│ PK  user_id        String   UNIQUE      │
│ UQ  email          String   UNIQUE      │
│ UQ  username       String   UNIQUE      │
│     hashed_password String              │
│     is_active      Boolean  DEFAULT true│
│     is_verified    Boolean  DEFAULT false│
│ IDX created_at     DateTime             │
│     last_login     DateTime  NULLABLE   │
│     total_analyses Int      DEFAULT 0   │
│     total_uploads  Int      DEFAULT 0   │
└─────────────────────────────────────────┘
```

**Indexes:**
- `user_id` (unique)
- `email` (unique)
- `username` (unique)

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | String (UUID) | Unique user identifier used in JWT tokens |
| `email` | String | User's email address (login credential) |
| `username` | String | Display name (3-50 alphanumeric characters) |
| `hashed_password` | String | bcrypt hash (12 rounds) - never store plain text |
| `is_active` | Boolean | Whether account is active (can login) |
| `is_verified` | Boolean | Whether email is verified |
| `created_at` | DateTime | Account creation timestamp (UTC) |
| `last_login` | DateTime | Last successful login (updated on each login) |
| `total_analyses` | Integer | Counter for usage statistics |
| `total_uploads` | Integer | Counter for usage statistics |

---

### 2. Audio Files Collection

**Collection Name**: `audio_files`

```javascript
{
  "_id": ObjectId("..."),
  "file_id": "uuid-v4-string",           // Unique identifier
  "filename": "my_track.wav",             // Original filename
  "file_path": "/data/uploads/uuid.wav",  // Server file path
  "file_size": 5242880,                   // Size in bytes (5MB)
  "duration": 180.5,                      // Duration in seconds
  "sample_rate": 44100,                   // Sample rate in Hz
  "channels": 2,                          // Mono=1, Stereo=2
  "format": "wav",                        // File format
  "user_id": "uuid-v4-string",           // Owner (FK to users)
  "uploaded_at": ISODate("2025-01-01T00:00:00Z"),
  "tags": ["house", "bass", "loop"],      // User-defined tags
  "metadata": {                           // Additional metadata
    "title": "My Track",
    "artist": "John Doe",
    "bpm": 128,
    "key": "C major"
  }
}
```

**Schema Diagram:**

```
┌─────────────────────────────────────────┐
│          audio_files                     │
├─────────────────────────────────────────┤
│ PK  file_id        String   UNIQUE      │
│     filename       String               │
│     file_path      String               │
│     file_size      Int                  │
│     duration       Float                │
│     sample_rate    Int                  │
│     channels       Int                  │
│     format         String               │
│ FK  user_id        String   NULLABLE    │
│ IDX uploaded_at    DateTime             │
│     tags           Array<String>        │
│     metadata       Object               │
└─────────────────────────────────────────┘
```

**Indexes:**
- `file_id` (unique)
- `user_id` (for user queries)
- `uploaded_at` (for sorting)
- Compound: `{user_id: 1, uploaded_at: -1}` (user timeline)

**Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `file_id` | String (UUID) | Unique file identifier |
| `filename` | String | Original uploaded filename |
| `file_path` | String | Absolute path to file on server |
| `file_size` | Integer | File size in bytes |
| `duration` | Float | Audio duration in seconds |
| `sample_rate` | Integer | Sample rate (e.g., 44100, 48000) |
| `channels` | Integer | Number of audio channels (1=mono, 2=stereo) |
| `format` | String | File format (wav, mp3, flac, etc.) |
| `user_id` | String (UUID) | Owner's user ID (nullable for anonymous) |
| `uploaded_at` | DateTime | Upload timestamp (UTC) |
| `tags` | Array | User-defined tags for organization |
| `metadata` | Object | Flexible metadata (title, artist, BPM, key) |

---

### 3. Analyses Collection

**Collection Name**: `analyses`

```javascript
{
  "_id": ObjectId("..."),
  "analysis_id": "uuid-v4-string",       // Unique identifier
  "file_id": "uuid-v4-string",           // FK to audio_files
  "user_id": "uuid-v4-string",           // FK to users
  
  // Audio features
  "tempo": 128.5,                         // BPM
  "key": "C",                             // Musical key
  "mode": "major",                        // Major or minor
  "time_signature": [4, 4],               // Time signature
  "duration": 180.5,                      // Duration in seconds
  
  // Spectral features
  "spectral_features": {
    "spectral_centroid": [1500.2, ...],   // Array of values
    "spectral_rolloff": [3000.5, ...],
    "mfcc": [[...], [...], ...],          // 2D array (13 coefficients)
    "chroma": [[...], [...], ...]         // Chromagram features
  },
  
  // AI analysis
  "ai_provider": "google_ai",             // AI provider used
  "ai_model": "gemini-2.0-flash-exp",    // Model version
  "ai_summary": "Energetic house track...", // AI-generated summary
  "ai_detailed": {                        // Detailed AI analysis
    "genre": "House",
    "mood": "Energetic",
    "instruments": ["synthesizer", "drums", "bass"],
    "production_quality": "High"
  },
  "production_tips": [                    // AI suggestions
    "Add more high-end frequencies",
    "Consider sidechain compression"
  ],
  "creative_ideas": [
    "Try adding a vocal sample",
    "Experiment with filter automation"
  ],
  "fl_studio_recommendations": [
    "Use Sytrus for leads",
    "Apply multiband compression"
  ],
  
  // Metadata
  "analysis_level": "advanced",           // basic, advanced, full
  "processing_time": 3.5,                 // Seconds to analyze
  "analyzed_at": ISODate("2025-01-01T00:00:00Z")
}
```

**Schema Diagram:**

```
┌──────────────────────────────────────────┐
│           analyses                        │
├──────────────────────────────────────────┤
│ PK  analysis_id    String   UNIQUE       │
│ FK  file_id        String   INDEXED      │
│ FK  user_id        String   NULLABLE     │
│     tempo          Float                 │
│     key            String                │
│     mode           String                │
│     time_signature Array<Int>           │
│     duration       Float                 │
│     spectral_features Object            │
│     ai_provider    String   NULLABLE     │
│     ai_model       String   NULLABLE     │
│     ai_summary     String   NULLABLE     │
│     ai_detailed    Object   NULLABLE     │
│     production_tips Array<String>        │
│     creative_ideas  Array<String>        │
│     fl_studio_recommendations Array      │
│     analysis_level String               │
│     processing_time Float                │
│ IDX analyzed_at    DateTime              │
└──────────────────────────────────────────┘
```

**Indexes:**
- `analysis_id` (unique)
- `file_id` (for file queries)
- `user_id` (for user queries)
- `analyzed_at` (for sorting)
- Compound: `{user_id: 1, analyzed_at: -1}` (user history)

---

### 4. Batch Jobs Collection

**Collection Name**: `batch_jobs`

```javascript
{
  "_id": ObjectId("..."),
  "batch_id": "uuid-v4-string",          // Unique identifier
  "user_id": "uuid-v4-string",           // FK to users
  "status": "processing",                 // pending, processing, completed, failed
  "total_files": 10,                      // Total files in batch
  "completed": 5,                         // Completed count
  "failed": 0,                            // Failed count
  "file_ids": [                           // Array of file UUIDs
    "file-uuid-1",
    "file-uuid-2",
    ...
  ],
  "results": {                            // Results per file
    "file-uuid-1": {
      "status": "completed",
      "analysis_id": "analysis-uuid-1"
    },
    "file-uuid-2": {
      "status": "failed",
      "error": "File too large"
    }
  },
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:05:00Z")
}
```

**Schema Diagram:**

```
┌──────────────────────────────────────────┐
│          batch_jobs                       │
├──────────────────────────────────────────┤
│ PK  batch_id       String   UNIQUE       │
│ FK  user_id        String   NULLABLE     │
│ IDX status         String                │
│     total_files    Int                   │
│     completed      Int      DEFAULT 0    │
│     failed         Int      DEFAULT 0    │
│     file_ids       Array<String>         │
│     results        Object                │
│ IDX created_at     DateTime              │
│     updated_at     DateTime              │
└──────────────────────────────────────────┘
```

**Indexes:**
- `batch_id` (unique)
- `user_id` (for user queries)
- `status` (for filtering)
- `created_at` (for sorting)
- Compound: `{user_id: 1, status: 1}` (user dashboard)

**Status Values:**
- `pending`: Job queued, not started
- `processing`: Currently processing files
- `completed`: All files processed successfully
- `failed`: Job failed (check `results` for details)

---

## Redis Key Patterns

### Key Naming Convention

```
Pattern: {category}:{identifier}:{sub_key}
Example: cache:analysis:file_id_123
         session:user_uuid_456
         ratelimit:user_uuid:audio_upload
```

### Cache Keys

```
┌──────────────────────────────────────────────────────┐
│              Redis Cache Patterns                     │
├──────────────────────────────────────────────────────┤
│                                                       │
│  1. Analysis Results                                 │
│     Key: cache:analysis:{file_hash}                  │
│     TTL: 3600 seconds (1 hour)                       │
│     Value: JSON (analysis object)                    │
│     Size: ~5KB per entry                             │
│                                                       │
│  2. Audio Features                                   │
│     Key: cache:audio_features:{file_id}              │
│     TTL: 86400 seconds (24 hours)                    │
│     Value: JSON (spectral features)                  │
│     Size: ~2KB per entry                             │
│                                                       │
│  3. AI Responses                                     │
│     Key: cache:ai_response:{file_id}:{provider}      │
│     TTL: 604800 seconds (7 days)                     │
│     Value: JSON (AI analysis)                        │
│     Size: ~3KB per entry                             │
│                                                       │
│  4. Similarity Results                               │
│     Key: cache:similarity:{vector_hash}              │
│     TTL: 1800 seconds (30 minutes)                   │
│     Value: JSON (similar files array)                │
│     Size: ~1KB per entry                             │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Session Keys

```
┌──────────────────────────────────────────────────────┐
│              Session Management                       │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Key: session:{session_id}                           │
│  TTL: 604800 seconds (7 days)                        │
│  Value: JSON                                         │
│                                                       │
│  Example:                                            │
│  {                                                    │
│    "user_id": "uuid-v4-string",                      │
│    "email": "user@example.com",                      │
│    "created_at": 1704067200,                         │
│    "last_active": 1704153600,                        │
│    "ip_address": "*************"                     │
│  }                                                    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Rate Limit Keys

```
┌──────────────────────────────────────────────────────┐
│              Rate Limiting Patterns                   │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Key: ratelimit:{user_id}:{endpoint}                 │
│  TTL: 60 seconds (sliding window)                    │
│  Value: Integer (request count)                      │
│                                                       │
│  Examples:                                           │
│    ratelimit:uuid:auth_login          → 10/min      │
│    ratelimit:uuid:audio_upload        → 20/min      │
│    ratelimit:uuid:ai_analyze          → 30/min      │
│    ratelimit:uuid:general_api         → 60/min      │
│                                                       │
│  Implementation:                                     │
│    1. INCR key                                       │
│    2. If count == 1, EXPIRE key 60                   │
│    3. If count > limit, return 429 error             │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Celery Keys

```
┌──────────────────────────────────────────────────────┐
│              Celery Task Queue Keys                   │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Queue Keys:                                         │
│    celery:queue:default                              │
│    celery:queue:audio_processing                     │
│    celery:queue:ai_analysis                          │
│    celery:queue:embeddings                           │
│                                                       │
│  Result Keys:                                        │
│    celery-task-meta-{task_id}                        │
│    TTL: 86400 seconds (24 hours)                     │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## ChromaDB Vector Storage

### Collection Structure

```
┌──────────────────────────────────────────────────────┐
│            ChromaDB Collection Schema                 │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Collection Name: audio_embeddings                   │
│  Dimension: 768 (sentence-transformers)              │
│  Distance: cosine similarity                         │
│                                                       │
│  Document Structure:                                 │
│  {                                                    │
│    "id": "file_uuid",                                │
│    "embedding": [0.1, 0.2, ...],  // 768-dim vector │
│    "metadata": {                                     │
│      "file_id": "uuid",                              │
│      "filename": "track.wav",                        │
│      "duration": 180.5,                              │
│      "tempo": 128.5,                                 │
│      "key": "C",                                     │
│      "tags": ["house", "bass"],                      │
│      "created_at": "2025-01-01T00:00:00Z"           │
│    }                                                  │
│  }                                                    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Similarity Search

```python
# Query similar audio files
results = collection.query(
    query_embeddings=[audio_embedding],
    n_results=10,
    where={"tempo": {"$gte": 120, "$lte": 130}},  # Filter by tempo
    include=["metadatas", "distances"]
)

# Result format
{
  "ids": [["file_1", "file_2", ...]],
  "distances": [[0.1, 0.2, ...]],      # Lower = more similar
  "metadatas": [[{...}, {...}, ...]]
}
```

---

## Index Strategies

### MongoDB Index Configuration

```javascript
// users collection
db.users.createIndex({ "user_id": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })

// audio_files collection
db.audio_files.createIndex({ "file_id": 1 }, { unique: true })
db.audio_files.createIndex({ "user_id": 1 })
db.audio_files.createIndex({ "uploaded_at": -1 })
db.audio_files.createIndex({ "user_id": 1, "uploaded_at": -1 })  // Compound
db.audio_files.createIndex({ "tags": 1 })                        // Array index

// analyses collection
db.analyses.createIndex({ "analysis_id": 1 }, { unique: true })
db.analyses.createIndex({ "file_id": 1 })
db.analyses.createIndex({ "user_id": 1 })
db.analyses.createIndex({ "analyzed_at": -1 })
db.analyses.createIndex({ "user_id": 1, "analyzed_at": -1 })     // Compound

// batch_jobs collection
db.batch_jobs.createIndex({ "batch_id": 1 }, { unique: true })
db.batch_jobs.createIndex({ "user_id": 1 })
db.batch_jobs.createIndex({ "status": 1 })
db.batch_jobs.createIndex({ "user_id": 1, "status": 1 })         // Compound
db.batch_jobs.createIndex({ "created_at": -1 })
```

### Index Performance Impact

```
┌──────────────────────────────────────────────────────┐
│           Index Performance Comparison                │
├──────────────────────────────────────────────────────┤
│                                                       │
│  Query: Find user by email                           │
│  Without Index: 150ms (collection scan)              │
│  With Index:    5ms (index seek)                     │
│  Improvement:   30x faster                           │
│                                                       │
│  Query: List user's files (sorted by date)           │
│  Without Index: 200ms                                │
│  With Compound Index: 15ms                           │
│  Improvement:   13x faster                           │
│                                                       │
└──────────────────────────────────────────────────────┘
```

---

## Data Relationships

### Entity Relationship Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       │ 1:N (one user has many files)
       │
       ▼
┌─────────────┐      1:N      ┌─────────────┐
│ audio_files ├──────────────▶│  analyses   │
└─────────────┘                └─────────────┘
       │
       │ M:1 (many files in one batch)
       │
       ▼
┌─────────────┐
│ batch_jobs  │
└─────────────┘
```

### Relationship Details

1. **User → Audio Files** (One-to-Many)
   - One user can upload many files
   - `audio_files.user_id` references `users.user_id`

2. **Audio File → Analyses** (One-to-Many)
   - One file can have multiple analyses (basic, advanced, full)
   - `analyses.file_id` references `audio_files.file_id`

3. **User → Batch Jobs** (One-to-Many)
   - One user can create many batch jobs
   - `batch_jobs.user_id` references `users.user_id`

4. **Batch Job → Audio Files** (Many-to-Many)
   - One batch job contains many files
   - One file can be in multiple batch jobs
   - `batch_jobs.file_ids` array contains `audio_files.file_id` references

---

## Migration Guide

### Database Migrations

```bash
# Run migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "Add new field"

# Rollback migration
python -m alembic downgrade -1
```

### Data Migration Scripts

```python
# Example: Add new field to existing documents
from samplemind.core.database.mongo import AudioFile

async def migrate_add_format():
    """Add 'format' field to all audio_files"""
    files = await AudioFile.find_all().to_list()
    
    for file in files:
        if not hasattr(file, 'format'):
            file.format = file.filename.split('.')[-1]
            await file.save()
    
    print(f"✅ Migrated {len(files)} documents")
```

---

## Backup & Restore

### MongoDB Backup

```bash
# Full database backup
mongodump --uri="mongodb://localhost:27017/samplemind" --out=/backup/mongo_$(date +%Y%m%d)

# Restore from backup
mongorestore --uri="mongodb://localhost:27017/samplemind" /backup/mongo_20250101

# Backup specific collection
mongodump --uri="mongodb://localhost:27017/samplemind" --collection=users --out=/backup
```

### Redis Backup

```bash
# Save snapshot
redis-cli SAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d).rdb

# Restore (replace RDB file and restart Redis)
cp /backup/redis_20250101.rdb /var/lib/redis/dump.rdb
systemctl restart redis
```

### ChromaDB Backup

```bash
# Backup persistent directory
tar -czf /backup/chroma_$(date +%Y%m%d).tar.gz /data/chroma

# Restore
tar -xzf /backup/chroma_20250101.tar.gz -C /data/
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-01  
**Owner**: Database Team

**Status**: ✅ Production Ready
