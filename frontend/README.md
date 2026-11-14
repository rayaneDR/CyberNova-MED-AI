# Frontend mission-control MVP

Run `npm ci` once, then `npm run dev` from this directory. Dependencies are unchanged from the initial scaffold. For production: `npm run lint`, `npm run typecheck`, `npm run build`, then `npm start`.

## Routes

| Route | Behavior |
| --- | --- |
| `/` | Mission and crew overview, vital cards, health trends, recent observations, sensor availability, last recorded timestamp |
| `/health` | Signal and time-range selection, exact values, activity context, quality summary, provenance |
| `/alerts` | Live backend sensor-quality observations, filters, explanations, backend acknowledgments; Ali analytics unavailable until integrated |
| `/check-in` | Samn–Perelli 1–7 validation, optional notes, live `POST /checkins` and SQLite history; Demo stays browser-local |
| `/radiation` | Separate live 24-hour dose, cumulative mission dose and source dose-rate series; Demo fixture radiation clearly labeled |
| `/research` | Curated NASA references, supporting context, limitations, and distinction between references and analyzed datasets |

## Demo and Live modes

The workspace header provides explicit **Demo fixtures** and **Live API** modes. Demo keeps the authored fictional session. Live calls FastAPI directly; a failed request stays an error and never switches to fixtures. The selected mode is remembered in browser storage. A Live error offers retry or an explicit switch back to Demo.

For local use, copy `.env.example` to `.env.local`, fill `NEXT_PUBLIC_MISSION_ID`, `NEXT_PUBLIC_ASTRONAUT_ID`, and `NEXT_PUBLIC_SOURCE_SESSION_ID` from `python -m backend.app.cli seed-demo`, and use the loopback API URL. Restart Next.js after changing environment values. Do not put a backend write token in a `NEXT_PUBLIC_*` variable.

The typed client in `src/lib/api-client.ts` follows the response schemas published by FastAPI OpenAPI. Live overview and health fetch the API astronaut roster, paginated measurements, alerts, radiation, and the honest analytics availability status. Check-in history and writes use `/checkins`; records are retrieved from SQLite after refresh. Radiation shows completed 24-hour dose, cumulative mission dose, and source `mSv/day` rates separately.

## Data boundary

- `src/lib/contracts.ts`: original telemetry v0.1 plus frontend-only workspace and check-in types.
- `src/lib/mock-data.ts`: preserved initial standalone fixture.
- `src/lib/mission-fixtures.ts`: three fictional astronauts, deterministic hourly telemetry, staged observations, radiation fixtures, curated source metadata.
- `src/lib/data-source.ts`: Demo fixture and browser-storage adapter, separate from Live API.
- `src/lib/api-client.ts`: typed FastAPI request/response client and data-mapping boundary.
- `src/components/mission-provider.tsx`: shared mode, source-specific astronaut list, loading/error/ready state, and request cancellation.
- `src/components/mission-shell.tsx`: persistent desktop sidebar, responsive navigation, mode switch, astronaut picker, and Demo-only controls.

In Demo mode, **Demo controls** select an empty response or simulated service failure. Select Adam Idrissi to inspect a missing current SpO₂ reading. Demo sensor status is recorded/synthetic, with no actual connection.

Demo check-ins save at `cybernova-check-ins-v1:<subjectId>` in localStorage. Live check-ins use `POST /checkins` and history loads from SQLite. Do not enter real personal health information. An invalid existing history is preserved and reported, never overwritten.

New input fatigue uses the proposed Samn–Perelli 1–7 scale per Ayoub's November 14 clarification. New records carry `fatigueScale: samn_perelli_1_7`; old v1 records are read as `legacy_demo_1_10` by their source format and displayed unchanged as /10. Reads do not rewrite storage or convert scores. The preserved shared telemetry draft and recorded fixtures remain separate legacy illustrative indices. Intake is mL and is not converted into the fixture hydration index. Form maxima are validation constraints, not recommended targets.

## Collaboration

FastAPI response schemas were made explicit as part of this integration. No files in analytics/, simulator/, research/, or shared/contracts/ were changed. Ali's analytics remain unavailable until his module is integrated. No clinical thresholds, diagnosis, medication advice, scientific results, or new anomaly algorithm were implemented.

See `../docs/integration-contract-v1.md` for the canonical quantities and input normalization decisions. This local integration is not a public deployment.
