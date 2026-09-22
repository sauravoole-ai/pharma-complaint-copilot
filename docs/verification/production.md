# Production Verification Record

Verified 2026-09-22 UTC with repository-owned synthetic samples only.

| Check | Observed result |
|---|---|
| Stable frontend | https://pharma-complaint-copilot.vercel.app |
| Immutable Vercel deployment | `dpl_6ZTce67auLBniFNv2qu3tVDybh46` — https://pharma-complaint-copilot-ix3rh5aud-sauravoole-1831s-projects.vercel.app (Ready) |
| Render backend | https://pharma-complaint-copilot-api.onrender.com |
| Render deployment | `dep-danvso3m8hqs73cp2610`, commit `61bb0bd16d33a1f332b7dbb11a2bedb40299d9d5` (live) |
| Backend health | HTTP 200 |
| CORS | `FRONTEND_ORIGIN=https://pharma-complaint-copilot.vercel.app`; response allow-origin matched exactly |
| Text intake | Structured draft populated with `AMX240602` and `48 capsules` |
| Correction consistency | `25 capsules` updated both the field and regenerated summary; no stale `48 capsules` remained in the summary |
| PDF intake | Foreign matter / visible particulate draft rendered with structured fields, summary, completeness, advisory risk, and human review |
| Advisory guard | No tested next action directed recall or regulatory notification; qualified human review remained required |
| Desktop | Branding, workspace, Copilot, ledger, controls, and public access verified without horizontal overflow |
| Pixel 7 | Controls and labels remained reachable and readable; no horizontal overflow; ledger reflowed correctly |
| Accessibility | Final WCAG 2 A/AA scan: zero violations; one `aria-hidden` decorative icon requires no user-facing action |
| Console/network | No page errors in completed workflows; no `POST /api/v1/complaints` request recorded |
| Logs | Render error-level and Vercel deployment logs clean for the checked period |
| Ledger | 0 records before and after; no record committed |
| Local checks | Backend: 36 passed, 1 skipped; frontend: 10 passed; Ruff, TypeScript, Vite build, and production dependency audit passed |

## Remaining limitations

The prototype does not claim validated QMS status, electronic signatures, medical-device status, regulatory validation, autonomous decision-making, OCR for scanned PDFs, authentication, or regulatory retention. The reviewer retains responsibility for every quality and regulatory decision. No complaint, patient, pharmacy, or batch data used for verification was real.
