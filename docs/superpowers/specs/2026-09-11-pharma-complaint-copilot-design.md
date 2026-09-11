# Pharma Complaint Copilot - Design Specification

Date: 2026-09-11  
Status: Approved design baseline  
Purpose: AIVOA Round 1 - AI Product Engineer internship assignment

## 1. Objective

Build an interview-defensible MVP that reproduces the workflow shown in the supplied AIVOA complaint-module demo. A quality reviewer can paste complaint text or upload a text-based PDF, receive structured AI-assisted extraction and risk triage, correct extracted values conversationally, review the resulting form, and explicitly commit the complaint to a PostgreSQL-backed ledger.

The product is a demonstration system, not a production pharmaceutical QMS and not a substitute for a qualified quality professional.

## 2. Success Criteria

The MVP succeeds when all of the following are true:

1. A user can submit realistic synthetic complaint text.
2. A user can upload a text-based complaint PDF.
3. A LangGraph workflow extracts and validates the complaint into a stable structured schema.
4. The React form is populated from the structured result through Redux state.
5. The UI shows an AI-suggested severity, next action, rationale, completeness result, and concise summary.
6. A conversational correction such as changing the batch number and affected quantity updates only the intended fields.
7. AI-derived values remain editable and are visibly presented as suggestions.
8. A complaint is written to PostgreSQL only after the user presses the explicit commit control.
9. The committed record is visible in a minimal complaint ledger.
10. Automated tests prove the principal backend, state-management, and end-to-end flows.

## 3. Scope

### 3.1 Required MVP

- Split-screen desktop interface based on the reference workflow:
  - left: structured Log Customer Complaint form;
  - right: Complaint Copilot conversation and ingestion panel.
- Responsive single-column fallback on narrow screens.
- Complaint ingestion through pasted text or a text-based PDF.
- Structured extraction for origin, customer, product, batch, dates, impact, defect, and requested action.
- AI-suggested initial risk assessment.
- Complaint completeness checker.
- Complaint summary.
- Conversational correction of an existing draft.
- Explicit human review and commit.
- PostgreSQL persistence and a small ledger view.
- Synthetic sample complaints for a reliable demonstration.

### 3.2 Deferred Features

These are intentionally excluded from the initial implementation:

- authentication and multi-tenancy;
- production OCR for scanned images;
- duplicate complaint detection;
- root-cause recommendations;
- CAPA recommendations;
- attachments retained after processing;
- electronic signatures or regulatory audit-trail claims;
- outbound notifications or integrations.

Deferred features may be attempted only after every required acceptance test passes.

## 4. User Experience

### 4.1 Draft States

- `idle`: no complaint submitted;
- `processing`: extraction workflow in progress;
- `needs_review`: extraction succeeded but one or more required fields are missing or uncertain;
- `ready_to_commit`: validation passed sufficiently for human review;
- `committing`: database write in progress;
- `committed`: durable record created;
- `failed`: processing or persistence failed with a recoverable explanation.

### 4.2 Demonstrated Flow

1. The initial form displays placeholders such as `Awaiting AI extraction`.
2. The copilot invites the reviewer to paste raw complaint text or upload a PDF.
3. Submission starts the LangGraph workflow and displays understandable progress.
4. The structured result populates the form.
5. The copilot explains what it extracted and surfaces missing or uncertain fields.
6. The reviewer can directly edit fields or type a correction in the conversation.
7. The correction endpoint applies a constrained patch and returns the updated draft.
8. When the draft is reviewable, the status becomes `Ready to Commit`.
9. The reviewer presses `Commit to QMS Ledger`.
10. The saved record appears in the ledger with its creation time and reviewed values.

### 4.3 Form Fields

Origin and customer:

- complaint source;
- customer name.

Product and batch:

- product type: API or FDF;
- product name;
- product strength;
- batch or lot number;
- affected quantity;
- manufacturing date;
- expiry date.

Facility and material impact:

- originating site block;
- impacted non-product material.

Defect analysis:

- complaint category;
- structured complaint description;
- customer-requested action.

AI assistance:

- suggested severity: `Minor`, `Major`, or `Critical`;
- suggested next action;
- initial risk-assessment rationale;
- missing fields;
- complaint summary.

## 5. Architecture

### 5.1 Frontend

- React with Vite.
- Redux Toolkit as the authoritative client-side workflow state.
- Focused UI units:
  - `ComplaintWorkspace`;
  - `ComplaintForm`;
  - `CopilotPanel`;
  - `WorkflowStatus`;
  - `ComplaintLedger`.
- One API client module maps HTTP responses to typed frontend models.
- Google Inter is the application font.

### 5.2 Backend

- Python and FastAPI.
- Pydantic request/response schemas.
- SQLAlchemy persistence against PostgreSQL.
- Focused service boundaries:
  - document/text ingestion;
  - LangGraph orchestration;
  - deterministic validation;
  - constrained draft correction;
  - complaint persistence.
- External-model calls are isolated behind an LLM adapter so they can be mocked in tests.

### 5.3 LangGraph Workflow

The graph state contains source text, extraction output, validation findings, risk suggestion, summary, errors, and processing messages.

Nodes execute in this order:

1. `normalize_input`: clean and bound the supplied text.
2. `extract_complaint`: obtain schema-constrained complaint fields.
3. `validate_extraction`: perform deterministic type, date, and required-field checks.
4. `assess_completeness`: classify missing and uncertain data.
5. `suggest_risk`: produce severity, next action, and concise rationale.
6. `summarize_complaint`: produce a short factual summary.
7. `assemble_draft`: return the complete draft and readiness state.

