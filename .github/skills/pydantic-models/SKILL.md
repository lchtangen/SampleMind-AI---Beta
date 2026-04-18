---
name: pydantic-models
description: Guide for creating Pydantic v2 models for API schemas. Use when defining request/response models.
---

## Pydantic v2 Models

### Pattern
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    file_path: str = Field(..., description="Path to audio file")
    level: str = Field(default="STANDARD", pattern="^(BASIC|STANDARD|DETAILED|PROFESSIONAL)$")

class AnalysisResult(BaseModel):
    bpm: float = Field(..., ge=20, le=300, description="Beats per minute")
    key: str = Field(..., description="Musical key (e.g., 'A minor')")
    duration: float = Field(..., ge=0, description="Duration in seconds")
    features: Optional[dict] = Field(default=None, description="Additional features")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_schema_extra": {"example": {"bpm": 140.0, "key": "A minor", "duration": 3.5}}}
```

### Best Practices
- Use `Field()` with descriptions for documentation
- Add validation constraints (ge, le, pattern, min_length, etc.)
- Use `model_config` for JSON schema examples
- Use `Optional[T]` with `None` defaults for optional fields
- Define response models for all API endpoints
