# Architecture

## Frontend MVP update

The six-screen frontend is documented in [frontend-mvp.md](frontend-mvp.md). The initial slice below is historical context. The current App Router root layout hosts a persistent client mission provider and shell; the server pages select the appropriate screen. The provider supports explicit Demo fixtures and Live API modes, cancellation, loading, empty and error states. Live mode uses typed FastAPI responses; Demo mode retains the mock adapter. Backend analytics and the integration-owned non-clinical personal-baseline engine are documented in [analytics-integration.md](analytics-integration.md). No teammate module or shared contract was changed for that integration.

The visual system uses dark navy surfaces with cyan accents. Daily check-ins use browser-local storage in Demo mode and persist through FastAPI/SQLite in Live mode. Live observations and radiation history map from backend contracts, while demo fixtures remain clearly marked synthetic.

## Initial slice

The Next.js App Router server page calls `getDashboardData()` in `frontend/src/lib/data-source.ts`. That function returns a fresh copy of deterministic synthetic fixtures. The page renders six indicators and sends serializable samples to a small client component for Recharts and metric selection. The rest of the page stays server rendered. Tailwind CSS v4 is configured through PostCSS; domain-specific CSS supplies the layout and visual tokens.

Palette: navy `#182f46`, blue `#1766ba`, mist `#f2f6fa`, white `#ffffff`, slate `#526477`, amber notice `#fff7df`. System Segoe UI/Arial avoids network font downloads. The overview uses a shared six-indicator grid above a wide signal window and a research context panel. Reading order stays linear on phones; no animation is needed for fixed samples.

## Ownership boundaries

```text
Amina: simulator ──telemetry──> Khawla: FastAPI + SQLite
                                      │
                              Ali: analytics + alerts
                                      │
Rayane: Next.js <── agreed API ─────────┘
Ayoub: research + JSON specifications ──> contract/science review
```

The diagram describes ownership. The FastAPI/SQLite service and Next.js-to-API adapter run locally. Rayane owns backend and integration; Ali owns statistical review; Amina owns simulator behavior; Ayoub owns indicator definitions and scientific evidence.

## Integration sequence

1. Keep the v1 schemas aligned with FastAPI response models and adapters.
2. Run Amina's original simulator only with registered source sessions and clearly synthetic data.
3. Have Ali review the independently implemented integration-owned baseline engine and Ayoub review scientific indicators and evidence before describing results as team-validated.
4. Keep all statistical observations non-diagnostic and independent of research-only thresholds.

Use explicit null for unavailable readings, never zero as a missing-value sentinel. Keep synthetic provenance through storage and transport. Never silently convert an API failure into mock mode. No real personal or patient data is needed for this MVP.

## Deployment and reliability

Rayane can deploy `frontend/` as the Next.js project root with `npm ci`, `npm run build`, and `npm start` on Node 24. Hosting is not configured or published. Live mode also needs the FastAPI service, SQLite persistence, environment configuration, and exact CORS origin; Demo mode remains available without the backend. NASA links require internet.

CI runs install, lint, route type generation/type checking, and production build. Backend and analytics tests cover the local integration. Radiation keeps source dose rates distinct from completed daily and cumulative dose quantities.
