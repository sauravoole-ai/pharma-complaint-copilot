# Pharma Complaint Copilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested React/FastAPI/LangGraph/PostgreSQL MVP that ingests synthetic pharmaceutical complaints, produces an editable AI-assisted draft, supports constrained conversational corrections, and commits only after human review.

**Architecture:** A Vite React client holds the active workflow in Redux Toolkit and calls versioned FastAPI endpoints. FastAPI separates ingestion, deterministic validation, LangGraph orchestration, constrained correction, and SQLAlchemy persistence; all LLM calls pass through one injectable Groq adapter. The implementation is local-first and deployed only after the complete acceptance suite passes.

**Tech Stack:** React 18, Vite, TypeScript, Redux Toolkit, Vitest, Testing Library, Python 3.12, FastAPI, Pydantic 2, LangGraph, Groq SDK, SQLAlchemy 2, Alembic, PostgreSQL 16, pytest, Playwright, PyMuPDF, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-09-11-pharma-complaint-copilot-design.md`

## Global Constraints

- Reproduce the demonstrated paste/PDF -> extraction -> review -> correction -> commit workflow.
- Use React with Redux Toolkit, Python with FastAPI, LangGraph, Groq, PostgreSQL, and Google Inter.
- Default `GROQ_MODEL` to `llama-3.3-70b-versatile`; never use the retired `gemma2-9b-it` model.
- Use only synthetic complaint data; never include real patient, customer, employee, or company information.
- Label severity, next action, and rationale as AI suggestions.
- Deterministic server validation decides readiness; the model does not.
- Never commit automatically after analysis or correction.
- Never expose API keys or raw provider/database errors.
- Do not copy code, copy, architecture, samples, or documentation from another candidate's repository.
- Deferred features remain excluded until the mandatory acceptance suite is green.
- No external submission, repository creation, deployment, or account mutation occurs without a final user-controlled checkpoint.

---

## File Map

### Backend

- `backend/pyproject.toml`: Python dependencies and pytest configuration.
- `backend/app/main.py`: application factory and router registration.
- `backend/app/config.py`: validated environment configuration.
- `backend/app/db.py`: SQLAlchemy engine/session lifecycle.
- `backend/app/domain/schemas.py`: stable API and LangGraph data contracts.
- `backend/app/db_models.py`: draft and committed-complaint tables.
- `backend/app/ai/llm.py`: injectable Groq structured-output adapter.
- `backend/app/ai/graph.py`: complaint-analysis LangGraph.
- `backend/app/services/validation.py`: deterministic validation/readiness rules.
- `backend/app/services/pdf_text.py`: bounded PDF text extraction.
- `backend/app/services/corrections.py`: allow-listed correction patches.
- `backend/app/repositories/complaints.py`: draft/complaint persistence.
- `backend/app/api/drafts.py`: text, file, and correction endpoints.
- `backend/app/api/complaints.py`: commit and ledger endpoints.
- `backend/app/api/health.py`: safe application/database health endpoint.
- `backend/alembic/versions/0001_complaint_tables.py`: initial PostgreSQL schema.

### Frontend

- `frontend/package.json`: frontend scripts and dependencies.
- `frontend/src/types/complaint.ts`: API-aligned TypeScript contracts.
- `frontend/src/api/client.ts`: typed HTTP boundary.
- `frontend/src/store/index.ts`: Redux store.
- `frontend/src/store/complaintSlice.ts`: draft lifecycle state and thunks.
- `frontend/src/components/ComplaintWorkspace.tsx`: two-panel composition.
- `frontend/src/components/ComplaintForm.tsx`: editable structured form.
- `frontend/src/components/CopilotPanel.tsx`: paste, PDF, messages, correction input.
- `frontend/src/components/WorkflowStatus.tsx`: status and progress feedback.
- `frontend/src/components/ComplaintLedger.tsx`: committed-record list.
- `frontend/src/styles.css`: responsive, restrained reference-inspired presentation.
- `frontend/src/App.tsx`: application shell and disclosure.

### Operations and QA

- `compose.yaml`: local PostgreSQL 16 service.
- `.env.example`: non-secret variable names and safe defaults.
- `.gitignore`: secrets, environments, caches, builds, and uploaded files.
- `samples/discoloration-complaint.txt`: synthetic text demonstration.
- `samples/foreign-matter-complaint.pdf`: generated synthetic PDF demonstration.
- `tests/e2e/complaint-workflow.spec.ts`: browser acceptance flow.
- `playwright.config.ts`: end-to-end configuration.
- `README.md`: setup, architecture, demo script, limitations, and model-deprecation note.
- `render.yaml`: FastAPI deployment configuration.
- `frontend/vercel.json`: SPA routing and deployment metadata.

---

### Task 1: Establish Domain Contracts and Deterministic Readiness

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/schemas.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/validation.py`
- Create: `backend/tests/test_validation.py`
- Create: `.gitignore`

