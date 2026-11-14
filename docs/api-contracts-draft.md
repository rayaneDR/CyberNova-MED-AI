# API contracts — draft v0.1

**Proposed only.** Khawla has not implemented or accepted these endpoints. Rayane, Khawla, Ali, Amina, and Ayoub must agree the draft before integration.

Proposed base URL: `http://localhost:8000`. No authentication design yet; do not expose a real-data service publicly based on this draft.

| Proposed route | Purpose | Owner |
| --- | --- | --- |
| `GET /api/v1/health` | Service health, no telemetry | Khawla |
| `GET /api/v1/subjects/{subjectId}/telemetry?limit=12` | Ascending timestamp samples | Khawla; Amina supplies synthetic values |

Telemetry response shape: `{ "schemaVersion": "0.1", "subjectId": "demo-crew-01", "synthetic": true, "samples": [...] }`. `synthetic` must agree with all sample flags; do not combine synthetic and real readings in one response. The `samples` array contains objects conforming to `shared/contracts/telemetry.schema.json`. Empty sessions return an empty array. Propose `limit` as an integer from 1–1000, default 12; backend owner confirms.

| Sample field | Type | Meaning / unit |
| --- | --- | --- |
| `schemaVersion` | `"0.1"` | Contract version |
| `subjectId` | string | Fictional ID for the demo |
| `timestamp` | string | UTC ISO-8601 date-time ending in Z |
| `synthetic` | boolean | Required provenance on each sample |
| `heartRateBpm` | number or null | Beats/minute |
| `spo2Percent` | number or null | Oxygen saturation percent |
| `respiratoryRatePerMin` | number or null | Breaths/minute |
| `sleepHours` | number or null | Hours in preceding 24 hours; illustrative fixture summary |
| `fatigueScore` | number or null | Illustrative 0–10 index; higher means more fatigue |
| `hydrationPercent` | number or null | Illustrative 0–100 index; not body water or measured hydration |

All fields are required, with null for unavailable values. Numeric schema bounds are shape constraints, not clinical thresholds. These JSON numbers are not strings with units. See the adjacent example JSON. The current fixture has 12 samples spaced five minutes apart; its daily summaries repeat across the short session deliberately.

Proposed error envelope: `{ "error": { "code": "SUBJECT_NOT_FOUND", "message": "Unknown subject" } }`. Proposed statuses: 404 unknown subject, 422 invalid query, 500 internal error. Network failure, invalid payloads, missing readings, and stale timestamps require explicit frontend states before API mode ships. Do not present an old fixture as current telemetry.

Open questions: acceptable sampling cadence and staleness policy; how daily summaries are aggregated; hydration and fatigue definitions; server-side validation library; CORS origin; authentication if scope expands; alert schema and evidence. Ali owns alert design, so no alert algorithm, threshold, or endpoint is invented here. Ayoub must approve scientific interpretation. Radiation is deferred.
