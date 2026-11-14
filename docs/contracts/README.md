# v1 design schemas and examples

These are canonical contract artifacts used by the implemented FastAPI response layer. `v1_design.py` contains Pydantic resource models; request handling, storage and ingestion live under `backend/`, while the non-clinical analytics engine lives under `analytics/`.

From the repository root:

```powershell
python docs/contracts/v1_design.py
```

This regenerates JSON Schema 2020-12 files for canonical resources, write inputs, and the acknowledgment input. JSON Schema describes field shape; the Python model validators also enforce cross-field semantics such as exact 24-hour periods and quantity/unit consistency. Foreign-key identity, session binding, idempotency, and timestamps relative to persisted mission state require backend application/database checks.

`examples-v1.json` contains fictional contract examples, not actual API responses, detected anomalies, baselines, mission histories, or normalized outputs of supplied files. Its `examples` keys match model names. The extra variants show source-only radiation and legacy fatigue without pretending that period, origin, or scale have been converted. Analytics schemas describe the current implementation; their configured values are engineering demo parameters only.

For source compatibility and exact proposed HTTP conventions, read ../integration-contract-v1.md. Do not modify the original files or promote evaluation_rules.json verification claims into active rules based on these schemas.