**Interfaces:**
- Produces: `ComplaintFields`, `RiskSuggestion`, `CompletenessResult`, `DraftAnalysisResult`, `DraftResponse`, `ComplaintResponse`, and `validate_and_classify(fields)`.
- `validate_and_classify(fields: ComplaintFields) -> tuple[CompletenessResult, DraftStatus]` is consumed by Tasks 3, 5, and 6.

- [ ] **Step 1: Write failing readiness tests**

```python
def test_missing_batch_requires_review():
    fields = complete_fields().model_copy(update={"batch_lot_number": None})
    completeness, status = validate_and_classify(fields)
    assert completeness.missing_fields == ["batch_lot_number"]
    assert status == DraftStatus.NEEDS_REVIEW

def test_complete_fields_are_ready_to_commit():
    completeness, status = validate_and_classify(complete_fields())
    assert completeness.is_complete is True
    assert status == DraftStatus.READY_TO_COMMIT
```

- [ ] **Step 2: Run the focused tests and confirm RED**

Run: `cd backend && python -m pytest tests/test_validation.py -q`

Expected: collection fails because `app.domain.schemas` does not exist.

- [ ] **Step 3: Implement the schemas and readiness policy**

Define `DraftStatus` with `idle`, `processing`, `needs_review`, `ready_to_commit`, `committing`, `committed`, and `failed`. Define all form fields as bounded optional strings, define `Severity` as `Minor | Major | Critical`, and make readiness require `complaint_source`, `customer_name`, `product_name`, `batch_lot_number`, `complaint_category`, and `complaint_description`.

```python
REQUIRED_FIELDS = (
    "complaint_source", "customer_name", "product_name",
    "batch_lot_number", "complaint_category", "complaint_description",
)

def validate_and_classify(fields: ComplaintFields):
    missing = [name for name in REQUIRED_FIELDS if not getattr(fields, name)]
    result = CompletenessResult(is_complete=not missing, missing_fields=missing)
    status = DraftStatus.READY_TO_COMMIT if not missing else DraftStatus.NEEDS_REVIEW
    return result, status
```

- [ ] **Step 4: Run the tests and static import check**

Run: `cd backend && python -m pytest tests/test_validation.py -q && python -m compileall app`

Expected: all tests pass and compilation exits zero.

- [ ] **Step 5: Commit the domain foundation**

```bash
git add .gitignore backend
git commit -m "feat: define complaint domain contracts"
```

---

### Task 2: Add PostgreSQL Persistence and Migration

**Files:**
- Create: `compose.yaml`
- Create: `scripts/init-test-db.sql`
- Create: `.env.example`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/db_models.py`
- Create: `backend/app/repositories/__init__.py`
- Create: `backend/app/repositories/complaints.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/0001_complaint_tables.py`
- Create: `backend/tests/integration/test_complaint_repository.py`

**Interfaces:**
- Consumes: `ComplaintFields`, `CompletenessResult`, `RiskSuggestion`, `DraftStatus`.
- Produces: `ComplaintRepository.create_draft`, `get_draft`, `update_draft`, `commit_draft`, and `list_complaints`.

- [ ] **Step 1: Write failing PostgreSQL repository tests**

```python
def test_commit_is_idempotent(repository, saved_ready_draft):
    first = repository.commit_draft(saved_ready_draft.id, "demo-token-1")
    second = repository.commit_draft(saved_ready_draft.id, "demo-token-1")
    assert second.id == first.id
    assert len(repository.list_complaints()) == 1
