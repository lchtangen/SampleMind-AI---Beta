# API Design Patterns — SampleMind AI

Standard patterns and conventions for all REST API endpoints.

## Base Pattern

All endpoints follow this structure:

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from samplemind.core.exceptions import ValidationError, AudioAnalysisError

router = APIRouter(prefix="/api/v1/feature", tags=["FeatureName"])
logger = logging.getLogger(__name__)

# ── Request/Response Models ──────────────────────────────────────────────

class FeatureRequest(BaseModel):
    """Request payload with validation."""
    parameter: str
    optional_param: int | None = None
    class Config:
        json_schema_extra = {
            "example": {"parameter": "value"}
        }

class FeatureResponse(BaseModel):
    """Response payload."""
    result: str
    status: str

# ── Endpoint ─────────────────────────────────────────────────────────────

@router.post("/operate", response_model=FeatureResponse)
@rate_limit("100/minute")
async def operate_feature(
    request: FeatureRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Descriptive title for the operation.
    
    This endpoint does X and returns Y.
    Requires authentication.
    Rate limited to 100 requests/minute.
    
    Args:
        request: FeatureRequest with parameters
        current_user: Authenticated user from JWT
    
    Returns:
        FeatureResponse with result and status
    
    Raises:
        HTTPException 400: Invalid parameters
        HTTPException 500: Processing error
    
    Examples:
        >>> POST /api/v1/feature/operate
        >>> {"parameter": "value"}
        >>> {"result": "processed", "status": "ok"}
    """
    try:
        # Validate input
        if not request.parameter:
            raise ValidationError("parameter is required")
        
        # Log operation start
        logger.info(
            "Operation started",
            extra={"user_id": current_user.user_id, "parameter": request.parameter}
        )
        
        # Process
        result = await process_operation(request.parameter)
        
        # Log success
        logger.info(
            "Operation complete",
            extra={"user_id": current_user.user_id, "result_size": len(result)}
        )
        
        return FeatureResponse(
            result=result,
            status="ok"
        )
        
    except ValidationError as exc:
        logger.warning("Invalid parameters", extra={"error": str(exc)})
        raise HTTPException(status_code=400, detail=str(exc))
    
    except AudioAnalysisError as exc:
        logger.error("Processing error", exc_info=True)
        raise HTTPException(status_code=500, detail="Processing failed")
    
    except Exception as exc:
        logger.error(
            "Unexpected error",
            extra={"error_type": type(exc).__name__},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Endpoint Categories

### 1. Analysis Endpoints

Return detailed analysis results:

```python
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """
    Analyze uploaded audio file.
    
    Returns: BPM, key, energy, mood, instruments, etc.
    """
    result = await engine.analyze_async(file.file)
    return AnalysisResponse.from_analysis(result)
```

**Pattern:**
- Accept file upload or path
- Process asynchronously if > 1s
- Return rich analysis object
- Status code 200 (success), 400 (invalid file), 500 (error)

### 2. Query Endpoints

Search and retrieve data:

```python
@router.get("/search", response_model=SearchResponse)
async def search_samples(
    query: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search samples by query.
    
    Query can be: "genre:trap bpm:140" or "dark aggressive kick"
    Results are paginated: limit (1-100), offset ≥ 0
    """
    results = await search_index.query(query, limit=limit, offset=offset)
    return SearchResponse(
        results=[SampleResult.from_index(r) for r in results],
        total=len(results),
        limit=limit,
        offset=offset
    )
```

**Pattern:**
- Accept query parameters with validation
- Support pagination (limit, offset or cursor)
- Return paginated response
- Status code 200 (success), 400 (invalid query), 404 (not found)

### 3. Mutation Endpoints

Create/update/delete operations:

```python
@router.post("/samples", response_model=SampleResponse, status_code=201)
async def create_sample(
    request: CreateSampleRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Create a new sample in the library.
    
    Returns: Created sample with ID and metadata.
    """
    sample = await db.create_sample(
        owner_id=current_user.user_id,
        **request.dict()
    )
    logger.info("Sample created", extra={"sample_id": sample.id})
    return SampleResponse.from_model(sample)

@router.put("/samples/{sample_id}", response_model=SampleResponse)
async def update_sample(
    sample_id: str,
    request: UpdateSampleRequest,
    current_user = Depends(get_current_active_user)
):
    """Update an existing sample."""
    sample = await db.get_sample(sample_id, owner_id=current_user.user_id)
    sample = await db.update_sample(sample_id, **request.dict(exclude_unset=True))
    return SampleResponse.from_model(sample)

@router.delete("/samples/{sample_id}", status_code=204)
async def delete_sample(
    sample_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete a sample (irreversible)."""
    await db.delete_sample(sample_id, owner_id=current_user.user_id)
    logger.info("Sample deleted", extra={"sample_id": sample_id})
    # Status 204 returns no content
```

**Pattern:**
- POST = create (201 Created)
- GET = read (200 OK)
- PUT = replace (200 OK)
- PATCH = partial update (200 OK)
- DELETE = remove (204 No Content)
- Include ownership checks for multi-tenant

### 4. Agent/Task Endpoints

Long-running background jobs:

```python
@router.post("/analyze-agent", response_model=TaskResponse, status_code=202)
async def start_agent_analysis(
    request: AgentAnalysisRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Start background agent analysis (async).
    
    Returns immediately with task ID.
    Poll with: GET /tasks/{task_id}
    """
    from samplemind.core.tasks.celery_app import celery_app
    
    result = celery_app.send_task(
        "samplemind.core.tasks.agent_tasks.run_analysis_agent",
        kwargs={"file_path": request.file_path, "user_id": current_user.user_id},
        queue="agents"
    )
    
    logger.info("Agent task submitted", extra={"task_id": result.id})
    return TaskResponse(task_id=result.id, status="submitted")

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Poll task status.
    
    Status: pending, running, completed, failed
    Use WebSocket for real-time updates (see /ws/tasks/{task_id})
    """
    result = AsyncResult(task_id, app=celery_app)
    
    if result.status == "PENDING":
        status = "pending"
    elif result.status == "PROGRESS":
        status = "running"
        progress = result.info.get("progress", 0)
    elif result.successful():
        status = "completed"
        result_data = result.get()
    else:
        status = "failed"
        error = str(result.info)
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        progress=progress,
        result=result_data,
        error=error
    )
```

**Pattern:**
- Returns 202 Accepted with task ID immediately
- Client polls /tasks/{task_id} for progress
- Support WebSocket for real-time updates
- Provide estimated completion time if available

## Response Format Standards

### Success Response (200-201)

```python
{
    "data": { /* actual result */ },
    "status": "ok",
    "timestamp": "2026-04-10T12:34:56Z"
}
```

### Paginated Response (200)

```python
{
    "results": [ /* array of items */ ],
    "pagination": {
        "total": 1000,
        "limit": 20,
        "offset": 0,
        "page": 1
    },
    "status": "ok"
}
```

### Error Response (4xx-5xx)

```python
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid parameters",
        "details": {
            "field": "bpm",
            "reason": "must be 50-200"
        }
    },
    "timestamp": "2026-04-10T12:34:56Z",
    "request_id": "req-abc123"
}
```

### Task Response (202)

```python
{
    "task_id": "task-abc123",
    "status": "submitted",
    "progress": 0,
    "estimated_completion_s": 30,
    "polling_url": "/api/v1/tasks/task-abc123",
    "websocket_url": "ws://localhost/ws/tasks/task-abc123"
}
```

## Authentication & Authorization

### Require Authentication

```python
@router.get("/protected")
async def protected_endpoint(
    current_user = Depends(get_current_active_user)
):
    """This endpoint requires JWT token."""
    return {"user_id": current_user.user_id}