The graph assists a human reviewer. It never writes to the complaint ledger.

### 5.4 LLM Selection

The brief's preferred `gemma2-9b-it` model was shut down by Groq on 2025-10-08. The implementation will therefore default to the brief-permitted `llama-3.3-70b-versatile`, configured through `GROQ_MODEL`, with no model name hard-coded into business logic.

Source: https://console.groq.com/docs/deprecations

## 6. API Contract

### `POST /api/v1/complaint-drafts/analyze-text`

Accepts complaint text. Returns the structured draft, copilot messages, completeness result, risk suggestion, and readiness state.

### `POST /api/v1/complaint-drafts/analyze-file`

Accepts one PDF within configured size limits. Extracts text locally and returns the same draft contract. Scanned PDFs return an explicit unsupported/insufficient-text response rather than fabricated content.

### `PATCH /api/v1/complaint-drafts/{draft_id}/conversation`

Accepts a correction message. The model returns a schema-constrained field patch; the server permits only known editable fields, applies the patch, reruns validation/completeness, and returns the updated draft.

### `POST /api/v1/complaints`

Commits a reviewed draft. The server revalidates the submitted values and persists one complaint. Repeated requests with the same commit token must not create duplicates.

### `GET /api/v1/complaints`

Returns recently committed complaints for the ledger.

### `GET /api/v1/health`

Returns application and database health without exposing secrets or internal errors.

## 7. Data Model

### `complaint_drafts`

- UUID primary key;
- source type;
- source-text hash;
- structured complaint JSON;
- completeness JSON;
- risk suggestion JSON;
- summary;
- workflow status;
- created and updated timestamps.

### `complaints`

- UUID primary key;
- immutable source draft ID;
- normalized complaint fields in queryable columns;
- AI suggestion fields;
- reviewer-confirmed status;
- commit token with a uniqueness constraint;
- created timestamp.

The MVP records the reviewed values and timestamps but does not claim compliance-grade electronic records or signatures.

## 8. Safety and Product Controls

- Only synthetic demonstration data is bundled.
- AI-generated severity and next actions are visibly labelled `Suggested`.
- The server never auto-commits after analysis.
- Deterministic validation, not the LLM, determines schema validity and readiness.
- Direct user edits take precedence over AI extraction.
- Corrections are allow-listed field patches rather than arbitrary object replacement.
- Unsupported or unreadable inputs fail clearly.
- Provider errors are converted to safe, actionable application errors.
- Secrets are loaded only from environment variables and excluded from version control.
- README and UI state that the project is an assignment demonstration, not a validated production QMS.

The human-review gate reflects pharmaceutical quality-system principles that complaints require controlled evaluation and investigation. References:

- ICH Q10 Pharmaceutical Quality System: https://database.ich.org/sites/default/files/Q10%20Guideline.pdf
- FDA CGMP records and reports: https://www.fda.gov/drugs/guidances-drugs/questions-and-answers-current-good-manufacturing-practice-requirements-records-and-reports
- WHO Quality Risk Management: https://www.who.int/docs/default-source/medicines/norms-and-standards/guidelines/production/trs981-annex2-who-quality-risk-management.pdf

## 9. Error Handling

- Empty input: `422` with a field-level message.
- Unsupported file: `415`.
- Oversized file: `413`.
- PDF without sufficient extractable text: `422`.
- Invalid model output after bounded repair/retry: `502` with no raw provider response.
- Model rate limit or timeout: `503` with a retryable message.
- Unknown draft: `404`.
- Invalid correction patch: `422`.
- Duplicate commit token: return the existing complaint rather than create another.
- Database unavailable: `503`; the unsaved draft remains in frontend state.

## 10. Verification Strategy

### Backend

- Unit tests for normalization, validation, correction allow-listing, readiness, and error mapping.
- LangGraph tests with a fake LLM adapter.
- API tests for text analysis, file analysis, correction, commit idempotency, ledger, and health.
- PostgreSQL integration test for persistence and uniqueness behavior.

### Frontend

- Redux reducer/thunk tests for all draft states.
- Component tests for form population, editing, progress, errors, and manual commit.

### End to end

- Paste the synthetic discoloration complaint.
- Verify extracted fields and `Major` suggestion.
- Correct the batch to `BMX240602` and quantity to `48 capsules`.
- Verify only those fields change.
- Commit once and verify one ledger entry.
- Upload the synthetic foreign-matter PDF.
- Verify a `Critical` suggestion and no automatic commit.
- Verify narrow and desktop layouts visually.

No live Groq call is required for automated tests. One controlled live call is used only for final integration verification and the demonstration.

## 11. Deployment

Development and testing are local first. Deployment begins only after the local acceptance suite passes.

Planned deployment topology:

- Vercel: static React frontend;
- Render: FastAPI backend;
- Supabase: managed PostgreSQL database;
- environment variables configured separately on each service;
- browser verification of the complete public workflow after deployment.

Deployment is valuable but not allowed to delay the mandatory repository and videos.

## 12. Submission Package

- Original GitHub repository with meaningful commit history.
- Clear setup instructions and architecture explanation.
- `.env.example` containing names only.
- Synthetic text and PDF samples.
- Product demonstration video.
- Separate code and architecture walkthrough video.
- Honest model-deprecation note.
- Submission-form responses reviewed before the user submits them.

The implementation must remain independently authored. Public repositories created for the same assignment are not implementation references and must not be copied.

## 13. Scope Check

This specification defines one cohesive MVP. Every component supports the demonstrated complaint-ingestion, review, correction, and commit journey. Deferred features do not enter implementation until the required acceptance suite is green.
