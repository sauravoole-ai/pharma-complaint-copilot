# Live Integration Record

Production verification completed on 2026-09-22 UTC using repository-owned synthetic samples only.

## Deployment

- Repository: https://github.com/sauravoole-ai/pharma-complaint-copilot
- Frontend: https://pharma-complaint-copilot.vercel.app
- Vercel production deployment: `dpl_6ZTce67auLBniFNv2qu3tVDybh46` (`https://pharma-complaint-copilot-ix3rh5aud-sauravoole-1831s-projects.vercel.app`), Ready.
- Backend: https://pharma-complaint-copilot-api.onrender.com
- Render deployment: `dep-danvso3m8hqs73cp2610`, commit `61bb0bd16d33a1f332b7dbb11a2bedb40299d9d5`, live.
- Health: `GET /api/v1/health` returned HTTP 200.
- CORS: `FRONTEND_ORIGIN=https://pharma-complaint-copilot.vercel.app`; the health response returned that exact allow-origin value.
- Groq model: `openai/gpt-oss-20b`.

## Synthetic workflow evidence

- Text sample `samples/discoloration-complaint.txt` produced a structured draft with batch `AMX240602` and `48 capsules`.
- The authorized correction to `25 capsules` updated the structured field and regenerated the summary with `25 capsules`; the stale `48 capsules` value was absent from the summary.
- PDF sample `samples/foreign-matter-complaint.pdf` produced a structured foreign-matter / visible-particulate draft with summary, completeness, advisory risk, and a human-review requirement.
- Suggested next actions did not direct a recall or regulatory notification. They remained internal containment/investigation and qualified human-quality-review guidance.
- Browser network evidence recorded only draft analysis/correction requests; it did not record `POST /api/v1/complaints`.
- Public ledger count was 0 before and after verification. No complaint was committed; temporary drafts may remain.

## Browser and operational checks

- Fresh unauthenticated desktop and Pixel 7-sized sessions rendered AIVOA branding, intake, Copilot, and ledger areas without horizontal overflow or clipped primary controls.
- The final Pixel 7 accessibility scan reported zero WCAG 2 A/AA violations. One decorative, `aria-hidden` ledger icon remained manual-review-only for contrast.
- Browser page-error output was clean during the completed workflows. Public HTML, JavaScript, CSS, and backend health returned HTTP 200.
- Render error-level logs and Vercel deployment logs were clean for the checked period.

## Local verification

- Backend: 36 passed, 1 opt-in live test skipped; Ruff lint and format checks passed.
- Frontend: 10 passed; TypeScript and Vite production build passed; production dependency audit reported zero vulnerabilities.
- Focused tracked-file secret scan reported zero findings.

This independently developed AIVOA assignment prototype is decision support only. It is not a validated QMS, medical device, electronic-signature system, regulatory determination engine, or official AIVOA product. All test inputs used for these checks are synthetic.
