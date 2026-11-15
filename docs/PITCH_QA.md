# Jury questions and answers

## 1. What NASA data does the project actually use?

The research screen includes a small snapshot derived from NASA OSDR OSD-53 catalog sample metadata. It represents thirteen catalog records grouped by the study's preflight, postflight and control metadata. No processed gene-expression values or NASA physiological measurements are analyzed. Dashboard telemetry and radiation values are synthetic.

## 2. Does CyberNova diagnose a condition or recommend treatment?

No. It presents measurements, quality issues and statistical observations for human review. It does not diagnose, recommend medication or provide treatment instructions. The analytical settings are engineering demo parameters and need scientific review.

## 3. How are statistical observations generated?

The current integration uses astronaut-, metric- and activity-specific context, a rolling median/MAD baseline, EWMA context and persistence after warm-up. Sensor quality events follow a separate path. This is a transparent engineering demonstration, not a validated medical method or threshold.

## 4. How do you distinguish sensor dropout and radiation quantities?

Missing or invalid sensor data stay missing and are shown as a data-quality observation; they are not interpreted as physiology. Radiation records retain their quantity and units: a dose rate in mSv/day is not automatically an accumulated 24-hour dose in mSv, and cumulative mission dose is separate. The MVP visualizes synthetic radiation data without clinical hazard thresholds.

## 5. What is live, and what happens if a service fails?

The public Vercel deployment serves the frontend and deterministic synthetic Demo mode. FastAPI and SQLite run locally for the end-to-end demo; Live mode uses the backend only when configured. Live failures are visible and do not silently switch to mocks. A presenter can explicitly switch to Demo mode and disclose that change.
