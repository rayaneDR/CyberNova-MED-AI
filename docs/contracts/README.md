# v1 design schemas and examples

These are proposed contract artifacts, not a backend implementation. `v1_design.py` contains Pydantic design models only: no API server, storage, ingestion adapters or analytics. Pydantic 2.14.1 was already available in the review environment; no project dependency was installed or changed.

From the repository root:

```powershell
python docs/contracts/v1_design.py
```

This regenerates eleven JSON Schema 2020-12 files for seven canonical resources, three write inputs, and the acknowledgment input. JSON Schema describes field shape; the Python model validators also enforce cross-field semantics such as exact 24-hour periods and quantity/unit consistency. Foreign-key identity, session binding, complete integration coverage, mission-start equality, idempotency, and timestamps relative to persisted mission state require the future backend's application/database checks.

`examples-v1.json` contains explicitly fictional design examples, not actual API responses, detected anomalies, baselines, mission histories, or normalized outputs of the supplied files. Its `examples` keys match model names. The extra variants show source-only radiation and legacy fatigue without pretending that period, origin, or scale have been converted.

For source compatibility and exact proposed HTTP conventions, read ../integration-contract-v1.md. Do not modify the original files or promote evaluation_rules.json verification claims into active rules based on these schemas.
