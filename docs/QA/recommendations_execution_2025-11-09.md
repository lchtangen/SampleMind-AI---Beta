# Recommendations Manual QA Execution Checklist

> Use this template while running the scenarios in `recommendations_manual_matrix.md`. Replace the placeholders with real values and attach evidence (screenshots, logs) as noted.

## 0. Test Session Metadata
- **Tester:** `<name>`
- **Environment:** `<dev | staging | prod>`
- **Backend build / commit:** `<hash>`
- **Frontend build:** `<hash>`
- **Date & time:** `<YYYY-MM-DD HH:MM TZ>`
- **Default recommendation mode:** `<fusion | rules>`
- **Feature flags:**
  - `RECS_RECOMMENDATION_MODE=`
  - `NEXT_PUBLIC_RECOMMENDATION_MODE=`
  - other relevant toggles

## 1. Pre-flight Checklist
- [ ] Backend up (`sm-dev` or deployed services) and reachable at `<base_url>`
- [ ] Frontend dashboard available at `<app_url>`
- [ ] Test account seeded with ≥5 analyzed audio files covering tempo/key variety
- [ ] Redis cache healthy (`redis-cli PING`)
- [ ] WebSocket connectivity verified (dashboard console: `connected: true`)

## 2. Scenario Execution Log
Fill the table while executing each QA case. Add more rows as needed.

| Case ID | Result (Pass/Fail/N/A) | Notes / Evidence | Screenshot / Log Path |
| --- | --- | --- | --- |
| QA-REC-001 |  |  |  |
| QA-REC-002 |  |  |  |
| QA-REC-003 |  |  |  |
| QA-REC-004 |  |  |  |
| QA-REC-005 |  |  |  |
| QA-REC-006 |  |  |  |
| QA-REC-007 |  |  |  |
| QA-REC-008 |  |  |  |
| QA-REC-009 |  |  |  |
| QA-REC-010 |  |  |  |
| QA-REC-011 |  |  |  |

## 3. Detailed Findings
Document any deviations, bugs, or UX observations. Attach log snippets where possible.

### 3.1 Failures / Blocking Issues
- **ID:** `<CASE_ID>`
  - **Description:** `<symptom>`
  - **Expected:** `<what should happen>`
  - **Actual:** `<what happened>`
  - **Logs / Evidence:** `<path or attach>`
  - **Severity:** `<blocker | major | minor>`
  - **Owner:** `<team>`

### 3.2 Observations / Improvements
- `<notes>`

## 4. Telemetry Validation
- [ ] Confirm `POST /api/v1/telemetry/recommendations` returns `202` with expected `accepted` count.
- [ ] Tail backend logs and verify structured events for `view`, `preview`, `accept`, `skip` with correct `mode` metadata.
- [ ] (Optional) Capture sample payload for analytics ingestion.

## 5. Recommendation Mode Toggle Verification
- **Fusion → Rules toggle:**
  - [ ] Dashboard switch updates UI state immediately (badge shows `Rules`).
  - [ ] `/recommendations/top?mode=rules` response `mode="rules"`.
  - [ ] Suggestions scores derived from `score_components.tempo_rules`, `key_rules`, etc.
  - [ ] Telemetry events include `context.mode = rules`.
- **Rules → Fusion toggle:**
  - [ ] Dashboard switch restores embedding-backed results (`source` contains `fusion` / `embedding-fusion`).
  - [ ] Vector results differ from rules list (attach diff screenshot or CSV).

## 6. Sign-off
- **Overall status:** `<pass | pass-with-notes | fail>`
- **Tester signature:** `<name>`
- **Date:** `<YYYY-MM-DD>`
- **Next actions:** `<bugs filed, follow-up tasks>`
