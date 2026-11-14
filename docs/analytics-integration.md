# Analytics integration and attribution

## Ownership and source preservation

Rayane owns the integration and current backend analytics implementation. Ali owns the intended statistical algorithms and review of statistical behavior. Ali's submitted prototype files are preserved unchanged under `analytics/originals/`:

| Original file | SHA-256 |
| --- | --- |
| `analysis (1).py` | `00DB7B70AEACC5BE20CEDAD01234FAB05C0ADA60143129C6111D68DCF6D7533E` |
| `test_analysis (1).py` | `772A49CEE099EC046669316DEFCF916AD9C214175723C62A6AC111EB0778BB28` |
| `simulate (1).py` | `5DB01BBD2677E43036A2AB7736E19F8B62A02D6D92CF10A0CAC83BB28C6DCFD0` |
| `app (1).py` | `C94D57289E74E3BB5333F3CF1C55309CCF47B0FFDDCD49BD457C8D096629209B` |

The prototype has simple hard-coded rules and demo printing; its `simulate`/Flask app is not used as the service or dashboard. The integrated path does not call `random` to fabricate live analytics. Amina's simulator and Ayoub's research files remain outside this change.

## Internal method

`analytics.engine.analyze_history` accepts canonical `MetricReading` records. The backend adapter reads canonical measurements and their recorded channel-quality rows from SQLite. Each channel is analyzed separately by astronaut, metric, and activity context. There is no cross-astronaut pooling and no fallback across activities.

Eligibility requires an aware timestamp, supported metric and exact unit, supported activity, nonempty source and reading ID, `quality=unverified`, a finite nonnegative JSON number, and (for SpO2) a value no greater than 100. Numeric strings and booleans are rejected. Explicit missing, invalid, conflicting, or source-reported disconnected inputs are excluded from baselines. Missing values and connectivity are not converted into physiological observations. Zero is retained because the canonical contract permits it; its interpretation requires source-quality review.

Exact duplicate records with the same scoped reading ID are counted once. Conflicting contents under the same ID are both excluded. Eligible measurements are sorted by UTC timestamp then reading ID so out-of-order source arrival is deterministic.

Warm-up requires at least 8 eligible baseline samples by default. The rolling history holds at most 30 values. The robust center is the median; robust dispersion is `1.4826 * MAD`, with engineering floors of 1 bpm, 0.1 percentage points, and 1 breath/minute for zero or very small spread. Those floors prevent division by zero and are not physiological limits. Candidate detection uses absolute robust score ≥3.5 or an EWMA score ≥3.0 in the same direction, while a robust guard score must also be ≥2.5. EWMA alpha is 0.25. A candidate must persist for 3 consecutive valid samples to emit one statistical observation for that episode. Candidate samples do not enter the baseline; noncandidate samples may update the rolling baseline. Parameters are environment-configurable and returned by the API.

These values are an engineering demonstration configuration, not reviewed clinical/statistical settings. Team review is required for cadence assumptions, sample minima, activity grouping, robust scale floors, EWMA parameters, candidate admission, and the definition of an episode before scientific claims are made. No evaluation rule or radiation limit is used.

## API behavior

`GET /analytics/summary` and `GET /alerts` recompute from the persisted, bounded demo history and idempotently materialize deterministic observations. This keeps the MVP restart-safe without adding a background worker. The baseline status is `ready` only when at least one metric/context has a full eligible warm-up; each metric/context also exposes its own status and count. No statistical observation is produced during warm-up or for a one-off candidate. Sensor-data issue events use their own alert kind and are not presented as statistical deviation.

Statistical event explanation and supporting values include algorithm version, source, quality, activity, baseline sample count, median, MAD, robust score, EWMA score, and configured thresholds. Acknowledgment is operational review only. It does not resolve a health condition.

## Ali review and further work

Before presenting these outputs as Ali-approved, have Ali review the independent implementation and tests. Add versioned calibration/evaluation against agreed non-clinical fixtures and analyze behavior under realistic simulator cadence, repeated episodes, missingness, and activity transitions. Do not add diagnoses, treatment guidance, or unverified physiological alert limits.
