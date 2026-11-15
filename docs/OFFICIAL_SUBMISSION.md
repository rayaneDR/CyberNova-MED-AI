# Official form copy — November 15, 2026

Prepared against the November 13 guide, read directly in the browser on November 15: https://www.spaceappschallenge.org/resources/project-submission-guide/ . The eight fields and requirements below were verified against that page. The public guide does not state character limits; the signed-in form and team registration remain unverified. The browser currently shows Login. The official Project Demo is the seven-slide deck. The local pitch is separately five minutes plus two minutes of questions.

## Project Name

CyberNova MED-AI

## High-Level Project Summary

CyberNova MED-AI is a crew-health monitoring prototype that brings synthetic telemetry, daily self-reports, sensor quality, explainable statistical observations and radiation tracking into one responsive mission-control dashboard. NASA research resources inform its design, and retrieved NASA OSDR catalog metadata supplies scientific context. The system preserves missing data and provenance and supports human review without diagnosis or treatment advice.

## Link to Project Demo

https://raw.githubusercontent.com/rayaneDR/CyberNova-MED-AI/release/space-apps-2026/submission/CyberNova-MED-AI-pitch-final-3d-official-v3.pdf

Seven-slide English PDF; public and viewable without authentication. Use the seven-slide deck for the official demo; do not substitute a five-minute recording for the official maximum 30-second video option.

## Link to Final Project

https://cybernova-med-ai.vercel.app

Public synthetic Demo mode. Complete source: https://github.com/rayaneDR/CyberNova-MED-AI/tree/release/space-apps-2026

## Detailed Project Description

Team CyberNova X addresses “Create Health Monitoring Software for Astronauts on Space Missions.” Long missions require reviewing health indicators alongside activity, timing, provenance and sensor quality. A missing channel needs a different explanation from a valid signal that changes relative to its history.

The prototype provides six screens: a crew overview, historical health trends, an observation center, a daily check-in, radiation tracking and NASA research. It displays heart rate, SpO2 and respiratory rate; the check-in records sleep, hydration and proposed Samn–Perelli fatigue scores from 1 to 7. Legacy 1–10 source records retain their original scale. Radiation quantities remain distinct: source dose rate, completed 24-hour exposure dose and cumulative mission dose.

Amina's Python simulator generates synthetic packets. FastAPI validates ingestion and stores records in SQLite. The statistical integration uses rolling median/MAD, EWMA context, baseline warm-up and persistence rules to produce explainable engineering observations. Missing or invalid channels remain data-quality events. Next.js displays source quality and context for human review. Demo mode uses deterministic fixtures; configured Live mode connects to the local backend and shows failures explicitly. The public deployment hosts the frontend Demo experience only.

Rayane leads the project and owns frontend, backend integration and deployment. Khawla contributed to the original backend/API work. Ali owns statistical analytics and review. Amina owns the simulator. Ayoub owns scientific indicators and research. Team names confirmed in the project: Rayane, Khawla, Ali, Amina and Ayoub. Full names and official Local Event membership require team-portal confirmation.

The product is a hackathon research prototype. All displayed crew telemetry, identities and radiation readings are synthetic. No NASA experimental measurement series is analyzed. Statistical parameters require review; no clinical validation, diagnosis, medication advice or NASA endorsement is claimed. Production use would require security controls, governed data and domain evaluation.

## Use of Super Intelligence (SI)

OpenAI Codex/ChatGPT assisted with code generation and integration, debugging, documentation, submission drafting and presentation construction. OpenAI image generation produced the astronaut/Earth/spacecraft background artwork; each occurrence in the official deck carries a visible “AI-generated visual” label. The slides also include an actual application screenshot and editable text and architecture objects. The presentation was authored with the OpenAI artifact-tool runtime. The simulator and authored Demo fixtures produce synthetic data; AI-assisted code and synthetic data provenance are disclosed in this description and repository documentation. No AI-generated audio or video is included. No NASA logos, flags or mission identifiers are used in generated artwork. Team review remains necessary before the originality declaration and final submission.

