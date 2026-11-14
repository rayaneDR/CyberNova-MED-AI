# CyberNova-MED-AI

CyberNova X · NASA Space Apps Challenge Meknes 2026 participant project.

A synthetic crew-wellbeing telemetry demonstrator. The frontend has six interactive mission-control screens; Python modules are reserved for their owners and are not implemented here.

**Local pitch submission: Sunday, November 15, 2026 at 12:30 Morocco time (Africa/Casablanca).** Deadline supplied by the team; verify event instructions separately.

## Run the demo

Use Node.js 24 LTS and npm 11 (Node 22 also supported).

```powershell
cd frontend
npm ci
npm run dev
```

Open http://localhost:3000. No API, database, credentials, or environment file is required. To prepare future configuration, copy the root `.env.example` to `frontend/.env.local`. Its API URL is reserved and not consumed yet.

```powershell
npm run lint
npm run typecheck
npm run build
npm start
```

Run these from `frontend/`. `typecheck` generates Next.js route types first, so it works on a clean checkout. `npm start` serves the production build after `npm run build`.

## Ownership and structure

| Directory | Owner | Scope |
| --- | --- | --- |
| `frontend/` | Rayane (`rayaneDR`) | Next.js App Router, TypeScript, Tailwind CSS, Recharts, Lucide; integration and deployment |
| `backend/` | Khawla | FastAPI, SQLite, API |
| `analytics/` | Ali | Statistical algorithms and alert generation |
| `simulator/` | Amina | Simulated sensors and telemetry |
| `research/` | Ayoub | Indicators, JSON specifications, scientific validity |
| `shared/contracts/` | All owners, coordinated by Rayane | Draft cross-module payloads |
| `docs/` | Rayane + team | Architecture, contracts, verification |
| `.github/` | Rayane | Frontend CI, pull request template |

## Current behavior

- Six routes: overview, health monitoring, alert center, daily check-in, radiation monitoring, and NASA research.
- Three fictional astronauts; global selection updates the session, charts, observations, and sensor status.
- Telemetry charts offer 6h/24h/3-day ranges, signal selection, and accessible exact-value tables with activity and quality context. Missing readings remain gaps.
- The 72-hour synthetic session ends November 14, 2026 at 12:00 UTC. It is recorded historical data, not live telemetry.
- Alert filters, authored explanations, history, and session-local review actions distinguish sensor failures from statistical deviations. No anomaly detection algorithm runs in the frontend.
- Validated daily check-ins save through the mock adapter to browser-local storage, separately for each astronaut. They do not alter the recorded fixture summaries. Hydration intake in mL is distinct from the illustrative hydration percentage index.
- Radiation charts show invented daily rates and cumulative exposure with 7/14-day ranges, unit conversion, and no hazard thresholds.
- `frontend/src/lib/data-source.ts` is the integration boundary. New workspace fixtures live in `mission-fixtures.ts`; the initial `mock-data.ts` fixture and v0.1 telemetry types remain available. No API is contacted.
- Demo controls expose loading, empty, and service-error states. NASA research remains readable independently of telemetry service state.
- Fatigue and hydration indices are illustrative, not validated measurements or medical scores. No NASA datasets are analyzed.
- No diagnosis, clinical thresholds, risk prediction, or automatic treatment advice. No model has been trained and no NASA endorsement is implied by the project name.

## Collaborate

See [CONTRIBUTING.md](CONTRIBUTING.md), [architecture](docs/architecture.md), and [draft API contracts](docs/api-contracts-draft.md). Research starting points are in [research/README.md](research/README.md). No NASA data is bundled; all fixture values are invented.

Public repository: [rayaneDR/CyberNova-MED-AI](https://github.com/rayaneDR/CyberNova-MED-AI). Created through the connected GitHub account and pushed from the local repository on November 14, 2026. The default branch is `main`; the actual Git remote is `https://github.com/rayaneDR/CyberNova-MED-AI.git`.

MIT licensed. Local initialization and validation results are recorded in `docs/verification.md`.

See [frontend MVP handoff](docs/frontend-mvp.md) for screen behavior, integration boundaries, and review checks.

Dependency limitation: npm reports seven moderate development-tool findings rooted in TypeScript ESLint's transitive minimatch dependency. A non-forcing audit dry run did not resolve them. ESLint 9 is deprecated but retained because ESLint 10 conflicts with the plugin peer ranges shipped by this Next.js configuration. See the verification report; do not use `--force` or bypass peer checks to hide this limitation.
