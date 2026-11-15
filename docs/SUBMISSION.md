# NASA Space Apps Challenge submission copy

**Project title:** CyberNova MED-AI  ·  **Team:** CyberNova X  ·  **Challenge:** Create Health Monitoring Software for Astronauts on Space Missions

## Project summary

CyberNova MED-AI is a responsive, research-oriented mission-control demonstrator for reviewing synthetic astronaut health telemetry, daily self-reports, sensor quality, explainable statistical observations, and radiation exposure tracking. A Next.js dashboard connects to a FastAPI and SQLite service, while an explicit Demo mode keeps a deterministic synthetic walkthrough available offline. Median/MAD and EWMA are used as transparent engineering methods for sustained, context-specific deviations after baseline warm-up; missing sensor data is represented separately. NASA OSDR OSD-53 catalog metadata provides research context, but no NASA experimental values are analyzed and no NASA data supplies dashboard vitals. The tool produces no diagnosis or treatment recommendations.

## Problem

Long-duration space missions require teams to review human-health observations amid changing activity, constrained sensing, and communication delays. Disconnected sensors and unusual readings need different explanations, while missing values and context must remain visible.

## Solution

A six-screen dashboard presents overview metrics, historical trends and quality, observation history, a Samnâ€“Perelli 1â€“7 fatigue/sleep/hydration check-in, radiation tracking with strict unit and time-period distinctions, and NASA research context. FastAPI validates synthetic simulator records and stores records in SQLite. The frontend explicitly distinguishes deterministic Demo fixtures from Live synthetic API mode.

## Innovation

The demonstrator separates source-quality events from statistical deviations and exposes the method, supporting statistics, activity context, and baseline warm-up. It avoids filling missing data with inferred values. This is an engineering approach for review, not an autonomous medical decision.

## Technology

Next.js App Router, TypeScript, Tailwind CSS, Recharts, Lucide, FastAPI, Pydantic, SQLAlchemy, SQLite, Python, rolling median, median absolute deviation (MAD), and EWMA.

## NASA data and research

The app displays a small derived NASA OSDR OSD-53 catalog-metadata snapshot: 13 catalog sample records (six astronaut preflight, six postflight, and one control-group record). No processed gene-expression measurements or NASA physiological time series are analyzed. NASA Human Research Program material and OSDR are research references, not inputs to synthetic telemetry. Details and limitations: [NASA data provenance](nasa-data-provenance.md).

## Impact

CyberNova demonstrates how transparent trends, provenance, quality context, and explicit uncertainty could support human review and inform future research prototypes for exploration missions. It is not currently an operational decision-support product.

## Limitations and responsible use

All dashboard telemetry, radiation, and demo identities are synthetic. The analytics parameters are engineering demo settings pending review by the statistical and scientific owners. The OSDR item is catalog metadata only. No diagnosis, clinical alert threshold, treatment advice, real-time sensor, or NASA endorsement is present. No validated clinical hazard threshold is used.

## AI use disclosure draft

AI tools assisted with implementation, editing and presentation artwork. Team members reviewed and remain responsible for the project content. No AI output is used to diagnose, recommend treatment, or make claims about astronaut health. This wording is a draft for the official platform's disclosure field; use the platform's own field and required wording if it differs.

## Presentation files

- Final reviewed seven-slide deck: [CyberNova-MED-AI-pitch-final-3d-reviewed-v2.pptx](../submission/CyberNova-MED-AI-pitch-final-3d-reviewed-v2.pptx)
- Matching PDF: [CyberNova-MED-AI-pitch-final-3d-reviewed-v2.pdf](../submission/CyberNova-MED-AI-pitch-final-3d-reviewed-v2.pdf)
- Five-minute timed script: [PITCH_SCRIPT.md](PITCH_SCRIPT.md)
- Jury Q&A: [PITCH_QA.md](PITCH_QA.md)

## Team

Rayane (team lead, frontend, integration, backend); Khawla (original backend/API contribution); Ali (statistical analytics owner/reviewer); Amina (simulator); Ayoub (indicators and scientific research).

## Links

- Public demo (synthetic Demo mode): https://cybernova-med-ai.vercel.app
- Complete project branch: https://github.com/rayaneDR/CyberNova-MED-AI/tree/release/space-apps-2026 (PR #1 is open; `main` remains unchanged until team review)
- Repository: https://github.com/rayaneDR/CyberNova-MED-AI
- Challenge: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
- NASA OSDR OSD-53: https://osdr.nasa.gov/bio/repo/data/studies/OSD-53

## Submission preparation and verification

Prepared materials: project title and summary, challenge selection, public demo/repository links, NASA data and reference provenance, a seven-slide English deck, speaker script, and AI-use disclosure draft. The 2026 official overview says teams submit from the Project tab on their team page and lists the global close as November 15 at 11:59 PM local time. The current public submission guide was not retrievable during this review, and the signed-in team Project tab was not available in this workspace; exact field names, character limits, required attachments and AI-disclosure wording therefore remain to be confirmed in the portal. Do not treat this prepared checklist as a substitute for that verification. The local pitch deadline of 12:30 Morocco time is organizer-provided and distinct. Do not submit until the team lead reviews the final materials and confirms both deadlines.