```

- [ ] **Step 2: Start PostgreSQL and confirm RED**

Run: `docker compose up -d db && cd backend && TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/complaints_test python -m pytest tests/integration/test_complaint_repository.py -q`

Expected: test collection fails because repository and tables do not exist.

- [ ] **Step 3: Implement configuration, models, migration, and repository**

Create `complaint_drafts` and `complaints` tables as defined in the spec. Store structured draft payloads in PostgreSQL JSONB, normalized committed fields in explicit columns, and enforce unique `commit_token` plus unique `source_draft_id`. Mount `scripts/init-test-db.sql` in Compose so PostgreSQL creates both `complaints` and `complaints_test` databases on first initialization.

```python
def commit_draft(self, draft_id: UUID, commit_token: str) -> ComplaintModel:
    existing = self.session.scalar(
        select(ComplaintModel).where(ComplaintModel.commit_token == commit_token)
    )
    if existing:
        return existing
    draft = self.require_ready_draft(draft_id)
    complaint = ComplaintModel.from_draft(draft, commit_token=commit_token)
    self.session.add(complaint)
    self.session.commit()
    return complaint
```

- [ ] **Step 4: Apply migration and run repository tests**

Run: `cd backend && DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/complaints alembic upgrade head`

Run: `cd backend && TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/complaints_test python -m pytest tests/integration/test_complaint_repository.py -q`

Expected: migration succeeds; repository tests pass.

- [ ] **Step 5: Commit persistence**

```bash
git add compose.yaml .env.example backend
git commit -m "feat: persist complaint drafts and ledger records"
```

---

### Task 3: Implement the Injectable LLM Adapter and LangGraph Analysis

**Files:**
- Create: `backend/app/ai/__init__.py`
- Create: `backend/app/ai/llm.py`
- Create: `backend/app/ai/graph.py`
- Create: `backend/tests/fakes.py`
- Create: `backend/tests/test_analysis_graph.py`

**Interfaces:**
- Consumes: domain schemas and `validate_and_classify`.
- Produces: `LLMAdapter.extract`, `suggest_risk`, `summarize`, `correction_patch`, and `run_analysis(source_text, source_type, llm)`.

- [ ] **Step 1: Write graph tests with a fake adapter**

```python
def test_graph_returns_reviewable_major_draft(fake_llm, discoloration_text):
    result = run_analysis(discoloration_text, SourceType.TEXT, fake_llm)
    assert result.fields.batch_lot_number == "AMX240602"
    assert result.risk.severity == Severity.MAJOR
    assert result.status == DraftStatus.READY_TO_COMMIT
    assert result.completeness.is_complete is True
