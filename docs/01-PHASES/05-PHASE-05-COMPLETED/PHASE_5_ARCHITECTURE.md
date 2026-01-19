# Phase 5: Web UI & Cloud Sync Architecture

**Status:** Planning/Roadmap
**Date:** January 18, 2026
**Estimated Timeline:** 8-12 weeks
**Prerequisites:** Phase 3 ✅, Phase 4.1+4.2 ✅

---

## Executive Summary

Phase 5 extends SampleMind from CLI-first to a multi-platform architecture with web interface and optional cloud synchronization. The design maintains offline-first philosophy while enabling cross-device workflows.

### Philosophy

**Primary:** CLI remains the feature-rich, high-performance interface for power users
**Secondary:** Web UI provides accessible alternative for casual users and DAW integration
**Tertiary:** Cloud sync (optional) enables cross-device workflows without breaking offline capability

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SampleMind v2 Architecture               │
└─────────────────────────────────────────────────────────────┘

User Interfaces (Frontend)
┌──────────────────┬──────────────────┬──────────────────┐
│   CLI (Textual)  │   Web UI (React) │   DAW Plugins    │
│   (Primary)      │   (Secondary)    │   (VST3/AU)      │
└────────┬─────────┴────────┬─────────┴────────┬─────────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                    ┌───────▼────────┐
                    │   FastAPI      │
                    │   /api/v1      │
                    │   (Middleware) │
                    └───────┬────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼────────────┐   ┌──────▼──────────┐   ┌───────▼──────┐
│  Audio Engine  │   │  Database       │   │  Cloud Sync  │
│  (Local)       │   │  (MongoDB)      │   │  (Optional)  │
└────────────────┘   └─────────────────┘   └──────────────┘
    │                       │                       │
    │ (Async/Thread)        │ (Motor)              │ (gRPC)
    │                       │                      │
┌───▼────────────────────────────────────────────────────────┐
│            Core Processing & Inference Layer                │
│     (Demucs, librosa, Ollama, spectral analysis)           │
└────────────────────────────────────────────────────────────┘
```

---

## 1. Web UI Architecture (React/Next.js)

### Technology Stack

```json
{
  "frontend": {
    "framework": "Next.js 14+ (App Router)",
    "ui": "React 18+ with TypeScript",
    "styling": "Tailwind CSS + shadcn/ui",
    "state": "TanStack Query + Zustand",
    "real-time": "WebSocket via Socket.io",
    "audio": "Tone.js + Web Audio API",
    "plots": "Plotly.js for spectral visualization"
  },
  "build": "Vercel or self-hosted",
  "bundler": "Turbopack (Next.js 14+)"
}
```

### Page Structure

```
src/app/
├── layout.tsx              # Root layout with auth provider
├── page.tsx                # Dashboard (main page)
├── (auth)/
│   ├── login/page.tsx
│   ├── register/page.tsx
│   └── forgot-password/page.tsx
├── library/
│   ├── page.tsx            # Sample library browser
│   ├── [id]/page.tsx       # Sample detail view
│   └── search/page.tsx     # Advanced search
├── analysis/
│   ├── page.tsx            # Batch analysis queue
│   ├── [id]/page.tsx       # Single analysis results
│   └── comparison/page.tsx # Side-by-side comparison
├── tools/
│   ├── classifier/page.tsx # AI classification
│   ├── mastering/page.tsx  # Mastering assistant
│   ├── separator/page.tsx  # Stem separation
│   └── spectral/page.tsx   # Real-time spectral analyzer
├── workspaces/
│   ├── page.tsx            # List workspaces
│   ├── [id]/page.tsx       # Workspace view
│   └── [id]/edit/page.tsx  # Workspace editor
├── settings/
│   ├── page.tsx            # User settings
│   ├── profile/page.tsx    # Profile edit
│   ├── api-keys/page.tsx   # API key management
│   └── cloud/page.tsx      # Cloud sync settings
├── daw-integration/
│   ├── page.tsx            # DAW setup
│   └── [daw]/page.tsx      # DAW-specific config
└── api/
    └── (route handlers)     # Route handlers instead of API routes
```

### Key Components

#### Dashboard Screen

```tsx
// src/app/page.tsx

import { DashboardLayout } from '@/components/layouts/dashboard'
import { StatsCard } from '@/components/dashboard/stats-card'
import { RecentAnalysis } from '@/components/dashboard/recent-analysis'
import { QuickActions } from '@/components/dashboard/quick-actions'

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="grid grid-cols-4 gap-4">
        {/* Statistics */}
        <StatsCard title="Library" value="1,234" trend={+5} />
        <StatsCard title="Analyses" value="567" trend={+12} />
        <StatsCard title="Disk Used" value="42.5 GB" trend={+2} />
        <StatsCard title="Cloud Sync" value="Synced" status="success" />
      </div>

      {/* Quick actions */}
      <QuickActions />

      {/* Recent analysis */}
      <RecentAnalysis limit={10} />
    </DashboardLayout>
  )
}
```

#### Sample Library Browser

```tsx
// src/app/library/page.tsx

