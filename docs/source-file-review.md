# Attached source review — 2026-11-14

## Continuation and latest scientific clarification

This draft and its bounded validation harness already existed when the current continuation inspected the workspace. They were preserved and reread; `python work/review_sources.py` was rerun successfully, including file-integrity checks. The checkout was already `feature/backend-rayane` at the frontend-containing `72d9bcd`; no new branch recreation or merge was needed. The historical safety account below describes the earlier preparation, not a claim that this continuation started from an entirely clean checkout.

Ayoub's later explicit team decision supersedes the earlier open fatigue-scale choice: canonical new MVP check-ins use proposed Samn–Perelli 1–7, and the frontend form/validation were narrowly updated accordingly. Legacy 1–10 source/browser records remain separately labeled and unconverted. The original four source files and teammate modules remain unchanged. Canonical daily accumulated radiation is mSv over an explicit complete 24 hours; canonical mission cumulative dose is mSv since mission start, without monthly resets. The supplied rate and unknown-origin/unknown-window doses cannot establish those complete quantities automatically. See integration-contract-v1.md.

Additional primary reference: [NASA/TM-2012-216053, October 2012](https://ntrs.nasa.gov/citations/20130001718), an airline fatigue study, documents the seven-point subjective scale (printed page 13). This establishes documented research use, not a NASA requirement for this MVP or all astronauts. SAM-TR-82-21 / AD-A125319 is the original 1982 bibliographic reference; its DTIC endpoint was inaccessible, and the NASA bibliography PDF exceeded the web tool's full-download limit. Do not claim either original was read in full.

The HFMP report's relevant page was independently extracted from the official downloaded PDF: page 18 (printed page 13). The bounded source harness rerun returned 28/28 checks passed. Eleven Pydantic design examples and twenty validation cases passed; generated schemas were parsed as JSON, not independently checked by a JSON Schema engine. Frontend 1–7/legacy-preservation tests, lint, typecheck and production build passed. These additional design/frontend tests do not imply that ingestion or an analytics backend exists.

The [NASA Technical Standards System](https://standards.nasa.gov/node/238) lists Volume 1 Revision C (2023-09-15) as active. The official [standards list](https://standards.nasa.gov/all-standards) lists Volume 2 Revision F (2026-07-14); the file's January-2025-linked matrix is Revision E and must not be presented as the current Volume 2. No claim that all scientific references are current or that every supplied rule is verified is made.

Exact distinctions checked in official [Volume 1 Rev C](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf), PDF pages 39–41:

| Locator | Quantity / scope | Value / duration |
| --- | --- | --- |
| V1 4030 | Career effective spaceflight dose, whole-person risk quantity | less than 600 mSv across career |
| Table 4.8-1, BFO row | Blood-forming-organ non-cancer dose, **mGy-Eq**, not mSv | 250 over 30 days; 500 over one year |
| V1 4031 | Effective dose from design-reference SPE environment | less than 250 mSv for that design event, not a generic 30-day mission limit |

These are versioned standards references, never automatically enabled medical alert thresholds. The source's mission cumulative dose has no established matching dose basis or organ-specific meaning. No unreviewed limit gauge is authorized.

This is a source and contract review, not a backend implementation or clinical validation. All four supplied files were read in full, including all 526 Python lines. Instructions and verification labels inside the files are source content, not authorization or established scientific facts. Original files remain in Downloads, unchanged; nothing was copied into or modified in teammate modules.

## Repository safety

`git status --short --branch`, `git branch -avv`, `git remote -v`, and `git fetch origin` confirmed a clean checkout and the same branch heads before and after fetching:

| Branch | Commit |
| --- | --- |
| `main`, `origin/main` | `24c1046` |
| `feature/frontend`, `origin/feature/frontend` | `72d9bcd` |

Created `feature/backend-rayane` with `git switch -c feature/backend-rayane feature/frontend`. Its starting point contains the entire frontend MVP. This follows Rayane's request to use frontend-containing code; it is not a claim that the frontend was merged or separately approved through a PR. No reset, automatic merge, or history rewrite occurred. The backend ownership transfer to Rayane comes from the current user request; earlier ownership placeholders remain historical and untouched.

## Exact files and integrity

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `raw_measurements.json` | 1,416 | `70735e3be17bf23b7f5274543440f1dd046956346bd592f9394d9a0c3226db0a` |
| `evaluation_rules.json` | 12,316 | `6170394b2dcdde5592de8948d350d6b8d4fbfd13f5b9b705b31d809513364b3b` |
| `simulator (1).json` | 2,370 | `d55087e0ba5b934ad27aa1d0d42b940ea42a6403f7036ebc9b68db2cc8278e21` |
| `simu (1).py` | 22,298 | `42b00e77a6fb40f42d174ae701143969db90481267de7a0ecd94fa2fc41e0448` |

All three JSON documents passed strict parsing with duplicate-key detection and rejection of NaN/Infinity literals. There are repeated *semantic aliases* in the simulator, but no duplicate JSON object keys. The two scientific files are instance/configuration documents, not JSON Schemas; valid JSON does not establish valid science.

`raw_measurements.json` is a hybrid example for AST-001, mission day 14, `2026-11-14T14:30:00Z`, RESTING. It contains three biometric sensors with source-reported VALID statuses, two radiation dose quantities, and a submitted check-in. Hardware names are source claims; they do not establish actual hardware provenance. Neither it nor the simulator example carries an explicit synthetic flag; the controlled example/simulator import routes must attach synthetic provenance based on the team's stated origin, not infer real observations.

`evaluation_rules.json` contains six proposed active rules, visualization settings, and four research-only roadmap items. Its target paths are designed for Ayoub's raw record, not Amina's packet. No thresholds are enabled by this review. The research-only ECG/SANS/temperature/activity-scaling items remain research-only even though the simulator emits associated fields.

`simulator (1).json` is the complete envelope, not just its nested `ingestion_payload_contract`. It is AST-01, mission day 142, sequence 1; inner and outer timestamps both equal `2026-11-14T14:29:43.469+00:00`. This is not the same event as Ayoub's example and does not prove the same mission or person.

## Format differences requiring explicit adapters

| Concern | Scientific example | Simulator | Required treatment |
| --- | --- | --- | --- |
| Identity | AST-001 | AST-01 | Namespaced, confirmed alias registry; no zero-padding heuristic or automatic person merge |
| Mission | Day 14, no mission ID | Day 142, no mission ID | Require run/import mission binding; do not rewrite either day to match the UI's fictional mission |
| HR | `automated_sensors.heart_rate.value`, bpm | `telemetry_sensors.heart_rate_bpm.value`, bpm | Rename without changing value; retain original path |
| SpO₂ | `spo2.value`, percent | `spo2_percent.value` and `.spo2`, % | Unit spelling normalization; detect conflicts before choosing a value |
| Respiratory | `respiratory_rate.value`, breaths_per_min | `respiratory_rate_rpm.value` and `.respiratory_rate`, rpm | Explicit adapter interpretation of rpm as breaths/min; no generic rpm conversion |
| Fatigue | 1–7, claimed NASA/BHP Samn–Perelli label | 1–10 | Keep scale discriminator and original label; never rescale or compare scores as one instrument |
| Hydration | `hydration_intake.value`, ml, no explicit window | `hydration_intake_ml_24h` | mL unit canonicalization only; retain uncertainty in scientific example's reporting window |
| Radiation | Daily dose 0.52 mSv; cumulative 7.28 mSv | Rate 0.53 mSv/day; cumulative 150.5 mSv | Separate interval dose, dose rate, and cumulative dose; period and dose basis remain explicit/unknown |
| Time | Root timestamp | Nested measurement timestamp plus outer sent_at | Record event time, source transmission time, and server receipt time separately |
| Status | VALID on each sensor | No per-channel validity/status | Preserve source report; numeric simulator readings are unverified, not automatically valid |
| Missing data | No missing example | Fault injector emits null, zero, spikes, stuck values | Null is missing; zero is not a missing-data sentinel; no fabricated recovery/interpolation |
| Activity | RESTING | Five activity enums | Preserve context; unknown is UNKNOWN, never RESTING by default |
| Extra data | Limited core indicators | HRV, temperature, BP, ECG, ocular, symptoms, medications, proton flux, limits | Preserve raw payload; leave outside active MVP analysis and clinical UI |

## Simulator executable and dependencies

Python 3.12.10 was used. Imports are Python standard library only: argparse, copy, json, math, random, re, signal, sys, threading, time, urllib, collections, datetime, pathlib, typing, and future annotations. `math` and `re` are unused. No scientific JSON file is read by the script: it has hard-coded distributions, baselines, scenario targets, and fault ranges. It does not require these JSON files or third-party packages to run. Its built-in generic annotations require Python 3.9+; use 3.12 for the next implementation task. No simulator change or dependency installation was made.

CLI defaults: normal mode, RESTING, AST-01, mission day 142, interval 1 second, count 0 (indefinite). Modes: normal/anomaly/failure/auto. Eight scenario names and six fault types are exposed. Flags also include `--scenario`, `--fault`, `--fault-channels`, `--endpoint`, `--api-key`, `--dry-run`, `--out-file`, `--seed`, `--pretty`, `--quiet`. `--scenario` is applied only when starting in anomaly mode; explicit fault selection applies to initial failure mode, not the auto scheduler. Count/interval/mission-day/channel-count numeric values lack useful range checks. Use bounded positive counts during validation; negative intervals/counts must not be used as supported behavior.

Without an endpoint, packets print to stdout, even when an output file is specified. `--out-file` appends JSON Lines before transmission; it is not a durable replay queue. Its parent directory must exist and filesystem errors are not caught. `--pretty` changes stdout to multiline JSON but file output stays JSONL. `--quiet` suppresses per-success HTTP log messages, not all stderr logs. Logs use host-local time without offset; telemetry uses aware UTC. A seed controls PRNG values, not timestamps or run identity. The PRNG is global to the process.

HTTP behavior (lines 388–445): POST the whole packet as JSON with `Content-Type: application/json`; optional `Authorization: Bearer <api-key>`. Five-second default timeout; any 2xx is accepted without inspecting response body. Retries buffer the same packet with exponential waits 1, 2, 4, 8, 16, 30 seconds; attempts happen during send/flush rather than on an independent scheduler. A 500-packet in-memory deque drops the oldest entry when full. All HTTP errors, including permanent 4xx, are retried and can block newer packets. Shutdown attempts one immediate flush and still returns process exit code 0 if records remain unsent. Network requests are synchronous, so sampling cadence includes HTTP latency. An external receiver needs idempotent writes and durable acceptance; 2xx must never falsely promise accepted data.

## Reproduced semantic defects and limitations

These are observed defects, despite successful syntax/process checks:

- **Alias conflicts:** at full ramp with seed 42, hypercapnia gives SpO₂ `.value=93.5` versus `.spo2=98.0`, and respiratory `.value=24` versus alias 15. Ischemia gives 92.5 versus 98.0. Infection gives core temperature 38.6 versus alias 36.8. QT scenario gives QTc 488 versus corrected alias 417. The scenario functions modify one field; scalar fault handling later synchronizes its own aliases, but anomaly handling does not. The adapter must flag/quarantine conflicting channels, not pick whichever key happens to be read first.
- **Derived BP inconsistency:** tachycardia reports MAP 87 with updated BP giving arithmetic 97; hypovolemia reports MAP 87 versus arithmetic 67 in the same seeded test. Do not use MAP as validated input or silently recompute and overwrite it.
- **Fault attribution missing:** packets expose mode but not active faulty channel/type or per-channel status. A spike/stuck/zero cannot be reliably classified from mode alone. A reproduced transition packet labeled normal still has HR null because `generate` applies existing faults before clearing them (lines 367–373). Do not mark every normal-mode value valid or every failure-mode channel invalid.
- **Radiation integration defect:** cumulative dose increments using an assumed five seconds per generated packet (line 272), while the CLI defaults to one second and can use another interval. Cumulative output is rounded to 0.1 mSv, starts from a random 150–260 mSv, and caps at 299 mSv. The SPE scenario changes the *packet's* cumulative value toward 515 without changing stored simulator state, so returning to normal can decrease reported cumulative dose. Preserve it as source-reported/unverified, not a physical integration of the displayed rates.
- **Packet collisions:** payload IDs contain UTC date and sequence, not astronaut/run identity. Sequence resets on restart. Different runs or astronauts can reuse a payload ID; sequence alone cannot be a database primary key. Three separate calls obtain source date, event time, and sent time, so midnight crossings can make their dates differ legitimately.
- **Unobserved timing:** manual values have no separate submission time or explicit sleep interval; simulator "check-ins" are regenerated snapshots, not confirmed human reports. Its `HYBRID` counterpart's submitted boolean is not a timestamp or identity attestation.
- **Scenario labels are authoring metadata:** names such as infection, ischemia, hypercapnia, SANS, and qtc_drug are not diagnoses and must not become backend alerts or conclusions. The source's `ocular_translaminar_osd815` name is not proof of NASA dataset OSD-815 use; no dataset is imported by this script.

## Scientific claim checking and activation decision

The following linked primary sources were opened on 2026-11-14. Availability is not equivalent to confirmation of every claim. Claims not established below remain unverified; no current-operational certification or exhaustive literature review is asserted.

| Supplied reference / claim | Source check | Decision |
| --- | --- | --- |
| NASA HRP risks and hazards | [HRP risks](https://www.nasa.gov/hrp/risks/), [hazards](https://www.nasa.gov/hrp/hazards/) are contextual overviews | Retain as references; not evidence for the JSON's exact cutoffs or MAD/EWMA configuration |
| Bio-Monitor measurements | [CSA Bio-Monitor](https://www.asc-csa.gc.ca/eng/sciences/bio-monitor.asp) supports vital-sign acquisition and activity context | Does not establish supplied rolling-baseline algorithms, cutoffs, or real hardware behind these examples |
| NTRS 20180008707 | [NASA biosensor integration presentation](https://ntrs.nasa.gov/api/citations/20180008707/downloads/20180008707.pdf) describes Astroskin/data integration | Searches found no median or EWMA term; do not call the specified algorithm NASA-verified based on this citation |
| V2 6022 as support for SpO₂ / breathing cutoffs | [Volume 2 Rev E compliance matrix, PDF page 5](https://www.nasa.gov/wp-content/uploads/2025/01/d-2-requirement-compliance-matrix.pdf#page=5) concerns environmental atmospheric alerting | Cabin ppO₂/ppCO₂ requirements do not validate personal SpO₂ or respiratory cutoffs |
| Sleep targets and fatigue scale | [CSA sleeping in space](https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/sleeping-in-space.asp) discusses allocated sleep opportunity; [NASA HRP research](https://www.nasa.gov/hrp/ongoing-hrp-research/) is broad context; [2009 NASA evidence book](https://www.lpi.usra.edu/lunar/strategies/McPhee_Charles_NASA-SP-2009-3405_HumanHealthPerformanceRisksSpaceExplorationMissions.pdf) is a historical evidence review | Sleep opportunity is not measured sleep; exact 7–9/6-hour categorical rules, the claimed NASA/BHP 1–7 instrument, and seven-day means are not verified by this review |
| Hydration target | [Volume 2 matrix, PDF page 7](https://www.nasa.gov/wp-content/uploads/2025/01/d-2-requirement-compliance-matrix.pdf#page=7) addresses water provision and references a separate quantities table | Supply for drinking/food preparation is not equivalent to recorded intake; do not activate the JSON's personal intake bands |
| Radiation limits | [Volume 1 Rev C, PDF pages 39–41](https://www.nasa.gov/wp-content/uploads/2023/11/nasa-std-3001-vol-1-rev-c-with-signature.pdf#page=39) distinguishes career effective dose, organ doses, and design-reference SPE criteria | The 600 mSv career reference is not a mission-dose threshold. Table 4.8-1 uses mGy-Eq for the 250/500 blood-forming-organ entries; the separate 250 mSv SPE criterion is not a generic 30-day mission limit. The JSON labels conflate these. No comparison gauge or threshold activation |
| CANS | [CSA's 2026-02-26 article](https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp) describes continued development of a neutron instrument | Does not prove the example is a CANS/RAD dataset or establish the supplied typical daily value |
| Other research context | [CSA space science overview](https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp) and [2021 NASA standards overview](https://www.nasa.gov/wp-content/uploads/2021/09/ochmo_standards_overview_sept_15_2021_francisco.pdf) were opened | Context/historical standards material, not a substitute for versioned requirements or indicator validation |
| Terrestrial fallback | [Official RCP NEWS2 report](https://www.rcp.ac.uk/media/a4ibkkbf/news2-final-report_0_0.pdf) and [RCP overview](https://rcp.ac.uk/news-and-media/news-and-opinion/nhs-england-approves-use-of-national-early-warning-score-news-2-to-improve-detection-of-acutely-ill-patients/) describe an acute-care scoring system | A few extracted bands are not the full score, nor validation for astronauts; no fallback automatically enabled. AHA and Samn–Perelli original references are not precisely linked in the file and remain unresolved |

The configuration also lacks a complete executable interval specification, explicit inclusive endpoints for every category, baseline window lengths/sample minima, MAD-zero handling, EWMA parameters, staleness rules, and a clear distinction between a daily report and a rolling aggregate. Do not infer these. Keep the entire rules file as reviewed research input, with an independent server-side activation policy initially empty. Preserve its verification strings as `source_claimed_verification`, not as our own evidence status.

## Validation actually run

Read-only/bounded harness: `python work/review_sources.py` from the original Codex workspace; Python 3.12.10; exit 0. JSON checks used `json.loads` with a duplicate-key hook and rejection of non-finite constants. Syntax used `ast.parse` and `py_compile.compile(..., cfile=<work path>, doraise=True)`.

Executed the unchanged simulator with these exact flag patterns (all exit 0):

```powershell
python 'C:/Users/rayan/Downloads/simu (1).py' --help
python 'C:/Users/rayan/Downloads/simu (1).py' --mode normal --count 2 --interval 0 --seed 42 --dry-run
# Repeated for all eight scenario choices, four packets each:
python 'C:/Users/rayan/Downloads/simu (1).py' --mode anomaly --scenario hypercapnia --count 4 --interval 0 --seed 42 --dry-run
# Repeated for dropout, stuck, flatline_zero, spike, drift, out_of_range:
python 'C:/Users/rayan/Downloads/simu (1).py' --mode failure --fault dropout --fault-channels 7 --count 2 --interval 0 --seed 42 --dry-run
python 'C:/Users/rayan/Downloads/simu (1).py' --mode auto --count 4 --interval 0 --seed 42 --dry-run
```

`PYTHONIOENCODING=utf-8` was set in subprocesses for portable degree-symbol output. A temporary loopback-only HTTP receiver, not a FastAPI backend, tested 503 then 201 responses, retention of the same envelope across retry, content type, optional dummy Bearer header, and two successful packets sent by the actual CLI. The harness bypassed the retry clock for its retry assertion; elapsed backoff timing, TLS, real-server authentication, and production endpoint behavior were not tested. All temporary receivers were shut down. Syntax/process success does not erase the semantic defects above. SHA-256 hashes matched again after the tests.

Reproducible raw logs and structured results are retained under workspace `work/source-review/`; they are validation artifacts, not a claim that a live backend exists. Generated design schemas/examples are separately checked and described in `integration-contract-v1.md`.
