# Production Verification Record

Status: **partial deployment; full production workflow not verified**.
Repository/database/backend deployment was authorized and performed. Frontend deployment,
full browser checks, videos, and submission remain pending. Form submission is not authorized.
See `live-integration.md` for dated observations; live deployment status is not proof of AI success.

This file is a factual run sheet, not evidence that production has passed. Replace each `PENDING` only with an observed result and UTC timestamp.

## Authorized destinations

| Item | Approved destination | Observed URL / identifier |
|---|---|---|
| GitHub repository | sauravoole-ai/pharma-complaint-copilot | https://github.com/sauravoole-ai/pharma-complaint-copilot |
| PostgreSQL database | Supabase | Project xmehpxotgxrnqatyucfp; no credentials recorded |
| Render backend | pharma-complaint-copilot-api | https://pharma-complaint-copilot-api.onrender.com |
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
| Text intake | Synthetic text creates a structured draft | FAILED: HTTP 502 ai_analysis_failed; cause unknown | 2026-09-12; exact time not retained |
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
- Backend health URL: `https://pharma-complaint-copilot-api.onrender.com/api/v1/health`
- Verification result: `PARTIAL; FULL WORKFLOW NOT PASSED`
- Verified by: `PENDING`
- Verified at (UTC): `PENDING`
- Remaining limitations: `PENDING`
