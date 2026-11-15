# Verification and release status — November 14, 2026

## Final presentation delivery recheck

- From `frontend/`: `npm run lint`, `npm run typecheck`, and `npm run build` all passed. The production build compiled and generated the app routes.
- From the repository root: `backend/.venv/Scripts/python.exe -m pytest analytics/tests backend/tests -q` — **51 passed**, with one upstream Starlette/AnyIO deprecation warning.
- Public HTTP checks returned **200** for `/`, `/health`, `/alerts`, `/check-in`, `/radiation`, and `/research` on the Vercel demo URL.
- A desktop browser opened the public overview in explicitly labeled Demo fixtures mode and showed fictional crew, synthetic vitals, and authored demo observations.
- Tracked-file review found no tracked `.env` files or SQLite database files; a credential-pattern scan returned no matches. `.env.example` templates are tracked.
- The new final reviewed deck has seven slides at 16:9; PPTX integrity and layout validation passed with zero findings. The matching PDF has seven pages. The original PPTX/PDF remain untouched. The deck is editable but static; no native PowerPoint animations were authored.
- The public Vercel deployment is frontend-only; its Demo mode does not contact the local FastAPI/SQLite service.
- No Space Apps submission was made. The current public 2026 Project Submission Guide did not load and the signed-in team Project tab was unavailable. Required field names, character limits, attachment constraints and AI disclosure wording still need confirmation in the official portal.

## Repository snapshot before this delivery commit

- Local integration history: `feature/analytics-integration` at `7f826b07d034469fcbc8c734d39114aa82f359e6`.
- `origin` is `https://github.com/rayaneDR/CyberNova-MED-AI.git`.
- GitHub identity and public repository were verified in the connected GitHub integration as `rayaneDR`; GitHub default branch `main` was at `24c1046`, and public `feature/frontend` was at `72d9bcd`.
- `git fetch origin --prune` succeeded. No remote feature/backend/analytics branch was present before this delivery. No existing local modifications were present before edits.
- The feature history contains `origin/main`; `git merge-base --is-ancestor origin/main HEAD` succeeded. No merge was performed.
- `gh` is not installed in this Windows environment. GitHub connector is available. A public release PR is open at https://github.com/rayaneDR/CyberNova-MED-AI/pull/1; it targets `main` and is mergeable. No merge was performed.

## Exact checks run

From `frontend/`:

```powershell
npm run lint
npm run typecheck
npm run build
```

All passed. Build produced the overview plus five additional pre-rendered screens. After local dev server startup, the NASA Research route rendered the OSDR metadata card. At the observed narrow browser viewport, the native mobile navigation expanded to all six route links. Existing saved responsive screenshots cover all six routes at 390 px and desktop sizes; no claim is made here about a fresh 375 px sweep in this session.

From repository root:

```powershell
backend/.venv/Scripts/python -m pytest analytics/tests backend/tests -q
```

Result: **51 passed, 1 dependency deprecation warning** (`anyio.abc.BlockingPortal` imported by Starlette's TestClient). No failing tests.

`git diff --check` passed. Tracked environment files are examples only: `.env.example`, `frontend/.env.example`, and `backend/.env.example`. `.gitignore` excludes local `.env*`, database files, virtual environments, caches, build output, and Playwright artifacts. No local secrets or database were added.

## Previously verified backend demonstration

The preceding integration task on this branch ran FastAPI and the Next.js frontend locally, ingested Amina's original simulator sample in normal/anomaly/dropout modes (19 accepted synthetic packets), observed backend measurements and separate data-quality/statistical records, submitted a synthetic check-in, and confirmed SQLite persistence after page refresh. Those integration steps were recorded in the earlier task session; they were not repeated as part of the documentation/UI-only change in this release commit.

## NASA source validation

The OSDR OSD-53 catalog and sample metadata API returned study and sample metadata. The processed-file endpoint returned content that failed ZIP validation. Therefore the app includes only a small derived catalog metadata summary and does not claim to ingest or analyze molecular measurement values. Details, transformation, date, and limits are in [NASA provenance](nasa-data-provenance.md).

## Deployment and security status

The frontend is deployed to https://cybernova-med-ai.vercel.app (Vercel production deployment `DT8kaTmpqhsk9YzxgRvi8XyYgwXB`, ready on 2026-11-14). Public HTTP checks returned 200 for `/`, `/research`, and `/check-in`; each response contained the synthetic Demo label. Vercel dry-run confirmed `.env.local` and `.vercel` were excluded. No backend URL or secret was configured in the Vercel project, so this public site uses synthetic Demo fixtures only. The API contains writable demo endpoints; the browser client does not send a write token. The local backend is documented for loopback-only use. Do not expose writes publicly until an authenticated proxy/client design, HTTPS, persistence, CORS, and environment configuration are implemented and reviewed.

## Pitch artifact status

The editable PowerPoint and seven-page PDF are in `submission/`. The PPTX first-party finalizer passed package integrity and layout checks: seven slides, 16:9, zero geometry/font-policy findings, and successful import. The PDF is built from the rendered seven slide PNG previews because the bundled runtime's direct PDF exporter failed on a missing `#standard-fonts/Helvetica` module; PDF magic and seven page objects were verified. Native PowerPoint execution was not verified.

## Dependency audit limitation

The repository's earlier dependency audit recorded moderate development-tool findings in transitive tooling and ESLint 9 deprecation; no force-upgrade or peer bypass was used. Recheck the current lockfile before any deployment.
