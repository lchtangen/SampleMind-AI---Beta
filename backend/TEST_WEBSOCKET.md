# 🔌 WebSocket Testing Guide

Test real-time WebSocket connections for SampleMind AI.

---

## 🚀 WebSocket Endpoint

**URL:** `ws://localhost:8000/api/v1/ws/{user_id}?token=YOUR_TOKEN`

**Purpose:** Real-time updates for:
- Upload progress
- Analysis status
- Notifications

---

## 🧪 Test with JavaScript (Browser Console)

1. **Open** http://localhost:8000/api/docs
2. **Open browser console** (F12)
3. **Paste and run:**

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/1?token=test');

// Handle connection open
ws.onopen = () => {
    console.log('✅ WebSocket connected!');
    
    // Send ping
    ws.send(JSON.stringify({
        type: 'ping'
    }));
};

// Handle messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Message received:', data);
};

// Handle errors
ws.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
};

// Handle close
ws.onclose = () => {
    console.log('❌ WebSocket closed');
};
```

---

## 📨 Message Types

### Client → Server

**Ping:**
```json
{
    "type": "ping"
}
```

**Subscribe:**
```json
{
    "type": "subscribe",
    "data": {
        "events": ["upload", "analysis"]
    }
}
```

### Server → Client

**Connection:**
```json
{
    "type": "connection",
    "data": {
        "status": "connected",
        "user_id": 1,
        "message": "WebSocket connection established"
    },
    "timestamp": "2025-10-19T20:00:00Z"
}
```

**Upload Progress:**
```json
{
    "type": "upload_progress",
    "data": {
        "audio_id": 1,
        "progress": 65.5,
        "status": "Uploading..."
    },
    "timestamp": "2025-10-19T20:00:00Z"
}
```

**Analysis Status:**
```json
{
    "type": "analysis_status",
    "data": {
        "audio_id": 1,
        "status": "processing",
        "progress": 45.0
    },
    "timestamp": "2025-10-19T20:00:00Z"
}
```

**Notification:**
```json
{
    "type": "notification",
    "data": {
        "title": "Analysis Complete",
        "message": "Your audio has been analyzed",
        "level": "success"
    },
    "timestamp": "2025-10-19T20:00:00Z"
}
```

---

## 🧪 Test with Python

```python
import websockets
import asyncio
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/v1/ws/1?token=test"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected!")
        
        # Wait for welcome message
        message = await websocket.recv()
        print(f"📨 Received: {message}")
        
        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))
        
        # Wait for pong
        response = await websocket.recv()
        print(f"📨 Pong: {response}")

# Run test
asyncio.run(test_websocket())
```

---

## 🔄 Integration with Audio Upload

When implementing file upload with progress:

```python
from app.api.v1.websocket import send_upload_progress

async def upload_with_progress(file, user_id, audio_id):
    total_size = len(file.content)
    uploaded = 0
    
    for chunk in file.chunks():
        # Upload chunk
        uploaded += len(chunk)
        progress = (uploaded / total_size) * 100
        
        # Send progress update
        await send_upload_progress(
            user_id=user_id,
            audio_id=audio_id,
            progress=progress,
            status=f"Uploading: {progress:.1f}%"
        )
```

---

## 🔄 Integration with Analysis

When running analysis:

```python
from app.api.v1.websocket import send_analysis_status

async def analyze_audio(audio_id, user_id):
    # Start
    await send_analysis_status(user_id, audio_id, "processing", progress=0)
    
    # Feature extraction (50%)
    features = extract_features()
    await send_analysis_status(user_id, audio_id, "processing", progress=50)
    
    # AI analysis (100%)
    results = ai_analyze(features)
    await send_analysis_status(
        user_id, audio_id, "completed", 
        progress=100, results=results
    )
```

---

## 📊 Current Implementation

**Status:** ✅ WebSocket endpoint active

**Features:**
- Connection management per user
- Message routing
- Ping/pong keep-alive
- Subscribe to events
- Broadcast and personal messages

**TODO:**
- JWT token validation
- Rate limiting per connection
- Reconnection handling
- Connection timeout
- Message queue for offline users

---

## 🎯 Frontend Integration

```typescript
class WebSocketClient {
    private ws: WebSocket;
    
    connect(userId: number, token: string) {
        this.ws = new WebSocket(
            `ws://localhost:8000/api/v1/ws/${userId}?token=${token}`
        );
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'upload_progress':
                    this.handleUploadProgress(data.data);
                    break;
                case 'analysis_status':
                    this.handleAnalysisStatus(data.data);
                    break;
                case 'notification':
                    this.showNotification(data.data);
                    break;
            }
        };
    }
    
    handleUploadProgress(data) {
        // Update progress bar
        updateProgressBar(data.audio_id, data.progress);
    }
    
    handleAnalysisStatus(data) {
        // Update UI with analysis status
        if (data.status === 'completed') {
            showResults(data.results);
        }
    }
    
    showNotification(data) {
        // Show toast notification
        toast(data.title, data.message, data.level);
    }
}
```

---

## ✅ Quick Verification

1. Server running: http://localhost:8000
2. WebSocket endpoint: `ws://localhost:8000/api/v1/ws/1?token=test`
3. Test in browser console
4. Should see connection and pong messages

---

**Status:** ✅ WebSocket implementation complete  
**Phase 7 Progress:** 60% (6/10 tasks)  
**Next:** Rate limiting, feature flags, or move to Phase 3 (Pages)
