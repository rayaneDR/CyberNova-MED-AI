# CyberNova MED-AI — five-minute pitch

**Total: 5:00.** The speaker notes are embedded in the seven-slide final deck. Keep the click-through rehearsal under each section's timebox. The telemetry, identities and scenario readings shown are synthetic.

## 1. CyberNova MED-AI — 0:00–0:20 (20 seconds)

Hello, we are CyberNova X from Meknes. CyberNova MED-AI is a transparent crew-health monitoring demonstrator for space missions. It puts readings, source quality and context in one place, while keeping people responsible for decisions. Dashboard telemetry and crew identities are synthetic. The space artwork in this presentation is generated and is not a NASA image.

## 2. The challenge — 0:20–0:55 (35 seconds)

The official challenge asks for software that gathers astronaut health indicators and helps astronauts evaluate their health. In space, a value needs its activity, time, source and quality beside it. A changing valid signal is different from a channel that stopped reporting. A statistical observation is also different from a medical conclusion. We make those distinctions visible and avoid diagnosis or treatment advice.

## 3. The solution — 0:55–1:40 (45 seconds)

The dashboard has six connected views: overview, health trends, alerts, daily check-in, radiation tracking and NASA research. It displays heart rate, oxygen saturation and respiratory rate, plus sleep, fatigue on the proposed Samn–Perelli 1–7 scale, and hydration. It labels synthetic data and shows provenance. Demo mode works offline with deterministic fixtures. Live mode connects explicitly to FastAPI; a Live API error stays an error and never silently falls back to mock data.

## 4. Technology pipeline — 1:40–2:30 (50 seconds)

Amina's Python simulator sends synthetic packets. Rayane's FastAPI ingestion validates units and source fields, then stores accepted measurements and check-ins in SQLite. Ali's statistical module produces observations using rolling median and median absolute deviation with EWMA context and persistence rules. The Next.js frontend displays those returned records. Quality events remain separate from statistical observations, and missing measurements remain missing. The public Vercel site hosts the frontend only; the backend is a local demo service. This is an engineering prototype, not a clinical protocol.

## 5. Working demo — 2:30–3:45 (75 seconds)

Start on Overview: this crew and the latest readings are synthetic. Open Health and show the selected history range, activity context and a visible sensor gap. The chart does not invent a value for the gap. In Alerts, distinguish sensor quality from a statistical observation. Only show observations the service actually returns; if the baseline is still warming up, show that state instead of manufacturing an alert. Submit a daily check-in and point out that fatigue accepts one through seven. Open Radiation and show the labels: a source dose rate in mSv per day is not a completed 24-hour dose in mSv, and cumulative mission dose is tracked separately. Finish on Research and say what is NASA catalog context versus synthetic telemetry.

## 6. NASA science and data — 3:45–4:40 (55 seconds)

The app includes a small NASA OSDR OSD-53 catalog metadata snapshot for a whole-blood gene-expression study. The project represents thirteen catalog sample metadata records: six preflight, six postflight and one control-group record. These are metadata counts, not experimental results. We did not import gene-expression values or NASA heart-rate, oxygen-saturation or respiratory-rate measurements. NASA references inform the research context; the live dashboard data are synthetic. We cite the sources and make no NASA endorsement claim. No unverified radiation limit is used as an alert threshold.

## 7. Impact and next steps — 4:40–5:00 (20 seconds)

Our contribution is a clear, testable workflow that preserves context and uncertainty. Next we need scientific review, appropriately governed source data, user evaluation and security work before any real health data use. CyberNova MED-AI is a hackathon prototype, not operational crew monitoring. Thank you.

## Timing

| Slide | Duration | Cumulative |
|---|---:|---:|
| 1. Title | 20 s | 0:20 |
| 2. Challenge | 35 s | 0:55 |
| 3. Solution | 45 s | 1:40 |
| 4. Pipeline | 50 s | 2:30 |
| 5. Demo | 75 s | 3:45 |
| 6. NASA data | 55 s | 4:40 |
| 7. Impact | 20 s | 5:00 |