## NASA Data

NASA resources actually used: the Human Research Program risks overview motivated visible mission context; the NASA sleep/scheduling risk resource informed daily sleep and subjective fatigue context; the NASA space-radiation resource informed the separate radiation tracking view. These resources support design context, not clinical thresholds or synthetic readings.

NASA OSDR OSD-53 catalog sample metadata was retrieved and summarized as thirteen catalog records: six preflight records, six postflight records and one control-group record. The Research screen presents these derived metadata counts separately from telemetry. This whole-blood gene-expression study does not supply dashboard heart rate, SpO2 or respiration.

On November 15 an official OSDR processed archive was successfully retrieved and ZIP-validated. It contains thirteen reporter/value tables. Its values were inspected for format only; no experimental measurement analysis or scientific visualization was added because reporter semantics, normalization and units were not fully established. Downloading a file is not presented as scientific analysis.

Under the supplied guide's “at least one NASA data source OR NASA resource actually used” criterion, the implemented and cited NASA research-resource use plus retrieved metadata meets the stated use requirement. Eligibility remains subject to official judging and the remaining submission requirements.

References:

- NASA HRP, Risks of Human Spaceflight: https://www.nasa.gov/hrp/risks/
- NASA, Risk from Inadequate Sleep and Irregular Schedules: https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/
- NASA HRP, Hazard: Space Radiation: https://www.nasa.gov/hrp/hazard-space-radiation/
- NASA OSDR, OSD-53, Spaceflight modulates gene expression in the whole blood of astronauts: https://osdr.nasa.gov/bio/repo/data/studies/OSD-53
- OSDR metadata API: https://visualization.osdr.nasa.gov/biodata/api/v2/dataset/OSD-53/assay/*/sample/*/metadata/
- Associated publication: https://doi.org/10.1038/npjmgrav.2016.39
- OSDR file manifest: https://osdr.nasa.gov/osdr/data/osd/files/53

## Space Agency Partner Data and Other References

No partner-agency measurement dataset is analyzed. CSA Bio-Monitor/radiation material appears in Ayoub's source specifications as background; its verification labels and thresholds are not automatically activated. Project research review: https://github.com/rayaneDR/CyberNova-MED-AI/blob/release/space-apps-2026/docs/source-file-review.md

Software references: Next.js https://nextjs.org/ ; React https://react.dev/ ; TypeScript https://www.typescriptlang.org/ ; Tailwind CSS https://tailwindcss.com/ ; Recharts https://recharts.org/ ; Lucide https://lucide.dev/ ; FastAPI https://fastapi.tiangolo.com/ ; Pydantic https://docs.pydantic.dev/ ; SQLAlchemy https://www.sqlalchemy.org/ ; SQLite https://sqlite.org/ ; Python https://www.python.org/ . Exact dependency versions are in the repository lockfile and requirements files. Dependencies retain their upstream licenses; the team's source is MIT licensed. The dashboard screenshot was captured from this project. Space artwork was generated with OpenAI image generation and is visibly labeled. No external stock photography, audio, video or minors' likenesses are included.

## Team lead actions before judging submission

1. Sign into Space Apps and open CyberNova X → Project tab.
2. Confirm all five members belong to the same Meknes Local Event and confirm their displayed names.
3. Paste the eight field sections above, checking the portal's field limits and required fields.
4. Open the Project Demo PDF and Final Project links in a private browser window.
5. Review and personally approve Terms and Conditions and All Work is Original.
6. Only after approval, click Submit for Judging and verify the success banner. Saving a draft alone is not submission.

Local pitch deadline: November 15, 2026, 12:30 Morocco time (organizer supplied). Official global deadline: November 15, 2026, 23:59 in the Local Event timezone (guide supplied).
