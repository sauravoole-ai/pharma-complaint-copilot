# Live Integration Record

Date: 2026-09-11 UTC

## Result

Live Groq execution was not run because `GROQ_API_KEY` is not configured in this workspace. No provider request or billable model call was made. The opt-in smoke test is present at `backend/tests/live/test_groq_smoke.py` and skips unless both `RUN_LIVE_AI=1` and the credential are supplied.

The configured model is `llama-3.3-70b-versatile`. Groq's current model page lists JSON Object Mode for that model: <https://console.groq.com/docs/model/llama-3.3-70b-versatile>.

## Offline verification

- Backend: 28 tests passed; Ruff lint and format checks passed; Python compilation passed.
- Frontend: 9 tests passed; TypeScript passed; Vite production build passed.
- Dependency audit: zero production vulnerabilities reported in both npm projects.
- PostgreSQL: Alembic generated PostgreSQL DDL with JSONB, foreign key, and uniqueness constraints. A live PostgreSQL migration was not possible because neither Docker nor PostgreSQL binaries are installed in the workspace.
- PDF: generated artifact is a valid one-page PDF and extraction recovered selectable complaint text.
- Browser E2E: Playwright discovered desktop Chromium and Pixel 7 scenarios, and both web servers started. Execution is blocked because the Chromium CDN download timed out on all five attempts; no visual-pass claim is made.

## Deployment configuration review

- `render.yaml` uses a Python web service, `backend/` root directory, frozen uv install, pre-deploy Alembic migration, `$PORT`, and `/api/v1/health`.
- `frontend/vercel.json` declares Vite, `npm run build`, and `dist` output.
- `DATABASE_URL`, `GROQ_API_KEY`, and `FRONTEND_ORIGIN` remain unsupplied deployment secrets/settings.
- No Git remote, GitHub repository, Render service, Vercel project, domain, or external environment variable was created or changed.

Reference configuration documentation:

- Render Blueprint spec: <https://render.com/docs/blueprint-spec>
- Vercel project configuration: <https://vercel.com/docs/project-configuration/vercel-json>
