# Five-minute pitch script

Target: ~600 words at 120–125 wpm. Keep the live walkthrough to 65 seconds (section 5).

## 1. CyberNova MED-AI — 0:00–0:25

Hello, we are CyberNova X from Meknes. CyberNova MED-AI is a research-oriented mission-control demonstrator for reviewing astronaut health observations with their activity, data quality, and provenance. Every crew member and measurement in this demo is synthetic.

## 2. The problem — 0:25–0:55

Spaceflight health monitoring faces long-duration missions, changing activity, constrained sensors, and communication delays. A dashboard must make it clear when a channel stops reporting and when a valid series differs from its own history. Those are different events. Neither should be turned into an unsupported medical conclusion.

## 3. Our solution — 0:55–1:35

We built six connected screens: a mission overview, health trends, an observation center, a daily self-report, radiation tracking, and NASA research context. The frontend can run on deterministic demo fixtures or connect explicitly to a FastAPI service. Live errors stay visible; they do not silently replace backend data with demo values. Synthetic simulator packets are validated and persisted in SQLite.

The experience is designed for human review. It shows heart rate, oxygen saturation, respiratory rate, sleep, subjective fatigue, and hydration intake with units and provenance.

## 4. How it works — 1:35–2:20

For eligible synthetic history, our current engineering demo computes astronaut-, metric-, and activity-specific baselines using a rolling median and median absolute deviation, then adds an exponentially weighted moving average. It requires a warm-up and sustained samples before creating a statistical observation. The page exposes method, context, and supporting values. Missing or invalid channels become data-quality observations, never physiological alerts.

The parameters are not medical thresholds or a validated protocol. They still require Ali's statistical review and Ayoub's scientific review before any stronger claim.

## 5. Demonstration — 2:20–3:25

[Run the deterministic six-screen sequence in the demo runbook.]

Here is the crew overview and last recorded sample. On the health screen, a gap remains visible. In alerts, a sensor issue is separate from a sustained statistical observation; if baseline warm-up is incomplete, we show that state. We submit a fatigue, sleep, and hydration check-in and confirm it is stored. Radiation is labeled synthetic; mSv per day stays a rate and is not presented as a completed daily dose. Finally, research context is separate from telemetry.

## 6. Science and NASA data — 3:25–4:15

NASA's Open Science Data Repository catalog provides context through OSD-53, a whole-blood gene-expression study with preflight and postflight sample metadata. We display a small count summary from catalog metadata only. We did not process expression values, and this study does not provide the heart-rate or oxygen-saturation data in our interface. The dashboard's readings remain synthetic. We cite NASA sources as references and do not imply NASA endorsement.

We also keep radiation quantities separate: a dose rate in mSv per day is not an accumulated daily dose in mSv. No unverified dose limit becomes an alert threshold.

## 7. Impact and next steps — 4:15–5:00

The value today is a transparent, testable integration pattern: preserve provenance, show missingness, separate sensor and statistical events, and leave decisions with people. Next, we need team review of analytical parameters, better validated and appropriately governed source data, security controls for any shared deployment, and user research with relevant domain experts.

CyberNova MED-AI is a hackathon prototype—not a medical device and not operational crew monitoring. Thank you.
