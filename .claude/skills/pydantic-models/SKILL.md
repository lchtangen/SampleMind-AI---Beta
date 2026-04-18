---
name: pydantic-models
description: Pydantic v2 request/response models with Field descriptions and union types
---

## Pydantic Models

### Version
Pydantic v2 — use v2 syntax throughout.

### Pattern
```python
from pydantic import BaseModel, Field

class SampleRequest(BaseModel):
    filename: str = Field(..., description="Audio file name")
    bpm: float | None = Field(None, ge=20, le=300, description="BPM")
    key: str | None = Field(None, pattern=r"^[A-G][#b]?[mM]?$")
    tags: list[str] = Field(default_factory=list)

class SampleResponse(BaseModel):
    id: int
    filename: str
    bpm: float | None
    analysis: dict[str, float] = Field(default_factory=dict)

    model_config = {"from_attributes": True}
```

### Rules
- Use `X | Y` union syntax (Python 3.12+), not `Optional[X]`
- Add `Field(description=...)` for API documentation
- Use `model_config = {"from_attributes": True}` for ORM integration
- Validate with `ge`, `le`, `pattern`, `min_length`, etc.
- Use `model_validate()` not `from_orm()` (v2 syntax)
- Define in the same route file or a shared `schemas.py`
