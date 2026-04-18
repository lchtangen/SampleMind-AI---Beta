---
applyTo: "src/samplemind/core/database/**/*.py"
---

# Database Instructions

- ORM: Tortoise ORM with aerich migrations
- Models: `core/database/tortoise_models.py` — TortoiseUser, TortoiseSample, TortoiseLibrary
- Default DB: SQLite for development, PostgreSQL for production
- Config: `aerich.ini` for migration settings
- Vector DB: ChromaDB at `core/database/chroma.py`
- FAISS: `core/search/faiss_index.py` — IndexFlatIP with 512-dim CLAP embeddings
- All DB operations must be `async` — use `await` with Tortoise queries
- Pattern: `await TortoiseSample.filter(bpm__gte=120).all()`
- Create pattern: `await TortoiseSample.create(filename="kick.wav", bpm=140.0)`
- Run migrations: `aerich migrate` then `aerich upgrade`
- Never use synchronous DB drivers in async contexts
