import { useEffect, useRef, useState, type ChangeEvent } from "react";

import { useAppDispatch, useAppSelector } from "../store";
import {
  analyzeFile,
  analyzeText,
  commitComplaint,
  loadLedger,
  resetWorkflow,
  saveFields,
  selectActiveDraft,
  selectError,
  selectHasUnsavedEdits,
  selectLedger,
  selectMessages,
  selectRequestStatus,
  sendCorrection,
  updateFieldLocally,
} from "../store/complaintSlice";
import type { ComplaintFields } from "../types/complaint";
import { ComplaintForm } from "./ComplaintForm";
import { ComplaintLedger } from "./ComplaintLedger";
import { CopilotPanel } from "./CopilotPanel";
import { WorkflowStatus } from "./WorkflowStatus";

export function ComplaintWorkspace() {
  const dispatch = useAppDispatch();
  const draft = useAppSelector(selectActiveDraft);
  const messages = useAppSelector(selectMessages);
  const requestStatus = useAppSelector(selectRequestStatus);
  const error = useAppSelector(selectError);
  const hasUnsavedEdits = useAppSelector(selectHasUnsavedEdits);
  const ledger = useAppSelector(selectLedger);
  const [sourceText, setSourceText] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const refreshedCommit = useRef<string | null>(null);
  const busy = requestStatus === "loading";
  const committedRecord = draft
    ? ledger.find((record) => record.source_draft_id === draft.id)
    : undefined;

  useEffect(() => {
    if (draft?.status === "committed" && refreshedCommit.current !== draft.id) {
      refreshedCommit.current = draft.id;
      void dispatch(loadLedger());
    }
  }, [dispatch, draft?.id, draft?.status]);

  function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void dispatch(analyzeFile(file));
    event.target.value = "";
  }

  function changeField(field: keyof ComplaintFields, value: string) {
    dispatch(updateFieldLocally({ field, value }));
  }

  function persistFields() {
    if (draft) void dispatch(saveFields({ draftId: draft.id, fields: draft.fields }));
  }

  function commit() {
    if (!draft) return;
    void dispatch(
      commitComplaint({ draftId: draft.id, commitToken: crypto.randomUUID() }),
    );
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Pharma Complaint Copilot home">
          <span className="brand-symbol" aria-hidden="true">A</span>
          <span><strong>AIVOA</strong><small>Quality intelligence</small></span>
        </a>
        <div className="environment"><span /> Controlled demo environment</div>
        <a className="ledger-link" href="#ledger">View ledger</a>
      </header>

      <main id="top">
        <section className="hero">
          <div>
            <p className="kicker">Customer complaint management</p>
            <h1>Turn complaint narratives into review-ready quality records.</h1>
            <p className="hero-copy">
              AI assists with extraction and triage. Your review remains the final control.
            </p>
          </div>
          <div className="hero-index" aria-hidden="true"><span>01</span> Intake & review</div>
        </section>

        {!draft ? (
          <section className="intake-card" aria-busy={busy}>
            <div className="intake-intro">
              <p className="eyebrow">Start a complaint</p>
              <h2>Paste the customer narrative</h2>
              <p>Include only the information received. Missing details stay visible for review.</p>
            </div>
            <label htmlFor="complaint-source" className="source-label">Complaint narrative</label>
            <textarea
              id="complaint-source"
              rows={8}
              value={sourceText}
              placeholder="Paste an email, call note, or written complaint here…"
              onChange={(event) => setSourceText(event.target.value)}
            />
            <div className="intake-actions">
              <button
                className="button button--primary"
                disabled={busy || !sourceText.trim()}
                onClick={() => void dispatch(analyzeText(sourceText))}
              >
                {busy ? "Analyzing…" : "Analyze complaint"}
              </button>
              <span>or</span>
              <button
                className="button button--secondary"
                disabled={busy}
                onClick={() => fileInput.current?.click()}
              >
                Upload text-based PDF
              </button>
              <input
                ref={fileInput}
                className="visually-hidden"
                type="file"
                accept="application/pdf"
                onChange={upload}
              />
            </div>
            {error && <p className="error-banner" role="alert">{error}</p>}
          </section>
        ) : (
          <>
            <div className="workspace-toolbar">
              <WorkflowStatus status={draft.status} completeness={draft.completeness} />
              <button
                className="text-button"
                onClick={() => {
                  setSourceText("");
                  dispatch(resetWorkflow());
                }}
              >
                Start another complaint
              </button>
            </div>
            {error && <p className="error-banner" role="alert">{error}</p>}
            {committedRecord && (
              <div className="commit-confirmation" role="status">
                <span aria-hidden="true">✓</span>
                Saved as QMS-{committedRecord.id.slice(0, 8).toUpperCase()}. The record is now
                visible in the ledger.
              </div>
            )}
            <section className="workspace" aria-busy={busy}>
              <article className="form-panel">
                <div className="panel-heading">
                  <div><p className="eyebrow">Structured record</p><h2>Complaint details</h2></div>
                  <span className="source-chip">Source · {draft.source_type.toUpperCase()}</span>
                </div>
                <ComplaintForm
                  fields={draft.fields}
                  missingFields={draft.completeness.missing_fields}
                  disabled={busy || draft.status === "committed"}
                  onChange={changeField}
                />
                <div className="review-actions">
                  <div>
                    <p>{hasUnsavedEdits ? "Form edits are not yet saved." : "All displayed edits are saved."}</p>
                    <button
                      className="button button--secondary"
                      disabled={!hasUnsavedEdits || busy}
                      onClick={persistFields}
                    >
                      Apply form edits
                    </button>
                  </div>
                  <button
                    className="button button--commit"
                    disabled={
                      busy || hasUnsavedEdits || draft.status !== "ready_to_commit"
                    }
                    onClick={commit}
                  >
                    Commit to QMS Ledger
                  </button>
                </div>
              </article>
              <CopilotPanel
                messages={messages}
                risk={draft.risk}
                summary={draft.summary}
                disabled={busy || draft.status === "committed" || hasUnsavedEdits}
                onCorrection={(message) =>
                  void dispatch(sendCorrection({ draftId: draft.id, message }))
                }
              />
            </section>
          </>
        )}
        <ComplaintLedger complaints={ledger} loading={busy && ledger.length === 0} />
      </main>
      <footer>
        <span>Decision-support prototype</span>
        <span>AI output requires qualified human review</span>
      </footer>
    </div>
  );
}
