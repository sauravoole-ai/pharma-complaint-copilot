# Live Integration Record

Historical local checkpoint: 2026-09-11 UTC. Deployment status update: 2026-09-18 UTC.

## Deployment status update

The sections below describe the original local checkpoint, not current deployment state.
GitHub publication and Render deployment subsequently occurred. On 2026-09-18, the
connected integrations confirmed both remote `main` and the latest live Render deploy
still use `f3cd68e1936f5f595d745d508d21d3ab1895f169`.

- Repository: https://github.com/sauravoole-ai/pharma-complaint-copilot
- API: https://pharma-complaint-copilot-api.onrender.com
- Database: Supabase project `xmehpxotgxrnqatyucfp`; backend-only schema applied previously.
- Prior live health check (2026-09-12): HTTP 200, database available.
- Prior live synthetic text analysis (2026-09-12): HTTP 502, `ai_analysis_failed`.
  The Groq root cause is not established. No success or end-to-end pass is claimed.
- On 2026-09-18, the connected Vercel team project list contained no project for this app.
- Safe Groq diagnostic code and regression tests exist locally only; not yet published.
- The modified local `backend/uv.lock` is invalid TOML and must not be published.
  Preserve that file; use the valid committed version in an isolated verification copy.
- Current workspace GitHub write access and CLI network restrictions block publication.
Authentication on the user's laptop does not authenticate this workspace.

## Live AI update: 2026-09-18 UTC

- Safe diagnostics deployed at commit `c37e21bac9bc98da2d301cf3ebf040f9b1e2c598`.
- `llama-3.3-70b-versatile` returned provider HTTP 404 during extraction.
- Render `GROQ_MODEL` was changed to `openai/gpt-oss-20b`; no secret changed.
- Synthetic text analysis returned HTTP 201 and created a review draft.
- Synthetic selectable-text PDF analysis returned HTTP 201 and created a ready-to-review draft.
- Conversational correction returned HTTP 200 and updated only the requested structured fields.
- No draft was committed to the ledger during these checks.
- A stale-value summary and overly directive suggested action were observed after correction/PDF
  analysis. They are tracked as release blockers; production workflow is not yet fully passed.

## Historical local result

## Fresh offline verification: 2026-09-18

An isolated archive of the committed source used its committed `backend/uv.lock`,
with only the local safe-diagnostics adapter and regression tests copied in.
The user's invalid modified lockfile remained untouched.

- Frozen dependency installation completed on Python 3.12.14.
- Backend: 32 passed, one opt-in live AI test skipped, one Starlette/AnyIO deprecation warning.
- Ruff lint/format and Python compilation passed.
- Alembic PostgreSQL SQL generation passed; this is not a live database test.
- Frontend: 9 tests passed; TypeScript and production build passed after `npm ci`.
- No live model call, ledger commit, external publication, or deployment occurred in this run.

## Original local AI result

Live Groq execution was not run because `GROQ_API_KEY` is not configured in this workspace. No provider request or billable model call was made. The opt-in smoke test is present at `backend/tests/live/test_groq_smoke.py` and skips unless both `RUN_LIVE_AI=1` and the credential are supplied.

The configured model is `llama-3.3-70b-versatile`. Groq's current model page lists JSON Object Mode for that model: <https://console.groq.com/docs/model/llama-3.3-70b-versatile>.

## Historical offline verification

- Backend: 28 tests passed; Ruff lint and format checks passed; Python compilation passed.
- Frontend: 9 tests passed; TypeScript passed; Vite production build passed.
- Dependency audit: zero production vulnerabilities reported in both npm projects.
- PostgreSQL: Alembic generated PostgreSQL DDL with JSONB, foreign key, and uniqueness constraints. A live PostgreSQL migration was not possible because neither Docker nor PostgreSQL binaries are installed in the workspace.
- PDF: generated artifact is a valid one-page PDF and extraction recovered selectable complaint text.
- Browser E2E: Playwright discovered desktop Chromium and Pixel 7 scenarios, and both web servers started. Execution is blocked because the Chromium CDN download timed out on all five attempts; no visual-pass claim is made.

## Historical deployment configuration review

- `render.yaml` uses a Python web service, `backend/` root directory, frozen uv install, pre-deploy Alembic migration, `$PORT`, and `/api/v1/health`.
- `frontend/vercel.json` declares Vite, `npm run build`, and `dist` output.
- `DATABASE_URL`, `GROQ_API_KEY`, and `FRONTEND_ORIGIN` remain unsupplied deployment secrets/settings.
- No Git remote, GitHub repository, Render service, Vercel project, domain, or external environment variable was created or changed.

Reference configuration documentation:

- Render Blueprint spec: <https://render.com/docs/blueprint-spec>
- Vercel project configuration: <https://vercel.com/docs/project-configuration/vercel-json>