```

- [ ] **Step 2: Run the graph test and confirm RED**

Run: `cd backend && python -m pytest tests/test_analysis_graph.py -q`

Expected: import fails because the graph is absent.

- [ ] **Step 3: Implement the adapter and graph**

Use Pydantic-validated structured outputs. The Groq adapter receives `Settings.groq_model`; provider exceptions become typed internal exceptions without embedding raw provider text in HTTP responses.

```python
builder = StateGraph(AnalysisState)
builder.add_node("normalize_input", normalize_input)
builder.add_node("extract_complaint", extract_complaint)
builder.add_node("validate_extraction", validate_extraction)
builder.add_node("assess_completeness", assess_completeness)
builder.add_node("suggest_risk", suggest_risk)
builder.add_node("summarize_complaint", summarize_complaint)
builder.add_node("assemble_draft", assemble_draft)
builder.add_edge(START, "normalize_input")
builder.add_edge("normalize_input", "extract_complaint")
builder.add_edge("extract_complaint", "validate_extraction")
builder.add_edge("validate_extraction", "assess_completeness")
builder.add_edge("assess_completeness", "suggest_risk")
builder.add_edge("suggest_risk", "summarize_complaint")
builder.add_edge("summarize_complaint", "assemble_draft")
builder.add_edge("assemble_draft", END)
analysis_graph = builder.compile()
```

- [ ] **Step 4: Run graph and validation tests**

Run: `cd backend && python -m pytest tests/test_analysis_graph.py tests/test_validation.py -q`

Expected: all tests pass without a live Groq request.

- [ ] **Step 5: Commit the analysis workflow**

```bash
git add backend/app/ai backend/tests
git commit -m "feat: orchestrate complaint analysis with LangGraph"
```

---

### Task 4: Expose Text and PDF Draft Analysis APIs

**Files:**
- Create: `backend/app/services/pdf_text.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/drafts.py`
- Create: `backend/app/api/health.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_pdf_text.py`
- Create: `backend/tests/test_draft_api.py`

**Interfaces:**
- Consumes: `run_analysis`, `ComplaintRepository.create_draft`, `Settings`, and injected `LLMAdapter`.
- Produces: `create_app(settings, llm_adapter, session_factory)`, module-level `app = create_app()`, and the analyze/health HTTP contracts returning `DraftResponse`.

- [ ] **Step 1: Write failing API and PDF boundary tests**

```python
def test_analyze_text_persists_and_returns_draft(client, complaint_text):
    response = client.post("/api/v1/complaint-drafts/analyze-text", json={"text": complaint_text})
    assert response.status_code == 201
    assert response.json()["fields"]["batch_lot_number"] == "AMX240602"