'use client'

import { useSamples } from '@/hooks/use-samples'
import { SampleGrid } from '@/components/library/sample-grid'
import { SampleFilters } from '@/components/library/sample-filters'
import { useCallback, useState } from 'react'

export default function LibraryPage() {
  const [filters, setFilters] = useState({
    tags: [],
    tempo: [60, 180],
    key: 'all',
    sort: 'recent',
    search: '',
  })

  const { samples, isLoading } = useSamples(filters)

  const handleTagFilter = useCallback((tag: string) => {
    setFilters(f => ({
      ...f,
      tags: f.tags.includes(tag)
        ? f.tags.filter(t => t !== tag)
        : [...f.tags, tag],
    }))
  }, [])

  return (
    <div className="space-y-6">
      <SampleFilters
        filters={filters}
        onChange={setFilters}
        onTagFilter={handleTagFilter}
      />
      <SampleGrid
        samples={samples}
        isLoading={isLoading}
        onSelect={(sample) => {
          // Navigate to detail
        }}
      />
    </div>
  )
}
```

---

## 2. FastAPI Backend Extension

### API Endpoints (/api/v1)

```python
# src/samplemind/interfaces/api/routes/

router = APIRouter(prefix="/api/v1", tags=["v1"])

# Auth
POST   /auth/login
POST   /auth/register
POST   /auth/logout
GET    /auth/me
POST   /auth/refresh

# Library Management
GET    /library                           # List samples
GET    /library/{sample_id}               # Get sample details
POST   /library                           # Upload sample
DELETE /library/{sample_id}               # Delete sample
PUT    /library/{sample_id}               # Update metadata

# Analysis
GET    /analysis                          # List analyses
POST   /analysis/{sample_id}              # Analyze sample
POST   /analysis/batch                    # Batch analysis
GET    /analysis/{analysis_id}            # Get results
GET    /analysis/{analysis_id}/waveform   # Get waveform data

# AI Tools
POST   /tools/classify                    # Classify sample
POST   /tools/master                      # Master audio
POST   /tools/separate                    # Stem separation
GET    /tools/spectral/{sample_id}        # Real-time spectral data

# Cloud Sync
GET    /sync/status                       # Get sync status
POST   /sync/enable                       # Enable cloud sync
POST   /sync/disable                      # Disable cloud sync
GET    /sync/history                      # Get sync history

# Workspaces
GET    /workspaces                        # List workspaces
POST   /workspaces                        # Create workspace
GET    /workspaces/{workspace_id}         # Get workspace
PUT    /workspaces/{workspace_id}         # Update workspace
DELETE /workspaces/{workspace_id}         # Delete workspace
```

### WebSocket Events

```python
# Real-time updates

client → server:
  - join_analysis: {"analysis_id": "123"}
  - request_spectral: {"sample_id": "456", "interval": 100}
  - stop_spectral: {}

server → client:
  - analysis_progress: {"progress": 0.75, "current_step": "..."}
  - analysis_complete: {"results": {...}}
  - spectral_frame: {"frequencies": [...], "magnitudes": [...]}
  - sample_updated: {"sample_id": "456", "metadata": {...}}
```

### Async Task Queue

```python
# src/samplemind/interfaces/api/tasks.py

from celery import Celery, shared_task
import redis
from rq import Queue

# Setup task queue
celery_app = Celery('samplemind')
celery_app.conf.broker_url = 'redis://localhost:6379'

@celery_app.task
async def analyze_sample_task(sample_id: str):
    """Async sample analysis"""
    sample = await db.samples.find_one({"_id": sample_id})
    engine = AudioEngine()
    results = await engine.analyze_audio_async(sample['path'])
    await db.analyses.insert_one({
        'sample_id': sample_id,
        'results': results,
        'timestamp': datetime.now(),
    })

@celery_app.task
async def classify_sample_task(sample_id: str):
    """Async AI classification"""
    classifier = AIClassifier()
    sample = await db.samples.find_one({"_id": sample_id})
    classification = classifier.classify_audio(...)
    await db.classifications.insert_one({...})

@celery_app.task
async def master_audio_task(sample_id: str, genre: str):
    """Async mastering"""
    mastering_engine = MasteringEngine()
    output_path = mastering_engine.auto_master(...)
    await db.mastering.insert_one({...})
