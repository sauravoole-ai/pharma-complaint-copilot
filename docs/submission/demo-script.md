# Product Demonstration Script

Target: **7–8 minutes** (assignment allowance: 5–10 minutes). Record a clean browser window at 1080p or higher. Use only the repository's synthetic samples and keep the browser console, API keys, provider dashboards, and personal notifications out of frame.

## Before recording

- Open the public frontend in an unauthenticated window and confirm the API health check passes.
- Start with an empty ledger or explain any synthetic records already present.
- Keep `samples/discoloration-complaint.txt` and `samples/foreign-matter-complaint.pdf` ready.
- Rehearse once while timing. Do not claim the prototype is a validated QMS or that suggested risk is a regulatory decision.

## Timed narration and actions

### 0:00–0:40 — Product problem and boundary

**Show:** landing header and the two-panel workspace.

**Say:** “Pharmaceutical complaint intake often begins as unstructured text or a PDF. Pharma Complaint Copilot converts that input into a reviewable draft, identifies missing information, and suggests risk triage. It supports the reviewer; it does not replace qualified quality judgment or a validated QMS.”

### 0:40–1:25 — Text complaint intake

**Show:** paste `samples/discoloration-complaint.txt`, then analyze.

**Say:** “The application accepts pasted complaint narratives. The request goes through a bounded API contract and a LangGraph workflow, while the interface makes the processing state and any safe failure visible.”

Pause until the result is complete; edit out only dead waiting time, not error states or missing steps.

### 1:25–2:35 — Structured review and AI outputs

**Show:** populated form, completeness state, summary, severity, rationale, and confidence.

**Say:** “The model proposes structured facts, a concise summary, and an advisory severity. Deterministic validation—not the model—decides whether required fields are complete. Missing data remains visibly missing rather than being fabricated.”

Call out the suggested **Major** classification for the synthetic discoloration scenario, but describe it as a suggestion.

### 2:35–3:35 — Controlled correction and direct review

**Show:** submit “Change the batch to BMX240602 and the quantity to 48.” Confirm only those fields change. Then make one direct field edit, save it, and show the status update.

**Say:** “Conversational corrections are converted into a minimal allow-listed patch. Direct reviewer edits are also persisted. Derived completeness, summary, and risk outputs are recalculated, and unsaved edits block commit.”

### 3:35–4:35 — Human commit and ledger

**Show:** the enabled commit action, commit once, then scroll to the ledger. If practical, refresh and show the record remains.

**Say:** “Nothing enters the ledger automatically. A ready draft requires explicit human confirmation. The API uses an idempotency token so an accidental retry does not create a duplicate, and committed records are loaded from PostgreSQL.”

### 4:35–5:55 — PDF complaint workflow

**Show:** start a new intake, upload `samples/foreign-matter-complaint.pdf`, and inspect its populated draft.

**Say:** “The same workflow accepts a bounded, selectable-text PDF. The foreign-matter scenario demonstrates a suggested **Critical** severity. Scanned-image OCR is intentionally outside this prototype and is rejected clearly rather than guessed.”

### 5:55–6:55 — Bonus AI and product value

**Show:** missing-field indicators, AI summary, rationale disclosure, and responsive layout if time permits.

**Say:** “The completeness checker and complaint summary are the focused bonus features. The design separates AI proposals, deterministic safeguards, and human control so the workflow is useful without overstating automation.”

### 6:55–7:35 — Close with scope and engineering value

**Show:** ledger and product title.

**Say:** “This submission demonstrates React and Redux, FastAPI, LangGraph, Groq, and PostgreSQL as one end-to-end product. Production OCR, authentication, e-signatures, role-based approval, and regulated retention are deliberate next steps—not features claimed here.”

## Product-video acceptance pass

- Duration is 5–10 minutes and the recording is watchable without account access.
- Text intake, PDF intake, correction, direct edit, completeness, risk, commit, and ledger are all visible.
- Both synthetic scenarios are used; no real patient, customer, batch, or company data appears.
- No API key, database URL, private dashboard, local path, email, or notification appears.
- The reviewer can distinguish model suggestions from deterministic checks and human approval.
- The public URL is shown only after it has passed the production verification record.