def test_scanned_pdf_is_rejected(client, image_only_pdf):
    response = client.post(
        "/api/v1/complaint-drafts/analyze-file",
        files={"file": ("scan.pdf", image_only_pdf, "application/pdf")},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "insufficient_pdf_text"
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `cd backend && python -m pytest tests/test_pdf_text.py tests/test_draft_api.py -q`

Expected: imports or routes fail.

- [ ] **Step 3: Implement bounded ingestion and API composition**

Accept only `application/pdf`, cap uploads at 5 MiB, limit extracted text to 30,000 characters, and reject fewer than 40 non-whitespace characters. Configure CORS from `FRONTEND_ORIGIN`; never use wildcard origins with credentials.

```python
@router.post("/analyze-text", response_model=DraftAnalysisResult, status_code=201)
def analyze_text(payload: AnalyzeTextRequest, deps: DraftDependencies = Depends(get_deps)):
    result = run_analysis(payload.text, SourceType.TEXT, deps.llm)
    return deps.repository.create_draft(result)
```

- [ ] **Step 4: Run focused and neighboring backend tests**

Run: `cd backend && python -m pytest tests/test_pdf_text.py tests/test_draft_api.py tests/test_analysis_graph.py tests/test_validation.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit the analysis APIs**

```bash
git add backend/app backend/tests
git commit -m "feat: expose text and PDF complaint analysis"
```

---

### Task 5: Add Constrained Conversational Corrections

**Files:**
- Create: `backend/app/services/corrections.py`
- Modify: `backend/app/api/drafts.py`
- Modify: `backend/app/ai/llm.py`
- Create: `backend/tests/test_corrections.py`
- Modify: `backend/tests/test_draft_api.py`

**Interfaces:**
- Consumes: `ComplaintRepository.get_draft/update_draft`, `LLMAdapter.correction_patch`, and `validate_and_classify`.
- Produces: `apply_correction(current_fields, message, llm) -> CorrectionResult` and `PATCH /api/v1/complaint-drafts/{draft_id}/conversation`.

- [ ] **Step 1: Write failing allow-list and behavioral tests**

```python
def test_batch_and_quantity_correction_changes_only_two_fields(fake_llm, complete_fields):
    updated = apply_correction(
        complete_fields,
        "The batch is BMX240602 and quantity is 48 capsules",
        fake_llm,
    )
    assert updated.fields.batch_lot_number == "BMX240602"
    assert updated.fields.affected_quantity == "48 capsules"
    assert updated.fields.customer_name == complete_fields.customer_name

def test_unknown_patch_key_is_rejected(fake_llm_with_forbidden_key, complete_fields):
    with pytest.raises(InvalidCorrection):
        apply_correction(complete_fields, "change owner", fake_llm_with_forbidden_key)
```

- [ ] **Step 2: Run correction tests and confirm RED**

Run: `cd backend && python -m pytest tests/test_corrections.py -q`

Expected: import fails because correction service is absent.

- [ ] **Step 3: Implement constrained patching and revalidation**

Define `EDITABLE_FIELD_NAMES` from `ComplaintFields.model_fields`. Reject empty patches, unknown keys, and values longer than the schema permits. Apply with `model_copy(update=patch)`, rerun deterministic completeness, and persist one assistant message describing the exact changed fields.

- [ ] **Step 4: Run correction and draft API tests**

Run: `cd backend && python -m pytest tests/test_corrections.py tests/test_draft_api.py -q`

Expected: all tests pass, including draft-not-found and invalid-patch responses.

- [ ] **Step 5: Commit corrections**

```bash
git add backend/app backend/tests
git commit -m "feat: support controlled complaint corrections"
```

---

### Task 6: Add Human-Controlled Commit, Ledger, and Health APIs

**Files:**
- Create: `backend/app/api/complaints.py`
- Modify: `backend/app/api/health.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_complaint_api.py`
- Create: `backend/tests/test_health_api.py`

**Interfaces:**
- Consumes: repository commit/list operations and domain response schemas.
- Produces: `POST /api/v1/complaints`, `GET /api/v1/complaints`, and safe `GET /api/v1/health`.

- [ ] **Step 1: Write failing commit-control tests**

```python
def test_incomplete_draft_cannot_be_committed(client, incomplete_draft_id):
    response = client.post("/api/v1/complaints", json={
        "draft_id": str(incomplete_draft_id), "commit_token": "token-a"
    })
    assert response.status_code == 409
    assert response.json()["code"] == "draft_not_ready"

def test_repeated_commit_returns_same_record(client, ready_draft_id):
    payload = {"draft_id": str(ready_draft_id), "commit_token": "token-b"}
    first = client.post("/api/v1/complaints", json=payload)
    second = client.post("/api/v1/complaints", json=payload)
    assert first.json()["id"] == second.json()["id"]
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `cd backend && python -m pytest tests/test_complaint_api.py tests/test_health_api.py -q`

Expected: complaint routes are absent.

- [ ] **Step 3: Implement commit, ledger, and health routes**

Map not-ready drafts to `409`, missing drafts to `404`, and unavailable database/model dependencies to a safe `503`. Health response contains only `status`, `database`, and application version.

- [ ] **Step 4: Run the complete backend suite**

Run: `cd backend && TEST_DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/complaints_test python -m pytest -q`

Expected: every backend unit/API/integration test passes.

- [ ] **Step 5: Check formatting and commit**

Run: `cd backend && ruff check app tests && ruff format --check app tests`

```bash
git add backend
git commit -m "feat: add reviewed complaint commit and ledger APIs"
```

### Checkpoint A: Backend Contract Lock

Stop if any backend test fails. Record the full test count, confirm no live Groq request occurred, and inspect `git status --short` before frontend work.

---

### Task 7: Scaffold the React Application and Redux Workflow

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/types/complaint.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/store/index.ts`
- Create: `frontend/src/store/complaintSlice.ts`
- Create: `frontend/src/store/complaintSlice.test.ts`

**Interfaces:**
- Consumes: versioned backend JSON contracts.
- Produces: `analyzeText`, `analyzeFile`, `sendCorrection`, `commitComplaint`, `loadLedger`, and selectors for active draft/status/messages.

- [ ] **Step 1: Write failing Redux lifecycle tests**

```typescript
it('moves an analyzed draft into ready_to_commit', () => {
  const state = reducer(initialState, analyzeText.fulfilled(readyDraft, 'r1', sampleText));
  expect(state.activeDraft?.status).toBe('ready_to_commit');
  expect(state.error).toBeNull();
});

it('preserves the draft when commit fails', () => {
  const state = reducer(stateWithReadyDraft, commitComplaint.rejected(error, 'r2', payload));
  expect(state.activeDraft?.id).toBe(readyDraft.id);
  expect(state.error).toBeTruthy();
});
```

- [ ] **Step 2: Install dependencies and confirm RED**

Run: `cd frontend && npm install && npm test -- --run src/store/complaintSlice.test.ts`

Expected: test fails because slice implementation is absent.

- [ ] **Step 3: Implement typed API and Redux state**

Use a discriminated state shape with `activeDraft`, `messages`, `ledger`, `requestStatus`, and `error`. Reject malformed API responses at the client boundary and use `VITE_API_BASE_URL` without hard-coded production URLs.

- [ ] **Step 4: Run frontend unit tests and typecheck**

Run: `cd frontend && npm test -- --run && npm run typecheck`

Expected: all tests and TypeScript checks pass.

- [ ] **Step 5: Commit frontend state foundation**

```bash
git add frontend
git commit -m "feat: establish complaint workflow state"
```

---

### Task 8: Build the Reference-Aligned Form and Copilot Experience

**Files:**
- Create: `frontend/src/components/ComplaintWorkspace.tsx`
- Create: `frontend/src/components/ComplaintForm.tsx`
- Create: `frontend/src/components/CopilotPanel.tsx`
- Create: `frontend/src/components/WorkflowStatus.tsx`
- Create: `frontend/src/components/ComplaintWorkspace.test.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles.css`

**Interfaces:**
- Consumes: Redux selectors/thunks from Task 7.
- Produces: the complete paste/PDF/form/correction/commit interaction surface.

- [ ] **Step 1: Write failing component behavior tests**

```typescript
it('populates editable fields and labels AI recommendations', async () => {
  renderWorkspaceWithState(readyDraftState);
  expect(screen.getByDisplayValue('AMX240602')).toBeInTheDocument();
  expect(screen.getByText('AI-suggested severity')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /commit to qms ledger/i })).toBeEnabled();
});

