# Shared contracts

`telemetry.schema.json` is draft v0.1 JSON Schema (2020-12) for one sample. `telemetry.example.json` is fictional and synthetic. Contract owners must agree changes before integration. The TypeScript mirror lives in `frontend/src/lib/contracts.ts`; keep it synchronized manually. Runtime API validation is not yet implemented.

Schema bounds express numeric shape only, not healthy ranges. Fatigue and hydration are illustrative indices requiring Ayoub's review. Timestamps are UTC; validators must enable `format` checks and enforce the UTC suffix pattern. The sample schema does not validate the proposed HTTP response envelope.
