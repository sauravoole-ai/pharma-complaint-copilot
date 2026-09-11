# Production Verification Record

Status: **not yet executed**. External repository, database, backend, frontend, environment-variable, and form operations require explicit user authorization at action time.

This file is a factual run sheet, not evidence that production has passed. Replace each `PENDING` only with an observed result and UTC timestamp.

## Authorized destinations

| Item | Approved destination | Observed URL / identifier |
|---|---|---|
| GitHub repository | PENDING | PENDING |
| PostgreSQL database | PENDING | Record provider/project name only; never record credentials |
| Render backend | PENDING | PENDING |
| Vercel frontend | PENDING | PENDING |

## Configuration checks

| Check | Expected | Result | UTC time |
|---|---|---|---|
| Backend database | PostgreSQL connection succeeds after migration | PENDING | PENDING |
| Backend AI | Groq key configured without disclosure | PENDING | PENDING |
| Groq model | `llama-3.3-70b-versatile`, unless deliberately changed and retested | PENDING | PENDING |
| Backend CORS | Exact public frontend origin | PENDING | PENDING |
| Frontend API origin | Exact public backend origin | PENDING | PENDING |
| Secrets | No secret appears in repository, build log, browser bundle, or this record | PENDING | PENDING |

## Public API checks

| Scenario | Expected evidence | Result | UTC time |
|---|---|---|---|
| Health | `GET /api/v1/health` returns healthy service/database response | PENDING | PENDING |
| Text intake | Synthetic text creates a structured draft | PENDING | PENDING |
| PDF intake | Selectable-text synthetic PDF creates a structured draft | PENDING | PENDING |
| Correction | Batch/quantity correction changes only permitted fields and reruns derived outputs | PENDING | PENDING |
| Direct edit | Edited form fields persist after blur/save | PENDING | PENDING |
| Commit gate | Incomplete or unsaved draft cannot commit | PENDING | PENDING |
| Commit | Explicit human action creates exactly one ledger record | PENDING | PENDING |
| Idempotency | Repeating the same commit token does not duplicate the record | PENDING | PENDING |
| Refresh | Committed ledger record reloads from PostgreSQL | PENDING | PENDING |
| Safe failure | Invalid input and unavailable dependencies produce bounded, non-secret errors | PENDING | PENDING |

## Unauthenticated browser checks

Run in a fresh private browser window with no provider session. HTTP success alone is insufficient.

| View | Visual acceptance criteria | Result | Evidence | UTC time |
|---|---|---|---|---|
| Desktop | Page renders; text/PDF intake, form, copilot, and ledger are visible and usable | PENDING | Screenshot/video timestamp | PENDING |
| Narrow / Pixel 7 | No clipped controls; cards and ledger reflow; primary actions remain reachable | PENDING | Screenshot/video timestamp | PENDING |
| Production root | Opens without a Vercel login/interstitial | PENDING | Private-window observation | PENDING |
| Browser console | No uncaught errors during the full workflow | PENDING | Console observation | PENDING |

## Final production verdict

- Frontend URL: `PENDING`
- Backend health URL: `PENDING`
- Verification result: `NOT RUN`
- Verified by: `PENDING`
- Verified at (UTC): `PENDING`
- Remaining limitations: `PENDING`
