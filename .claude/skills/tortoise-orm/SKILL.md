---
name: tortoise-orm
description: Async Tortoise ORM with aerich migrations for SQLite/PostgreSQL
---

## Tortoise ORM

### Models
Location: `src/samplemind/core/database/tortoise_models.py`
Models: TortoiseUser, TortoiseSample, TortoiseLibrary

### Query Patterns
```python
# Filter
samples = await TortoiseSample.filter(bpm__gte=120, key="Am").all()

# Create
sample = await TortoiseSample.create(filename="kick.wav", bpm=140.0)

# Get or 404
sample = await TortoiseSample.get_or_none(id=sample_id)

# Update
await TortoiseSample.filter(id=1).update(bpm=145.0)

# Delete
await TortoiseSample.filter(id=1).delete()

# Relations
user = await TortoiseUser.get(id=user_id).prefetch_related("samples")
```

### Migrations
```bash
aerich migrate    # Generate migration
aerich upgrade    # Apply migration
```
Config: `aerich.ini`

### Rules
- All DB operations must be `async` with `await`
- SQLite for development, PostgreSQL for production
- Never use synchronous DB drivers in async contexts
- Use `get_or_none()` instead of `get()` to avoid exceptions