it('disables commit while required fields are missing', () => {
  renderWorkspaceWithState(needsReviewState);
  expect(screen.getByRole('button', { name: /commit to qms ledger/i })).toBeDisabled();
});
```

- [ ] **Step 2: Run the component test and confirm RED**

Run: `cd frontend && npm test -- --run src/components/ComplaintWorkspace.test.tsx`

Expected: component imports fail.

- [ ] **Step 3: Implement accessible components and restrained styling**

Match the workflow rather than copying the screenshot pixel-for-pixel. Use a two-column workspace above 960 px and one column below it. Keep all inputs labelled, expose progress with `aria-live`, show missing fields, and provide direct field editing plus a correction message input.

- [ ] **Step 4: Run component, type, and production-build checks**

Run: `cd frontend && npm test -- --run && npm run typecheck && npm run build`

Expected: tests pass and Vite produces `dist/`.

- [ ] **Step 5: Commit the primary experience**

```bash
git add frontend
git commit -m "feat: build complaint form and copilot workspace"
```

---

### Task 9: Add Ledger UI and Complete Client Integration

**Files:**
- Create: `frontend/src/components/ComplaintLedger.tsx`
- Create: `frontend/src/components/ComplaintLedger.test.tsx`
- Modify: `frontend/src/components/ComplaintWorkspace.tsx`
- Modify: `frontend/src/store/complaintSlice.ts`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `loadLedger`, `commitComplaint`, and committed complaint contracts.
- Produces: post-commit confirmation and visible committed-record history.

- [ ] **Step 1: Write failing ledger tests**

```typescript
it('shows one committed record after an idempotent commit', async () => {
  renderLedger([committedComplaint]);
  expect(screen.getAllByTestId('ledger-row')).toHaveLength(1);
  expect(screen.getByText('BMX240602')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the ledger test and confirm RED**

Run: `cd frontend && npm test -- --run src/components/ComplaintLedger.test.tsx`

Expected: component import fails.

- [ ] **Step 3: Implement ledger and commit feedback**

Render complaint ID, customer, product, batch, suggested severity, and creation time. Never imply electronic-signature or compliance validation. After commit, show the saved ID and refresh the ledger once.

- [ ] **Step 4: Run all frontend checks**

Run: `cd frontend && npm test -- --run && npm run typecheck && npm run build`

Expected: all checks pass.

- [ ] **Step 5: Commit the completed client flow**

```bash
git add frontend
git commit -m "feat: show committed complaint ledger"
```

### Checkpoint B: Local Product Lock

Run the backend and frontend together using PostgreSQL. Manually exercise paste, edit, correction, commit, ledger, error, and responsive states. Stop and debug before adding samples, deployment configuration, or polish if any core behavior differs from the spec.

---

### Task 10: Add Synthetic Samples, End-to-End Tests, and Documentation

**Files:**
- Create: `samples/discoloration-complaint.txt`
- Create: `scripts/generate_sample_pdf.py`
- Create: `samples/foreign-matter-complaint.pdf`
- Create: `tests/e2e/complaint-workflow.spec.ts`
- Create: `playwright.config.ts`
- Create: `package.json`
- Create: `README.md`

**Interfaces:**
- Consumes: the complete local frontend/backend workflow.
- Produces: reproducible samples, automated browser proof, and an interview-ready repository guide.

- [ ] **Step 1: Write the failing browser acceptance test**

```typescript
test('analyze, correct, and commit a synthetic complaint', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Complaint text').fill(sampleComplaint);
  await page.getByRole('button', { name: 'Analyze complaint' }).click();
  await expect(page.getByLabel('Batch / Lot Number')).toHaveValue('AMX240602');
  await page.getByLabel('Correction message').fill(
    'The batch is BMX240602 and affected quantity is 48 capsules'
  );
  await page.getByRole('button', { name: 'Send correction' }).click();
  await expect(page.getByLabel('Batch / Lot Number')).toHaveValue('BMX240602');
  await page.getByRole('button', { name: 'Commit to QMS Ledger' }).click();
  await expect(page.getByTestId('ledger-row')).toHaveCount(1);
});
```

- [ ] **Step 2: Run the browser test and confirm RED**

Run: `npm install && npm run test:e2e`

Expected: fixture/sample wiring fails before it is implemented.

- [ ] **Step 3: Add synthetic samples and deterministic test wiring**

Generate the PDF from a fixed script so no opaque binary is hand-authored. The E2E environment injects the fake LLM adapter through backend configuration; the normal application configuration continues to require a real Groq key.

- [ ] **Step 4: Write the README and run the complete local acceptance suite**

README sections: problem, workflow, architecture, LangGraph nodes, setup, environment variables, tests, sample data, safety limitations, retired-model decision, deployment, demo script, and interview discussion points.

Run: `docker compose up -d db && npm run verify`

`npm run verify` must run backend tests, Ruff, frontend tests, TypeScript, production build, and Playwright in that order.

Expected: every stage passes without a live Groq call.

- [ ] **Step 5: Commit samples, QA, and documentation**

```bash
git add samples scripts tests playwright.config.ts package.json README.md
git commit -m "test: verify the complete complaint workflow"
```

---

### Task 11: Run Controlled Live Integration and Deployment Preparation

**Files:**
- Create: `render.yaml`
- Create: `frontend/vercel.json`
- Modify: `README.md`
- Create: `docs/verification/live-integration.md`
- Create: `backend/tests/live/test_groq_smoke.py`

**Interfaces:**
- Consumes: a user-provided local `GROQ_API_KEY` and the complete verified application.
- Produces: deployment-ready manifests and a factual live-integration record.

- [ ] **Step 1: Add a live smoke-test specification**

The test submits the synthetic discoloration complaint, requires schema-valid extraction, verifies all required fields are non-empty, and confirms the AI output is labelled as suggested. It does not assert an exact prose response.

- [ ] **Step 2: Run one controlled Groq smoke test**

Run: `cd backend && RUN_LIVE_AI=1 python -m pytest tests/live/test_groq_smoke.py -q`

Expected: one schema-valid analysis completes using the configured current model. If rate-limited or unavailable, record the failure accurately and preserve the fully passing fake-adapter suite.

- [ ] **Step 3: Add deployment manifests**

Render starts `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, runs Alembic before startup through the platform release command, and receives secrets only through platform configuration. Vercel builds `frontend/` and uses `VITE_API_BASE_URL` for the public backend.

- [ ] **Step 4: Re-run offline verification and inspect secret hygiene**

Run: `npm run verify`

Run: `git grep -nE '(gsk_[A-Za-z0-9]{20,}|postgres(ql)?://[^[:space:]]+:[^@[:space:]]+@)' -- . ':!docs/superpowers/plans/*' || true`

Expected: all verification passes and secret scan returns no matches.

- [ ] **Step 5: Commit deployment preparation**

```bash
git add render.yaml frontend/vercel.json README.md docs/verification/live-integration.md
git commit -m "chore: prepare verified application deployment"
```

### Checkpoint C: Stop Before External Actions

Stop before creating or changing any GitHub repository, Supabase project, Render service, Vercel project, environment variable, or submission form. Present the exact proposed external actions and request user authorization at action time.

---

### Task 12: Deploy, Verify, and Prepare the Submission Package

**Files:**
- Modify: `README.md`
- Create: `docs/verification/production.md`
- Create: `docs/submission/demo-script.md`
- Create: `docs/submission/code-walkthrough.md`
- Create: `docs/submission/form-checklist.md`

**Interfaces:**
- Consumes: user-authorized GitHub, Supabase, Render, and Vercel operations.
- Produces: verified public URLs and a reviewed submission package; it does not submit the external form automatically.

- [ ] **Step 1: Publish the original repository after user authorization**

Create or use only the user-approved GitHub repository. Push the existing commit history without rewriting authorship or incorporating another candidate's work.

- [ ] **Step 2: Provision and configure authorized services**

Create the Supabase PostgreSQL database, Render backend, and Vercel frontend only after the user approves those exact destinations. Configure secrets without printing their values.

- [ ] **Step 3: Verify the deployed application**

Verify public health, text analysis, PDF analysis, correction, direct field editing, commit, ledger, desktop rendering, narrow rendering, refresh persistence, and safe failure behavior. Record URLs, UTC timestamps, status codes, and visual results in `docs/verification/production.md`.

- [ ] **Step 4: Write and rehearse the two demo scripts**

Product video: problem, text complaint, extraction, suggested risk, correction, commit, ledger, PDF complaint, and disclaimer.

Code video: frontend action, Redux thunk, FastAPI route, LangGraph nodes, LLM adapter, deterministic validation, PostgreSQL commit, tests, and model-deprecation decision.

- [ ] **Step 5: Run final multi-pass review**

Review assignment compliance, demo fidelity, functional correctness, code quality, product usefulness, domain safety, recruiter clarity, originality, accessibility, responsiveness, deployment reliability, README accuracy, video timing, form completeness, and secret hygiene.

- [ ] **Step 6: Commit final factual documentation**

```bash
git add README.md docs/verification/production.md docs/submission
git commit -m "docs: prepare verified internship submission"
```

### Final Human Submission Gate

Provide the repository URL, frontend URL, backend health URL, both video URLs, and proposed form answers to the user for inspection. Do not submit the Google Form or send any message to AIVOA until the user explicitly approves the final external submission.
