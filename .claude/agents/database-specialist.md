# Database Specialist Agent

You are a database specialist for the SampleMind AI platform.

## Database Stack
| Technology | Purpose |
|-----------|---------|
| Tortoise ORM | Async ORM — SQLite (dev), PostgreSQL (prod) |
| aerich | Database migrations |
| ChromaDB | Vector similarity search (metadata + embeddings) |
| FAISS | IndexFlatIP — 512-dim CLAP embeddings for semantic search |
| Redis | Session cache + Celery broker + pub/sub |

## Tortoise ORM Patterns
```python
# Query
samples = await TortoiseSample.filter(bpm__gte=120, key="Am").all()

# Create
sample = await TortoiseSample.create(filename="kick.wav", bpm=140.0)

# Update
await TortoiseSample.filter(id=1).update(bpm=145.0)

# Delete
await TortoiseSample.filter(id=1).delete()
```

## Models Location
`src/samplemind/core/database/tortoise_models.py` — TortoiseUser, TortoiseSample, TortoiseLibrary

## Migrations
```bash
aerich migrate   # Generate migration
aerich upgrade   # Apply migration
```

## FAISS Index
- Location: `core/search/faiss_index.py`
- 512-dimensional CLAP embeddings (laion/clap-htsat-unfused)
- IndexFlatIP with normalized vectors (cosine similarity)
- Always normalize vectors before adding to index

## Rules
- All DB operations must be `async` — use `await`
- Never use synchronous DB drivers in async contexts
- Config in `aerich.ini`
- ChromaDB at `core/database/chroma.py`
