# Submission Form Checklist

Submission form named in the assignment: <https://forms.gle/n8ukhVBtNEWnTydV7>

The exact live form labels were not accessible during local preparation. Do not infer or pre-submit hidden fields. Open the form manually, map its current labels to the evidence below, and stop before the final Submit button until the user approves.

## Required evidence

| Deliverable | Value | Acceptance gate |
|---|---|---|
| Candidate identity/contact fields | `PENDING — user enters/reviews` | Matches the application identity |
| GitHub repository | `PENDING` | Correct repository; accessible to reviewers; default branch contains verified commit; README renders |
| Product demo video | `PENDING` | Separate 5–10 minute link; opens without access request; follows `demo-script.md` |
| Code walkthrough video | `PENDING` | Separate 5–10 minute link; opens without access request; follows `code-walkthrough.md` |
| Frontend deployment, if requested | `PENDING` | Private-window visual workflow passes `production.md` |
| Backend/health URL, if requested | `PENDING` | Public health and end-to-end production checks pass |
| Additional text fields | `PENDING — transcribe exact live label before drafting` | Concise, factual, no unsupported claims |

## Proposed short project description

> Pharma Complaint Copilot is a human-in-the-loop complaint-intake prototype for pharmaceutical quality teams. A React/Redux interface sends pasted text or selectable-text PDFs to FastAPI, where a LangGraph workflow uses Groq for structured extraction, advisory risk classification, and summarization. Deterministic completeness rules, controlled corrections, explicit reviewer commit, idempotency, and PostgreSQL persistence keep AI assistance separate from final human control.

## Proposed highlights

- End-to-end mandatory stack: React, Redux Toolkit, FastAPI, LangGraph, Groq, PostgreSQL, and Inter.
- Text and bounded PDF intake with structured, reviewable fields.
- Bonus completeness checker and AI-generated summary.
- Controlled natural-language corrections plus persisted direct edits.
- Explicit human commit, idempotent ledger writes, and responsive review UI.
- Tests across domain contracts, APIs, orchestration, state, components, build, and browser workflow.

## Honest scope statement

> This is an assignment prototype and decision-support demonstration, not a validated pharmaceutical QMS or regulatory decision engine. OCR for scanned documents, authentication, electronic signatures, RBAC, immutable audit trails, and regulated retention are outside the current scope.

## Final multi-pass review

Mark each only after inspecting the actual repository, recordings, and public deployment.

| Pass | Questions | Result |
|---|---|---|
| Assignment compliance | Are both 5–10 minute videos present and is the mandatory stack demonstrated? | PENDING |
| Demo fidelity | Does the flow cover text/PDF input, structured form, copilot risk, correction, commit, and ledger? | PENDING |
| Functional correctness | Do happy paths, validation, retries, persistence, and safe failures behave as claimed? | PENDING |
| Code quality | Are contracts, orchestration, persistence, and UI responsibilities understandable and test-backed? | PENDING |
| Product usefulness | Does the demo explain time saved while preserving reviewer control? | PENDING |
| Domain safety | Are AI outputs advisory and regulated capabilities never overstated? | PENDING |
| Recruiter clarity | Can a reviewer understand the problem, contribution, architecture, and trade-offs quickly? | PENDING |
| Originality | Does the submission explain deliberate product/engineering choices rather than present opaque generated code? | PENDING |
| Accessibility | Are labels, focusable controls, status messages, contrast, and keyboard use acceptable? | PENDING |
| Responsiveness | Does the full workflow remain usable at desktop and Pixel 7 widths? | PENDING |
| Deployment reliability | Do private-window UI, API, database persistence, CORS, and refresh tests pass? | PENDING |
| README accuracy | Are setup, API routes, limitations, and verification commands current? | PENDING |
| Video quality/timing | Is each link public, audible, readable, secret-free, and 5–10 minutes? | PENDING |
| Form completeness | Does every required live field contain the correct reviewed link or answer? | PENDING |
| Secret hygiene | Are `.env`, keys, tokens, database URLs, dashboards, and personal data absent? | PENDING |

## Locked submission sequence

1. Confirm the final commit and fresh test evidence.
2. Confirm the repository link in a signed-out browser.
3. Complete the production verification record, if a deployment is supplied.
4. Record and upload both videos; verify both links signed out.
5. Copy the exact live form labels and assemble a final answer sheet.
6. Present every URL and answer to the user for approval.
7. Only after explicit approval, submit the form once and save the confirmation evidence.
