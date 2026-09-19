# Code and Architecture Walkthrough

This reference follows one request end to end and highlights the system's principal engineering decisions.

## Files to pre-open

1. `frontend/src/components/ComplaintWorkspace.tsx`
2. `frontend/src/store/complaintSlice.ts`
3. `frontend/src/api/client.ts`
4. `backend/app/api/drafts.py`
5. `backend/app/ai/graph.py`
6. `backend/app/ai/llm.py`
7. `backend/app/services/validation.py`
8. `backend/app/repositories/complaints.py`
9. `backend/app/api/complaints.py`
10. `backend/app/db_models.py`
11. Representative backend, frontend, and end-to-end tests

## Timed walkthrough

### 0:00–0:45 — Architecture and trust boundary

Use the README architecture diagram. Explain that the React client handles interaction, Redux coordinates asynchronous state, FastAPI validates the boundary, LangGraph orchestrates analysis, Groq supplies structured proposals, deterministic rules enforce completeness, and PostgreSQL persists drafts and reviewed records.

### 0:45–1:50 — Frontend input to Redux

In `ComplaintWorkspace.tsx`, show the mutually exclusive text/PDF paths, input constraints, disabled/loading states, and accessible labels. Move to `complaintSlice.ts` and trace `analyzeText` or `analyzeFile` from its `createAsyncThunk` through pending, fulfilled, and rejected state.

Emphasize that the active draft, messages, ledger, request status, and safe error state are explicit rather than hidden in components.

### 1:50–2:35 — Typed API boundary

In `api/client.ts`, show `VITE_API_BASE_URL`, multipart PDF upload, JSON requests, error parsing, and Zod response validation. Explain that malformed server data is rejected at the client boundary instead of silently entering Redux.

### 2:35–3:30 — FastAPI intake routes

In `backend/app/api/drafts.py`, trace `/analyze-text` and `/analyze-file`. Show Pydantic request/response types, bounded PDF parsing, source type, SHA-256 source hashing, and safe 4xx/5xx responses. Mention that raw complaint text is not stored in the draft table.

### 3:30–4:35 — LangGraph and Groq

In `backend/app/ai/graph.py`, follow the nodes: normalize input, extract, validate, assess completeness, suggest risk, summarize, and assemble the draft. In `llm.py`, show the adapter protocol and Groq structured-output calls.

Explain the model choice factually: the assignment's preferred `gemma2-9b-it` is retired,
and live verification found the allowed `llama-3.3-70b-versatile` unavailable to the configured
Groq project (HTTP 404). The implementation therefore uses the current production model
`openai/gpt-oss-20b`, which supports JSON Object Mode, through configurable `GROQ_MODEL`.

### 4:35–5:25 — Deterministic safety and corrections

In `services/validation.py`, show that required-field completeness and commit readiness are deterministic. Then show the correction service and route: a natural-language instruction becomes a minimal allow-listed field patch; unsupported, empty, or invalid changes fail safely; accepted edits rerun completeness, risk, and summary.

### 5:25–6:35 — Persistence and human commit

In `repositories/complaints.py`, explain persisted JSONB draft state and the normalized committed complaint. Trace `POST /api/v1/complaints` in `api/complaints.py`: the draft must be ready, the user must explicitly commit, and a unique commit token makes retries idempotent. Show the Alembic migration rather than claiming schema creation happens magically.

### 6:35–7:35 — Frontend review loop

Return to the Redux slice and workspace components. Show direct-edit dirty state, save-before-commit behavior, correction messages, advisory AI labels, and ledger refresh. Explain how responsive CSS changes the ledger from a table into cards on narrow screens.

### 7:35–8:25 — Verification strategy

Show one backend contract/workflow test, one Redux/component test, and the Playwright happy-path specification. Explain that unit/integration tests use deterministic fakes and an in-memory test database, while production remains PostgreSQL plus Groq. Point to `docs/verification/live-integration.md` and `docs/verification/production.md` so local evidence is not confused with live verification.

### 8:25–8:55 — Trade-offs and extension point

Close with the deliberate exclusions: production OCR, authentication, e-signatures, RBAC, regulated retention, and validated-QMS claims. A strong extension answer is to add authenticated roles and an immutable audit-event table before expanding into duplicate detection, root-cause, or CAPA recommendations.

## Interview readiness prompts

Be able to answer, without notes:

- Why LangGraph is useful here instead of one opaque prompt.
- Why completeness is deterministic while extraction/risk/summary are model-assisted.
- What prevents an incomplete, stale, or duplicate commit.
- How an invalid LLM response is contained.
- Why raw source text is hashed rather than retained.
- How you would add OCR, authentication, audit trails, and evaluation datasets.
- Which tests would change if a complaint field or workflow node were added.
- What the prototype proves and what would still be required for a regulated production system.

## Walkthrough review checklist

- One complete request is traced from input to Redux, HTTP, FastAPI, LangGraph/Groq, validation, database, response, and rendered form.
- The correction and explicit commit paths are explained, not merely shown.
- Tests, failure behavior, configuration, model choice, and trade-offs are covered.
- No secret or personal data is included.
- Every claim matches the committed code and current verification records.
