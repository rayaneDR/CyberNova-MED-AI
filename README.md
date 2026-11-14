# CyberNova-MED-AI

CyberNova X · NASA Space Apps Challenge Meknes 2026 participant project.

A synthetic crew-wellbeing telemetry demonstrator. The initial vertical slice is a standalone Next.js dashboard; Python modules are reserved for their owners and are not implemented here.

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

- Six synthetic indicators: heart rate, SpO₂, respiratory rate, sleep duration, fatigue, hydration.
- Switch the chart between heart rate, SpO₂, and respiratory rate; expand its exact data table.
- The session is fixed at November 14, 2026, 08:00–08:55 UTC, not live telemetry.
- `frontend/src/lib/data-source.ts` is the only data adapter. It returns typed fixtures from `mock-data.ts`; no other module is required.
- Fatigue and hydration are illustrative indices, not validated measurements or medical scores. Optional radiation visualization is deferred.
- No diagnosis, clinical thresholds, risk prediction, or automatic treatment advice. No model has been trained and no NASA endorsement is implied by the project name.

## Collaborate

See [CONTRIBUTING.md](CONTRIBUTING.md), [architecture](docs/architecture.md), and [draft API contracts](docs/api-contracts-draft.md). Research starting points are in [research/README.md](research/README.md). No NASA data is bundled; all fixture values are invented.

GitHub publication was not performed during initialization because GitHub CLI was unavailable. See [publication steps](docs/github-setup.md); this README does not assert that a remote exists.

MIT licensed. Local initialization and validation results are recorded in `docs/verification.md`.

Dependency limitation: npm reports seven moderate development-tool findings rooted in TypeScript ESLint's transitive minimatch dependency. A non-forcing audit dry run did not resolve them. ESLint 9 is deprecated but retained because ESLint 10 conflicts with the plugin peer ranges shipped by this Next.js configuration. See the verification report; do not use `--force` or bypass peer checks to hide this limitation.
