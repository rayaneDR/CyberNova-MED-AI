# Architecture

## Initial slice

The Next.js App Router server page calls `getDashboardData()` in `frontend/src/lib/data-source.ts`. That function returns a fresh copy of deterministic synthetic fixtures. The page renders six indicators and sends serializable samples to a small client component for Recharts and metric selection. The rest of the page stays server rendered. Tailwind CSS v4 is configured through PostCSS; domain-specific CSS supplies the layout and visual tokens.

Palette: navy `#182f46`, blue `#1766ba`, mist `#f2f6fa`, white `#ffffff`, slate `#526477`, amber notice `#fff7df`. System Segoe UI/Arial avoids network font downloads. The overview uses a shared six-indicator grid above a wide signal window and a research context panel. Reading order stays linear on phones; no animation is needed for fixed samples.

## Planned ownership boundaries (not implemented)

```text
Amina: simulator ──telemetry──> Khawla: FastAPI + SQLite
                                      │
                              Ali: analytics + alerts
                                      │
Rayane: Next.js <── agreed API ─────────┘
Ayoub: research + JSON specifications ──> contract/science review
```

The arrows describe proposed responsibilities, not running integrations. Khawla owns persistence, validation, CORS, and API failure semantics. Ali owns algorithms and alert output; Amina owns simulator behavior. Ayoub owns indicator definitions and the scientific evidence. No implementation for these modules is supplied.

## Integration sequence

1. Agree draft v0.1 contracts and validate sample payloads with all owners.
2. Khawla exposes the agreed API; Amina supplies clearly marked synthetic samples.
3. Rayane adds a validated API adapter behind `getDashboardData`, explicit error/empty/stale states, and a clearly labeled mode selector if needed. `NEXT_PUBLIC_API_BASE_URL` is reserved; changing it currently has no effect.
4. Ali and Ayoub agree any alert semantics and evidence before alerts reach the UI. Do not infer clinical alerts from fixture values.

Use explicit null for unavailable readings, never zero as a missing-value sentinel. Keep synthetic provenance through storage and transport. Never silently convert an API failure into mock mode. No real personal or patient data is needed for this MVP.

## Deployment and reliability

Rayane can deploy `frontend/` as the Next.js project root with `npm ci`, `npm run build`, and `npm start` on Node 24. Hosting is not configured or published by this initialization. No Python service is needed for the demo. Fixed fixtures and local fonts permit an offline local pitch after packages are installed. The NASA link requires internet.

CI runs install, lint, route type generation/type checking, and production build. Runtime integration tests should be added when the API exists. Optional radiation stays outside the draft payload until units, provenance, and meaning are agreed.