```

### Authorization (Role-based)

```python
@router.delete("/samples/{sample_id}")
async def admin_delete(
    sample_id: str,
    current_user = Depends(get_current_active_user)
):
    """Only admins can delete samples."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Delete...
```

### Resource Ownership

```python
@router.put("/samples/{sample_id}")
async def update_my_sample(
    sample_id: str,
    request: UpdateRequest,
    current_user = Depends(get_current_active_user)
):
    """Only the owner can update."""
    sample = await db.get_sample(sample_id)
    
    if sample.owner_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your sample")
    
    # Update...
```

## Rate Limiting

All endpoints must have rate limiting:

```python
@router.post("/analyze", response_model=AnalysisResponse)
@rate_limit("100/minute")  # 100 requests per minute
@rate_limit("1000/hour")   # 1000 requests per hour
async def analyze(request: AnalysisRequest):
    pass
```

**Standard limits:**
- Public endpoints: 100/minute
- Authenticated endpoints: 1000/hour
- Admin endpoints: unlimited
- Analysis: 10/minute (expensive)

## Documentation Standards

All endpoints must include:

```python
@router.post("/endpoint")
async def endpoint(request: RequestModel):
    """
    One-line summary of what the endpoint does.
    
    Longer description explaining the behavior, side effects,
    and any important notes.
    
    Args:
        request: The request payload
    
    Returns:
        ResponseModel: The response payload
    
    Raises:
        HTTPException 400: When input validation fails
        HTTPException 500: When processing fails
    
    Examples:
        >>> POST /api/v1/endpoint
        >>> {"field": "value"}
        >>> {"result": "success"}
    """
```

## Testing Pattern

All endpoints should have tests:

```python
def test_endpoint_success(async_client, authenticated_user):
    """Test happy path."""
    response = async_client.post(
        "/api/v1/endpoint",
        json={"field": "value"},
        headers={"Authorization": f"Bearer {authenticated_user.token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_endpoint_invalid_input(async_client):
    """Test validation error."""
    response = async_client.post(
        "/api/v1/endpoint",
        json={"field": ""}  # Invalid: empty
    )
    assert response.status_code == 400
    assert "required" in response.json()["error"]["message"]

def test_endpoint_unauthorized(async_client):
    """Test missing auth."""
    response = async_client.post("/api/v1/endpoint", json={})
    assert response.status_code == 401
```

## Common Patterns

### Async Processing

Use Celery for operations > 3 seconds:

```python
@router.post("/heavy-compute", status_code=202)
async def heavy_compute(request):
    task = celery_app.send_task(
        "my_app.tasks.heavy_computation",
        kwargs={"data": request.data}
    )
    return {"task_id": task.id}
```

### Filters & Search

Support flexible filtering:

```python
@router.get("/samples")
async def list_samples(
    genre: str | None = None,
    bpm_min: int | None = None,
    bpm_max: int | None = None,
    sort_by: str = "created_at",
    order: str = "desc"
):
    """List with optional filters."""
    query = db.samples
    if genre: query = query.filter(genre=genre)
    if bpm_min: query = query.filter(bpm__gte=bpm_min)
    if bpm_max: query = query.filter(bpm__lte=bpm_max)
    return query.order_by(sort_by, order).all()
```

### Bulk Operations

Support batch requests:

```python
@router.post("/samples/batch")
async def bulk_create_samples(request: BulkCreateRequest):
    """Create multiple samples at once."""
    samples = []
    for item in request.items:
        sample = await db.create_sample(**item)
        samples.append(sample)
    return {"created": len(samples)}
```

## See Also

- **Error Handling:** See `ERROR_HANDLING_GUIDE.md`
- **Local Setup:** See `SETUP_LOCAL.md`
- **Architecture:** See `ARCHITECTURE.md`
