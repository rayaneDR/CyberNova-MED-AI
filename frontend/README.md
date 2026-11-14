# Frontend mission-control MVP

Run `npm ci` once, then `npm run dev` from this directory. Dependencies are unchanged from the initial scaffold. For production: `npm run lint`, `npm run typecheck`, `npm run build`, then `npm start`.

## Routes

| Route | Behavior |
| --- | --- |
| `/` | Mission and crew overview, vital cards, health trends, recent observations, sensor availability, last recorded timestamp |
| `/health` | Signal and time-range selection, exact values, activity context, quality summary, provenance |
| `/alerts` | Authored statistical/sensor observations, filters, history, explanations, session-local review actions |
| `/check-in` | Required numeric validation, optional notes, asynchronous mock submission, per-astronaut browser-local history |
| `/radiation` | Synthetic daily µSv/day and cumulative mSv, selectable series/ranges, exact-value table |
| `/research` | Curated NASA references, supporting context, limitations, and explicit data provenance |

## Data boundary

- `src/lib/contracts.ts`: original telemetry v0.1 plus frontend-only workspace and check-in types.
- `src/lib/mock-data.ts`: preserved initial standalone fixture.
- `src/lib/mission-fixtures.ts`: three fictional astronauts, deterministic hourly telemetry, staged observations, radiation fixtures, curated source metadata.
- `src/lib/data-source.ts`: preserved `getDashboardData`; new `getWorkspaceData`, `getCheckIns`, `validateCheckIn`, and `submitCheckIn`. API configuration remains reserved and unused.
- `src/components/mission-provider.tsx`: shared selected astronaut and mock response state. Fetch cancellation prevents late responses from replacing the selected session.
- `src/components/mission-shell.tsx`: persistent desktop sidebar, horizontally scrollable mobile navigation, astronaut picker, demo controls.

Use the header's **Demo controls** to select an empty response or service failure and test recovery. Select Adam Idrissi to inspect a missing current SpO₂ reading. Every sensor status is explicitly recorded/synthetic, with no actual connection.

Check-ins save at `cybernova-check-ins-v1:<subjectId>` in localStorage, at most 30 records per astronaut. The crew selection defaults to Maya on page reload; reselect the astronaut to inspect their saved history. Do not enter real personal health information. An invalid existing history is preserved and reported, never overwritten. Review markers in the alert center last until leaving that screen.

The input fatigue scale is 1–10 as requested; the preserved shared telemetry draft still allows 0–10 for its separate illustrative index. Intake is mL and is not converted into the fixture hydration index. Form maxima are validation constraints, not recommended targets.

## Collaboration

No files in backend/, analytics/, simulator/, research/, or shared/contracts/ were changed. Proposed workspace/observations/radiation/check-in response types need agreement with their owners before real API integration. No clinical thresholds, diagnosis, medication advice, scientific results, or actual anomaly algorithm were implemented.

See `../docs/frontend-mvp.md` for verification and remaining integration work.
