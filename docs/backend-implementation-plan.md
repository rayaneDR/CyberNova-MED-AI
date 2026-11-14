# Backend implementation plan — next task, not implementation

## Starting point and boundaries

Use `feature/backend-rayane`, based on `72d9bcd` (complete frontend MVP). Remote main is still `24c1046`; no automatic merge, reset, or history rewrite is authorized. The existing untracked source-review draft was preserved, reread, and its source/syntax checks rerun. This task adds contract documentation/design schemas and the specifically requested frontend fatigue correction only. The four Downloads originals, teammate modules, old shared contract and original frontend branch remain intact.

Rayane now owns backend/, FastAPI, SQLite, frontend integration, deployment and coordination. Khawla's old placeholder documentation reflects an earlier assignment and is not modified here. Amina continues to own simulator/, Ali analytics/, and Ayoub research/. Do not copy a rewritten simulator or implement an approximation of Ali's mathematical module to fill a missing dependency.

## Decisions already settled

- Canonical MVP fatigue: proposed Samn–Perelli 1–7, integer only. Preserve 1–10 separately; no conversion or mixed-scale baselines. New frontend local records include explicit scale; old browser records remain labeled legacy.
- Canonical radiation: completed 24-hour accumulated dose and cumulative dose since mission start, both mSv. Rates remain source rate records. No unknown-period daily dose or random-origin source cumulative total may masquerade as a complete canonical accumulated dose.
- Synthetic-only MVP. Every ingress must carry trusted synthetic provenance from its registered source session; real-data mode is outside scope.
- No scientific rule is auto-activated. Missing analytics is reported as unavailable/not_configured, never fabricated healthy/nominal output.

## Ordered implementation slices

### 1. Resolve integration configuration, then create the thin backend shell

Confirm source-specific identity mappings and missions with Rayane/Amina/Ayoub. Do not guess that AST-001 = AST-01 = demo-crew-01. Register mission start, aliases, format version, and a new run UUID for each simulator process. Unresolved bindings can be kept as separate fictional subjects; they block combined-person views, not syntax review.

In the next task, add `backend/app/` with settings, database connection, models/schemas and application entry point, plus `backend/tests/`. Choose Python 3.12 and pin compatible FastAPI, Pydantic v2, Uvicorn and pytest versions after checking the actual environment. Prefer SQLite's standard-library driver and explicit migrations for this small demo; do not add a second ORM without a concrete need. Bind development to loopback; configure exact frontend CORS origin. Add a server-only `.env.example` without credentials. A write token must be configured before shared hosting; no privileged frontend NEXT_PUBLIC token.

Acceptance: reproducible environment install, migration/init command, `GET /health` returning storage readiness accurately, and no unimplemented imports from teammate modules.

### 2. Persist immutable ingress and stable identity first

Create tables for missions, astronauts, namespaced aliases, source sessions, ingest receipts/raw bodies, measurements, per-channel sensor health, source check-in snapshots/user check-ins, radiation readings, and operational alert acknowledgments. Reserve statistical-observation storage/interface for Ali without generating fake records. Research metadata can stay a reviewed registry, never an executable rules engine.

Essential constraints/indexes:

- Unique alias `(mission_id,namespace,external_id)` and source session UUID; foreign keys enabled.
- Unique `(source_session_id,source_record_id)` with exact-body SHA-256, persisted original receipt, sequence metadata, and receive/event timestamps.
- Measurement/time indexes `(mission_id,astronaut_id,observed_at,id)`; separate observation/detected-time indexes.
- Source-derived resource IDs/ingest links written atomically so retries cannot duplicate check-ins or radiation.
- WAL/busy timeout for concurrent demo reads/writes; explicit transactions, rollback on partial failure, test-backed schema versioning.

Acceptance: same packet replay returns original IDs; changed bytes with same key return 409; restart/new run cannot collide; failed transaction leaves no half-ingested records; event time determines latest values, not HTTP arrival order.

### 3. Implement adapters without changing Amina's files

Implement `canonical_v1`, `ayoub_raw_v1`, and `amina_simulator_v1` adapters in backend/. Keep raw payloads immutable. Validate body size, JSON duplicate keys/non-finite values, types, dates/units and session bindings. Preserve activity and missing data. Normalize spelling only for agreed equivalent units. Channel alias conflicts become canonical null/quality conflict with both source paths retained. Document unsupported raw channels instead of silently applying clinical thresholds.

Source snapshot fatigue 1–10 is never converted. Ayoub's 1–7 field maps under the latest team decision with its original label retained; no NASA-mandate claim. Source daily-dose records without windows and source cumulative values without mission origins stay explicitly source-only. Do not implement rate integration until the assumptions and source defects are resolved.

Acceptance: fixtures cover the actual four supplied files, all observed alias mismatches, nulls, zeros, invalid units, day/identity mismatch, timestamp offsets, mode/quality independence, and exact source provenance. The raw rules JSON is not executed.

### 4. Ship ingestion plus core read APIs as one vertical slice