```

---

## 3. Cloud Sync Architecture

### Design Principles

1. **Offline-First**: App works without cloud
2. **Opt-In**: Cloud sync is optional, disabled by default
3. **Privacy-Focused**: Only metadata synced, not audio files
4. **Conflict Resolution**: Last-write-wins with versioning
5. **Selective Sync**: User controls what syncs

### Data Sync Flow

```
Local Changes
    ↓
[Offline Queue]
    ↓
(Network Available?)
    ├─ No → Wait for network
    └─ Yes ↓
    [Prepare Delta]
         ↓
    [Send to Cloud]
         ↓
    [Merge & Resolve Conflicts]
         ↓
    [Update Local State]
```

### Cloud Sync Implementation

```python
# src/samplemind/integrations/cloud_sync.py

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
import asyncio

@dataclass
class SyncEvent:
    """Single sync operation"""
    action: str  # 'create', 'update', 'delete'
    collection: str  # 'samples', 'analyses', 'workspaces'
    document_id: str
    data: Dict
    timestamp: datetime
    device_id: str

class CloudSyncManager:
    """Manages cloud synchronization"""

    def __init__(self, api_base: str, auth_token: str):
        self.api_base = api_base
        self.auth_token = auth_token
        self.offline_queue: List[SyncEvent] = []
        self.is_syncing = False

    async def enable_sync(self) -> bool:
        """Enable cloud sync"""
        # Authenticate with cloud
        result = await self._authenticate()
        if result:
            # Start background sync worker
            asyncio.create_task(self._sync_worker())
        return result

    async def _sync_worker(self):
        """Background worker that syncs periodically"""
        while self.enabled:
            try:
                await self._sync_queue()
                # Check for remote changes
                await self._pull_changes()
            except Exception as e:
                logger.error(f"Sync error: {e}")

            # Wait before next sync
            await asyncio.sleep(60)  # Sync every minute

    async def _sync_queue(self):
        """Sync offline queue to cloud"""
        if not self.offline_queue:
            return

        self.is_syncing = True
        try:
            for event in self.offline_queue:
                await self._upload_event(event)
            self.offline_queue.clear()
        finally:
            self.is_syncing = False

    async def _upload_event(self, event: SyncEvent):
        """Upload single event to cloud"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/sync/events",
                json=event.dict(),
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            return response.status_code == 200

    async def _pull_changes(self):
        """Check for remote changes"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base}/sync/changes",
                params={"since": self.last_sync_time},
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )

            changes = response.json()
            for change in changes:
                await self._apply_remote_change(change)
```

### Sync Settings UI

```tsx
// src/app/settings/cloud/page.tsx

'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Toggle } from '@/components/ui/toggle'
import { ProgressBar } from '@/components/ui/progress-bar'

export default function CloudSyncPage() {
  const { data: syncStatus, isLoading } = useQuery({
    queryKey: ['sync-status'],
    queryFn: () => fetch('/api/v1/sync/status').then(r => r.json()),
    refetchInterval: 5000, // Real-time status
  })

  const { mutate: enableSync } = useMutation({
    mutationFn: () => fetch('/api/v1/sync/enable', { method: 'POST' }),
    onSuccess: () => {
      // Refresh status
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Cloud Sync</h1>
        <Toggle
          pressed={syncStatus?.enabled}
          onPressedChange={(enabled) => {
            if (enabled) enableSync()
          }}
        >
          {syncStatus?.enabled ? 'Enabled' : 'Disabled'}
        </Toggle>
      </div>

      {syncStatus?.syncing && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Syncing...</p>
          <ProgressBar value={syncStatus.progress} max={100} />
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="font-semibold">Last Sync</h3>
          <p className="text-sm text-muted-foreground">
            {syncStatus?.last_sync_time}
          </p>
        </div>
        <div>
          <h3 className="font-semibold">Items Synced</h3>
          <p className="text-sm">
            {syncStatus?.total_synced} items
          </p>
        </div>
      </div>

      {/* Select what to sync */}
      <div className="space-y-3">
        <h3 className="font-semibold">Sync Options</h3>
        {['library_metadata', 'analysis_results', 'workspaces', 'settings'].map((option) => (
          <label key={option} className="flex items-center gap-2">
            <input type="checkbox" defaultChecked />
            <span className="text-sm">{option.replace(/_/g, ' ')}</span>
          </label>
        ))}
      </div>
    </div>
  )
}
```

---

## 4. Database Schema (MongoDB)

```javascript
// Collections structure

db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "email", "created_at"],
      properties: {
        _id: { bsonType: "objectId" },
        email: { bsonType: "string" },
        username: { bsonType: "string" },
        password_hash: { bsonType: "string" },
        profile: {
          bsonType: "object",
          properties: {
            full_name: { bsonType: "string" },
            avatar_url: { bsonType: "string" },
            bio: { bsonType: "string" }
          }
        },
        settings: {
          bsonType: "object",
          properties: {
            theme: { enum: ["light", "dark", "auto"] },
            sync_enabled: { bsonType: "bool" },
            sync_items: {
              bsonType: "array",
              items: { bsonType: "string" }
            }
          }
        },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
})

db.createCollection("samples", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "user_id", "filename", "path"],
      properties: {
        _id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        filename: { bsonType: "string" },
        path: { bsonType: "string" },
        file_size: { bsonType: "long" },
        duration: { bsonType: "double" },
        sample_rate: { bsonType: "int" },
        metadata: {
          bsonType: "object",
          properties: {
            title: { bsonType: "string" },
            description: { bsonType: "string" },
            tags: { bsonType: "array", items: { bsonType: "string" } },
            tempo: { bsonType: "int" },
            key: { bsonType: "string" },
            mode: { enum: ["major", "minor"] }
          }
        },
        synced_to_cloud: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
})

