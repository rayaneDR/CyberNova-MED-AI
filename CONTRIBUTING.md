# Contributing

Rayane coordinates integration and owns the demo branch. Keep changes small and preserve other owners' work.

1. Clone the repository once Rayane has published and verified its actual URL.
2. Start from current `main`: `git switch main`, `git pull --ff-only`.
3. Create a branch such as `frontend/crew-overview`, `backend/telemetry-api`, `analytics/alerts`, `simulator/session`, or `research/indicators`.
4. Work in your owned directory. Discuss cross-directory changes and contract edits with the affected owners before implementation.
5. Submit a pull request describing behavior, checks, and any contract changes. Rayane coordinates review and merging.

Frontend changes must pass `npm ci`, `npm run lint`, `npm run typecheck`, and `npm run build` in `frontend/`. Commit `package-lock.json` with dependency changes; use npm consistently. CI checks this frontend slice only.

Backend, analytics, and simulator owners choose their own Python environments, dependencies, and meaningful checks. Do not commit virtual environments, SQLite files, personal data, credentials, or `.env.local`.

The payload in `shared/contracts/telemetry.schema.json` is draft v0.1. Agree field names, units, time zones, null behavior, and provenance before connecting modules. Keep the frontend TypeScript mirror synchronized. Real API failures must show an error; never silently display fixtures as live data.

Use UTC ISO-8601 timestamps in telemetry. Use Africa/Casablanca for the submission deadline. Label every synthetic dataset and demo surface. No diagnosis or automatic treatment advice. Ayoub reviews scientific claims and source provenance; invented indices cannot be presented as NASA-validated scores.

Before the pitch: freeze nonessential features, run production checks, rehearse using fixtures without the API, and keep a local demo available.