Implement `/astronauts`, `/measurements`, `/ingest/simulator`, `/checkins`, and `/radiation` contracts from integration-contract-v1.md. Return 201 only after durable acceptance and 200 on exact replay. Enforce canonical Samn–Perelli validation on user reports, while source snapshots remain distinctly typed. Cursor reads need stable filters/order/snapshot semantics; return explicit empty lists and proper errors.

Use the unchanged simulator CLI with `--endpoint 'http://127.0.0.1:8000/ingest/simulator?source_session_id=<registered-run-uuid>'`. The endpoint URL carries the run UUID because the current CLI cannot add custom session headers. Use a bounded count and explicit source astronaut/mission day. Document that the original transmitter retries permanent 4xx and exits zero even with unsent data; do not call process exit zero proof of successful ingestion.

Acceptance: actual unchanged CLI packet reaches SQLite, duplicate delivery is safe, GET retrieves its canonical representation, and known source-only radiation/fatigue limitations remain visible.

### 5. Add honest analytics availability and operational observation surfaces

Implement `/analytics/summary` as not_configured until Ali provides a stable callable contract. `/alerts` may expose actual sensor data issues without claiming physiological deviation; statistical observations remain empty/unavailable. Add acknowledgment persistence when needed; server identity/time are authoritative, acknowledgments never resolve medical status or alter sensor values.

Ali supplies baseline scope, window/minimum samples, activity conditioning, median/MAD handling including zero MAD, EWMA parameters, score definitions, algorithm versioning and sufficient/insufficient-data behavior. Integrate his implementation as supplied, with his tests, rather than recreating it in backend/. Amina's diagnosis-like scenario names stay authoring metadata and never become conclusions.

### 6. Connect the existing frontend through its adapter

Keep explicit mock/API modes and distinguish both in the UI. Add runtime response validation and AbortSignal support; fetch real UUID subjects, paginate historical data deliberately, and retain timestamps/quality. Extend the frontend's activity/quality types rather than collapsing unknown/EVA/sleep into Lab work or Complete. Handle loading, empty, stale and failed API requests without a silent fixture fallback.

Wire canonical check-in submission/history; do not silently upload browser-local legacy reports. Require an explicit demo migration if the team wants it. Keep fatigue scale in every record and display denominator correctly. Display hydration intake in mL without inventing a hydration percentage. Update radiation UI to `daily_exposure_dose_msv` (mSv over a stated 24 hours) and mission cumulative mSv; render source rates separately or mark canonical series unavailable. Remove monthly-reset assumptions and avoid summing already-cumulative values. Existing fixture values are not converted to Samn–Perelli merely because they are numerically small.

Acceptance: all six routes still work; errors/sensor failures are distinct; real backend values are visible; no fake Ali observations; fatigue and radiation labels preserve their scientific meaning. Run lint, typecheck and production build, plus desktop/mobile interaction tests.

### 7. Verify end-to-end, document, and prepare review

Tests must include actual request/response validation, durable SQLite reads, replay/conflict, transaction rollback, missing and corrupt data, source-ID/run collisions, cross-mission filters, canonical/legacy fatigue isolation, exact 24-hour radiation windows, cumulative mission origin/month continuity, and aliases conflicting under the actual simulator scenarios. Do not assert live HTTP success from the temporary review receiver or syntax-only validation.

Before deployment, confirm source claims/rule activation with Ayoub and baseline outputs with Ali; keep all thresholds disabled unless separately reviewed and justified. Radiation stays visualization/tracking only. Preserve real source version, quantity, organ/tissue, exposure category and duration if any standard limit is documented. No autonomous diagnoses or treatment recommendations.

Commit in small slices on the feature branch, report exact commands/results and remaining blocked inputs, and request review before merge. No automatic merge into main.

## Source-owner handoff requests

| Owner | Specific unresolved input |
| --- | --- |
| Amina | Agree aliases/mission binding and run identity; synchronize aliases; emit per-channel quality/fault metadata; preserve actual event intervals; correct fixed-five-second cumulative integration and transient scenario cumulative jumps; keep original supplied file unchanged pending her revision |
| Ali | Deliver versioned callable inputs/outputs, baseline definitions, statistical method settings, minimum samples, missing/invalid/legacy-scale exclusions and tests |
| Ayoub | Confirm 1–7 wording/assessment protocol and source labels; review exact source locators and dose basis; clarify 24-hour source reporting periods and mission start; resolve conflated radiation categories; supply evidence for any proposed active rule |
| Rayane | Confirm roster aliases and missions, approve API contract, source sessions, local/shared deployment/auth scope, frontend adapter migration and review order |

## Work completed in this review

All supplied file bytes and Python lines were read. Strict JSON parsing, Python AST/bytecode syntax checks, CLI modes/scenarios/faults, and bounded loopback POST/retry behavior were executed. Original hashes remained unchanged. Contract-design schemas/examples and focused fatigue frontend checks are documented with actual results in the integration/source-review documents. These results do not constitute backend, analytics, scientific or deployed-system certification.
