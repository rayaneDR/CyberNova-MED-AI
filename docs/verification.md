# Initialization and verification — November 14, 2026

## Workspace and GitHub status

Inspected the starting workspace with `Get-Location`, `Get-ChildItem -Force`, and `rg --files --hidden -g '!node_modules' -g '!.git' .`. It contained only empty `outputs/` and `work/` directories. No existing project files were overwritten. No applicable parent AGENTS.md was found. Deliverable repository: `outputs/CyberNova-MED-AI/` under the original workspace.

`git status --short --branch` initially reported that the starting workspace was not a Git repository. `gh auth status` failed because the GitHub CLI command was unavailable; common installation paths were absent too. GitHub authentication, repository existence, visibility, and remote URL could not be verified. **No GitHub repository was created and no initial commit was pushed.** `git remote -v` returns no remotes. Follow `docs/github-setup.md` for exact manual authentication and publication steps.

## Environment and final versions

`node --version`: `v24.20.0`; `npm --version`: `11.19.0`; `git --version`: `2.54.0.windows.1`.

| Direct package | Resolved version |
| --- | --- |
| Next.js / eslint-config-next | 16.4.6 |
| React / React DOM / React IS | 19.3.1 |
| Tailwind CSS / @tailwindcss/postcss | 4.3.5 |
| Recharts | 3.10.1 |
| Lucide React | 1.73.0 |
| TypeScript | 5.9.3 |
| ESLint | 9.39.5 |
| @types/node | 24.19.2 |
| @types/react / @types/react-dom | 19.3.0 |

Versions and peer requirements were checked with `npm view next version engines --json`, `npm view react version`, `npm view recharts version peerDependencies --json`, `npm view eslint-config-next version peerDependencies --json`, `npm view tailwindcss version`, and `npm view lucide-react version`. Next.js installation requirements were also checked against https://nextjs.org/docs/app/getting-started/installation. `package-lock.json` captures the installed dependency tree.

## Exact setup and frontend commands

Commands below ran from the starting workspace unless a working directory is specified.

```powershell
New-Item -ItemType Directory -Path outputs/CyberNova-MED-AI -Force
git init -b main outputs/CyberNova-MED-AI
```

Both succeeded. Source/configuration/documentation files were then created. From the repository root:

```powershell
git config user.name Rayane
git config user.email rayaneDR@users.noreply.github.com
```

These set repository-local commit identity only, not global settings or GitHub authentication. The noreply address is not asserted to be a verified GitHub email.

From `frontend/`:

| Exact command | Result |
| --- | --- |
| `npm install --save-exact` | Passed; 400 packages added, 407 audited; initial download took about 9 minutes |
| `npm run lint` (initial) | Failed on one anonymous PostCSS default-export warning; corrected by naming the exported config |
| `npm run typecheck` (initial) | Passed |
| `npm run build` (initial) | Passed; static homepage generated |
| `npm audit --json` | Reported seven moderate development-tool findings |
| `npm audit fix --dry-run --json` | Exit 1; no dependency update that resolved the findings proposed; no forced fix applied |
| `npm install --save-dev --save-exact eslint@10.15.0` | Installed with peer warnings; `npm ls eslint` exposed incompatible plugin peer ranges |
| `npm install --save-dev --save-exact eslint@9.39.5` | Restored compatible version; this is the final version |
| `npm ci` (final clean installation) | Passed; 400 packages added, 407 audited in about 3 minutes |
| `npm ls --depth=0` (after clean installation) | Passed; no invalid peers or extraneous entries reported |
| `npm run lint` (final) | Passed with zero warnings |
| `npm run typecheck` (final) | Passed: route types generated and TypeScript completed |
| `npm run build` (final) | Passed: routes `/`, `/_not-found`, and `/icon.svg` statically generated |
| `npm audit --omit=dev --audit-level=moderate` | Passed: zero production dependency vulnerabilities |
| `npm start -- --hostname 127.0.0.1 --port 3000` | Passed: production server ready |

The final lint/type/build sequence used PowerShell exit guards so a failed earlier check would stop subsequent checks. CI contains the same clean-install, lint, typecheck, build steps, but GitHub Actions has not run because publication is pending.

## Browser and HTTP verification

Used `npx --yes --package @playwright/cli playwright-cli` for browser smoke checks, without adding browser automation dependencies to the project.

Commands included:

```powershell
npx --yes --package @playwright/cli playwright-cli -s=cybernova open about:blank
npx --yes --package @playwright/cli playwright-cli -s=cybernova goto http://127.0.0.1:3000
npx --yes --package @playwright/cli playwright-cli -s=cybernova select e82 spo2Percent
npx --yes --package @playwright/cli playwright-cli -s=cybernova resize 1440 1000
npx --yes --package @playwright/cli playwright-cli -s=cybernova click e152
npx --yes --package @playwright/cli playwright-cli -s=cybernova resize 390 844
npx --yes --package @playwright/cli playwright-cli -s=cybernova eval "() => ({width: innerWidth, scrollWidth: document.documentElement.scrollWidth, sampleRows: document.querySelectorAll('tbody tr').length, selected: document.querySelector('select').value})"
npx --yes --package @playwright/cli playwright-cli -s=cybernova-final open http://127.0.0.1:3000
```

Element references came from fresh browser snapshots. Verified six indicators, synthetic labeling and disclaimer, metric selection, and table expansion. Mobile evaluation returned `{ "width": 390, "scrollWidth": 390, "sampleRows": 12, "selected": "spo2Percent" }`. Desktop and mobile screenshots were visually inspected. An initial favicon 404 was fixed with `src/app/icon.svg`; the final fresh browser load reported no console events in its snapshot. Screenshot evidence lives in ignored `output/playwright/`.

`Invoke-WebRequest -Uri 'http://127.0.0.1:3000'` and `Invoke-WebRequest -Uri 'http://127.0.0.1:3000/icon.svg'` returned HTTP 200; the homepage included the synthetic-data label.

## Limitations and other checks

- Seven moderate findings remain in development tooling, rooted in minimatch via TypeScript ESLint: https://github.com/advisories/GHSA-g3hv-75wg-m249. The selected tooling still requires minimatch 10; the advisory lists a fix in 11.0.1. No unsupported transitive override was introduced. ESLint 9 is deprecated, but the ESLint 10 experiment exposed incompatible peer ranges in bundled React/import/accessibility plugins. Revisit these together after the hackathon or when compatible packages are available.
- Optional JSON Schema validation using Python was attempted and could not run: `ModuleNotFoundError: No module named 'jsonschema'`. No Python dependency or teammate module was installed. The example and schema are drafts, not a verified API implementation.
- `git check-ignore frontend/node_modules frontend/.next frontend/.env.local` confirmed generated files and secrets are ignored. `git diff --check` passed.
- NASA research links were checked via web research. They provide background, not clinical validation. No live telemetry, AI model, backend, analytics, simulator, radiation model, or deployment was implemented.
- Repository-local initial commit command: `git add .` then `git commit -m "chore: initialize CyberNova MED AI workspace and frontend demo"`. Final branch/status and HEAD are verified after this report is written. No remote URL exists locally; no URL is invented here.
