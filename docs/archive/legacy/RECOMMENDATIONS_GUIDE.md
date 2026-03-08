# SampleMind Recommendations Runbook

## 1. Overview
- **Purpose:** Provide operational guidance for the context-aware recommendations service powering dashboard suggestions.
- **Scope:** FastAPI `/api/v1/recommendations/*`, background embedding/index refresh, WebSocket fan-out, and frontend telemetry loop.
- **Owners:** ML Platform (primary), Web Core (secondary).
- **Service Tier:** Tier 2 (core experience, 30 min MTTR target).

## 2. Architecture Snapshot
- **Request flow:**
  1. Frontend `useRecommendations` fetches `/recommendations/top` (mode `fusion` default).
  2. `RecommendationService` merges cached context + vector store query (pgvector planned; in-memory fallback now).
  3. Results pushed back to client and broadcast via WebSocket (`recommendations_update`).
  4. Telemetry events (`view/preview/accept/skip`) streamed to `/telemetry/recommendations` for logging/analytics.
- **Key components:**
  - `RecommendationService` (fusion engine, rule engine, recency fallback).
  - `VectorStore` facade (`backend/app/services/vector_store.py`).
  - `EmbeddingService` ensures CLAP or hash embeddings are present post-analysis.
  - Context cache (Redis, fallback in-memory) for per-user session state.
- **Data dependencies:** `audio_files`, `audio_analyses`, `audio_embeddings`, `audio_import_jobs`.

## 3. Configuration & Feature Flags
- **Backend env (`.env`):**
  - `RECS_USE_CLAP` — enable CLAP embeddings (default `false`).
  - `RECS_EMBEDDING_DIM` — vector dimension (default `512`).
  - `RECS_EMBEDDING_FALLBACK` — fallback embedding strategy (`fingerprint`).
  - `RECS_RECOMMENDATION_MODE` — default engine (`fusion` or `rules`).
- **Frontend env (`.env.local`):**
  - `NEXT_PUBLIC_RECOMMENDATION_MODE` — mirrors backend for consistent default toggle.
- **Runtime toggle (UI):** Dashboard mode switch calls `/recommendations/top?mode={fusion|rules}`.
- **Operational flags:**
  - `RECS_VECTOR_AUTO_REFRESH=1` (future) — auto-refresh vector cache after bulk imports.
  - `RECS_WS_BROADCAST` (future) — gate WebSocket fan-out per env.

## 4. Operational Runbook
### 4.1 Health Checks
- `GET /api/v1/recommendations/top?top_k=1` with valid JWT should return 200 + at least fallback suggestion.
- Check FastAPI logs for `RecommendationService` latency (target <200 ms aggregation).
- WebSocket heartbeat: subscribe via dashboard, expect `recommendations_update` JSON after context change.

### 4.2 Common Tasks
- **Warm vector cache:**
  ```bash
  # inside backend shell
  python scripts/vector_store_refresh.py  # TODO: script under development
  ```
  Temporary workaround: restart backend to trigger lazy refresh.
- **Force embedding regeneration:**
  ```bash
  http POST :8000/api/v1/audio/analyze audio_id=<id> Authorization:"Bearer <token>"
  ```
- **Switch recommendation mode:**
  ```bash
  export RECS_RECOMMENDATION_MODE=rules
  # reload application / restart deployment
  ```
  Frontend: set `NEXT_PUBLIC_RECOMMENDATION_MODE` and rebuild or toggle via dashboard UI.

### 4.3 Incident Response
1. **Identify impact:** Check telemetry logs (`track_recommendations` entries) and error spikes.
2. **Check dependencies:**
   - Redis reachable? (`sm-health` or `redis-cli PING`).
   - Database migration alignment (`alembic current`).
3. **Mitigation options:**
   - Flip to `rules` mode to bypass vector store.
   - Enable deterministic fallback only (force `top_k=5&mode=rules`).
4. **Escalation:** ML Platform on-call if embeddings/vector scoring degraded for >30 min.

## 5. Telemetry & Observability
- **Event endpoint:** `POST /api/v1/telemetry/recommendations` (returns `accepted` count).
- **Log format:** Structured JSON with `event_type`, `session_id`, `user_id`, `context`, `metadata`.
- **Dashboards:**
  - Pending: integrate with Elastic Stack or DataDog; interim use `tail -f backend/logs/app.log | jq`.
- **Alerting ideas:**
  - Rate of `skip` events spike >3σ → signals poor relevance.
  - Absence of `view` events for >10 min → WebSocket or fetch failure.

## 6. QA & Release Checklist
- Run manual matrix (`docs/QA/recommendations_manual_matrix.md`), focus on QA-REC-010 toggle behaviour.
- Execute automated suite:
  ```bash
  pytest backend/tests/test_recommendations.py backend/tests/test_recommendations_api.py
  pnpm lint
  ```
- Capture screenshots of fusion vs. rules UI for release notes.
- Update `PROJECT_PHASE_TRACKER.md` status when verifying closure.

## 7. Troubleshooting Cheatsheet
| Symptom | Likely Cause | Resolution |
| --- | --- | --- |
| `/top` 500 error | Missing embeddings after migration | Run analyze endpoint or `EmbeddingService.ensure_embedding` via script |
| Empty suggestions | Context cache stale or no audio | Clear cache (`redis-cli FLUSHDB` in dev) or upload baseline tracks |
| Mode toggle no-op | Frontend env mismatch | Ensure both backend `RECS_RECOMMENDATION_MODE` and frontend default aligned; check network tab for `mode=` query |
| Telemetry drop | Network or auth failure | Verify `Authorization` header injected; inspect logs for 401 |
| WebSocket updates missing | Background task failure | Check `backend/app/api/v1/recommendations.py` logs; ensure ASGI workers have WS workers enabled |

## 8. Open Issues / Follow-ups
- Implement persistent vector store refresh job post-import.
- Ship `vector_store_refresh.py` helper and document usage.
- Automate telemetry ingestion pipeline (DataDog/Segment integration).
- Add Grafana dashboard for recommendation latency & adoption metrics.