db.createCollection("analyses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "sample_id", "user_id"],
      properties: {
        _id: { bsonType: "objectId" },
        sample_id: { bsonType: "objectId" },
        user_id: { bsonType: "objectId" },
        analysis_type: { enum: ["basic", "detailed", "forensics", "all"] },
        results: {
          bsonType: "object",
          properties: {
            tempo: { bsonType: "double" },
            key: { bsonType: "string" },
            features: {
              bsonType: "object",
              properties: {
                spectral_centroid: { bsonType: "double" },
                mfcc: { bsonType: "array" },
                chromagram: { bsonType: "array" }
              }
            }
          }
        },
        created_at: { bsonType: "date" }
      }
    }
  }
})
```

---

## 5. DAW Integration

### VST3/AU Plugin Structure

```cpp
// src/daw_plugins/samplemind_plugin/

class SampleMindPlugin : public Steinberg::Vst::AudioEffect {
  // VST3 plugin that:
  // 1. Sends sample data to backend
  // 2. Receives analysis results
  // 3. Updates DAW parameters
  // 4. Stores in cloud via sync manager

  void process(ProcessData& data) override {
    // Stream audio to backend for real-time analysis
    backend_client.stream_audio(data.inputs);

    // Get real-time spectral data
    auto spectral = backend_client.get_spectral();
    // Update visualization
  }
}
```

---

## 6. Implementation Roadmap

### Phase 5.1: Web UI Foundation (Weeks 1-3)

- [ ] Next.js project setup
- [ ] Authentication (OAuth 2.0)
- [ ] Dashboard and library UI
- [ ] Upload sample handler
- [ ] Basic styling with Tailwind

### Phase 5.2: API Integration (Weeks 4-5)

- [ ] FastAPI endpoint implementation
- [ ] WebSocket setup for real-time
- [ ] Database schema creation
- [ ] File upload storage
- [ ] Analysis results retrieval

### Phase 5.3: Analysis Tools UI (Weeks 6-7)

- [ ] Classification screen
- [ ] Mastering assistant UI
- [ ] Stem separation interface
- [ ] Spectral analyzer visualization
- [ ] Results export

### Phase 5.4: Cloud Sync (Weeks 8-10)

- [ ] Cloud sync manager
- [ ] Offline queue implementation
- [ ] Conflict resolution logic
- [ ] Sync settings UI
- [ ] Data migration tools

### Phase 5.5: DAW Integration (Weeks 11-12)

- [ ] VST3 plugin wrapper
- [ ] Audio streaming to backend
- [ ] Real-time visualization
- [ ] Parameter automation
- [ ] Testing and optimization

---

## Success Criteria

- [ ] Web UI loads in <2 seconds
- [ ] File upload completes in <5 seconds
- [ ] Analysis results display in <100ms
- [ ] Cloud sync works offline-first
- [ ] VST3 plugin loads without errors
- [ ] 50 end-to-end tests passing
- [ ] Performance targets met (Lighthouse >90)
- [ ] User documentation complete

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | Next.js | Full-stack JS, SSR ready |
| **Styling** | Tailwind CSS | Productivity, consistency |
| **Real-time** | WebSocket + Socket.io | Low latency updates |
| **State** | TanStack Query | Server state management |
| **DAW** | VST3/AU first | Modern standard, broad support |
| **Sync** | Custom gRPC | More control than cloud APIs |

---

**Next Steps:** After Phase 5 completion, gather user feedback and consider Phase 4.3 (Neural Audio Generation) based on demand.

**Document prepared:** January 18, 2026

---
