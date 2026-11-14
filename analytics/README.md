# Analytics engine

`engine.py` provides a deterministic, non-clinical demonstration of personal-baseline monitoring for the three MVP telemetry channels. It is isolated from ingestion and persistence; `backend/app/analytics_adapter.py` translates canonical stored measurements into engine inputs.

Ali's supplied files are preserved byte-for-byte in `originals/` and credited in [`../docs/analytics-integration.md`](../docs/analytics-integration.md). The implementation here is an integration-owned replacement built after reviewing that prototype, not a claim that the original prototype implemented these safeguards.

The engine does not diagnose, recommend treatment, or use Ayoub's unverified evaluation rules as thresholds. See the integration note for eligibility, warm-up, median/MAD and EWMA behavior, configuration, and current limits.
