# Pitch Q&A preparation

**What is actually NASA data here?**

Only derived catalog metadata counts from NASA OSDR OSD-53. No gene-expression values or biometric records feed the dashboard. Telemetry and radiation values are synthetic.

**Does the system diagnose a health problem?**

No. It surfaces source-quality issues separately from sustained statistical deviations. Both need human context; neither is a medical alert or diagnosis.

**How does the anomaly method work?**

It filters by source, channel quality, exact unit, astronaut and activity context; establishes a rolling median/MAD baseline; adds an EWMA signal; then requires configured warm-up and persistence. It is a non-clinical engineering demonstrator with settings pending review.

**Why no NASA heart-rate or SpO2 dataset?**

The verified OSD-53 catalog describes whole-blood gene-expression samples, not those vital signs. We chose honest metadata context instead of relabeling an unrelated dataset.

**What if a sensor fails?**

The value remains missing and a data-quality observation is shown separately. The system does not infer physiology from a missing sample.

**Is radiation an automatic safety alert?**

No. We visualize only synthetic records and keep dose-rate and accumulated dose quantities separate. There are no limits or medical hazard categories in the MVP.

**What persists?**

The local backend persists demo telemetry/check-ins in SQLite. Demo mode check-ins are browser-local. Shared/public deployment is not claimed; production would require persistent hosting, authentication for writes, HTTPS, CORS, and security review.

**What is next?**

Have Ali and Ayoub review the statistical and scientific design, improve source-data provenance, test with domain experts, and design privacy/security controls before any real data use.
