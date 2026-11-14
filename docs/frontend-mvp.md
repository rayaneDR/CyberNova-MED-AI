# Frontend MVP handoff

Base inspected: clean `main` at `24c1046`. Implementation branch: `feature/frontend`. Main is not merged or rewritten. The original application already provided a typed mock boundary, v0.1 telemetry shape, six indicator values, a simple chart, CI, and collaboration documentation. These are extended into six mission-control screens, with the original standalone fixture/adapter entry point retained.

## Behavior and ownership

See `frontend/README.md` for routes and data boundaries. UI and mocks are in frontend/ only. Backend, analytics, simulator, research, shared contracts, and dependencies are unchanged. Next.js generated `frontend/AGENTS.md` during development; its version-specific documentation instructions were read and followed.

The crew/provider state persists across client navigation. A full reload intentionally defaults to the first astronaut. Each astronaut has a separate fixed 72-hour session and distinct per-browser check-in history. The simulated mission is at day 14 of 30, ending its recorded telemetry at 2026-11-14T12:00:00Z. This is historical synthetic data, not a live sensor feed.

Sensor loss is separate from statistical deviation in icons, labels, filters, and explanations. Statistical observations are pre-authored fixture records; no part of Ali's algorithm is implemented. Review markers affect only screen-local UI state. The history's resolved status remains the original fixture status.

Check-in validation: sleep 0–24 hours; integer fatigue 1–10; intake 0–10,000 mL; optional notes up to 500 characters. Empty required numeric inputs are rejected rather than coerced to zero. Validation applies again inside the mock adapter. Save failures keep form values, show no false success, and preserve invalid stored records. Successful saves persist to localStorage, maximum 30 entries per astronaut. Fixture vitals and daily summaries are not changed by a self-report.

Radiation rates and cumulative dose are invented. Cumulative mSv is the sum of all daily µSv divided by 1,000. Selecting seven days does not reset cumulative exposure. No hazard thresholds or clinical categories are rendered.

The NASA cards link to the three existing curated references and explain both their relevance and their limits. Sources were reopened and checked November 14, 2026. No NASA dataset is imported or analyzed, and no reference validates our demo values or scores.

## Review and verification

- `npm run lint`: passed with zero warnings after implementation.
- `npm run typecheck`: passed after explicitly typing the observation fixtures.
- Browser navigation smoke checks: astronaut selection, sensor gaps, 72/6-sample ranges, observation type/history filters, review action, filter-empty state, service-empty/error recovery, and removal of stale values.
- Check-in browser checks: blank/out-of-range rejection, valid asynchronous save, history after reload and astronaut reselection, isolation between astronauts.
- Radiation checks: daily/cumulative selection, 7/14-day ranges, and exact cumulative unit conversion.
- Responsive screenshots and overflow checks cover all six routes at phone, tablet, and desktop sizes. Evidence is in ignored `output/playwright/` so review artifacts do not add binary files to the source commit.
- `npm run build`: passed; overview and all five additional routes pre-rendered successfully.
- `npm start -- --hostname 127.0.0.1 --port 3000`: passed. All six production routes returned HTTP 200 with no runtime errors or console warnings on the valid screens. Unknown route returned HTTP 404 with working overview recovery (the expected missing-resource console entry is separate from valid-route checks).
- Production checks also verified rapid astronaut switching cannot restore an older response, and keyboard navigation reaches the skip link first and moves focus to main.
- Corrupted browser-storage check: read and save errors were shown; no false success was shown; the invalid original record was preserved.
- `impeccable.cmd detect --json frontend/src`: returned no findings. `git diff --check`: passed.

## Remaining integration work

Khawla must provide agreed live API endpoints; Ali owns real statistical algorithms/alerts; Amina owns simulator output; Ayoub reviews indicator definitions and scientific claims. The frontend-only workspace extensions are proposals, not changes to the shared draft. Add runtime validation, authentication if needed, and live-mode staleness/failure semantics before integrating real data. Do not silently fall back to fixtures on real API errors.

Current limitations: browser-local check-ins are not shared with the team; review markers are not persisted; mission values and all measurements are synthetic; no hosting deployment is performed. Existing development-tool audit findings and ESLint 9 deprecation remain as documented in `verification.md`; no new dependencies were introduced.
