---
name: tortoise-orm
description: Guide for database operations with Tortoise ORM. Use when creating models, running queries, or managing migrations.
---

## Tortoise ORM Database Operations

### Models
Located at `src/samplemind/core/database/tortoise_models.py`:
- `TortoiseUser` — User accounts
- `TortoiseSample` — Audio sample metadata
- `TortoiseLibrary` — Sample library collections

### CRUD Patterns
```python
# Create
sample = await TortoiseSample.create(filename="kick.wav", bpm=140.0, key="A minor")

# Read
samples = await TortoiseSample.filter(bpm__gte=120).all()
sample = await TortoiseSample.get_or_none(id=sample_id)

# Update
await TortoiseSample.filter(id=sample_id).update(bpm=145.0)

# Delete
await TortoiseSample.filter(id=sample_id).delete()
```

### Migrations
```bash
aerich migrate   # Generate migration
aerich upgrade   # Apply migration
aerich downgrade # Rollback
```

### Rules
- All queries must use `await`
- Use `.prefetch_related()` for eager loading
- Config: `aerich.ini`
- Default: SQLite, Production: PostgreSQL
