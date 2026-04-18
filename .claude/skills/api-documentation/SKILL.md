---
name: api-documentation
description: Swagger/ReDoc API docs and docs/v3/ project documentation
---

## API Documentation

### Auto-Generated
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI schema:** `http://localhost:8000/openapi.json`

### Improving API Docs
```python
@router.get(
    "/api/v1/samples/{sample_id}",
    response_model=SampleResponse,
    summary="Get sample by ID",
    description="Retrieve a sample's metadata and analysis results.",
    responses={404: {"description": "Sample not found"}},
)
async def get_sample(sample_id: int) -> SampleResponse:
    """Get a sample by its unique identifier."""
    ...
```

### Project Documentation
- Active docs: `docs/v3/` — CHECKLIST.md, STATUS.md, ROADMAP.md
- Guides: `docs/guides/`
- Navigation: `docs/INDEX.md`
- Do NOT use `docs/02-ROADMAPS/` (stale)

### Rules
- Add `summary` and `description` to all router decorators
- Use Pydantic `Field(description=...)` for schema docs
- Document error responses in `responses={}` parameter
- Keep docs/v3/CHECKLIST.md updated when completing items
