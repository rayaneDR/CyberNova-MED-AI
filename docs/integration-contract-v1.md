# Integration contract v1 — proposed, 2026-11-14

This document began as a proposed design. As of the current `feature/backend-rayane` work, FastAPI/SQLite implements the MVP routes, the frontend supports explicit Live API mode, and the actual OpenAPI response schemas are available at `/openapi.json`. The design remains the scientific and normalization reference; use the running OpenAPI document as the authoritative wire shape where implementation details differ. This integration preserves `shared/contracts/` and teammate modules. Main remains unmerged. Rayane owns backend and frontend integration; Amina owns simulation, Ali owns baselines/statistics, and Ayoub owns scientific review.

## Decisions incorporated from Ayoub

**New canonical fatigue uses Samn–Perelli 1–7, integers only.** This is the team's proposed MVP instrument, not a NASA mandate. Preserve source-specific 1–10 records with their declared scale; never rescale, relabel a score of 2 as 1–7 merely because it fits, or pool the two instruments in one baseline. The frontend form and adapter now create explicit `samn_perelli_1_7` records. Previously saved browser records keep their 1–10 values and display a legacy label; reads do not rewrite storage. The original telemetry fixtures remain legacy illustrative indices.

Scientific reference: Samn, S. W. and Perelli, L. P., *Estimating Aircrew Fatigue: A Technique with Application to Airlift Operations*, USAF School of Aerospace Medicine, SAM-TR-82-21, December 1982, accession AD-A125319. The indexed text of the official [NASA bibliography](https://ntrs.nasa.gov/api/citations/19830027362/downloads/19830027362.pdf?attachment=true) identifies that report; the full bibliography exceeded the web retrieval size limit. The original DTIC PDF endpoint was unavailable during this review; it is not claimed to have been read. [NASA/TM-2012-216053](https://ntrs.nasa.gov/citations/20130001718), PDF page 18 / printed page 13, explicitly describes a subjective 1–7 scale in an airline fatigue study. The NASA PDF was downloaded and its relevant page inspected locally after web timeouts. This supports documented use, not a universal astronaut or NASA/BHP requirement. Form endpoints show fully alert at 1 and completely exhausted at 7; no operational fitness decision or automatic cutoff is implemented. Fatigue is assessed **now**, while sleep and intake describe the preceding reporting window.

**Canonical radiation has two accumulated quantities:**

| Canonical quantity | Meaning | Unit | Required temporal definition |
| --- | --- | --- | --- |
| `daily_exposure_dose_msv` | Total simulated dose over a completed 24-hour interval | mSv | Explicit UTC start/end exactly 86,400 elapsed seconds apart |
| `cumulative_mission_dose_msv` | Total simulated dose since this mission began | mSv | Start equals registered mission start; end is the accumulation cutoff |

The record's `quantity` discriminator carries these names and its numeric amount is `value`. Retain dose basis separately; mSv alone does not establish effective dose, organ dose, or a validated dosimeter quantity. Daily periods are defined elapsed UTC intervals, not implicit calendar months or local midnight. Mission cumulative dose never resets at a month boundary. Source-only records `source_dose_rate_msv_day`, `source_interval_dose_msv`, and `source_cumulative_dose_msv` preserve information that cannot yet meet these canonical accumulated definitions.

Amina's `dose_equivalent_rate_msv_day` is a **rate**, retained as `source_dose_rate_msv_day`, unit `mSv/day`; it cannot fill a daily-dose chart. Ayoub's daily-dose value has no exact interval and initially becomes `source_interval_dose_msv`, unit `mSv`, with an unknown window. Both supplied cumulative values lack a documented mission-start history and initially become `source_cumulative_dose_msv`, not a certified complete mission total. Attach warnings, retain the original labels, and show “period/origin unconfirmed” if displayed. Do not discard the originals or rewrite Amina's format.

Derivation may be added only after Amina and Rayane agree actual event intervals, rate interpretation and dose basis, maximum gap, and mission-start offset. Proposed method, if approved: piecewise-constant integration `dose_msv = Σ(rate_msv_per_day × covered_seconds / 86400)`. Store method, source-reading IDs and covered interval in derived-record provenance. No integration across uncovered gaps, duplicate intervals, or conflicting quantities; an incomplete day remains incomplete, never scaled to a full day. Do not infer the interval from CLI defaults: the current script increments its own cumulative value using a hard-coded five seconds per packet. A negative cumulative delta is a source consistency issue, not a monthly reset or “negative radiation.”

## Names, identity, time, and validation

Use snake_case JSON fields, server-generated UUID record IDs, UUID mission IDs, aware timestamps serialized to UTC `Z`, finite JSON numbers, and explicit null for missing/invalid/conflicting measurements. `docs/contracts/v1_design.py` is executable Pydantic design documentation; its adjacent generated schemas describe the seven requested models plus write-input variants. They do not implement ingestion, API routes, analytics, or storage. Use Pydantic after JSON Schema checks: cross-field validators are not fully expressed in generated JSON Schema.

- `Astronaut`: `id`, `mission_id`, `display_name`, `role`, `aliases[{namespace,value}]`, `synthetic:true`. A mission has a configured start timestamp and per-source session bindings. Alias uniqueness is `(mission_id, namespace, value)`.
- `Measurement`: `MeasurementInput` plus `id` and `provenance`. Input includes `astronaut_id`, `mission_id`, nullable positive `mission_day`, `observed_at`, `synthetic:true`, activity enum, and the three core readings. Canonical names/units: `heart_rate_bpm` / bpm; `spo2_percent` / percent; `respiratory_rate_per_min` / breaths/min. A reading contains `value`, exact `unit`, `quality`, and nonempty `source_paths`.
- `CheckIn`: `CheckInInput` plus `id`/provenance. `report_kind` is `user_demo`, `source_snapshot`, or `simulator_snapshot`; submission timestamp and reporting window are distinct from source observation time. Sleep is `sleep_hours` (0–24), intake is `hydration_intake_ml` (0–10,000 input limit), notes ≤500 characters. Canonical `fatigue` is nullable `{value:1..7,scale:"samn_perelli_1_7",source_scale_label,assessed_at}`. `legacy_fatigue` separately holds original 1–10 scores; it never populates canonical fatigue. New user reports require all three core inputs, submission time, a reporting window, and a fatigue assessment timestamp. Legacy/source snapshots may have unknown windows/times; do not manufacture them from a packet timestamp.
- `RadiationReading`: `RadiationInput` plus `id`/provenance; see quantity table above. Also includes quality, dose basis, integration window, method and source paths. Daily-dose validation requires a complete 24 hours; mission cumulative validation additionally needs the registered mission start and source coverage, enforced by the application/database layer. The supplied file cannot establish this.
- `SensorHealth`: separate channel-quality record linked by `measurement_id`, with source-reported status/hardware claims, issue codes, connectivity, last sample time, and last non-null sample time. A missing reading is known missing data; it is not proof of disconnected hardware. Without connection metadata, connectivity is `unknown`. “Non-null” does not mean clinically valid or recent.
- `StatisticalObservation`: Ali-produced only; links to actual measurement IDs and baseline ID; carries method (`median_mad`/`ewma`), algorithm version, metric, score, context, detection time and explanation. No record is emitted when Ali's module is unavailable. Simulator scenario labels never become these records.
- `ResearchSource`: URL, agency, source version, locator, accessed time, narrowly supported claim, limitation, independent verification state, original `source_claimed_verification`, `used_as_dataset:false`, `active_for_evaluation:false`. Evidence status is claim-specific, never copied wholesale from `VERIFIED`.

All stored records link to immutable ingestion provenance: format, run/import session UUID, external record ID, optional source transmission time, server receipt time, ingest UUID, and exact-body SHA-256. Keep original raw payload bytes separately, including unsupported channels; do not mix unmodeled clinical fields into active MVP analysis.

Identity is explicit: `AST-001`, `AST-01`, and `demo-crew-01` are **not automatically the same person**. Register aliases only after Rayane/Ayoub/Amina confirm them. Until then, use separate source-specific fictional subjects and missions, or reject unresolved aliases. Preserve mission days 14 and 142 as supplied; never rewrite day 142 to fit the UI's day-14 mission. Reject a session/mission/alias mismatch with 422.

Quality states: `unverified` (a structurally accepted value, not clinical verification), `missing`, `invalid`, `conflict`. Non-unverified readings have canonical `value:null`; raw input remains available for review. Percent bounds 0–100, nonnegative rates, finite numbers, known unit spellings and type checks are structural checks, not health thresholds. Reject numeric strings, booleans as numbers, NaN/Infinity, duplicate JSON keys, and malformed/naive timestamps. Zero is a retained value when structurally allowed, never a missing sentinel; no clinical conclusion is inferred. Values outside agreed schema constraints are quarantined by channel with a warning. Missing a required envelope/identity/unit is a request-level 422, not a fabricated null.

## Source adapters

| External path (relative to indicated source) | Canonical target / transformation |
| --- | --- |
| Ayoub root `astronaut_id` / simulator `ingestion_payload_contract.ingestion_context.astronaut_id` | Resolve through the session's namespaced alias registry; preserve original string |
| Ayoub root `record_id` / simulator nested `payload_id` | External ID retained in provenance; not a global database primary key |
| Ayoub root `timestamp_utc` / simulator nested `timestamp_utc` | Measurement `observed_at`; preserve original text and normalize aware offsets to UTC |
| Simulator `simulator.sent_at` | `provenance.source_sent_at`, not observation time; server adds receipt time |
| Both `mission_day` and `activity_context` | Preserve supplied day; enum RESTING/SLEEP/EXERCISE/EVA_PREP/EVA_ACTIVE. Missing activity becomes UNKNOWN with warning, not RESTING |
| Ayoub `automated_sensors.heart_rate.value` / simulator `telemetry_sensors.heart_rate_bpm.value` | `heart_rate_bpm.value`, identical number, bpm |
| Ayoub `.spo2.value` / simulator `.spo2_percent.value` and `.spo2` | `spo2_percent`, percent; `%` normalized only after verifying source format |
| Ayoub `.respiratory_rate.value` / simulator `.respiratory_rate_rpm.value` and `.respiratory_rate` | `respiratory_rate_per_min`, breaths/min. The simulator's rpm spelling has this source-specific meaning only |
| Ayoub sensor status VALID/hardware string | Preserve source report/claim in SensorHealth; quality remains unverified after structural checks |
| Simulator no status or hardware metadata | Null source status/model, issue STATUS_UNREPORTED, connectivity unknown; mode does not identify faulty channels |
| Ayoub `manual_checkin.submitted` | Preserve assertion; `source_snapshot`, actual `submitted_at:null` unless independently supplied |
| Ayoub fatigue value 2 / scale label 1-to-7 | Canonical 2/7 with original scale label, assessed time unknown; proposed mapping approved by latest team instruction, no NASA-mandate claim |
| Simulator `fatigue_score_1_10` | `fatigue:null`; `legacy_fatigue` retains original score and 1–10 scale |
| Ayoub sleep hours / intake ml | Copy values to hours/mL; reporting window unknown unless separately documented |
| Simulator sleep hours / intake `_ml_24h` | Copy values; label simulator snapshot, retain stated 24h duration but exact window unknown; do not create a human submission |
| Source radiation fields | Preserve by quantity as described above; no mSv/day → daily mSv conversion without integration metadata |
| HRV, BP, ECG, core temperature, ocular, symptoms, medications, proton flux, source limits | Raw archival/source metadata only in this MVP; no derived clinical rules or medication recommendations |

Repeated aliases must agree numerically including null consistency. A conflicting alias makes the affected canonical channel null/quality conflict with both paths recorded. Do not prefer `.value` over an alias simply because it appears first. The simulator has reproduced conflicts under hypercapnia/ischemia/infection/QT scenarios. Extra ECG aliases are still recorded as raw warnings, without implementing ECG analytics. Do not silently recompute inconsistent mean arterial pressure and overwrite source data.

## API conventions

Proposed local base: `http://localhost:8000`, using the unprefixed routes requested below. These routes are now implemented and documented by the live OpenAPI spec; schema examples in this section remain normative design examples and are not guaranteed to match every response envelope byte-for-byte. JSON only, body ≤1 MiB, UTC timestamps, same-object schemas for canonical write bodies/read objects. `application/json` writes require an explicitly registered `source_session_id` UUID query parameter binding mission, permitted aliases, source format and synthetic provenance. It is not an authentication secret. The seed/admin CLI registers local demo sessions; no public registration endpoint is implied.

Canonical writes also require `Idempotency-Key: <UUID>`. Source raw records use their record ID; simulator packets use nested payload ID. Server uniqueness: `(source_session_id, source_record_id)`. Exact-byte replay returns HTTP 200 and the original receipt/resources; same key with different bytes returns 409. Preserve simulator sequence as metadata, never as a global key. Start a new run/session UUID on simulator restart, even on the same day. Retried identical packets reuse the same session and ID. Out-of-order event times are accepted and stored as historical; they cannot overwrite “latest” by receipt order.

Successful new writes return 201 **only after one atomic durable transaction** stores the raw ingest, canonical resources, health rows and warnings. A partial channel-quality issue can return 201 with accepted-but-quarantined channel warnings; a malformed envelope is rejected before insertion. Storage failure returns 503, never a fake acceptance. Duplicate receipt returns 200 with `duplicate:true`. Because Amina accepts all 2xx without reading their body, do not use 202 for an unimplemented queue. Her current transmitter retries even 4xx and may block the stream; configure identity/format correctly before unattended runs.

Common error schema:
```json
{"error":{"code":"VALIDATION_ERROR","message":"Unknown astronaut alias for source session","details":[{"path":"ingestion_context.astronaut_id","issue":"UNRESOLVED_ALIAS"}],"request_id":"REQ-demo"}}
```
HTTP 400 malformed JSON/duplicate keys, 401 absent/invalid configured auth, 404 missing resource, 409 idempotency/state conflict, 413 body too large, 422 semantic input error, 503 unavailable persistence. Error messages must not expose tokens or raw sensitive payloads. MVP is synthetic-only; `synthetic:false` is rejected. Local development can use loopback-only access; before shared deployment require a configured token for writes/acknowledgment, exact frontend CORS origin, and server-derived actor identity. Never embed a privileged token in NEXT_PUBLIC variables.

### Read parameters and list responses

`GET /astronauts` accepts required `mission_id:UUID` and standard pagination. Measurements/check-ins/radiation/alerts require `astronaut_id:UUID` and `mission_id:UUID`; optional aware `from` inclusive, `to` exclusive, `limit` integer 1–500 (default 100), and opaque `cursor`. Reject `from >= to` or an invalid/mismatched cursor with 422. Order ascending by `(observed_at,id)`; alerts use `(detected_at,id)`. Cursor binds filter, sort and a receipt-time snapshot, so late inserts do not change an existing paginated snapshot. A fresh first-page read includes later ingests. No offset pagination or invented hourly samples. The frontend paginates to exhaustion as needed or explicitly labels partial data.

Common list: `{"items":[<typed objects>],"next_cursor":null,"synthetic":true}`. Empty is a 200 with `items:[]`; service failure is not an empty list. Astronauts sort by ID. Add `report_kind` and `fatigue_scale` check-in filters; `quantity` radiation filter; `kind=sensor_data_issue|statistical_observation` and `acknowledged` boolean alert filters. Reject unknown enum values.

### Required and optional endpoints

| Endpoint | Exact request/response design | MVP priority |
| --- | --- | --- |
| `GET /health` | No body/query. 200 `{status:"ok",contract_version:"1.0.0",storage:"ready",analytics:"ready",synthetic_only:true}`. 503 `{status:"unavailable",contract_version:"1.0.0",storage:"unavailable",analytics:"ready",synthetic_only:true}` | Required readiness |
| `GET /astronauts` | Mission UUID + pagination; common list of Astronaut | Required |
| `POST /measurements` | `source_session_id`, required `input_format=canonical_v1|ayoub_raw_v1`; body MeasurementInput or unchanged Ayoub raw JSON. Format must match registered session. Canonical requires Idempotency-Key. 201/200 receipt below. Raw import can atomically add source check-in/radiation snapshots too | Required canonical writes; Ayoub import required compatibility |
| `GET /measurements` | Common filters/list of exact Measurement objects; top-level `sensor_health:SensorHealth[]` contains health records linked to this page's measurement IDs. It is an envelope extension, never an extra field inside a strict Measurement object | Required |
| `POST /ingest/simulator` | `source_session_id`; unchanged complete Amina envelope, not just its nested payload. Optional configured Bearer token. Receipt 201/200 | Required simulator integration |
| `POST /checkins` | `source_session_id` + Idempotency-Key; CheckInInput; ordinary user path requires report_kind=user_demo and canonical 1–7 fatigue, legacy_fatigue=null. Returns 201 `{item:CheckIn,duplicate:false}`; replay 200 same record/duplicate true | Required |
| `GET /checkins` | Common list of CheckIn, including scale/source fields. Snapshot records must remain distinguishable from human submissions | Required |
| `POST /radiation` | `source_session_id` + Idempotency-Key; RadiationInput. Returns 201 `{item:RadiationReading,duplicate:false}`, replay 200 same item/duplicate true. Source-only vs completed-dose classification is validated | Optional manual/import path; ingestion already stores radiation |
| `GET /radiation` | Common list of RadiationReading; default canonical daily/cumulative only; explicit quantity filter needed for source-only values. Unknown-period/source-only values never fill completed-day charts | Required |
| `GET /analytics/summary` | Required astronaut/mission and optional from/to. 200 summary below; no invented median/MAD/EWMA results | Required honest frontend availability contract; statistical results optional pending Ali |
| `GET /alerts` | Common filters/list of AlertEnvelope below; returns analytics and baseline status. Sensor data issues can appear independently from sustained statistical observations | Required history/status surface |
| `PATCH /alerts/{alert_id}/acknowledge` | UUID path, body AcknowledgeInput `{acknowledged:true,note:string≤500}`. Server derives actor/time. 200 `{item:AlertEnvelope}`; repeat by same actor is idempotent and keeps first ack time. 404 unknown, 409 incompatible state | Optional for first ingestion demo; required before claiming persistent review |

Simulator request shape checks: root project string, simulator object with `mode` normal/anomaly/failure (auto outputs chosen mode), nullable scenario string (authoring metadata only), finite ramp 0–1, positive sequence fitting signed SQLite int64, aware sent_at. Require nested ingestion context with nonempty payload/astronaut IDs, positive mission_day, aware timestamp; telemetry/radiation objects; optional snapshot fields may be absent/null. Required telemetry channel nodes need unit strings; their values can be null; alias/value disagreement is a channel issue. Preserve unrecognized source fields in raw JSON; do not treat them as new canonical metrics or execute rules. This is a version-pinned adapter for the supplied unversioned packet format.

Receipt schema: `ingest_id:UUID`, `duplicate:boolean`, `synthetic:true`, `measurement_ids:UUID[]`, `checkin_ids:UUID[]`, `radiation_ids:UUID[]`, `warnings:{code:string,path:string,message:string}[]`. Shape/provenance warnings are not medical alerts. Each ingest's original receipt is stable on retry.

AlertEnvelope: `{id:UUID,astronaut_id:UUID,mission_id:UUID,detected_at:UTC,kind:"sensor_data_issue"|"statistical_observation",synthetic:true,sensor_health:SensorHealth|null,statistical_observation:StatisticalObservation|null,acknowledgment:null|{actor_id:string,acknowledged_at:UTC,note:string}}`. Exactly one payload matches kind. Sensor alerts refer to a genuinely observed missing/invalid/conflicting channel, not scenario labels or a claimed diagnosis. Acknowledgment is operational review, not treatment, medical resolution, or a change to source quality. Deduplicate sensor issues by ingest/channel/code; no invented “resolved” status from acknowledgment.

### Example requests/responses (proposed, not executed against a backend)

Full canonical write/read examples for every model are in `contracts/examples-v1.json`. IDs below are illustrative; register actual session/alias bindings first.

```http
GET /health
```
```json
{"status":"ok","contract_version":"1.0.0","storage":"ready","analytics":"ready","synthetic_only":true}
```
```http
GET /astronauts?mission_id=11111111-1111-4111-8111-111111111111
GET /measurements?mission_id=11111111-1111-4111-8111-111111111111&astronaut_id=22222222-2222-4222-8222-222222222222&limit=100
GET /checkins?mission_id=11111111-1111-4111-8111-111111111111&astronaut_id=22222222-2222-4222-8222-222222222222&report_kind=user_demo
GET /radiation?mission_id=11111111-1111-4111-8111-111111111111&astronaut_id=22222222-2222-4222-8222-222222222222&quantity=daily_exposure_dose_msv
GET /alerts?mission_id=11111111-1111-4111-8111-111111111111&astronaut_id=22222222-2222-4222-8222-222222222222&kind=statistical_observation
```
Each list uses the common envelope; object items are instances of the named schema. For unavailable statistical observations:
```json
{"items":[],"next_cursor":null,"synthetic":true,"analytics_status":"ready","baseline_status":"insufficient_baseline"}
```
No-observation is not equivalent to a “healthy” astronaut.

```powershell
# Preserve supplied bodies; these commands are examples for the future service.
curl.exe -X POST 'http://localhost:8000/measurements?input_format=ayoub_raw_v1&source_session_id=33333333-3333-4333-8333-333333333333' -H 'Content-Type: application/json' --data-binary '@C:/Users/rayan/Downloads/raw_measurements.json'
python 'C:/Users/rayan/Downloads/simu (1).py' --mode normal --count 5 --interval 1 --astronaut-id AST-01 --mission-day 142 --endpoint 'http://localhost:8000/ingest/simulator?source_session_id=44444444-4444-4444-8444-444444444444'
```
The simulator's first packet can yield:
```json
{"ingest_id":"55555555-5555-4555-8555-555555555555","duplicate":false,"synthetic":true,"measurement_ids":["66666666-6666-4666-8666-666666666666"],"checkin_ids":["77777777-7777-4777-8777-777777777777"],"radiation_ids":["88888888-8888-4888-8888-888888888888","99999999-9999-4999-8999-999999999999"],"warnings":[{"code":"LEGACY_FATIGUE_SCALE","path":"manual_checkin.fatigue_score_1_10","message":"Retained as 1–10; canonical fatigue is unavailable"},{"code":"RADIATION_PERIOD_UNCONFIRMED","path":"radiation_dosimetry_sensors","message":"Rate and cumulative source values are not completed canonical daily/mission doses"}]}
```

Canonical measurement write: POST `/measurements?input_format=canonical_v1&source_session_id=<session-uuid>`, JSON body `examples-v1.json:MeasurementInput`, Idempotency-Key UUID. Returns the receipt envelope. POST `/checkins?source_session_id=<session-uuid>` uses `CheckInInput` example and returns `{item:<CheckIn example>,duplicate:false}`. POST `/radiation?source_session_id=<session-uuid>` uses `RadiationInput` example and returns `{item:<RadiationReading example>,duplicate:false}`. These exact request objects are machine-readable examples, not placeholders for source-converted data.

```http
GET /analytics/summary?mission_id=11111111-1111-4111-8111-111111111111&astronaut_id=22222222-2222-4222-8222-222222222222
```
```json
{"astronaut_id":"22222222-2222-4222-8222-222222222222","mission_id":"11111111-1111-4111-8111-111111111111","analytics_status":"ready","baseline_status":"insufficient_baseline","statistical_observations_count":0,"latest_measurement_at":null,"algorithm_version":"personal-baseline-mad-ewma-v1","configuration":{"history_window":30,"minimum_baseline":8,"robust_z_threshold":3.5,"baseline_guard_z":2.5,"ewma_alpha":0.25,"ewma_z_threshold":3.0,"required_consecutive":3,"dispersion_floors":{"heart_rate_bpm":1.0,"spo2_percent":0.1,"respiratory_rate_per_min":1.0}},"metrics":[],"synthetic":true}
```
`latest_measurement_at` may contain the actual stored latest event timestamp; it remains null for no data. The current Rayane-owned integration calls the isolated, credited analytics implementation described in `../docs/analytics-integration.md`. The response includes explicit per-metric/activity baseline counts and configuration; insufficient baseline is not a nominal result. Parameters are for a synthetic engineering demonstration and do not activate health thresholds.

```http
PATCH /alerts/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/acknowledge
Content-Type: application/json
Authorization: Bearer <configured-user-token>

{"acknowledged":true,"note":"Reviewed sensor-data quality"}
```
Response: `{item:<same AlertEnvelope with acknowledgment populated from authenticated actor/server time>}`. `acknowledged:false` is rejected; no unacknowledge operation is proposed. Unknown IDs return 404, never create an alert.

## Backend-to-frontend mapping

The implemented frontend adapter/types leave source modules intact. Preserve mock mode as an explicit demo choice; API error must show an error, not silently invoke getWorkspaceData fixtures.

| Current frontend field/behavior | v1 mapping / necessary UI adjustment |
| --- | --- |
| Astronaut id/name/role/initials | API UUID/display_name/role; derive initials from display name. Mock IDs are separate aliases until explicitly linked |
| `heartRateBpm`, `spo2Percent`, `respiratoryRatePerMin` | Canonical reading values; preserve quality separately and show null as unavailable. Do not convert missing into zero |
| `timestamp`, activity, quality | observed_at UTC; keep full activity enum instead of collapsing EVA/SLEEP/UNKNOWN into Lab work; replace binary Complete/Signal gap with channel-specific quality labels |
| Global mission day/name | Registered mission/source metadata; no UI day-14 overwrite of a day-142 source |
| Sleep/fatigue/hydration on telemetry fixture | Read independently from eligible CheckIn; do not copy most recent report onto every historical sample. Show report time/window and unavailable where no suitable report exists |
| Check-in `fatigueScore` | 1–7 canonical input with explicit scale. Legacy histories are separately labeled `/10`; legacy telemetry fixture scores remain illustrative `/10` |
| `hydrationPercent` | No mapping from mL intake. Show intake in mL or unavailable index; never compute a percentage from arbitrary targets |
| Sensor connected/available labels | Known source quality, last sample, unknown connection metadata; recorded/non-live labels remain until a live contract is built |
| Mock observations/resolved | Separate operational data-quality issues from Ali-produced statistical observations; acknowledgment never means medically resolved |
| Radiation `dailyMicroSv` / µSv/day chart | Replace with canonical accumulated `daily_exposure_dose_msv`, mSv and explicit 24h windows. Source rate gets a separate rate label, not a daily-dose point. Source cumulative history stays unverified until origin is known |
| Cumulative exposure | Use mission-bound canonical cumulative totals when available; no month reset. Do not re-sum source cumulative totals or double-count a day |
| NASA cards | Reviewed source claims/limitations; no NASA dataset analyzed unless an actual versioned dataset pipeline is added and documented |

The current Live frontend maps canonical accumulated radiation dose and mission cumulative dose independently from source dose rates. Demo mode retains its clearly labeled synthetic rate fixture. Check-in form and API persistence use Samn–Perelli 1–7; source 1–10 remains source-specific.

## Science activation and unresolved review

All `evaluation_rules.json` rules remain disabled, including entries named active_mvp_rules. Preserve original verification labels as source claims. NASA/CSA contextual sources are references, not analyzed datasets. Source-review details and radiation category corrections are in source-file-review.md. Required team decisions: confirm identity/mission aliases; actual Samn–Perelli item wording/protocol; source snapshot windows and fatigue assessment times; valid sensor statuses; simulator alias/fault metadata fixes; real time integration and mission origin; dose basis and source uncertainty. Ali must specify sample minima/windows, activity conditioning, MAD=0 behavior, EWMA parameters, baseline versioning, missing-data handling, and statistical observation schema before analytics is enabled. No backend, simulator scenario, or AI text may autonomously diagnose or recommend medication/treatment.

## Design validation

Run `python docs/contracts/v1_design.py` to generate schemas. `python work/validate_contract_design.py` from the original workspace validates every example using installed Pydantic 2.14.1, exercises required rejection cases, and checks JSON syntax. These are contract-design tests, not API/database or clinical tests. The original design-review note made no live backend success claim; implementation and local runtime verification are recorded separately in the integration task report.

Actual results: eleven example models validated; twenty positive/negative cases passed; eleven generated JSON Schema documents parsed. An independent JSON Schema engine was not available, so no claim of separate JSON Schema engine validation is made. `node work/test_fatigue_boundary.cjs` passed canonical bounds, legacy preservation, read-without-rewrite and scale-tagged submission checks. A production Playwright check verified exactly seven choices, legacy /10 history, a saved /7 report, and no overflow at 390px. `npm run lint`, `npm run typecheck`, and `npm run build` all passed. The first schema-generation attempt used the wrong working directory and failed; the corrected repository-root command succeeded before these validation results were reported.
