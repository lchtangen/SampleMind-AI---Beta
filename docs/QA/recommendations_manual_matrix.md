# Recommendations Manual QA Matrix

| ID | Scenario | Preconditions | Steps | Expected Result | Notes |
|----|----------|---------------|-------|-----------------|-------|
| QA-REC-001 | Baseline fusion ranking | User has at least 5 analyzed tracks with tempo/key metadata; embeddings generated | 1. Log in as test user<br>2. Set context BPM 128 / Key C major / Mood uplifting<br>3. Open dashboard recommendations<br>4. Note top 3 items | Track(s) matching BPM/key appear first; telemetry logs `view` events; API response includes `score_components` with tempo/key | Verify backend logs contain `recommendation_event` with matching context metadata |
| QA-REC-002 | Tempo mismatch penalty | Same library as QA-REC-001 | 1. Change context BPM to 90<br>2. Refresh recommendations | Tracks around BPM 90 surface; previous high-tempo track drops in ranking with reduced tempo score | Confirm tempo score component < previous scenario |
| QA-REC-003 | Key-relative boost | Library contains tracks in relative key (e.g., A minor vs C major) | 1. Set context Key C major<br>2. Record top suggestion<br>3. Adjust context to A minor<br>4. Refresh | Relative key tracks gain ~0.1 bonus and may move up; `score_components.key_relative` present when applicable | Capture screenshot of rationale tag |
| QA-REC-004 | Mood overlap weighting | Tracks tagged with `mellow`, `cinematic` etc. | 1. Set mood tags to `mellow, cinematic`<br>2. Refresh panel<br>3. Click `Preview` on top result | Suggestions sharing mood tags have `score_components.mood_overlap`; preview button fires `recommendation.preview` telemetry | Validate telemetry endpoint receives event with action `preview` |
| QA-REC-005 | Accept + skip interactions | Any context | 1. Click `Use Sample` on a suggestion<br>2. Click `Dismiss` on another | Telemetry endpoint logs `accept` and `skip`; UI updates only after explicit refresh (for now) | Check server log for sequential events with correct rank |
| QA-REC-006 | Cold-start fallback | User with only uploaded (not analyzed) track | 1. Trigger recommendations without context | Response includes fallback suggestion with `source` = fallback | Ensure console warning absent and fallback score ~0.1 |
| QA-REC-007 | Auth token expiry | Use browser dev tools to delete token storage | 1. Refresh dashboard recommendations | Telemetry client skips sending events (console warning in dev); API requests redirected to login | Confirm no telemetry POST without token |
| QA-REC-008 | Telemetry persistence check | App running with logging enabled | 1. Interact with panel (view, preview, accept, skip)<br>2. Tail backend logs | Each interaction outputs structured log with session_id, user_id, metadata | Share log snippet with ops for ingestion |
| QA-REC-009 | API contract validation | Use REST client (cURL/Postman) | 1. POST `/api/v1/recommendations/context` with JWT<br>2. GET `/api/v1/recommendations/top?top_k=5` | Response matches schema (context, suggestions with metadata) | Record response sample; confirm `score_components` keys align with docs |
| QA-REC-010 | A/B mode toggle (rules) | Feature flag `RECS_RECOMMENDATION_MODE` set to `rules`, env `NEXT_PUBLIC_RECOMMENDATION_MODE=rules`, or dashboard toggle | 1. Switch mode to Rules via dashboard toggle (or call `/api/v1/recommendations/top?mode=rules`)<br>2. Observe UI auto-refresh | Suggestions source displays `rules`; ranking follows tempo/key heuristics only | Compare ranking before/after toggle |
| QA-REC-011 | Regression: context reset | After several interactions | 1. Change context fields<br>2. Observe panel update<br>3. Reload page | Context persists via API; view telemetry triggers once per unique suggestion set | Ensure no duplicate view events after reload |

## Execution Notes
- Run after `pytest backend/tests/test_recommendations*.py` and a fresh `pnpm lint`.
- Telemetry verification currently relies on API log output; integration with analytics pipeline TBD.
- Optional: set `NEXT_PUBLIC_RECOMMENDATION_MODE=rules` in `.env.local` to force rules mode across sessions.
- Capture findings in `docs/QA/recommendations_execution_checklist.md` (duplicate per run) with sample responses and screenshots.
